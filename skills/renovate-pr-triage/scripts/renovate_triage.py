#!/usr/bin/env python3
"""Find open Renovate PRs across the authenticated user's personally-owned
repos, report which ones are safe to merge, and (with --merge) merge exactly
that set after re-checking each one is still safe.

Shells out to the `gh` CLI for all GitHub access, so it reuses the caller's
existing `gh auth login` session instead of handling credentials itself.
"""
import argparse
import json
import re
import subprocess
import sys
import time

PAGE_SIZE = 40  # GitHub's GraphQL search rejects statusCheckRollup lookups above ~50 nodes/page
MAX_PAGES_DEFAULT = 15

SEARCH_QUERY = """
query($q: String!, $cursor: String, $n: Int!) {
  search(query: $q, type: ISSUE, first: $n, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes {
      ... on PullRequest {
        number
        title
        url
        body
        isDraft
        author { login }
        repository { nameWithOwner }
        mergeStateStatus
        commits(last: 1) {
          nodes { commit { statusCheckRollup { state } } }
        }
      }
    }
  }
}
"""

RECHECK_QUERY = """
query($owner: String!, $name: String!, $num: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $num) {
      state
      mergeStateStatus
      commits(last: 1) {
        nodes { commit { statusCheckRollup { state } } }
      }
    }
  }
}
"""

RENOVATE_LOGIN_RE = re.compile(r"renovate", re.IGNORECASE)
SEMVER_RE = re.compile(r"\d+\.\d+(?:\.\d+)?")
SEPARATOR_ROW_RE = re.compile(r"^\|?[\s:|-]+\|?$")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def clean_cell(text):
    text = MARKDOWN_LINK_RE.sub(r"\1", text)
    text = text.replace("`", "").strip()
    return text.replace("|", "/")  # a literal pipe would break the table we print later


def parse_dependency_rows(body):
    """Every Renovate PR body opens with a markdown table listing the
    packages it touches, but the column set and order vary per-repo config
    (some have Type, some have Age/Confidence/Pending, some don't) — so read
    the header row to find where Package/Update/Change actually are instead
    of assuming a fixed layout."""
    lines = (body or "").splitlines()
    col_index = None
    i = 0
    while i < len(lines) - 1:
        line = lines[i].strip()
        if line.startswith("|") and SEPARATOR_ROW_RE.match(lines[i + 1].strip()):
            cells = [c.strip().lower() for c in line.strip("|").split("|")]
            if "package" in cells:
                col_index = {name: idx for idx, name in enumerate(cells)}
                i += 2
                break
        i += 1
    if col_index is None:
        return []

    pkg_i = col_index.get("package")
    change_i = col_index.get("change")
    update_i = col_index.get("update")
    rows = []
    while i < len(lines) and lines[i].strip().startswith("|"):
        cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        pkg = clean_cell(cells[pkg_i]) if pkg_i is not None and pkg_i < len(cells) else ""
        if pkg:
            rows.append({
                "package": pkg,
                "change": clean_cell(cells[change_i]) if change_i is not None and change_i < len(cells) else "",
                "update": clean_cell(cells[update_i]) if update_i is not None and update_i < len(cells) else "",
            })
        i += 1
    return rows


def summarize_rows(rows, title, max_items=3):
    if not rows:
        return title  # onboarding PRs ("Configure Renovate") carry no dependency table
    parts = [f"{r['package']}: {r['change']}" if r["change"] else r["package"] for r in rows[:max_items]]
    summary = "; ".join(parts)
    if len(rows) > max_items:
        summary += f"; +{len(rows) - max_items} more"
    return summary


def gh(*args, check=True):
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {result.stderr.strip()}")
    return result


def graphql(query, **fields):
    args = ["api", "graphql", "-f", f"query={query}"]
    for key, value in fields.items():
        args += ["-F", f"{key}={value}"]
    result = gh(*args, check=False)
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)


def graphql_with_retry(query, attempts=3, **fields):
    for attempt in range(1, attempts + 1):
        resp = graphql(query, **fields)
        if resp is not None:
            return resp
        time.sleep(attempt * 2)
    return None


def fetch_renovate_prs(login, max_pages):
    prs = []
    cursor = "null"
    page = 0
    while True:
        page += 1
        resp = graphql_with_retry(
            SEARCH_QUERY,
            q=f"is:pr is:open user:{login} archived:false",
            cursor=cursor,
            n=PAGE_SIZE,
        )
        if resp is None:
            print(f"warning: page {page} failed after 3 attempts (GitHub timeout/error) "
                  "— stopping early with partial results", file=sys.stderr)
            break

        search = resp["data"]["search"]
        for node in search["nodes"]:
            login_field = (node.get("author") or {}).get("login", "")
            if RENOVATE_LOGIN_RE.search(login_field):
                prs.append(node)

        page_info = search["pageInfo"]
        if not page_info["hasNextPage"] or page >= max_pages:
            break
        cursor = page_info["endCursor"]

    return prs


def version_major_differs(text):
    versions = SEMVER_RE.findall(text or "")
    return len(versions) >= 2 and versions[0].split(".")[0] != versions[-1].split(".")[0]


def is_major_bump(title, rows):
    if rows:
        # Some repo configs' dependency table has no Update column at all
        # (e.g. Package/Change/Age/Confidence only) — every row's "update"
        # comes back empty in that case, which must NOT be read as "nothing
        # here is major". Fall back to each row's own Change cell instead.
        if any(r["update"] for r in rows):
            return any(r["update"].lower() == "major" for r in rows)
        return any(version_major_differs(r["change"]) for r in rows)
    # No parsed dependency table (custom PR body template) — fall back to
    # comparing version numbers found in the title.
    return version_major_differs(title)


def ci_state(pr):
    nodes = pr.get("commits", {}).get("nodes", [])
    if not nodes:
        return "NONE"
    state = nodes[0]["commit"]["statusCheckRollup"]
    return (state or {}).get("state") or "NONE"


def classify(pr, rows):
    """Returns (ready: bool, reason: str). Ready only when CI is green (or
    absent), GitHub reports the PR as cleanly mergeable, and it's not a
    major bump. Renovate's own PR body carries a dependency table with an
    explicit major/minor/patch update-type column — reading that is far
    more reliable than guessing from the title, which varies a lot with
    commitMessage config."""
    ci = ci_state(pr)
    mss = pr.get("mergeStateStatus") or "UNKNOWN"
    major = is_major_bump(pr.get("title", ""), rows)

    if pr.get("isDraft"):
        return False, "draft PR"
    if ci == "FAILURE":
        return False, "CI failing"
    if ci == "PENDING":
        return False, "CI still running"
    if mss in ("DIRTY", "CONFLICTING"):
        return False, "merge conflict"
    if mss == "BLOCKED":
        return False, "required review/check not satisfied"
    if mss == "UNKNOWN":
        return False, "GitHub still computing mergeability, retry shortly"
    if mss == "UNSTABLE":
        return False, "non-required check failing"
    if major:
        return False, "major version bump — needs manual review"
    if mss == "CLEAN" and ci in ("SUCCESS", "NONE"):
        return True, ""
    return False, f"unrecognized state (ci={ci} merge={mss})"


def pad(text, width):
    # Table columns are padded with spaces (not just `-`-delimited) so the
    # raw script output is already readable before any markdown renderer
    # touches it — this is read directly off the terminal as often as not.
    return text + " " * max(0, width - len(text))


def print_repo_table(repo, rows):
    headers = ["PR", "Status", "Summary", "Reason"]
    widths = [max(len(headers[i]), max((len(r[i]) for r in rows), default=0)) for i in range(4)]
    print(f"## {repo}\n")
    print("| " + " | ".join(pad(h, w) for h, w in zip(headers, widths)) + " |")
    print("|" + "|".join("-" * (w + 2) for w in widths) + "|")
    for row in rows:
        print("| " + " | ".join(pad(c, w) for c, w in zip(row, widths)) + " |")
    print()


def print_report(prs):
    by_repo = {}
    for pr in prs:
        repo = pr["repository"]["nameWithOwner"]
        by_repo.setdefault(repo, []).append(pr)

    ready_prs = []
    for repo in sorted(by_repo):
        table_rows = []
        for pr in sorted(by_repo[repo], key=lambda p: p["number"], reverse=True):
            dep_rows = parse_dependency_rows(pr.get("body", ""))
            ready, reason = classify(pr, dep_rows)
            summary = summarize_rows(dep_rows, pr["title"])
            if len(summary) > 90:
                summary = summary[:87] + "..."
            status = "✅ Ready" if ready else "⛔ Blocked"
            if ready:
                ready_prs.append(pr)
            table_rows.append([f"#{pr['number']}", status, summary, reason])
        print_repo_table(repo, table_rows)

    print(f"{len(ready_prs)}/{len(prs)} ready to merge.")
    return ready_prs


def recheck(pr):
    owner, name = pr["repository"]["nameWithOwner"].split("/", 1)
    resp = graphql(RECHECK_QUERY, owner=owner, name=name, num=pr["number"])
    if resp is None:
        return None
    fresh_pr = resp["data"]["repository"]["pullRequest"]
    ci = ci_state(fresh_pr)
    mss = fresh_pr.get("mergeStateStatus") or "UNKNOWN"
    still_ready = fresh_pr.get("state") == "OPEN" and mss == "CLEAN" and ci in ("SUCCESS", "NONE")
    return still_ready, fresh_pr.get("state"), mss, ci


def wait_until_ready(pr, timeout, interval):
    """Poll one PR's fresh state until it's cleanly mergeable, genuinely
    blocked, or the timeout elapses.

    Two different things both need waiting out here, and this can't tell
    them apart up front: the PR's own CI can still be running (ci=PENDING),
    and — because every open PR against a base branch gets its
    mergeability recomputed whenever anything merges into that base —
    merging the previous PR in this same run routinely flips a sibling's
    mergeStateStatus to UNKNOWN/UNSTABLE for a while even though nothing
    is actually wrong with it. Both settle on their own; a merge conflict
    or a real CI failure doesn't, so those return immediately instead of
    waiting out the full timeout.
    """
    repo = pr["repository"]["nameWithOwner"]
    num = pr["number"]
    elapsed = 0
    while True:
        rechecked = recheck(pr)
        if rechecked is None:
            return None, "could not re-check state"
        still_ready, state, mss, ci = rechecked
        if state != "OPEN":
            return False, f"no longer open (state={state})"
        if still_ready:
            return True, None
        if mss in ("DIRTY", "CONFLICTING", "BLOCKED") or ci == "FAILURE":
            return False, f"merge={mss} ci={ci}"
        if elapsed >= timeout:
            return False, f"still not settled after {timeout}s (merge={mss} ci={ci})"
        print(f"  ⏳ {repo} #{num}: merge={mss} ci={ci}, waiting ({elapsed}s/{timeout}s)...")
        time.sleep(interval)
        elapsed += interval


def merge_method_for(repo, cache):
    if repo not in cache:
        result = gh("api", f"repos/{repo}",
                     "--jq", "{squash: .allow_squash_merge, merge: .allow_merge_commit, rebase: .allow_rebase_merge}")
        perms = json.loads(result.stdout)
        if perms.get("squash"):
            cache[repo] = "--squash"
        elif perms.get("merge"):
            cache[repo] = "--merge"
        else:
            cache[repo] = "--rebase"
    return cache[repo]


def merge_ready_prs(ready_prs, wait_timeout, wait_interval):
    # One PR at a time, on purpose: merging into a base branch makes GitHub
    # recompute mergeability for every other open PR against that base, so
    # firing merges back-to-back stomps on the next PR's freshly-rechecked
    # state before it's settled. Waiting for each PR to actually land (or
    # definitively fail) before touching the next one avoids that.
    print(f"\nMerging one at a time (each PR gets up to {wait_timeout}s to settle before it's skipped)...")
    merge_method_cache = {}
    for pr in ready_prs:
        repo = pr["repository"]["nameWithOwner"]
        num = pr["number"]

        ok, reason = wait_until_ready(pr, wait_timeout, wait_interval)
        if ok is None:
            print(f"  ⚠️  {repo} #{num}: {reason}, skipped")
            continue
        if not ok:
            print(f"  ⚠️  {repo} #{num}: {reason}, skipped — re-run the triage report to see current status")
            continue

        method = merge_method_for(repo, merge_method_cache)
        result = gh("pr", "merge", pr["url"], method, "--delete-branch", check=False)
        if result.returncode == 0:
            print(f"  ✅ {repo} #{num}: merged ({method.lstrip('-')})")
        else:
            print(f"  ❌ {repo} #{num}: merge failed — check manually (gh pr view {num} -R {repo} --web)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--merge", action="store_true",
                         help="Merge PRs classified as ready (re-checks each one first)")
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES_DEFAULT,
                         help=f"Max search result pages of {PAGE_SIZE} PRs each (default {MAX_PAGES_DEFAULT})")
    parser.add_argument("--repo", default=None,
                         help="Only include repos whose name contains this substring "
                              "(case-insensitive), e.g. --repo vicinae")
    parser.add_argument("--wait-timeout", type=int, default=600,
                         help="With --merge, max seconds to wait for a single PR's CI/mergeability "
                              "to settle before skipping it (default 600)")
    parser.add_argument("--wait-interval", type=int, default=15,
                         help="With --merge, seconds between re-checks while waiting (default 15)")
    args = parser.parse_args()

    login = gh("api", "user", "--jq", ".login").stdout.strip()

    # user:<login> scopes the search to repos owned by that user's personal
    # namespace, excluding org repos — this keeps the triage to
    # "personally-owned repos" rather than everything the account can push to.
    prs = fetch_renovate_prs(login, args.max_pages)

    if args.repo:
        needle = args.repo.lower()
        prs = [pr for pr in prs if needle in pr["repository"]["nameWithOwner"].lower()]

    if not prs:
        scope = f" matching '{args.repo}'" if args.repo else ""
        print(f"No open Renovate PRs found in {login}'s personally-owned repos{scope}.")
        return

    print(f"Renovate PRs for {login} (personal repos only) — {len(prs)} found\n")
    ready_prs = print_report(prs)

    if args.merge and ready_prs:
        merge_ready_prs(ready_prs, args.wait_timeout, args.wait_interval)


if __name__ == "__main__":
    main()
