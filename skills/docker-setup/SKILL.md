---
name: docker-setup
version: "1.0.0"
description: "Add Docker to an existing project — analyze the codebase to generate a fitting Dockerfile, .dockerignore, and .hadolint.yaml, prompt before adding docker-compose, and propose a CI build stage in existing GitHub Actions workflows."
tags: [docker, dockerfile, hadolint, docker-compose, github-actions, ci-cd]
---

# Docker Setup — retrofit Docker onto an existing project

Use when asked to "add Docker", "dockerize this project", "add a Dockerfile" on a project that doesn't have one yet (or has a stale one).

## Use Alongside

- `dockerfile` — deeper Dockerfile design, caching, and hardening reference once the base file exists
- `docker-compose` — deeper Compose service modeling if the user wants multi-service orchestration
- `github-actions-docker` — the full CI build/push pattern this skill proposes wiring in; that skill owns the pattern's details, this skill only decides *whether* and *where* to add it

## When to Use

- Repo has no `Dockerfile` and the user wants one added, tailored to what the project actually is.
- Repo has a `Dockerfile` but no `.dockerignore` / `.hadolint.yaml`, or they look stale.
- Repo has GitHub Actions and the user wants a Docker build wired into CI.

## Procedure

### 1. Detect existing setup first — never blind-overwrite

- Check for `Dockerfile`, `Dockerfile.*`, `.dockerignore`, `.hadolint.yaml`/`.hadolint.yml`, `docker-compose.yml`/`compose.yaml`, and `.github/workflows/*.yml`.
- If any exist, read them, summarize what's there, ask whether to leave, extend, or replace before touching it. A partially-Dockerized repo (e.g. compose file but no Dockerfile) is common — don't assume "no Dockerfile" means nothing else exists.

### 2. Analyze the project before writing anything

Determine language, package manager, build step, run command, and listen port by reading manifests — don't guess:

| Signal file | Stack | Notes to extract |
|---|---|---|
| `package.json` | Node.js | `engines.node`, package manager from lockfile (`package-lock.json`→npm, `pnpm-lock.yaml`→pnpm, `yarn.lock`→yarn), `scripts.build`/`scripts.start`, framework (Next.js, etc.) |
| `go.mod` | Go | Go version, module path, `main` package location |
| `pyproject.toml` / `requirements.txt` / `Pipfile` | Python | Python version, dependency manager (poetry/pip/pipenv), entrypoint (WSGI app, `manage.py`, etc.) |
| `Cargo.toml` | Rust | Rust edition, bin name |
| `Gemfile` | Ruby | Ruby version, Rails vs. plain |
| `pom.xml` / `build.gradle` | Java/Kotlin | JDK version, Maven vs. Gradle |
| `composer.json` | PHP | PHP version, framework (Laravel, etc.) |

Also check: is this a service (needs to run/listen) or a CLI/batch tool (runs and exits) — this changes whether `EXPOSE`/healthcheck make sense. If ambiguous, ask.

### 3. Generate the Dockerfile

Multi-stage by default (build stage + slim runtime stage), non-root `USER`, pinned base image tag (prefer a specific minor version over `latest`), `.dockerignore`-aware `COPY`. Match the stack detected in step 2. Example shape (Node, adapt per stack):

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY --from=build /app/dist ./dist
RUN addgroup -S app && adduser -S app -G app
USER app
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

For a service, add `HEALTHCHECK` only if the app already exposes a health endpoint (check routes/README first — don't invent one). For a CLI/batch tool, drop `EXPOSE`/`HEALTHCHECK` and set `ENTRYPOINT`/`CMD` to the binary.

Defer to the `dockerfile` skill for language-specific base image choices, layer-caching order, and further hardening beyond this first pass.

### 4. Generate `.dockerignore` — deny by default, allowlist only what the build needs

Start with `*` (ignore everything), then add back only the files/dirs the build actually `COPY`s, rather than starting from an allow-all list and subtracting known-bad paths. This fails safe: anything new added to the repo later (secrets, local env files, scratch dirs) is excluded from the build context by default instead of leaking in until someone remembers to blocklist it.

```gitignore
# Deny everything by default
*

# Allow only what the Dockerfile COPYs — match step 3's COPY lines exactly
!package.json
!package-lock.json
!src
!src/**
!tsconfig.json
```

Notes:
- Directories need both `!dir` and `!dir/**` — Docker won't descend into a re-included directory to re-include its contents unless the contents are separately un-ignored.
- Keep this list in lockstep with the Dockerfile's `COPY` instructions: every `COPY <path>` needs a matching `!<path>` here, and nothing else. If the Dockerfile does `COPY . .` (common for the builder stage before a leaner runtime `COPY --from=build`), the allowlist should cover everything genuinely required to build (lockfile, source dir, config files) — still not `.git`, `.env`, `node_modules`, editor/CI directories, etc.
- Re-verify this list whenever the Dockerfile's `COPY` lines change — a stale allowlist causes confusing "file not found" build failures, not a security issue, so it's a cheap thing to double check first.

### 5. Generate `.hadolint.yaml`

Keep defaults strict; only ignore rules that don't fit the generated Dockerfile's intentional choices (e.g. `DL3059` if consecutive `RUN`s are intentional for layer caching/readability):

```yaml
failure-threshold: warning
ignored:
  - DL3059 # Multiple consecutive `RUN` instructions — acceptable for readability/caching here
override:
  error:
    - DL3002 # Last USER should not be root
    - DL3025 # Use JSON notation for CMD/ENTRYPOINT
trustedRegistries:
  - docker.io
  - ghcr.io
```

Run `hadolint Dockerfile` (or `docker run --rm -i hadolint/hadolint < Dockerfile` if not installed locally) against the generated file and fix findings before calling this step done — don't ship a Dockerfile with unaddressed hadolint errors.

### 6. Prompt for docker-compose — don't assume

Ask the user (don't just add it) whether they want a `docker-compose.yml`. Signals worth surfacing in the question: detected runtime dependencies from manifests (DB driver, Redis client, message broker client, etc.) suggest services they may want stubbed in Compose. If yes, hand off to the `docker-compose` skill for the actual service modeling — this skill only scaffolds a minimal file wiring the built image plus any detected dependency services, not full production Compose config.

### 7. If GitHub Actions is present, propose (don't auto-add) a Docker build stage

- Check `.github/workflows/*.yml` for an existing pipeline.
- If found, propose adding a Docker build job following [Docker's official GitHub Actions guide](https://docs.docker.com/build/ci/github-actions/) — in practice this means the pattern already codified in the `github-actions-docker` skill: `docker/setup-buildx-action`, `docker/metadata-action`, `docker/build-push-action` with `cache-from`/`cache-to: type=gha`, build-then-smoke-test-then-push staged so PRs build without pushing.
- Present this as a proposal with a diff/new-file preview, not a silent edit — CI changes are shared, visible state.
- If no workflow exists, ask whether to create one at all before scaffolding `.github/workflows/docker.yml` — don't introduce GitHub Actions into a repo that isn't using it just because Docker was added.
- Delegate to the `github-actions-docker` skill for the actual workflow content once the user agrees to proceed.

### 8. Verify before finishing

- `docker build .` succeeds locally.
- `hadolint Dockerfile` passes (or documented, accepted ignores only).
- `.dockerignore` allowlist matches the Dockerfile's `COPY` lines exactly — no more, no less.
- If Compose was added: `docker compose config` validates without error.
- If a CI stage was proposed and accepted: confirm the workflow references the right Dockerfile path/context and that push is gated to non-PR events.

## Non-Goals

- Not for bulk/multi-repo rollout — one project at a time, tailored to what's actually there.
- Not for choosing a hosting/registry strategy (ECR vs. GHCR vs. Docker Hub) — that's a decision to surface to the user, not assume.
- Not a substitute for `dockerfile`, `docker-compose`, or `github-actions-docker` — this skill decides *whether/what* to add on a bare project; those skills own the depth once the base files exist.
