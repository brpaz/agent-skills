---
name: gitleaks-setup
version: "1.0.0"
description: "Add or update Gitleaks secret-scanning to an existing repo — GitHub Action workflow, .gitleaks.toml, hook via lefthook/pre-commit, Taskfile task, devenv/mise tool pin — idempotently, without clobbering existing config."
tags: [gitleaks, security, github-actions, pre-commit, lefthook, taskfile, devenv, mise, secret-scanning]
---

# Gitleaks Setup — retrofit secret scanning onto an existing repo

Use this skill when asked to "add gitleaks", "add secret scanning", "set up gitleaks" on a project that already exists (not a fresh scaffold).

## When to Use

- Repo has no `.github/workflows/gitleaks.yml` yet and user wants CI secret scanning.
- Repo has gitleaks already but config looks stale/default and user wants it reviewed.
- User wants a local hook (lefthook or pre-commit) in addition to (or instead of) CI.
- Repo has a Taskfile, devenv, or mise config that should gain a gitleaks task/tool pin.

## Procedure

1. **Detect existing setup first** — never blind-overwrite.
   - Check for `.github/workflows/gitleaks.yml`, `.gitleaks.toml`, `lefthook.yml`/`lefthook.yaml`, `.pre-commit-config.yaml`, `Taskfile.yml`/`Taskfile.yaml`, `devenv.nix`/`devenv.yaml`, and `.mise.toml`/`mise.toml`.
   - If present, read it, summarize what's there, ask whether to leave, extend, or replace before touching it.
   - Hook tooling: prefer whichever is already in the repo (lefthook vs pre-commit). Don't introduce a second hook manager. If neither exists, ask which the user wants, or default to lefthook for non-Python repos / pre-commit for Python repos.

2. **CI workflow** — add `.github/workflows/gitleaks.yml`:

   ```yaml
   name: gitleaks
   on: [push, pull_request]
   jobs:
     scan:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
           with:
             fetch-depth: 0
         - uses: gitleaks/gitleaks-action@v2
           env:
             GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
   ```

   `fetch-depth: 0` is required — gitleaks scans full history by default; shallow checkout produces false negatives.

3. **Config file** — only add `.gitleaks.toml` if the repo needs custom allowlisting (test fixtures, known false-positive patterns, vendored files). Don't add a boilerplate config with nothing in it; default gitleaks rules are fine without one.

   ```toml
   [allowlist]
   description = "project-specific false positives"
   paths = [
     '''testdata/.*''',
   ]
   ```

4. **Local hook** — only if the project already uses a hook manager, or the user explicitly asks for local enforcement, not just CI.

   **If `lefthook.yml`/`lefthook.yaml` exists** (or user picks lefthook): add/merge a `pre-commit` command — don't clobber existing commands under that hook.

   ```yaml
   pre-commit:
     commands:
       gitleaks:
         run: gitleaks protect --staged --verbose --redact
   ```

   If lefthook isn't installed yet, note it needs `lefthook install` once locally (or add that call to the Taskfile/devenv setup task from step 5/6).

   **If `.pre-commit-config.yaml` exists** (or user picks pre-commit):

   ```yaml
   - repo: https://github.com/gitleaks/gitleaks
     rev: v8.21.2   # check latest tag before pinning
     hooks:
       - id: gitleaks
   ```

5. **Taskfile task** — if `Taskfile.yml`/`Taskfile.yaml` exists, add a `gitleaks` (or `security:gitleaks`) task rather than expecting users to remember the raw CLI invocation. Match the naming/namespacing convention already used by other tasks in the file.

   ```yaml
   tasks:
     gitleaks:
       desc: Scan repo for leaked secrets
       cmds:
         - gitleaks detect --source . --redact -v
   ```

   If the Taskfile has a `ci` or `check`/`test` aggregate task that runs other linters, add `gitleaks` as a dependency there too (`deps: [gitleaks]`) only if that matches the existing pattern for other scanners.

6. **devenv / mise tool pin** — if the repo manages its toolchain via one of these, pin gitleaks there instead of (or in addition to) leaving install to the CI step:

   **devenv** (`devenv.nix`): add to `packages`:

   ```nix
   { pkgs, ... }: {
     packages = [
       pkgs.gitleaks
       # ...existing packages
     ];
   }
   ```

   **mise** (`.mise.toml` / `mise.toml`): add under `[tools]`:

   ```toml
   [tools]
   gitleaks = "latest"   # or pin an exact version, e.g. "8.21.2"
   ```

   Only touch these if the file already exists — don't introduce devenv or mise into a repo that isn't using them just to install one CLI.

7. **Verify before finishing**:
   - Run `gitleaks detect --source . -v` locally if the CLI is available, to confirm the repo passes clean (or surface pre-existing findings to the user rather than silently shipping a red CI job).
   - If findings turn up, report them — do not decide unilaterally to add them to an allowlist to make CI green.
   - If a Taskfile task was added, run it (`task gitleaks`) to confirm it works.
   - If a hook was added, confirm the hook manager is installed/initialized (`lefthook install` / `pre-commit install`) — a hook config with no installed manager silently does nothing.

## Non-Goals

- Not for bulk/multi-repo rollout — that's a scripted codemod (e.g. octoherd) job, not a per-repo interactive skill.
- Not for scaffolding a brand-new repo — use the project's normal bootstrap flow (e.g. `project-webapp` skill or copier template) and bake gitleaks into that instead.
