---
name: renovate-pr-triage
description: Finds every open Renovate bot PR across the authenticated user's personally-owned GitHub repos, classifies each as ready-to-merge or blocked (CI failing, merge conflict, major version bump, review required, etc.), shows a per-repo report, and — only after the user explicitly confirms — merges exactly the ones that qualify. Use whenever the user wants to clear out a backlog of Renovate dependency-bump PRs, asks "merge my renovate PRs", "clean up dependency PRs across my repos", "what renovate PRs can I merge", or wants a bulk-merge workflow for automated dependency update PRs specifically (not general PR triage — see the pr-triage skill for that).
---

# Renovate PR Triage

Clear a Renovate PR backlog across many personal repos in one pass, without
blindly merging anything that isn't actually safe.

## Why this is a two-step flow, not one command

Merging a PR is visible and only cheaply reversible (revert commit, not a
free undo) — and across dozens of personal repos, a single run can touch a
lot of PRs at once. So this skill always shows the full per-repo report
first and stops. Only merge once the user has looked at the report and
explicitly says to proceed (e.g. "merge them", "go ahead", "merge the ready
ones"). Never pass `--merge` on the first invocation.

## What counts as "ready to merge"

A PR qualifies only when **all** of these hold:
- CI is green, or the repo has no CI configured at all.
- GitHub reports it as cleanly mergeable (no conflicts, no unmet branch
  protection requirement).
- It is not a major version bump. Every Renovate PR body opens with a
  dependency table (columns vary per repo config — some have Type, some
  have Age/Confidence — so the script reads the header row to find
  Package/Update/Change rather than assuming a fixed layout) with an
  explicit update-type column (major/minor/patch/pin/digest); the script
  reads that first, and falls back to comparing version numbers in the
  title only when a PR uses a custom template with no table at all.

Everything else is reported with a specific blocking reason (CI failing, CI
still running, merge conflict, blocked on required review/check, major
bump, etc.) so the user can see *why* a given PR isn't in the ready set —
this is usually more useful to them than the ready list itself, since it's
where the actual decisions live.

"Personally-owned repos" means the account's own namespace (`user:<login>`
in the GitHub search), not org repos — org repos usually have other
maintainers and shared review/CI conventions this skill has no visibility
into, so it stays out of that scope.

## Running it

```bash
python3 scripts/renovate_triage.py
```

Prints one markdown table per repo — columns `PR | Status | Summary |
Reason` — followed by a `<ready>/<total> ready to merge.` line, then exits;
no merging happens yet. The Summary column is built from that PR's parsed
dependency table (`package: old → new`, joined for multi-package PRs, e.g.
Renovate's grouped "update all non-major deps"), not the raw PR title —
this is what actually tells the user what's changing, since Renovate
titles get terse or vague on grouped updates. A PR with no dependency
table at all (e.g. the "Configure Renovate" onboarding PR) falls back to
showing its title.

After the user confirms, re-run with `--merge`:

```bash
python3 scripts/renovate_triage.py --merge
```

This reprints the same report, then merges the ready ones **one at a time**,
waiting for each to actually be safe to touch before moving to the next.
This matters because merging into a base branch makes GitHub recompute
mergeability for every other open PR against that base — so a PR that was
`CLEAN` in the report can show up `UNKNOWN` or `UNSTABLE` moments later for
no reason of its own, just because a sibling PR merged first. The script
polls each PR (every 15s, up to 600s by default — `--wait-interval` /
`--wait-timeout` to change either) and only gives up early when the state
is a real blocker (merge conflict, required check actually failing) rather
than transient recompute noise. Don't reach for firing merges concurrently
or re-invoking `--merge` repeatedly to work around a slow settle — this is
what the waiting is for.

Each repo's merge method (squash / merge commit / rebase) is read from
that repo's settings rather than assumed, and it deletes the head branch
after merging (Renovate recreates it on the next run, so this doesn't lose
anything).

Needs `gh` authenticated (`gh auth status`) with repo write access. No other
dependencies — stdlib only.

If the report needs to go deeper than 15 pages of 40 PRs (600 PRs), raise
it: `--max-pages 25`. To scope either mode to a subset of repos, use
`--repo <substring>` (case-insensitive match against `owner/name`), e.g.
`--repo vicinae`.

## After running

Show the user the ready-to-merge rows, same shape as the script's tables
(PR, Summary, per repo) — the Summary column is the point, since it's what
tells them what's actually changing, not just that something is. For the
blocked ones, only call out patterns worth their attention (e.g. "12 repos
have failing CI on every renovate PR" is worth a sentence; listing all 200
individually is not) — the full detail is already in the script output
above if they want to scroll to it.

If the user wants to act on a specific blocked PR (see why CI is failing,
resolve a conflict, review a major bump), use `gh pr view <url> --web` or
`gh pr checks <url>` — don't try to re-derive that from data this script
already fetched.
