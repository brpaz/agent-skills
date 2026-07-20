---
name: zensical-setup
version: "1.0.0"
description: "Add Zensical (the Rust-powered successor to Material for MkDocs) to a new or existing project — generate zensical.toml, scaffold docs/, migrate an existing mkdocs.yml, and wire a GitHub Pages deploy workflow, idempotently, without clobbering existing config."
tags: [zensical, mkdocs, material-for-mkdocs, docs, static-site-generator, github-actions, github-pages]
---

# Zensical Setup — add or migrate to Zensical documentation tooling

Use when asked to "set up Zensical", "add Zensical docs", "migrate from MkDocs/Material for MkDocs to Zensical", or "bootstrap a docs site" on a project that wants one. Reference: [zensical.org/docs](https://zensical.org/docs/), [github.com/zensical/zensical](https://github.com/zensical/zensical).

Zensical is the Rust/Python static site generator built by the Material for MkDocs team as its next-generation successor — same theme lineage, millisecond differential builds, and it can read an existing `mkdocs.yml` directly so migration doesn't require a rewrite on day one.

## Use Alongside

- `github-actions-docker` — if the project wants more than the default Pages deploy workflow (e.g. a PR preview build), that skill owns the broader CI pattern; this skill only wires the minimal `docs.yml` Zensical ships by default.
- `renovate-setup` / `gitleaks-setup` — if already run, reuse whatever label/schedule conventions they established rather than inventing new ones for the docs workflow.

## When to Use

- Repo has no docs tooling yet and the user wants a Markdown-driven site.
- Repo already uses MkDocs or Material for MkDocs (`mkdocs.yml` present) and the user wants to move to Zensical.
- Repo has Zensical already but `zensical.toml` looks like an untouched default and the user wants it tuned.

## Procedure

### 1. Detect existing setup first — never blind-overwrite

- Check for `zensical.toml`, `mkdocs.yml`/`mkdocs.yaml`, an existing `docs/` directory, and `.github/workflows/*.yml` that already build/deploy docs.
- If `zensical.toml` already exists: `zensical new` itself refuses to run (errors if the config file is already there) — read the existing file, report what's configured, and ask whether to leave, extend, or replace before touching it.
- If only `mkdocs.yml`/`mkdocs.yaml` exists (MkDocs or Material for MkDocs project, no Zensical yet): this is a migration, not a fresh install — see step 3.

### 2. Confirm Python tooling

Zensical is a Python package with a Rust core; it requires **Python ≥ 3.10**. Check `python3 --version` and how the repo manages Python (`pyproject.toml`, `requirements.txt`, `.python-version`, `uv.lock`) to install consistently with the rest of the project rather than introducing a second convention:

```bash
# pip, inside a venv
python3 -m venv .venv && source .venv/bin/activate
pip install zensical

# uv (preferred if the repo already uses uv)
uv add --dev zensical

# conda/mamba
conda install -c conda-forge zensical
```

A Docker image is also published at `zensical/zensical` on Docker Hub if the project prefers not to install a local toolchain.

### 3. Fresh install vs. migration

**Fresh install** (no existing docs config):

```bash
zensical new [directory]
```

This scaffolds, without overwriting anything already present:

```
.
├─ .github/workflows/docs.yml   # GitHub Pages deploy workflow
├─ docs/
│  ├─ index.md
│  └─ markdown.md
└─ zensical.toml
```

**Migration from `mkdocs.yml`** (Material for MkDocs already in place):

- Zensical reads `mkdocs.yml`/`mkdocs.yaml` natively — `zensical build`/`zensical serve` will pick it up automatically if no `zensical.toml` exists (config file resolution order: `zensical.toml` → `mkdocs.yml` → `mkdocs.yaml`), so the site can run unchanged as a first step.
- For a project that wants to commit to Zensical long-term, port the config to `zensical.toml` (TOML is the recommended format going forward) rather than leaving `mkdocs.yml` as the source of truth indefinitely — translate the `mkdocs.yml` top-level keys into the `[project]` table (see step 4), and `theme:` options into `[project.theme]`.
- Flag to the user: plugin/extension parity with the MkDocs ecosystem is still growing (Zensical is young — check the current plugin list in the docs before assuming a `mkdocs-*` plugin the project relies on already works), so a straight migration should be validated with `zensical build --strict` before trusting it in CI.

### 4. `zensical.toml` — core `[project]` fields

Don't paste every commented-out option from the bootstrap template — set only what the project analysis in step 3 justifies:

```toml
[project]
site_name = "Documentation"                 # required
site_description = "…"
site_author = "…"
site_url = "https://example.com/"           # set if publishing online
copyright = """
Copyright &copy; 2026 The authors
"""
# docs_dir = "docs"    # default; cannot be "."
# site_dir = "site"    # default; this is the build output, gitignore it

[project.theme]
# variant = "classic"          # default is "modern"; "classic" = traditional Material for MkDocs look
language = "en"
features = [
  "content.code.copy",
  "content.code.select",
  "navigation.instant",
  "navigation.instant.prefetch",
  "navigation.tracking",
  "navigation.top",
  "search.highlight",
]

[[project.theme.palette]]
scheme = "default"
toggle.icon = "lucide/sun"
toggle.name = "Switch to dark mode"

[[project.theme.palette]]
scheme = "slate"
toggle.icon = "lucide/moon"
toggle.name = "Switch to light mode"
```

Notes:
- Navigation: if no `nav` array is set, Zensical derives it from the `docs_dir` directory structure — only add an explicit `nav = [...]` if the project needs an order or grouping the file tree doesn't already express.
- `[project.theme.icon].logo` gives a built-in icon (e.g. `"lucide/smile"`) if there's no project logo yet; a real logo file goes in `[project.theme]` as `logo = "assets/logo.png"` (path relative to `docs_dir`).
- `[project.markdown_extensions.*]` mirrors PyMdown Extensions config (`admonition`, `pymdownx.superfences`, `pymdownx.tabbed`, etc.) — only add entries the content actually uses; don't cargo-cult the full bootstrap list into a project that won't use e.g. `arithmatex` or `mermaid` fences.

### 5. Preview and build

```bash
zensical serve                    # dev server, default http://localhost:8000, live reload
zensical serve -o                 # also opens the browser
zensical serve -a 0.0.0.0:8080    # custom bind address/port

zensical build                    # one-shot build to site_dir (default: site/)
zensical build -c                 # --clean: clear cache before building
zensical build -s                 # --strict: abort the build on warnings — use in CI
```

All three commands accept `-f/--config-file` to point at a config file outside the default resolution order. Note `serve --strict` is currently a no-op upstream (prints a warning) — only `build --strict` actually enforces it, so CI validation should call `build`, not rely on `serve`.

### 6. Deploy workflow

The scaffolded `.github/workflows/docs.yml` builds and publishes to GitHub Pages on push to `main`/`master`:

```yaml
name: Documentation
on:
  push:
    branches:
      - master
      - main
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/configure-pages@v6
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v6
        with:
          python-version: 3.x
      - run: pip install zensical
      - run: zensical build --clean
      - uses: actions/upload-pages-artifact@v5
        with:
          path: site
      - uses: actions/deploy-pages@v5
        id: deployment
```

If the repo already has a docs/CI workflow (from a prior MkDocs setup or `github-actions-docker`), don't add a second one — update the existing job's build step to `zensical build --clean` instead. If it doesn't deploy to GitHub Pages (e.g. Netlify/Cloudflare Pages/S3), swap the publish steps but keep `pip install zensical && zensical build --clean` as the build step, and add `zensical build --strict` as a separate PR-check job so broken docs fail CI before merge rather than only failing at deploy time.

Before wiring this in, confirm the repo's GitHub Pages source is set to "GitHub Actions" (Settings → Pages) — that's an account/repo-setting change outside this skill's scope, flag it rather than assuming it's already set.

### 7. `.gitignore`

Ensure the build output directory is ignored — check for an existing entry before adding:

```gitignore
/site/
```

(Adjust the path if `site_dir` was customized in step 4.)

## Non-Goals

- Not for authoring documentation content itself — this skill sets up the tool, not the docs.
- Not a full `mkdocs.yml` → `zensical.toml` translator for every possible MkDocs plugin — flag plugins with no known Zensical equivalent rather than guessing at a silent drop.
- Not for provisioning GitHub Pages / custom domain DNS — those are repo/account-level settings to hand back to the user.
- Not a substitute for the [Zensical docs](https://zensical.org/docs/) on advanced topics (custom theme packaging, multi-language sites, `mkdocstrings`-style auto-doc plugins) — link out rather than re-deriving them here.
