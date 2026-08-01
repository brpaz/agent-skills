---
name: copier-scaffold
version: "1.0.0"
description: "Scaffold a new project with Copier. Before writing any project from scratch (new Go library, Python project, TypeScript project, Rust project, Docker image, GitHub Action, Ansible role, Terraform/Ansible IaC, browser extension, VSCode/Gnome/Vicinae extension, Astro site, FluxCD project, etc.), search brpaz's GitHub for a matching copier-* template and offer to use it instead of hand-rolling boilerplate. Use whenever the user says 'new project', 'scaffold', 'bootstrap', 'start a new repo/library/CLI/extension', or names a stack that could match an existing template."
tags: [copier, scaffolding, templates, bootstrap, github]
---

# Copier Scaffold — scaffold new projects from brpaz's Copier templates

Use when starting a brand-new project. Reference: [copier.readthedocs.io](https://copier.readthedocs.io/).

### 1. Discover available templates

All of brpaz's copier templates are tagged with the GitHub topic `copier-template`. List them before assuming none exist:

```bash
gh search repos --owner brpaz --topic copier-template --json name,description,url,updatedAt
```

This is the authoritative, up-to-date list — don't rely on memory of what templates exist, new ones get added. If `gh` isn't authenticated or the search fails, fall back to browsing https://github.com/brpaz?tab=repositories&q=copier-.

### 2. Match the request to a template

Compare the user's stack/intent against the `name`/`description` fields returned above. Typical mappings (confirm against the live list, don't hardcode this as gospel — it changes):

| User wants | Template repo |
|---|---|
| Go library | `copier-go` |
| Python project | `copier-python` |
| TypeScript project | `copier-typescript` |
| Rust project | `copier-rust` |
| Docker image | `copier-docker-image` |
| GitHub Action (TypeScript) | `copier-github-action-ts` |
| GitHub Action (Docker) | `copier-github-action-docker` |
| Ansible role | `copier-ansible-role` |
| Terraform + Ansible IaC | `copier-iac` |
| FluxCD / GitOps project | `copier-fluxcd` |
| Astro website | `copier-astro` |
| Browser extension | `copier-browser-ext` |
| VSCode extension | `copier-vscode-ext` |
| Gnome extension | `copier-gnome-ext` |
| Vicinae extension | `copier-vicinae-ext` |
| A new Copier template itself | `copier-copier` |
| Release Drafter config only (not a full project) | `copier-release-drafter` |

If nothing matches, say so plainly and proceed with scaffolding from scratch per the normal. don't force-fit an unrelated template.

If more than one template plausibly fits, list the candidates with their `description` and ask the user to pick rather than guessing.

### 3. Prefer the local checkout, fall back to GitHub

Local clones live at `~/Code/Templates/copier-<name>/` (the directory name doesn't always match the repo name exactly — check `ls ~/Code/Templates/ | grep copier`). If a matching local checkout exists:

```bash
git -C ~/Code/Templates/copier-<name> pull
```

Pull first so the scaffold uses the latest version, then run copier against that local path. If no local checkout exists, run copier directly against the GitHub shorthand — no need to clone manually, copier does it:

```bash
copier copy gh:brpaz/<repo> <destination>
```

### 4. Run copier

```bash
copier copy <source> <destination>
```

- `<source>` is either the local path from step 3 or the `gh:brpaz/<repo>` shorthand.
- `<destination>` is the new project directory — confirm the path and name with the user before running if it wasn't explicit (this creates a new directory and, for most of brpaz's templates, runs post-generation tasks).
- Copier templates can define `_tasks` that execute shell commands after generation (git init, installing hooks, etc. — see any template's `copier.yml`). Copier will prompt for `--trust` itself when a template defines tasks; since these are the user's own templates the intent is legitimate, but still treat the confirmation prompt as real and don't script around it.
- Answer the interactive prompts as they come up, using context already known about the project (name, description, GitHub repo slug) instead of asking the user to retype what they already told you.

### 5. After generation

q::wq- `cd` into the new project and read the generated `README.md` — brpaz's templates typically document their own next steps (e.g. `devenv shell`, enabling GitHub Actions, setting secrets).

- Don't assume the new project needs `docker-setup`, `renovate-setup`, etc. run again — these templates usually already bake that in. Check what's already there before layering another skill on top of it.
