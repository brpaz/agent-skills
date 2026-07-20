# Skills

> My personal collection of reusable agent skills.

## Available skills

<!-- skills-index:start -->
- [`adr-writer`](skills/adr-writer/SKILL.md) — Capture major technical decisions in an architecture decision record (ADR)
- [`application-healthchecks`](skills/application-healthchecks/SKILL.md) — Design web app and API health checks with RFC-style JSON responses, probe separation, and production-safe dependency policies.
- [`conventional-commits`](skills/conventional-commits/SKILL.md) — Write Conventional Commits messages and set up commitlint, versioning, and changelog workflows.
- [`devenv`](skills/devenv/SKILL.md) — Define Nix-based development environments with devenv.sh, including task runners, Docker Compose workflows, services, and containers.
- [`direnv`](skills/direnv/SKILL.md) — Set up per-directory environments with direnv for `.envrc` loading, variable management, and nix/devenv/asdf integration.
- [`docker-compose`](skills/docker-compose/SKILL.md) — Define multi-container Docker applications in compose files, including services, networks, volumes, profiles, and health checks.
- [`docker-setup`](skills/docker-setup/SKILL.md) — Add Docker to an existing project — analyze the codebase to generate a fitting Dockerfile, .dockerignore, and .hadolint.yaml, prompt before adding docker-compose, and propose a CI build stage in existing GitHub Actions workflows.
- [`dockerfile`](skills/dockerfile/SKILL.md) — Create and improve Dockerfiles with multi-stage builds, caching, security hardening, and debugging guidance.
- [`github-actions-docker`](skills/github-actions-docker/SKILL.md) — Build, smoke-test, and publish Docker images with GitHub Actions using current official actions, release-published triggers, short-SHA test tags, and Compose CI stacks.
- [`gitleaks-setup`](skills/gitleaks-setup/SKILL.md) — Add or update Gitleaks secret-scanning to an existing repo — GitHub Action workflow, .gitleaks.toml, hook via lefthook/pre-commit, Taskfile task, devenv/mise tool pin — idempotently, without clobbering existing config.
- [`golang-development`](skills/golang-development/SKILL.md) — Write and review Go code with idiomatic project structure, errors, concurrency, testing, and performance guidance.
- [`golang-slog`](skills/golang-slog/SKILL.md) — Implement structured logging in Go with log/slog, including logger setup, common attributes, context propagation, redaction, and performance-minded patterns.
- [`golang-testing`](skills/golang-testing/SKILL.md) — Write idiomatic Go tests — unit tests, table-driven patterns, mocking, and testcontainers-go integration tests against real Postgres, Redis, and other containerised dependencies.
- [`playwright-devenv`](skills/playwright-devenv/SKILL.md) — Set up Playwright browser automation in devenv.sh on NixOS, including browser installation, version pinning, and troubleshooting.
- [`project-webapp`](skills/project-webapp/SKILL.md) — Bootstrap a Nuxt 4 web application with Drizzle ORM, Nuxt UI, Tailwind CSS, Docker, GitHub Actions, Release Drafter, and Renovate.
- [`readme-writer`](skills/readme-writer/SKILL.md) — Create and improve README files with structured installation, usage, API, and contribution guidance.
- [`release-drafter`](skills/release-drafter/SKILL.md) — Configure Release Drafter for automated release notes, label-based categorization, and semantic version suggestions in GitHub Actions.
- [`release-drafter-setup`](skills/release-drafter-setup/SKILL.md) — Add or update Release Drafter on an existing repo — GitHub Action workflow, .github/release-drafter.yml, required labels via EndBug/label-sync — idempotently, without clobbering existing config, with a production-readiness review of anything already in place.
- [`renovate-setup`](skills/renovate-setup/SKILL.md) — Add or update Renovate on an existing project — infer the tech stack, generate a renovate.json tuned to it (managers, grouping, schedule, automerge, digest pinning), following https://docs.renovatebot.com/ best practices, idempotently, without clobbering existing config.
- [`structured-logging`](skills/structured-logging/SKILL.md) — Design language-agnostic structured logs with consistent fields, correlation IDs, safe context, and production-ready observability guidance.
- [`tailwind-v4`](skills/tailwind-v4/SKILL.md) — Configure Tailwind CSS v4 with Oxide, CSS-first directives, migration steps, and production guidance.
- [`vicinae-extensions`](skills/vicinae-extensions/SKILL.md) — Build Vicinae launcher extensions with React/TypeScript, @vicinae/api, commands, and native UI components.
- [`zensical-setup`](skills/zensical-setup/SKILL.md) — Add Zensical (the Rust-powered successor to Material for MkDocs) to a new or existing project — generate zensical.toml, scaffold docs/, migrate an existing mkdocs.yml, and wire a GitHub Pages deploy workflow, idempotently, without clobbering existing config.
<!-- skills-index:end -->

## Getting started

### Installation

To install these skills, the simplest way is to use the [skills](https://github.com/vercel-labs/skills) CLI tool. You will need to have Node.js installed on your machine first. Follow the instructions [here](https://nodejs.org/en/download/) to install Node.js if you haven't already.

```bash
npx skills add brpaz/agent-skills
```

This command will prompt you to select which skills you want to install from this repository. To install all the skills, run the following command:

```bash
npx skills add brpaz/agent-skills -g --all
```

Alternatively you can clone this repository and copy or symlink the skill directories into your local skills directory.

## LICENSE

All skills in this repository are licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute these skills in your projects. Please refer to the LICENSE file for more details on the terms and conditions of the license.
