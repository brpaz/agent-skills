---
name: release-drafter-setup
version: "1.0.0"
description: "Add or update Release Drafter on an existing repo — GitHub Action workflow, .github/release-drafter.yml, required labels via EndBug/label-sync — idempotently, without clobbering existing config, with a production-readiness review of anything already in place."
tags: [release-drafter, github-actions, release, changelog, label-sync]
---

# Release Drafter Setup — retrofit onto an existing repo

Use when asked to "add release drafter", "set up automated release notes", "draft releases from merged PRs" on a project that already exists. For config-option reference (template variables, replacers, advanced autolabeler patterns) see the `release-drafter` skill — this skill is only the setup procedure.

## When to Use

- Repo has no `.github/workflows/release-drafter.yml` yet and user wants draft releases generated from merged PRs.
- Repo has Release Drafter already but config looks stale/default and user wants it reviewed.

## Procedure

1. **Detect existing setup first** — never blind-overwrite, and never assume existing config is fine just because it's present.
   - Check for `.github/workflows/release-drafter.yml`, `.github/release-drafter.yml`, `.github/labels.yml`, and a label-sync workflow (`.github/workflows/label-sync.yml` or similar using `EndBug/label-sync`).
   - If any exist, **review them for production-readiness** before deciding to leave, extend, or replace:
     - Workflow triggers both `push` (updates draft) and `pull_request` with `types: [opened, reopened, synchronize]` (enables autolabeling) — missing either breaks half the feature silently.
     - `permissions:` includes `contents: write` and `pull-requests: write` — the most common cause of a draft that never appears.
     - The action is pinned to a version tag (`@v6`), not `@master`/`@main` — unpinned actions are a supply-chain risk on a production repo.
     - Every label referenced in `categories`, `version-resolver`, and `autolabeler` actually exists in `.github/labels.yml` (or `gh label list`) — a label used in config but never created just means that category/version bump never fires.
     - `tag-template` matches the format of tags already published in the repo (`gh release list` / `git tag`) — a mismatch causes a new draft every merge instead of updating one.
   - Report findings to the user as a short list (what's fine, what's not) and confirm before changing anything.

2. **CI workflow** — add `.github/workflows/release-drafter.yml` (or fix the issues found in step 1 on the existing one):

   ```yaml
   name: Release Drafter
   on:
     push:
       branches: [main]
     pull_request:
       types: [opened, reopened, synchronize]

   permissions:
     contents: write
     pull-requests: write

   jobs:
     update_release_draft:
       runs-on: ubuntu-latest
       steps:
         - uses: release-drafter/release-drafter@v6
           env:
             GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
   ```

3. **Config file** — add `.github/release-drafter.yml` with this config (the project standard — use as-is unless the user asks for changes):

   ```yaml
   name-template: '$RESOLVED_VERSION'
   tag-template: 'v$RESOLVED_VERSION'
   categories:
     - title: 'Breaking Changes'
       labels:
         - breaking
     - title: 🚀 Features
       labels:
         - feature
     - title: 🐛 Bug Fixes
       labels:
         - bug
     - title: 🔐 Security updates
       labels:
         - security
     - title: ⚠️ Maintenance
       labels:
         - maintenance
     - title: 📄 Documentation
       labels:
         - docs
     - title: 🧩 Dependency Updates
       labels:
         - dependencies
       collapse-after: 5
   change-template: '- $TITLE @$AUTHOR (#$NUMBER)'
   change-title-escapes: '\\<*_&' # You can add # and @ to disable mentions, and add ` to disable code blocks.
   exclude-labels:
     - 'skip-changelog'
   version-resolver:
     major:
       labels:
         - 'breaking'
     minor:
       labels:
         - feature
         - performance
     patch:
       labels:
         - 'bug'
         - 'maintenance'
         - 'dependencies'
         - 'security'
         - 'docs'
   autolabeler:
     - label: breaking
       title:
         - '/^break!:/i'
         - '/^BREAKING CHANGE:/i'
       branch:
         - '/^breaking\//'
     - label: feature
       title:
         - '/^feat:/i'
       branch:
         - '/^feature\//'
         - '/^feat\//'
     - label: bug
       title:
         - '/^fix:/i'
       branch:
         - '/^fix\//'
         - '/^bugfix\//'
         - '/^hotfix\//'
     - label: security
       title:
         - '/^security:/i'
       branch:
         - '/^security\//'
     - label: performance
       title:
         - '/^perf:/i'
       branch:
         - '/^perf\//'
     - label: maintenance
       title:
         - '/^chore:/i'
         - '/^refactor:/i'
         - '/^style:/i'
       branch:
         - '/^chore\//'
         - '/^refactor\//'
         - '/^maintenance\//'
     - label: docs
       title:
         - '/^docs:/i'
       branch:
         - '/^docs\//'
         - '/^documentation\//'
     - label: dependencies
       title:
         - '/^deps:/i'
         - '/^build:/i'
       branch:
         - '/^renovate\//'
         - '/^dependabot\//'
         - '/^deps\//'
   template: |
     # What's Changed
     $CHANGES

     **Full Changelog**: <https://github.com/$OWNER/$REPOSITORY/compare/$PREVIOUS_TAG...v$RESOLVED_VERSION>
   ```

   This config assumes Conventional Commits PR titles (`feat:`, `fix:`, `chore:`, etc.) drive autolabeling by title, with matching branch-name prefixes as a fallback. If the repo doesn't follow Conventional Commits, flag this to the user before installing — autolabeler won't fire and every PR will need a manual label.

4. **Labels via [EndBug/label-sync](https://github.com/EndBug/label-sync)** — the config above references `breaking`, `feature`, `bug`, `security`, `maintenance`, `docs`, `dependencies`, `performance`, `skip-changelog`. Manage these declaratively instead of one-off `gh label create` calls.

   **If `.github/labels.yml` already exists**: merge in only the entries below that are missing by `name` — never drop or overwrite labels already defined there.

   **If it doesn't exist**, create `.github/labels.yml`:

   ```yaml
   - name: breaking
     color: D73A49
     description: Breaking change

   - name: feature
     color: 0E8A16
     description: New feature

   - name: bug
     color: D93F0B
     description: Bug fix

   - name: security
     color: EE0701
     description: Security update

   - name: maintenance
     color: FEF2C0
     description: Maintenance / chore

   - name: docs
     color: 0075CA
     description: Documentation

   - name: dependencies
     color: 0366D6
     description: Dependency update

   - name: performance
     color: FBCA04
     description: Performance improvement

   - name: skip-changelog
     color: FFFFFF
     description: Exclude from release notes
   ```

   **If no label-sync workflow exists**, add `.github/workflows/label-sync.yml`:

   ```yaml
   name: Sync labels

   on:
     push:
       branches: [main]
       paths:
         - .github/labels.yml
     workflow_dispatch:

   jobs:
     labels:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: EndBug/label-sync@v2
           with:
             config-file: .github/labels.yml
   ```

   If a label-sync workflow already exists but points at a different config path, use that path instead of introducing a second one.

5. **Verify before finishing**:
   - Confirm workflow permissions are `contents: write` + `pull-requests: write`.
   - If `gh` is available, run `gh workflow list` to confirm both workflows registered.
   - Run the label-sync workflow once (`gh workflow run label-sync.yml` or merge the `labels.yml` change to `main`) and confirm with `gh label list` that all labels referenced by `release-drafter.yml` now exist.
   - Recommend the user merge one test PR to confirm a draft release appears and gets the right category/label before considering setup done — report this as a pending step if you can't do it yourself.

## Non-Goals

- Not for bulk/multi-repo rollout — that's a scripted codemod job, not a per-repo interactive skill.
- Not for publishing/tagging strategy decisions (auto-publish on tag, monorepo per-service configs, semantic-release integration) — those are real design choices; surface the options from the `release-drafter` reference skill and ask rather than picking one.
- Not a substitute for the `release-drafter` skill's config reference — come back to that skill for template variables, replacers, or advanced autolabeler patterns.
