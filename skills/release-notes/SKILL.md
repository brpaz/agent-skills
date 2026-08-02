---
name: release-notes
version: "1.0.0"
description: "Generate release notes from all commits/PRs merged since the latest published GitHub release. Reuses .github/release-drafter.yml (categories, version-resolver, template, exclude-labels) when present; falls back to Conventional Commits grouping otherwise."
tags: [release-notes, changelog, release-drafter, git, github, conventional-commits, versioning]
---

# Release Notes — generate from commits since the last published release

Use when asked to "generate release notes", "write a changelog for this release", "draft the next release notes", or "what's changed since the last release". This produces the notes text (and optionally a GitHub draft release) — it does not set up Release Drafter itself; use the `release-drafter-setup` skill for that.

## When to Use

- User wants release notes / a changelog for everything merged since the last published release.
- Repo has `.github/release-drafter.yml` and the user wants notes that match its categories/format without waiting for the Action to run (e.g. running it locally, or the repo doesn't push to `main` in a way that triggers the workflow).
- Repo has no Release Drafter config at all — fall back to a Conventional-Commits-based summary.

## Procedure

### 1. Find the latest **published** release

Not the latest tag, and not a draft — release-drafter and `gh` both distinguish drafts from published releases, and the user asked specifically for "since the latest published release".

```bash
gh release list --exclude-drafts --limit 1 --json tagName,publishedAt,isLatest
```

- If `gh` isn't available or the repo has no GitHub remote, fall back to `git describe --tags --abbrev=0` and tell the user this can't distinguish a published release from a tag that only exists locally or backs a draft.
- If there are no releases yet, treat this as the first release: gather commits from the repo root (`git rev-list --max-parents=0 HEAD`) to `HEAD`.

### 2. Detect Release Drafter config

Check for `.github/release-drafter.yml` (or the path referenced by a custom `config-name` in `.github/workflows/release-drafter.yml`, if the default doesn't exist). If found, read and reuse, verbatim, whatever it defines:

- `categories` — label → section-title mapping
- `version-resolver` — label → major/minor/patch mapping, plus `default`
- `exclude-labels` / `include-labels`
- `template`, `change-template`, `category-template`, `no-changes-template`
- `autolabeler` — regex/glob rules, used in step 4 if a PR has no real labels yet
- `exclude-contributors`

If no config exists, don't invent one — fall back to the Conventional Commits grouping in step 4b and say so in the output ("no release-drafter.yml found, grouped by commit type").

### 3. Gather what changed since that release

Prefer PR-level data over raw commits — it's what release-drafter itself uses (labels, author, PR number), and this repo's `release-drafter-setup`/`release-drafter` skills already assume a PR-based workflow:

```bash
gh pr list --state merged --base <default-branch> --search "merged:>=<published_at_date>" \
  --json number,title,author,labels,url,mergedAt
```

If `gh` isn't available, or the repo merges via direct pushes to the default branch rather than PRs (check `git log --merges` — few/no merge commits is a signal), fall back to raw commits instead:

```bash
git log <last-tag>..HEAD --pretty=format:'%H%x09%an%x09%s'
```

Either way, exclude merge commits of Release Drafter's own draft-release bookkeeping, if any, and drop anything matching `exclude-labels`/skip markers already configured.

### 4. Categorize

**4a. Config present (PR data available):** for each merged PR, match its real labels against `categories`. If a PR has no labels yet (common when generating notes ahead of the Action running), simulate `autolabeler`: test the PR title/branch/changed files against the configured regex/glob rules and assign the resulting label before categorizing. Apply `exclude-labels`/`include-labels` exactly as release-drafter would.

**4b. No config, or no PR data (raw commits):** group by Conventional Commit type prefix, using the same section names as this repo's own `release-drafter-setup` default config for consistency:

| Prefix | Section |
|---|---|
| `feat` | 🚀 Features |
| `fix` | 🐛 Bug Fixes |
| `security` | 🔐 Security updates |
| `chore`, `refactor`, `style` | ⚠️ Maintenance |
| `docs` | 📄 Documentation |
| `deps`, `build` | 🧩 Dependency Updates |
| `perf` | (Performance, if the repo's config has no equivalent, add one) |
| anything else / no prefix | Other Changes |

A `type!:` or `BREAKING CHANGE:` footer always goes in a leading "Breaking Changes" section regardless of its other type.

### 5. Resolve the next version

- If `version-resolver` is defined, apply it: find the highest-priority label present across all included changes (major > minor > patch) and bump the previous version's corresponding component. Use `default` when nothing matches.
- If no config, use the same precedence via Conventional Commit types: any `!`/`BREAKING CHANGE` → major, any `feat` → minor, otherwise → patch.
- Base the bump on the previous published release's version, not on any version string in the working tree (package.json, etc.) unless the user says those are out of sync and should be used instead.

### 6. Render

- If a `template` exists in the config, fill in `$CHANGES` (grouped per `category-template`/`change-template`), `$CONTRIBUTORS` (minus `exclude-contributors`), `$PREVIOUS_TAG`, `$RESOLVED_VERSION`, `$OWNER`/`$REPOSITORY` exactly as release-drafter would render them, so the output matches what the Action would have produced.
- Otherwise, use a plain default: one `##` heading per category in the order defined (or the table order from step 4b), each entry as `- $TITLE (#$NUMBER) @$AUTHOR` or `- $SUBJECT ($SHORT_SHA)` for raw commits, plus a full-changelog compare link (`https://github.com/$OWNER/$REPOSITORY/compare/$PREVIOUS_TAG...$NEW_TAG`) when a GitHub remote is known.

### 7. Present, don't auto-publish

Show the rendered notes to the user. Creating or publishing an actual GitHub release is a repo-visible action — confirm before doing either:

- **Draft only** (safe default if asked to "create" it): `gh release create <tag> --draft --title <title> --notes-file <file>`.
- **Publish**: only if the user explicitly asks — never publish (non-draft) a release without that explicit ask, and never overwrite an existing draft's content without showing the diff first.

## Non-Goals

- Not for setting up Release Drafter itself (workflow, config, labels) — that's the `release-drafter-setup` skill; this skill only consumes an existing config.
- Not for choosing a versioning/branching strategy — it resolves *a* next version from existing config or Conventional Commits, it doesn't decide the project's versioning policy.
- Not a substitute for running the actual Release Drafter GitHub Action in CI — this is for on-demand/local generation (e.g., previewing notes, or repos where the Action hasn't run yet), not a replacement for it.
