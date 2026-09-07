# Skills

> My personal collection of reusable agent skills.

## Available skills

<!-- skills-index:start -->
- [`adr-writer`](skills/adr-writer/SKILL.md) — Capture major technical decisions in an architecture decision record (ADR)
- [`application-healthchecks`](skills/application-healthchecks/SKILL.md) — Design web app and API health checks with RFC-style JSON responses, probe separation, and production-safe dependency policies.
- [`backend-best-practices`](skills/backend-best-practices/SKILL.md) — Personal backend engineering principles covering API design and testing. Stack-agnostic. Load this skill when designing APIs, writing tests, reviewing backend code, or building new endpoints. Triggers on tasks involving REST API design, endpoint creation, pagination, HTTP status codes, input validation, integration testing, or test strategy decisions.
- [`bspec-prd-discovery`](skills/bspec-prd-discovery/SKILL.md) — Discovery skill for Bruno's personal spec workflow. Shapes project-level or feature-level product requirements directly in the PRD with a single question-driven loop.
- [`bspec-story-implementation`](skills/bspec-story-implementation/SKILL.md) — Implementation skill for Bruno's personal spec workflow. Works one GitHub story at a time, either implementing directly or routing non-trivial work back to technical architecture while keeping delivery scoped to the smallest useful vertical slice.
- [`bspec-story-review`](skills/bspec-story-review/SKILL.md) — Read-only review skill for Bruno's personal spec workflow. Reviews one implemented GitHub story against the issue, PRD, architecture document, ADRs, and validation evidence, then produces actionable feedback for the implementation loop.
- [`bspec-story-sync`](skills/bspec-story-sync/SKILL.md) — Synchronization skill for Bruno's personal spec workflow. Decomposes the business PRD into small vertical stories and reconciles them into GitHub issues with stable labels, bodies, and safe update rules.
- [`bspec-technical-architecture`](skills/bspec-technical-architecture/SKILL.md) — Technical architecture skill for Bruno's personal spec workflow. Shapes docs/ARCHITECTURE.md, drives a feedback loop, and records durable decisions via ADRs when needed.
- [`bspec-workflow`](skills/bspec-workflow/SKILL.md) — Shared conventions for Bruno's personal spec-driven workflow. Defines logical artifacts, issue labels, workflow states, story IDs, implementation planning, and review markers.
- [`contributing-guide`](skills/contributing-guide/SKILL.md) — Generate or update CONTRIBUTING.md by inferring dev setup, build/test commands, commit and branch conventions, and PR/issue process directly from the codebase — not from a generic template. Use when asked to create, add, write, or refresh a CONTRIBUTING.md, contributor guide, or contribution guidelines for a project.
- [`conventional-commits`](skills/conventional-commits/SKILL.md) — Write Conventional Commits messages and set up commitlint, versioning, and changelog workflows.
- [`copier-scaffold`](skills/copier-scaffold/SKILL.md) — Scaffold a new project with Copier. Before writing any project from scratch (new Go library, Python project, TypeScript project, Rust project, Docker image, GitHub Action, Ansible role, Terraform/Ansible IaC, browser extension, VSCode/Gnome/Vicinae extension, Astro site, FluxCD project, etc.), search brpaz's GitHub for a matching copier-* template and offer to use it instead of hand-rolling boilerplate. Use whenever the user says 'new project', 'scaffold', 'bootstrap', 'start a new repo/library/CLI/extension', or names a stack that could match an existing template.
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
- [`release-notes`](skills/release-notes/SKILL.md) — Generate release notes from all commits/PRs merged since the latest published GitHub release. Reuses .github/release-drafter.yml (categories, version-resolver, template, exclude-labels) when present; falls back to Conventional Commits grouping otherwise.
- [`renovate-pr-triage`](skills/renovate-pr-triage/SKILL.md) — Finds every open Renovate bot PR across the authenticated user's personally-owned GitHub repos, classifies each as ready-to-merge or blocked (CI failing, merge conflict, major version bump, review required, etc.), shows a per-repo report, and — only after the user explicitly confirms — merges exactly the ones that qualify. Use whenever the user wants to clear out a backlog of Renovate dependency-bump PRs, asks "merge my renovate PRs", "clean up dependency PRs across my repos", "what renovate PRs can I merge", or wants a bulk-merge workflow for automated dependency update PRs specifically (not general PR triage — see the pr-triage skill for that).
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
