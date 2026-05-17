# Skills

> My personal collection of reusable agent skills.

## Available skills

- [`adr-writer`](skills/adr-writer/SKILL.md) — Architecture decision record skill for capturing major technical decisions in an ADR directory with context, alternatives, and consequences.
- [`conventional-commits`](skills/conventional-commits/SKILL.md) — Conventional Commits specification expert. Use when writing commit messages, configuring commit linting, setting up automated versioning, or generating changelogs.
- [`devenv`](skills/devenv/SKILL.md) — Nix-based development environment management with `devenv.sh`, including `devenv.nix`, `devenv.yaml`, locks, services, tasks, and integrations.
- [`direnv`](skills/direnv/SKILL.md) — Per-directory environment management with `direnv`, including `.envrc` patterns, secure loading, and tool integration.
- [`docker-compose`](skills/docker-compose/SKILL.md) — Multi-container Docker orchestration with Compose for local development and service-based environments.
- [`dockerfile`](skills/dockerfile/SKILL.md) — Production-ready Dockerfile authoring with multi-stage builds, caching, security hardening, and best practices.
- [`golang`](skills/golang/SKILL.md) — Go programming best practices, idioms, testing, concurrency, project structure, and performance guidance.
- [`playwright-devenv`](skills/playwright-devenv/SKILL.md) — Playwright browser automation setup inside `devenv.sh` environments on NixOS.
- [`project-webapp`](skills/project-webapp/SKILL.md) — Production-ready Nuxt 4 webapp bootstrap with Drizzle ORM, Nuxt UI, Tailwind CSS, Docker, GitHub Actions, Release Drafter, and Renovate.
- [`readme-writer`](skills/readme-writer/SKILL.md) — README authoring skill for creating and improving project documentation.
- [`release-drafter`](skills/release-drafter/SKILL.md) — Automated release notes and release workflow setup using Release Drafter and GitHub Actions.
- [`tailwind-v4`](skills/tailwind-v4/SKILL.md) — Tailwind CSS v4 guidance covering CSS-first configuration, migration, and production best practices.
- [`vicinae-extensions`](skills/vicinae-extensions/SKILL.md) — Vicinae launcher extension development with React, TypeScript, and the `@vicinae/api` SDK.

## Getting started

### Installation

To install these skills, the simplest way is to use the [skills](https://github.com/vercel-labs/skills) CLI tool. You will need to have Node.js installed on your machine first. Follow the instructions [here](https://nodejs.org/en/download/) to install Node.js if you haven't already.

```bash
npx skills add brpaz/agent-skills
```

Alternatively you can clone this repository and copy or symlink the skill directories into your local skills directory.

## LICENSE

All skills in this repository are licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute these skills in your projects. Please refer to the LICENSE file for more details on the terms and conditions of the license.
