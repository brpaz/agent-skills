---
name: github-actions-docker
version: "1.0.0"
description: "Build, smoke-test, and publish Docker images with GitHub Actions using current official actions, release-published triggers, short-SHA test tags, and Compose CI stacks."
tags: [github-actions, docker, ci-cd, buildx, compose]
---

# GitHub Actions Docker - Build, Smoke Test, and Publish Images

Use this skill when setting up GitHub Actions workflows for Docker image CI/CD.

## Use Alongside

- `dockerfile` for image design, caching, and Dockerfile hardening
- `docker-compose` for deeper Compose service modeling and health-check guidance

## When to Use

- Creating a GitHub Actions workflow that builds Docker images
- Migrating from ad-hoc `docker build && docker push` pipelines
- Adding multi-platform publishing by default
- Running smoke tests against a loaded image before pushing
- Testing multi-service applications with `docker-compose.ci.yml`
- Keeping CI and local validation aligned through `scripts/ci.sh`

## Default Stance

- Use the official Docker actions stack:
  - `actions/checkout@v6`
  - `docker/setup-qemu-action@v4`
  - `docker/setup-buildx-action@v4`
  - `docker/metadata-action@v6`
  - `docker/login-action@v4`
  - `docker/build-push-action@v7`
- Prefer **multi-platform by default** for published images: `linux/amd64,linux/arm64`
- Use a **test-before-push** flow:
  1. build a test image
  2. `load: true`
  3. run smoke tests
  4. run the final push build
- Prefer `docker/metadata-action` for all tags and OCI labels instead of hand-rolled shell tag logic
- Use Buildx caching in every workflow; prefer `cache-to/cache-from: type=gha` for simple GitHub-hosted CI, or registry cache when you want stronger cross-runner reuse
- Push only outside pull requests
- Set `provenance: mode=max` explicitly for production pushes and enable `sbom: true` when publishing production images
- For multi-service apps, keep CI dependencies in `docker-compose.ci.yml` and non-secret defaults in `.env.ci`
- Put the same validation steps in `scripts/ci.sh` so developers can run the same flow locally

## Why This Pattern

This skill prefers a two-build workflow because it gives fast validation without giving up proper multi-platform publishing:

- the first build creates a locally loaded image for smoke tests
- the second build performs the final multi-platform push
- Docker documents that the later build can reuse cache, so the second build is mostly paying for the additional platform work rather than rebuilding everything from scratch

## Recommended Action Order

When multi-platform support is enabled:

1. `actions/checkout`
2. `docker/setup-qemu-action`
3. `docker/setup-buildx-action`
4. `docker/login-action` (only when push is possible)
5. `docker/metadata-action`
6. `docker/build-push-action` for test image (`load: true`, single-platform)
7. smoke tests
8. `docker/build-push-action` for final publish (`push: true`, multi-platform)

`setup-qemu-action` should run before `setup-buildx-action` when QEMU is needed.

## Recommended Repository Layout

```text
.github/
  workflows/
    docker.yml
docker-compose.ci.yml
.env.ci
scripts/
  ci.sh
Dockerfile
.dockerignore
```

## Core Workflow Pattern

```yaml
name: docker

on:
  pull_request:
  push:
    branches: [main]
  release:
    types: [published]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
  PLATFORMS: linux/amd64,linux/arm64

jobs:
  docker:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      attestations: write
      id-token: write

    steps:
      - name: Checkout
        uses: actions/checkout@v6

      - name: Compute short SHA
        id: vars
        shell: bash
        run: echo "short_sha=${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v4

      - name: Set up Buildx
        uses: docker/setup-buildx-action@v4

      - name: Log in to GHCR
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v4
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract Docker metadata
        id: meta
        uses: docker/metadata-action@v6
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha
            type=semver,pattern={{version}},enable=${{ github.event_name == 'release' }}
            type=semver,pattern={{major}}.{{minor}},enable=${{ github.event_name == 'release' }}
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build smoke-test image
        uses: docker/build-push-action@v7
        with:
          context: .
          file: ./Dockerfile
          platforms: linux/amd64
          load: true
          tags: local/test-image:sha-${{ steps.vars.outputs.short_sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Run shared CI script
        env:
          IMAGE_TAG: local/test-image:sha-${{ steps.vars.outputs.short_sha }}
        run: ./scripts/ci.sh

      - name: Build and push multi-platform image
        if: github.event_name != 'pull_request'
        uses: docker/build-push-action@v7
        with:
          context: .
          file: ./Dockerfile
          platforms: ${{ env.PLATFORMS }}
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          annotations: ${{ steps.meta.outputs.annotations }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          provenance: mode=max
          sbom: true
```

## Required Workflow Behavior

- **Pull requests**: build, load, smoke test, run CI checks, do not push
- **Default branch**: build, smoke test, run CI checks, then push multi-platform image
- **Published releases**: use the `release.published` event and metadata-derived version tags rather than tag-push triggers

## Tagging and Metadata

Prefer `docker/metadata-action` for:

- branch tags
- PR tags
- release-driven semver tags
- SHA tags
- OCI labels
- annotations passed to the final publish build

Do not hand-maintain separate shell logic for every tag type unless you have a very unusual release policy.

## Multi-Platform Guidance

Default published platforms:

```yaml
platforms: linux/amd64,linux/arm64
```

Guidance:

- Use `linux/amd64` for the loaded smoke-test image unless you have a specific reason to test another platform locally in CI
- Keep the final publish step multi-platform
- If you need to **load** a multi-platform image into the local Docker store, that requires extra Docker daemon setup with the containerd image store; do not add that complexity unless it solves a real need
- For very heavy builds, consider Docker's newer distributed builder workflow patterns, but keep the simple single-job Buildx flow as the default

## Smoke Test Guidance

Smoke tests should verify the container can boot and serve its most critical behavior. Good examples:

- process starts successfully
- health endpoint returns success
- CLI image responds to `--help` or `version`
- web app can boot with CI config

Avoid turning smoke tests into your entire integration suite.

For service-style applications, prefer starting the app in the Compose CI stack and running `smoke.sh` against the running application instead of launching a separate `docker run` just for smoke testing.

Example `scripts/smoke.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

curl --fail --show-error --silent http://127.0.0.1:8080/healthz >/dev/null
```

## `docker-compose.ci.yml` Pattern

For multi-service applications, prefer bringing the app container up inside the Compose CI stack alongside its dependencies, then run smoke and test scripts against the running application.

Use `docker-compose.ci.yml` for supporting services such as:

- Postgres
- Redis
- MinIO
- Mailpit
- OpenSearch

If `scripts/ci.sh` already starts and stops Compose dependencies, do not duplicate `docker compose up/down` in the workflow.

Example:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    env_file:
      - .env.ci
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 20

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 20

  app:
    image: "${IMAGE_TAG}"
    env_file:
      - .env.ci
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://127.0.0.1:8080/healthz || exit 1"]
      interval: 5s
      timeout: 5s
      retries: 20
```

If the image does not contain `curl`, use an app-appropriate healthcheck command instead of forcing `curl` into the image just for CI.

## `.env.ci` Pattern

Use `.env.ci` for non-secret CI defaults that should also work locally.

Example:

```dotenv
APP_ENV=ci
LOG_LEVEL=debug
PORT=8080

POSTGRES_DB=app_test
POSTGRES_USER=app
POSTGRES_PASSWORD=app
DATABASE_URL=postgres://app:app@postgres:5432/app_test?sslmode=disable

REDIS_URL=redis://redis:6379/0
```

Rules:

- keep `.env.ci` non-secret
- use GitHub Actions secrets for real credentials
- use Compose `env_file` for convenience, not for secret management
- make local and CI defaults match unless there is a strong reason not to

## Health Checks and Readiness

Do not rely on bare `depends_on` for readiness. In CI stacks:

- add explicit health checks for Postgres, Redis, and other dependencies
- use `depends_on: condition: service_healthy` when Compose is orchestrating test dependencies
- prefer `docker compose ... up -d --wait --wait-timeout <seconds>` so Compose waits for healthchecks to pass before smoke or integration tests start
- fail fast when a dependency never becomes healthy

## `scripts/ci.sh` Pattern

Put the real validation logic in `scripts/ci.sh`, then let both GitHub Actions and local developers call the same script.

This prevents your workflow YAML from becoming the only source of truth.

Example:

```bash
#!/usr/bin/env bash
set -euo pipefail

IMAGE_TAG="${IMAGE_TAG:-}"
BUILD_IMAGE="${BUILD_IMAGE:-0}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.ci.yml}"
ENV_FILE="${ENV_FILE:-.env.ci}"

if [[ -z "$IMAGE_TAG" ]]; then
  printf 'IMAGE_TAG is required\n' >&2
  exit 1
fi

if [[ "$BUILD_IMAGE" == "1" ]]; then
  docker buildx build \
    --load \
    --platform linux/amd64 \
    -t "$IMAGE_TAG" \
    .
fi

export IMAGE_TAG

cleanup() {
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" down -v || true
}
trap cleanup EXIT

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --wait --wait-timeout 120


./scripts/smoke.sh
./scripts/test.sh
```

Recommended properties:

- executable and documented
- deterministic
- safe to run repeatedly
- owns cleanup via `trap`
- validates required env vars up front, especially `IMAGE_TAG`
- does not build by default; only builds when `BUILD_IMAGE=1`
- accepts configurable `COMPOSE_FILE` and `ENV_FILE`, defaulting to `docker-compose.ci.yml` and `.env.ci`
- starts the Compose stack with `--wait --wait-timeout` so healthchecks gate smoke and test execution
- uses the same `.env.ci` and `docker-compose.ci.yml` files as GitHub Actions

## Cache Guidance

### Simple default

For GitHub-hosted runners:

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

### When to prefer registry cache

Prefer registry cache when:

- you want cache reuse across more workflows and runners
- builds are large and frequent
- you need stronger reuse than GitHub cache gives you

Example:

```yaml
cache-from: type=registry,ref=ghcr.io/acme/app:buildcache
cache-to: type=registry,ref=ghcr.io/acme/app:buildcache,mode=max
```

## Provenance, SBOM, and Secrets

For production pushes:

```yaml
provenance: mode=max
sbom: true
```

Rules:

- do not expect provenance or SBOM output from the `load: true` smoke-test build
- use secret mounts in the Dockerfile for build secrets
- do not pass secrets as plain build args because they can leak into build records and attestations

## Registry Login Guidance

Prefer explicit login steps per registry.

Examples:

### GHCR

```yaml
- uses: docker/login-action@v4
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

### Docker Hub

```yaml
- uses: docker/login-action@v4
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

Use tokens, not passwords.

## Local vs CI Contract

The contract should be:

- GitHub Actions orchestrates runner setup, auth, metadata, and publish
- `scripts/ci.sh` owns the actual validation sequence
- `scripts/ci.sh` should require `IMAGE_TAG` rather than silently defaulting it
- `scripts/ci.sh` should not build by default; set `BUILD_IMAGE=1` only when the script itself must perform the image build
- `scripts/ci.sh` should accept `COMPOSE_FILE` and `ENV_FILE` overrides while defaulting to `docker-compose.ci.yml` and `.env.ci`
- if the workflow pre-builds and loads the smoke-test image, pass `IMAGE_TAG` and let `BUILD_IMAGE` stay unset
- use a short-SHA test image tag to reduce collisions between runs
- `.env.ci` and `docker-compose.ci.yml` are shared between local and CI execution

If the local script and workflow drift apart, fix the drift instead of adding more one-off workflow shell logic.

## Review Checklist

- Uses `actions/checkout`, `docker/setup-qemu-action`, `docker/setup-buildx-action`, `docker/metadata-action`, `docker/login-action`, and `docker/build-push-action`
- Uses `docker/metadata-action` outputs for tags and labels
- Builds a single-platform image with `load: true` before CI validation
- Runs smoke tests against the running application before any push
- Uses a short-SHA test image tag to avoid collisions between runs
- Allows `scripts/ci.sh` callers to override compose/env file paths when needed
- Publishes multi-platform images by default
- Does not push on pull requests
- Uses caching
- Uses `.env.ci`, `docker-compose.ci.yml`, and `scripts/ci.sh`
- Adds health checks for Postgres/Redis and other dependencies
- Keeps secrets out of `.env.ci`
- Uses explicit provenance/SBOM settings on production pushes

## Anti-Patterns

- Building and pushing before any smoke test
- Hand-rolling Docker tag logic instead of using `docker/metadata-action`
- Treating PR builds and release builds as completely different validation paths
- Storing secrets in `.env.ci`
- Using Compose `depends_on` without health checks and calling the stack “ready”
- Duplicating the whole CI sequence in YAML instead of centralising it in `scripts/ci.sh`
- Starting and stopping Compose both in the workflow and inside `scripts/ci.sh`
- Letting `scripts/ci.sh` guess a default `IMAGE_TAG` instead of failing fast when it is missing
- Making image build the default path instead of an explicit opt-in
- Hardcoding the compose/env file paths inside `scripts/ci.sh` when simple env overrides would make it reusable
- Starting a separate `docker run` smoke container when the app is already brought up via Compose
- Reusing a fixed smoke-test image tag across concurrent CI runs
- Publishing only `linux/amd64` by default when the image is meant for general use
- Loading and testing a multi-platform image locally when a single-platform smoke-test image is enough

## Quick Template

```yaml
- uses: actions/checkout@v6
- id: vars
  run: echo "short_sha=${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"
- uses: docker/setup-qemu-action@v4
- uses: docker/setup-buildx-action@v4
- uses: docker/metadata-action@v6
  id: meta
  with:
    images: ghcr.io/${{ github.repository }}
- uses: docker/build-push-action@v7
  with:
    platforms: linux/amd64
    load: true
    tags: local/test-image:sha-${{ steps.vars.outputs.short_sha }}
- run: IMAGE_TAG=local/test-image:sha-${{ steps.vars.outputs.short_sha }} ./scripts/ci.sh
- uses: docker/build-push-action@v7
  if: github.event_name != 'pull_request'
  with:
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ${{ steps.meta.outputs.tags }}
    labels: ${{ steps.meta.outputs.labels }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
    provenance: mode=max
    sbom: true
```
