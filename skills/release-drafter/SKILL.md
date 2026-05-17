---
name: release-drafter
version: "1.0.0"
description: "Configure Release Drafter for automated release notes, label-based categorization, and semantic version suggestions in GitHub Actions."
tags: [github-actions, release, changelog, versioning, automation]
---

# Release Drafter - Automated Release Notes

Use this skill when creating automated release notes workflows with GitHub Actions. Release Drafter drafts release notes by aggregating merged pull requests, categorizing them by labels, and suggesting version numbers based on semantic versioning.

## When to Use

- Adding automated release note drafting to a GitHub repository
- Setting up PR autolabeling based on file paths, branches, or title patterns
- Configuring semantic version resolution (patch/minor/major) from PR labels
- Creating a publication workflow that publishes draft releases via GitHub Actions

## What is Release Drafter?

Release Drafter automatically:
- Creates draft releases as PRs are merged
- Categorizes changes by PR labels (Features, Bug Fixes, etc.)
- Suggests next version number (patch, minor, major)
- Auto-labels PRs based on files/branches/title/body
- Maintains a changelog in draft releases
- Publishes releases on demand

**Key benefit:** Always have release notes ready - just review and publish.

## Quick Start

### Step 1: Create GitHub Actions Workflow

Create `.github/workflows/release-drafter.yml`:

```yaml
name: Release Drafter

on:
  push:
    branches:
      - main
  pull_request:
    types: [opened, reopened, synchronize]

permissions:
  contents: read

jobs:
  update_release_draft:
    permissions:
      contents: write
      pull-requests: write
    runs-on: ubuntu-latest
    steps:
      - uses: release-drafter/release-drafter@v6
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Step 2: Create Configuration File

Create `.github/release-drafter.yml`:

```yaml
template: |
  ## What's Changed
  
  $CHANGES
```

### Step 3: Merge a PR

Once you merge a pull request, Release Drafter will:
1. Create a draft release (if none exists)
2. Add the PR to the release notes
3. Update the version number

**That's it.** You now have automated release notes.

## Basic Configuration

### Minimal Config

```yaml
# .github/release-drafter.yml
template: |
  ## Changes
  
  $CHANGES
```

### Recommended Config

```yaml
# .github/release-drafter.yml
name-template: 'v$RESOLVED_VERSION'
tag-template: 'v$RESOLVED_VERSION'

template: |
  ## What's Changed
  
  $CHANGES

change-template: '- $TITLE @$AUTHOR (#$NUMBER)'

categories:
  - title: '🚀 Features'
    labels:
      - 'feature'
      - 'enhancement'
  - title: '🐛 Bug Fixes'
    labels:
      - 'fix'
      - 'bugfix'
      - 'bug'
  - title: '📚 Documentation'
    label: 'documentation'
  - title: '🧰 Maintenance'
    label: 'chore'

version-resolver:
  major:
    labels:
      - 'major'
  minor:
    labels:
      - 'minor'
  patch:
    labels:
      - 'patch'
  default: patch
```

## Configuration Options

### Core Settings

| Option | Required | Description |
|--------|----------|-------------|
| `template` | Yes | Body of the draft release. Use template variables. |
| `name-template` | No | Release name template. Example: `"v$NEXT_PATCH_VERSION"` |
| `tag-template` | No | Release tag template. Example: `"v$NEXT_PATCH_VERSION"` |
| `change-template` | No | Format for each PR entry. Default: `"* $TITLE (#$NUMBER) @$AUTHOR"` |
| `header` | No | Prepended to `template` |
| `footer` | No | Appended to `template` |

### Advanced Settings

| Option | Description |
|--------|-------------|
| `category-template` | Template for category headings. Default: `"## $TITLE"` |
| `version-template` | Custom version format. Default: `"$MAJOR.$MINOR.$PATCH"` |
| `change-title-escapes` | Characters to escape in PR titles. Default: `""` |
| `no-changes-template` | Text when no PRs merged. Default: `"* No changes"` |
| `no-contributors-template` | Text when no contributors. Default: `"No contributors"` |
| `sort-by` | Sort by `merged_at` or `title`. Default: `merged_at` |
| `sort-direction` | `ascending` or `descending`. Default: `descending` |
| `prerelease` | Mark as prerelease. Default: `false` |
| `latest` | Mark as latest. Values: `true`, `false`, `legacy`. Default: `true` |
| `commitish` | Target branch/commit. Default: workflow ref |

## Template Variables

### Main Template Variables

Use in `template`, `header`, `footer`, `name-template`, `tag-template`:

| Variable | Description | Example |
|----------|-------------|---------|
| `$CHANGES` | List of merged PRs | (formatted list) |
| `$CONTRIBUTORS` | Comma-separated contributor list | `@alice, @bob, @charlie` |
| `$PREVIOUS_TAG` | Previous release tag | `v1.2.3` |
| `$REPOSITORY` | Current repository | `myorg/myapp` |
| `$OWNER` | Repository owner | `myorg` |

### Version Variables

| Variable | Description | Example (from v1.2.3) |
|----------|-------------|----------------------|
| `$NEXT_PATCH_VERSION` | Next patch version | `v1.2.4` |
| `$NEXT_MINOR_VERSION` | Next minor version | `v1.3.0` |
| `$NEXT_MAJOR_VERSION` | Next major version | `v2.0.0` |
| `$RESOLVED_VERSION` | Auto-resolved by labels | (varies) |

### Change Template Variables

Use in `change-template`:

| Variable | Description | Example |
|----------|-------------|---------|
| `$NUMBER` | PR number | `42` |
| `$TITLE` | PR title | `Add alien technology` |
| `$AUTHOR` | PR author username | `gracehopper` |
| `$BODY` | PR body | `Fixed spelling mistake` |
| `$URL` | PR URL | `https://github.com/...` |
| `$BASE_REF_NAME` | Base branch | `main` |
| `$HEAD_REF_NAME` | PR branch | `fix/bug-123` |

### Category Template Variables

Use in `category-template`:

| Variable | Description |
|----------|-------------|
| `$TITLE` | Category title |

## Categorize Pull Requests

Group PRs by labels into sections:

```yaml
categories:
  - title: '🚀 Features'
    labels:
      - 'feature'
      - 'enhancement'
  
  - title: '🐛 Bug Fixes'
    labels:
      - 'fix'
      - 'bugfix'
      - 'bug'
  
  - title: '📚 Documentation'
    label: 'documentation'
  
  - title: '🔒 Security'
    label: 'security'
  
  - title: '⬆️ Dependencies'
    label: 'dependencies'
    collapse-after: 5  # Collapse if more than 5 PRs
  
  - title: '🧰 Maintenance'
    labels:
      - 'chore'
      - 'refactor'
```

**Result:**

```markdown
## 🚀 Features

- Add authentication system @alice (#123)
- Implement dark mode @bob (#124)

## 🐛 Bug Fixes

- Fix memory leak in parser @charlie (#125)

## ⬆️ Dependencies

<details>
<summary>6 changes</summary>

- Bump lodash from 4.17.19 to 4.17.21 @dependabot (#126)
- Update typescript to 5.0.0 @dependabot (#127)
...
</details>
```

**Note:** `collapse-after` automatically collapses categories with many PRs.

## Auto-Label Pull Requests

Automatically label PRs based on file changes, branch name, title, or body:

```yaml
autolabeler:
  # Label by files changed
  - label: 'documentation'
    files:
      - '*.md'
      - 'docs/**/*'
  
  # Label by branch name (regex)
  - label: 'feature'
    branch:
      - '/^feature\/.+/'
      - '/^feat\/.+/'
  
  - label: 'bugfix'
    branch:
      - '/^fix\/.+/'
      - '/^bugfix\/.+/'
  
  # Label by PR title (regex)
  - label: 'breaking'
    title:
      - '/breaking change/i'
      - '/BREAKING:/i'
  
  # Label by PR body (regex)
  - label: 'needs-review'
    body:
      - '/JIRA-[0-9]{1,4}/'
  
  # Multiple matchers (any match = label applied)
  - label: 'dependencies'
    files:
      - 'package.json'
      - 'package-lock.json'
      - 'go.mod'
      - 'go.sum'
    title:
      - '/^(build|deps):/i'
```

**Matchers:**
- `files` - Glob patterns
- `branch` - Regex
- `title` - Regex
- `body` - Regex

**Logic:** Matchers are evaluated independently. Label is applied if **any** matcher succeeds.

## Version Resolution

Auto-increment version based on PR labels:

```yaml
version-resolver:
  major:
    labels:
      - 'breaking'
      - 'major'
  minor:
    labels:
      - 'feature'
      - 'enhancement'
      - 'minor'
  patch:
    labels:
      - 'fix'
      - 'bugfix'
      - 'patch'
  default: patch
```

**Logic:**
1. Scan all PRs since last release
2. Find highest priority label (major > minor > patch)
3. Increment that version component
4. Use `default` if no matching labels found

**Example:**

Current version: `v1.2.3`

Merged PRs:
- PR #1: labels `[bugfix]` → patch
- PR #2: labels `[feature]` → minor
- PR #3: labels `[fix]` → patch

Highest: `minor`

Result: `$RESOLVED_VERSION` = `1.3.0`

## Exclude/Include Pull Requests

### Exclude by Label

```yaml
exclude-labels:
  - 'skip-changelog'
  - 'no-release-notes'
  - 'duplicate'
```

PRs with these labels are omitted from release notes.

### Include Only Specific Labels

```yaml
include-labels:
  - 'production-ready'
  - 'approved'
```

**Only** PRs with these labels appear in release notes.

**Note:** `exclude-labels` and `include-labels` can be used together. Include is applied first, then exclude.

## Exclude Contributors

Remove specific users from `$CONTRIBUTORS`:

```yaml
exclude-contributors:
  - 'dependabot'
  - 'dependabot[bot]'
  - 'github-actions[bot]'
  - 'myusername'
```

Useful for:
- Hiding bots
- Hiding yourself to highlight external contributors

## Replacers

Search and replace in generated changelog:

```yaml
replacers:
  # Link CVE IDs
  - search: '/CVE-(\\d{4})-(\\d+)/g'
    replace: 'https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-$1-$2'
  
  # Link Jira tickets
  - search: '/JIRA-([0-9]+)/g'
    replace: 'https://jira.example.com/browse/JIRA-$1'
  
  # Expand usernames
  - search: '@myorg-bot'
    replace: 'MyOrg Automation Bot'
  
  # Remove internal references
  - search: '/\\[INTERNAL\\].*/g'
    replace: ''
```

Replacers run **in order** on the final changelog body.

## Advanced Template Examples

### Include Previous Tag and Date

```yaml
name-template: 'v$RESOLVED_VERSION'
tag-template: 'v$RESOLVED_VERSION'

template: |
  ## Changes since $PREVIOUS_TAG
  
  $CHANGES
  
  **Full Changelog**: https://github.com/$OWNER/$REPOSITORY/compare/$PREVIOUS_TAG...v$RESOLVED_VERSION
```

### Contributor Shoutouts

```yaml
template: |
  ## What's Changed
  
  $CHANGES
  
  ## 👏 Contributors
  
  Thanks to all contributors who made this release possible: $CONTRIBUTORS
```

### Complex Multi-Section Template

```yaml
template: |
  ## 📦 Release v$RESOLVED_VERSION
  
  ### What's Changed
  
  $CHANGES
  
  ### 🔗 Links
  
  - [Documentation](https://docs.example.com)
  - [Migration Guide](https://docs.example.com/migration/v$RESOLVED_VERSION)
  - [Full Changelog](https://github.com/$OWNER/$REPOSITORY/compare/$PREVIOUS_TAG...v$RESOLVED_VERSION)
  
  ### 👥 Contributors
  
  $CONTRIBUTORS
  
  ---
  
  **Installation:** `npm install $REPOSITORY@$RESOLVED_VERSION`

header: |
  🎉 We're excited to announce the release of v$RESOLVED_VERSION!

footer: |
  ---
  
  Found a bug? [Report it here](https://github.com/$OWNER/$REPOSITORY/issues/new)
```

## Prerelease Configuration

### Basic Prerelease

```yaml
prerelease: true
```

Draft releases will be marked as prerelease.

### Prerelease with Identifier

```yaml
prerelease: true
prerelease-identifier: 'beta'
```

Versions will be: `v1.2.3-beta.1`, `v1.2.3-beta.2`, etc.

**Automatic prerelease increment:** Each merge bumps the prerelease number.

### Conditional Prerelease (via Action Input)

```yaml
# .github/workflows/release-drafter.yml
- uses: release-drafter/release-drafter@v6
  with:
    prerelease: ${{ github.ref != 'refs/heads/main' }}
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Prereleases on non-main branches, regular releases on main.

## Non-Semantic Versioning Projects

Override version format:

```yaml
version-template: '$MAJOR.$MINOR'
```

If current version is `2.5`, then:
- `$NEXT_MINOR_VERSION` = `2.6`
- `$NEXT_MAJOR_VERSION` = `3.0`

### Date-Based Versioning

```yaml
version-template: 'YYYY.MM.DD'
name-template: 'Release $RESOLVED_VERSION'
tag-template: 'release-$RESOLVED_VERSION'
```

Requires manual version setting via action input.

## Action Inputs

Override configuration via workflow:

```yaml
- uses: release-drafter/release-drafter@v6
  with:
    config-name: my-custom-config.yml
    name: 'Custom Release Name'
    tag: 'v1.2.3'
    version: '1.2.3'
    publish: true
    prerelease: false
    latest: true
    commitish: 'main'
    disable-autolabeler: false
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

| Input | Description |
|-------|-------------|
| `config-name` | Config file name (relative to `.github/`). Default: `release-drafter.yml` |
| `name` | Override release name |
| `tag` | Override tag name |
| `version` | Override version (bypasses resolver) |
| `publish` | Immediately publish release. Default: `false` |
| `prerelease` | Mark as prerelease |
| `latest` | Mark as latest |
| `commitish` | Target branch/commit |
| `header` | Prepend text to body |
| `footer` | Append text to body |
| `disable-autolabeler` | Disable auto-labeling |

## Action Outputs

Use outputs in subsequent steps:

```yaml
- uses: release-drafter/release-drafter@v6
  id: release_drafter
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

- name: Use release info
  run: |
    echo "Release ID: ${{ steps.release_drafter.outputs.id }}"
    echo "Release URL: ${{ steps.release_drafter.outputs.html_url }}"
    echo "Tag: ${{ steps.release_drafter.outputs.tag_name }}"
    echo "Version: ${{ steps.release_drafter.outputs.resolved_version }}"
```

| Output | Description |
|--------|-------------|
| `id` | Release ID |
| `name` | Release name |
| `tag_name` | Tag name |
| `body` | Release body (markdown) |
| `html_url` | Release page URL |
| `upload_url` | Asset upload URL |
| `resolved_version` | Resolved version (e.g., `1.2.3`) |
| `major_version` | Major component |
| `minor_version` | Minor component |
| `patch_version` | Patch component |

## Complete Workflow Examples

### Basic: Draft Only

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
  draft:
    runs-on: ubuntu-latest
    steps:
      - uses: release-drafter/release-drafter@v6
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Advanced: Auto-Publish on Tag

```yaml
name: Release

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    types: [opened, reopened, synchronize]

permissions:
  contents: write
  pull-requests: write

jobs:
  draft:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: release-drafter/release-drafter@v6
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  publish:
    if: startsWith(github.ref, 'refs/tags/')
    runs-on: ubuntu-latest
    steps:
      - uses: release-drafter/release-drafter@v6
        with:
          publish: true
          name: 'Release ${{ github.ref_name }}'
          tag: ${{ github.ref_name }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Production: Draft, Build, Publish

```yaml
name: Release Pipeline

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    types: [opened, reopened, synchronize]

permissions:
  contents: write
  pull-requests: write

jobs:
  draft:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: release-drafter/release-drafter@v6
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  build-and-publish:
    if: startsWith(github.ref, 'refs/tags/')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build artifacts
        run: |
          npm ci
          npm run build
          npm run package
      
      - uses: release-drafter/release-drafter@v6
        id: release
        with:
          publish: true
          name: 'Release ${{ github.ref_name }}'
          tag: ${{ github.ref_name }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Upload artifacts
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ steps.release.outputs.upload_url }}
          asset_path: ./dist/myapp.zip
          asset_name: myapp-${{ github.ref_name }}.zip
          asset_content_type: application/zip
```

### Monorepo: Multiple Drafts

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
  draft-api:
    runs-on: ubuntu-latest
    steps:
      - uses: release-drafter/release-drafter@v6
        with:
          config-name: release-drafter-api.yml
          name: 'API v$RESOLVED_VERSION'
          tag: 'api/v$RESOLVED_VERSION'
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  draft-web:
    runs-on: ubuntu-latest
    steps:
      - uses: release-drafter/release-drafter@v6
        with:
          config-name: release-drafter-web.yml
          name: 'Web v$RESOLVED_VERSION'
          tag: 'web/v$RESOLVED_VERSION'
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Integration Patterns

### With Semantic Release

Use Release Drafter for drafts, semantic-release for publishing:

```yaml
name: Release

on:
  push:
    branches: [main]

jobs:
  draft:
    runs-on: ubuntu-latest
    steps:
      - uses: release-drafter/release-drafter@v6
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### With Changesets

```yaml
name: Release

on:
  push:
    branches: [main]

jobs:
  draft:
    runs-on: ubuntu-latest
    steps:
      - uses: release-drafter/release-drafter@v6
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  changesets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: changesets/action@v1
        with:
          publish: npm run release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### With Docker Build

```yaml
name: Release

on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: release-drafter/release-drafter@v6
        id: release
        with:
          publish: true
          tag: ${{ github.ref_name }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: |
            myorg/myapp:${{ steps.release.outputs.resolved_version }}
            myorg/myapp:latest
```

## Troubleshooting

### Draft Not Created

**Symptoms:** Workflow runs but no draft appears.

**Causes:**
1. No PRs merged since last release
2. All PRs excluded by `exclude-labels`
3. `include-labels` filtering out all PRs
4. Insufficient permissions

**Solutions:**
```yaml
permissions:
  contents: write
  pull-requests: write
```

### Auto-Labeler Not Working

**Symptoms:** PRs not getting labels.

**Causes:**
1. Workflow doesn't trigger on PR events
2. Regex patterns incorrect
3. `disable-autolabeler: true`

**Solutions:**
```yaml
on:
  pull_request:
    types: [opened, reopened, synchronize]
```

### Version Not Incrementing

**Symptoms:** `$RESOLVED_VERSION` stays the same.

**Causes:**
1. No PRs with version labels
2. `version-resolver` not configured
3. Previous release tag format doesn't match `tag-template`

**Solutions:**
- Ensure PRs have labels matching `version-resolver`
- Check tag format: `v1.2.3` vs `1.2.3`

### Multiple Drafts Created

**Symptoms:** New draft for each merge.

**Cause:** Tag template doesn't match existing releases.

**Solution:** Ensure `tag-template` format matches published releases.

## Recommended Practices

### Label Strategy

**Recommended labels:**

```yaml
# Create these labels in your repo
- name: 'breaking'
  color: 'D73A49'
  description: 'Breaking change'

- name: 'feature'
  color: '0E8A16'
  description: 'New feature'

- name: 'bugfix'
  color: 'D93F0B'
  description: 'Bug fix'

- name: 'documentation'
  color: '0075CA'
  description: 'Documentation'

- name: 'dependencies'
  color: '0366D6'
  description: 'Dependency update'

- name: 'skip-changelog'
  color: 'FFFFFF'
  description: 'Exclude from release notes'
```

### Workflow Organization

```
.github/
  workflows/
    release-drafter.yml      # Main workflow
  release-drafter.yml         # Main config
  release-drafter-api.yml     # Per-service config (monorepo)
  release-drafter-web.yml
```

### Security

```yaml
permissions:
  contents: write        # Minimum for creating releases
  pull-requests: write   # Minimum for auto-labeling
  # Don't grant unnecessary permissions
```

### Template Guidance

- **Use emojis** for visual categories
- **Link to full changelog** for detailed history
- **Thank contributors** to encourage contributions
- **Include upgrade instructions** if breaking changes
- **Link to documentation** for new features

## Common Configurations

### Dependabot-Friendly

```yaml
autolabeler:
  - label: 'dependencies'
    files:
      - 'package.json'
      - 'package-lock.json'
    branch:
      - '/^dependabot\//'

categories:
  - title: '⬆️ Dependencies'
    label: 'dependencies'
    collapse-after: 10

exclude-contributors:
  - 'dependabot'
  - 'dependabot[bot]'
```

### Conventional Commits Compatible

```yaml
autolabeler:
  - label: 'breaking'
    title:
      - '/^[a-z]+(\(.+\))?!:/'
      - '/^BREAKING CHANGE:/'
  
  - label: 'feature'
    title:
      - '/^feat(\(.+\))?:/'
  
  - label: 'bugfix'
    title:
      - '/^fix(\(.+\))?:/'
  
  - label: 'documentation'
    title:
      - '/^docs(\(.+\))?:/'
  
  - label: 'chore'
    title:
      - '/^chore(\(.+\))?:/'

version-resolver:
  major:
    labels: ['breaking']
  minor:
    labels: ['feature']
  patch:
    labels: ['bugfix']
  default: patch
```

### Bot-Focused

```yaml
autolabeler:
  - label: 'renovate'
    branch:
      - '/^renovate\//'
  
  - label: 'dependabot'
    branch:
      - '/^dependabot\//'

categories:
  - title: '🤖 Automated Updates'
    labels:
      - 'renovate'
      - 'dependabot'
    collapse-after: 5

exclude-contributors:
  - 'renovate[bot]'
  - 'dependabot[bot]'
  - 'github-actions[bot]'
```

## Rules

- **ALWAYS trigger on both push and pull_request events** - push updates drafts, pull_request enables auto-labeling.
- **ALWAYS set proper permissions** - `contents: write` and `pull-requests: write` are required.
- **ALWAYS configure version-resolver** if using `$RESOLVED_VERSION` - otherwise it defaults to patch.
- **ALWAYS use consistent tag format** - `tag-template` must match your existing tags (e.g., `v1.2.3` vs `1.2.3`).
- **ALWAYS test config with a test PR** before relying on it - create a PR, merge it, check draft.
- **Use autolabeler extensively** - reduces manual labeling work and ensures consistent categorization.
- **Use collapse-after for dependency categories** - keeps release notes readable.
- **Exclude bot contributors** from `$CONTRIBUTORS` - focuses on human contributions.
- **Create labels before using them** - autolabeler and categories won't work with non-existent labels.
- **Pin action version** (`@v6`) - don't use `@latest` or `@master` in production.
- **Use emoji in category titles** - improves readability and visual appeal.
- **Link to full changelog** in template - provides access to complete history.
- **Store config in default branch** - Release Drafter only reads from default branch.

## Quick Reference

### Minimal Production Config

```yaml
# .github/workflows/release-drafter.yml
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
  draft:
    runs-on: ubuntu-latest
    steps:
      - uses: release-drafter/release-drafter@v6
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

```yaml
# .github/release-drafter.yml
name-template: 'v$RESOLVED_VERSION'
tag-template: 'v$RESOLVED_VERSION'

template: |
  ## What's Changed
  $CHANGES

change-template: '- $TITLE @$AUTHOR (#$NUMBER)'

categories:
  - title: '🚀 Features'
    labels: ['feature', 'enhancement']
  - title: '🐛 Bug Fixes'
    labels: ['fix', 'bugfix', 'bug']
  - title: '📚 Documentation'
    label: 'documentation'
  - title: '🧰 Maintenance'
    label: 'chore'

version-resolver:
  major:
    labels: ['breaking', 'major']
  minor:
    labels: ['feature', 'minor']
  patch:
    labels: ['fix', 'patch']
  default: patch

autolabeler:
  - label: 'feature'
    branch: ['/^feat(ure)?\/.+/']
  - label: 'bugfix'
    branch: ['/^(fix|bugfix)\/.+/']
  - label: 'documentation'
    files: ['*.md', 'docs/**/*']
  - label: 'dependencies'
    files: ['package*.json', 'go.mod', 'go.sum']
```

## Resources

- [Release Drafter Repository](https://github.com/release-drafter/release-drafter)
- [GitHub Marketplace](https://github.com/marketplace/actions/release-drafter)
- [Configuration Schema](https://github.com/release-drafter/release-drafter/blob/master/schema.json)
- [Example Configurations](https://github.com/release-drafter/release-drafter/tree/master/docs)

## Inputs

- GitHub repository with PRs and labels
- Release Drafter config (`.github/release-drafter.yml`) defining categories, version templates, and autolabel rules

## Outputs

- A GitHub Actions workflow (`.github/workflows/release-drafter.yml`) that maintains a living draft release, updated on every merged PR
- Draft release notes categorised by label and a suggested next semantic version

## Examples

```yaml
# .github/release-drafter.yml — minimal config
template: |
  ## Changes
  $CHANGES
categories:
  - title: "🚀 Features"
    labels: [feature]
  - title: "🐛 Bug Fixes"
    labels: [bug]
version-resolver:
  major: { labels: [breaking] }
  minor: { labels: [feature] }
  default: patch
```
