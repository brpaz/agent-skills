---
name: renovate-setup
version: "1.0.0"
description: "Add or update Renovate on an existing project — infer the tech stack, generate a renovate.json tuned to it (managers, grouping, schedule, automerge, digest pinning), following https://docs.renovatebot.com/ best practices, idempotently, without clobbering existing config."
tags: [renovate, dependencies, automation, github-actions, docker]
---

# Renovate Setup — retrofit dependency automation onto an existing project

Use when asked to "add Renovate", "set up dependency updates", "automate dependency bumps" on a project that already exists. Reference: [docs.renovatebot.com](https://docs.renovatebot.com/).

## Use Alongside

- `release-drafter-setup` — if already run, its `dependencies` label should be reused here instead of inventing a second one.
- `docker-setup` / `dockerfile` / `docker-compose` — if Docker is present, Renovate should track base image and Compose image tags too, not just app dependencies.
- `github-actions-docker` — if GitHub Actions workflows exist, Renovate should pin/update action versions, not just runtime dependencies.

## When to Use

- Repo has no Renovate config yet and the user wants automated dependency PRs.
- Repo has Renovate already but the config looks like an unmodified default and the user wants it tuned to the actual stack.

## Procedure

### 1. Detect existing setup first — never blind-overwrite, review before trusting

- Check for `renovate.json`, `renovate.json5`, `.github/renovate.json`, `.renovaterc`/`.renovaterc.json`, and a `"renovate"` key in `package.json`.
- If found, read it and check against the best-practice list below rather than assuming it's fine:
  - `extends` includes `config:best-practices` (or at least `config:recommended`) — a bare `{}` or hand-rolled config missing this misses vulnerability alerts, sane defaults, and lockfile maintenance.
  - A `schedule` exists — otherwise PRs can land at any hour and flood the repo.
  - `packageRules` don't blanket-automerge majors — that's a common footgun in copy-pasted configs.
  - Labels referenced actually exist in the repo (`gh label list`).
  - Enabled managers actually match what's in the repo (e.g. a `dockerfile` manager entry in a repo with no Dockerfile is dead config, and — more importantly — a repo *with* Docker/GitHub Actions but no matching manager config means those surfaces are silently unmanaged).
- Report findings, then ask whether to leave, extend, or replace before touching it.

### 2. Analyze the project before writing config

Read manifests to determine which Renovate managers are relevant — don't enable managers for ecosystems that aren't present, and don't skip ones that are:

| Signal file(s) | Renovate manager(s) to enable/tune | Notes |
|---|---|---|
| `package.json` + lockfile | `npm` | Detect npm/pnpm/yarn from lockfile; if `workspaces`/`pnpm-workspace.yaml`, this is a monorepo — group accordingly |
| `go.mod` | `gomod` | On by default; note Go's own minimum-version selection semantics |
| `pyproject.toml` (poetry/pdm) / `requirements*.txt` / `Pipfile` | `poetry`, `pip_requirements`, `pipenv` | Enable only the one(s) actually used |
| `Cargo.toml` | `cargo` | |
| `Gemfile` | `bundler` | |
| `composer.json` | `composer` | |
| `pom.xml` / `build.gradle*` | `maven` / `gradle` | |
| `Dockerfile*` | `dockerfile` | Pin digests (see step 4) |
| `docker-compose.yml`/`compose.yaml` | `docker-compose` | Same image references as above |
| `.github/workflows/*.yml` | `github-actions` | Pin action digests (see step 4) |
| `*.tf` | `terraform` | If present |
| `Chart.yaml` / `helmfile.yaml` | `helm-values`/`helmv3` | If present |

Also check: is there already a commit-message convention (`commitlint` config, `conventional-commits` skill signal) — if so, set `semanticCommits: "enabled"` with a matching `semanticCommitType`; if not, leave `semanticCommits: "auto"` (Renovate infers from git history).

### 3. Base config

Prefer `renovate.json` at repo root (widest tool compatibility) unless the repo already uses JSON5/JSONC elsewhere, in which case `renovate.json5` with comments is fine. Start from `config:best-practices` and layer only what the stack analysis justifies — don't paste in every option available:

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "config:best-practices",
    ":dependencyDashboard",
    "helpers:pinGitHubActionDigests"
  ],
  "timezone": "UTC",
  "schedule": ["before 6am on monday"],
  "labels": ["dependencies"],
  "prConcurrentLimit": 10,
  "prHourlyLimit": 2,
  "lockFileMaintenance": {
    "enabled": true,
    "schedule": ["before 6am on monday"]
  },
  "packageRules": [
    {
      "matchUpdateTypes": ["minor", "patch"],
      "matchCurrentVersion": "!/^0/",
      "groupName": "minor and patch updates",
      "automerge": true
    },
    {
      "matchUpdateTypes": ["major"],
      "automerge": false,
      "labels": ["dependencies", "major-update"]
    }
  ]
}
```

Notes:
- `config:best-practices` already turns on vulnerability alerts, dependency dashboard, and rate limiting — don't re-declare what it already sets, only override what this project needs differently.
- `labels: ["dependencies"]` — reuse the label from `release-drafter-setup` if that skill's already been run on this repo (check `.github/labels.yml` / `.github/release-drafter.yml` first); otherwise confirm the label exists or will be created before shipping this config.
- `matchCurrentVersion: "!/^0/"` excludes 0.x packages from the automerge group, since semver treats minor bumps as breaking below 1.0 — don't automerge those blindly.
- `timezone`/`schedule` should be asked about, not assumed — default to UTC Monday morning only as a starting point.

### 4. Stack-specific tuning (only add what step 2 found)

**Docker / Compose** (if `Dockerfile`/`docker-compose.yml` present):

```json
{
  "packageRules": [
    {
      "matchManagers": ["dockerfile", "docker-compose"],
      "pinDigests": true
    }
  ]
}
```

**GitHub Actions** (if `.github/workflows/` present): the `helpers:pinGitHubActionDigests` preset in the base config already handles this — no extra packageRule needed unless the user wants actions grouped separately from app dependencies.

**Monorepo / workspaces** (if `workspaces` in `package.json` or `pnpm-workspace.yaml`):

```json
{
  "packageRules": [
    {
      "matchFileNames": ["packages/**"],
      "groupName": "workspace dependencies"
    }
  ]
}
```

**Python** (if `pyproject.toml` with poetry): confirm `poetry` manager is picking up the right lock file path; no extra config needed for a single-project layout.

**Private/internal registries**: if any manifest points at a private registry or internal package scope, this needs `hostRules`/`packageRules` with credentials sourced from repo/org secrets — flag this to the user rather than guessing at auth, since it touches secrets management.

### 5. Validate before finishing

```bash
npx --yes renovate-config-validator
# or, without a local Node toolchain:
docker run --rm -v "$PWD":/repo -w /repo renovate/renovate renovate-config-validator
```

Fix any validator errors before considering the file done — an invalid config fails silently in the Renovate app/job rather than erroring visibly to the user.

### 6. Note what this skill does *not* do — enabling the bot

Writing `renovate.json` only prepares the repo; it does not turn Renovate on. Flag as a pending step, don't claim it's live:

- **Mend Renovate App (hosted, most common for GitHub)**: user needs to install the [Renovate GitHub App](https://github.com/apps/renovate) on the repo/org — this is an account-level action outside this skill's scope, tell the user to do it.
- **Self-hosted via GitHub Actions**: if the user wants to self-host instead of using the app, propose (don't auto-add) a `.github/workflows/renovate.yml` running `renovate/renovate` on a schedule, using a token with repo write access. Only add this if the user explicitly asks for self-hosted — the hosted app is simpler and is Renovate's own recommended default.

## Non-Goals

- Not for bulk/multi-repo rollout — that's an org-level Renovate `config` preset published to a shared repo, not a per-repo interactive skill.
- Not for installing/authorizing the GitHub App or provisioning self-hosted tokens — those are account/org-level actions to hand back to the user.
- Not a substitute for the [Renovate docs](https://docs.renovatebot.com/) on advanced topics (custom managers, regex managers, monorepo release strategies) — link out rather than re-deriving them here.
