---
name: conventional-commits
description: "Conventional Commits specification expert. USE WHEN writing commit messages, configuring commit linting, setting up automated versioning, or generating changelogs. Covers commit message structure, types, scopes, breaking changes, automated tooling (commitlint, semantic-release, standard-version), and best practices for maintainable git history."
---

# Conventional Commits - Structured Commit Messages

Use this skill when writing commit messages, setting up commit linting, or implementing automated versioning and changelog generation based on the Conventional Commits specification.

## Philosophy

**Conventional Commits** is a specification for adding human and machine-readable meaning to commit messages.

**Core benefits**:
- **Automated versioning** - Determine semantic version bumps (major/minor/patch)
- **Automated changelogs** - Generate CHANGELOG.md from commit history
- **Better history** - Structured, searchable, filterable commit log
- **Clear communication** - Team understands impact of changes
- **Tooling integration** - CI/CD can act on commit types

**Key principle**: Commit messages are not just history—they're documentation and automation triggers.

## Specification Overview

### Basic Structure

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Simple Example

```
feat(auth): add JWT token refresh endpoint
```

### Complete Example

```
feat(auth)!: migrate to OAuth 2.0

Replace custom authentication with OAuth 2.0 standard.
This improves security and enables SSO integration.

BREAKING CHANGE: API endpoints /login and /logout have been removed.
Use /oauth/authorize and /oauth/token instead.

Closes #123
Refs #456
```

## Commit Message Components

### 1. Type (Required)

**Format**: `<type>`

**Purpose**: Describes the category of change.

**Standard types**:

| Type | Description | Version Bump | Changelog Section |
|------|-------------|--------------|-------------------|
| `feat` | New feature | MINOR (0.x.0) | Features |
| `fix` | Bug fix | PATCH (0.0.x) | Bug Fixes |
| `docs` | Documentation only | PATCH* | Documentation |
| `style` | Code style (formatting, whitespace) | None* | None |
| `refactor` | Code refactoring (no behavior change) | None* | None |
| `perf` | Performance improvement | PATCH | Performance |
| `test` | Adding/updating tests | None* | None |
| `build` | Build system or dependencies | None* | Build System |
| `ci` | CI/CD configuration | None* | CI |
| `chore` | Maintenance tasks | None* | Chores |
| `revert` | Reverts a previous commit | Depends | Reverts |

*Version bump behavior depends on configuration

**Examples**:
```
feat: add user profile page
fix: resolve memory leak in data processor
docs: update installation guide
style: format code with prettier
refactor: extract validation logic to separate module
perf: optimize database queries
test: add unit tests for auth service
build: upgrade webpack to v5
ci: add Docker build step
chore: update dependencies
revert: revert "feat: add experimental feature"
```

### 2. Scope (Optional)

**Format**: `<type>(<scope>)`

**Purpose**: Specifies the area of codebase affected.

**Common scopes** (project-dependent):

**For web applications**:
```
feat(auth): add password reset
feat(ui): update button styles
feat(api): add rate limiting
feat(db): add user index
```

**For libraries**:
```
fix(parser): handle edge case in JSON parsing
feat(compiler): add source map generation
docs(api): document new methods
```

**For monorepos**:
```
feat(web): add landing page
fix(mobile): resolve crash on Android
chore(deps): update shared dependencies
```

**Scope naming conventions**:
- Lowercase
- Short (1-2 words)
- Consistent across team
- Match project structure (e.g., module names)

**Multiple scopes**:
```
feat(api,ui): add user search functionality
```

**No scope** (when change is global):
```
chore: update Node.js version
docs: update README
```

### 3. Description (Required)

**Format**: `<type>[scope]: <description>`

**Rules**:
- Lowercase first letter (unless proper noun)
- No period at the end
- Imperative mood ("add" not "added" or "adds")
- Concise (<72 characters recommended)
- Describes WHAT changed, not HOW

**Good examples**:
```
feat(auth): add two-factor authentication
fix(api): resolve race condition in user creation
docs: update contributing guidelines
refactor(parser): simplify token handling logic
```

**Bad examples**:
```
feat(auth): Added two-factor authentication.  ❌ (past tense, period)
fix(api): Fixes the race condition         ❌ (present tense, not imperative)
docs: Updated README.md file.              ❌ (period, past tense)
refactor: changes to parser                ❌ (vague, lowercase after colon)
```

### 4. Breaking Change Indicator (Optional)

**Format**: `<type>[scope]!: <description>` or `BREAKING CHANGE:` in footer

**Purpose**: Signals a breaking change that requires major version bump.

**Method 1: `!` after type/scope**:
```
feat(api)!: change response format to JSON:API spec
```

**Method 2: `BREAKING CHANGE:` footer**:
```
feat(api): update user endpoint

BREAKING CHANGE: Response format changed to JSON:API specification.
Old format: { user: {...} }
New format: { data: { type: "user", attributes: {...} } }
```

**Method 3: Both (recommended for clarity)**:
```
feat(api)!: change response format to JSON:API spec

BREAKING CHANGE: Response format changed. See migration guide.
```

**Breaking change guidelines**:
- Always include in footer when using `!`
- Explain what broke and how to migrate
- Consider adding migration guide link
- Use for incompatible API changes

### 5. Body (Optional)

**Format**: Blank line after description, then body text.

**Purpose**: Provides context, motivation, and implementation details.

**When to include**:
- Complex changes that need explanation
- Non-obvious implementation decisions
- Context for "why" not just "what"
- Breaking changes details

**Structure**:
- Use imperative mood (like description)
- Wrap at 72 characters
- Multiple paragraphs allowed (separated by blank lines)
- Can include bullet points

**Example**:
```
refactor(auth): migrate from JWT to session-based auth

Session-based authentication provides better security for our
use case since we can invalidate sessions server-side. JWTs
cannot be invalidated without maintaining a blocklist.

Implementation notes:
- Redis used for session storage
- Session TTL set to 24 hours
- Auto-renewal on activity
```

### 6. Footer (Optional)

**Format**: Blank line after body, then footer(s).

**Purpose**: References, breaking changes, co-authors.

**Common footers**:

**Issue references**:
```
Closes #123
Fixes #456
Resolves #789
Refs #101
```

**Breaking changes**:
```
BREAKING CHANGE: API endpoint /users renamed to /accounts
```

**Co-authors**:
```
Co-authored-by: Jane Doe <jane@example.com>
Co-authored-by: John Smith <john@example.com>
```

**Reviewed by**:
```
Reviewed-by: Alice <alice@example.com>
```

**Complete example with multiple footers**:
```
feat(api)!: change authentication flow

Migrate from basic auth to OAuth 2.0 for better security
and third-party integration support.

BREAKING CHANGE: /login endpoint removed. Use /oauth/authorize instead.
Closes #234
Refs #189
Co-authored-by: Jane Doe <jane@example.com>
```

## Full Examples

### Feature Addition

```
feat(checkout): add guest checkout option

Allow users to complete purchases without creating an account.
Guest users receive order confirmation via email and can track
orders using order number and email combination.

Closes #145
```

### Bug Fix

```
fix(payment): resolve double charge issue

Prevent duplicate payment processing when user clicks
"Pay Now" multiple times. Added request deduplication
using idempotency keys.

Fixes #892
```

### Breaking Change

```
feat(api)!: migrate to GraphQL

Replace REST API with GraphQL for better flexibility
and reduced over-fetching.

BREAKING CHANGE: All REST endpoints under /api/v1 have been
removed. Use GraphQL endpoint at /graphql instead.
See migration guide: docs/migration-v2.md

Closes #567
```

### Documentation

```
docs(readme): add Docker deployment guide

Include step-by-step instructions for deploying the application
using Docker Compose, including environment variables and
volume configuration.
```

### Refactoring

```
refactor(database): extract repository pattern

Move database queries from controllers to repository classes
for better separation of concerns and testability.

No functional changes.
```

### Performance Improvement

```
perf(search): optimize full-text search queries

Replace LIKE queries with full-text search indexes.
Reduces average search time from 800ms to 50ms.

Refs #234
```

### Dependency Update

```
build(deps): upgrade React to v18

Update React and React DOM to v18 for concurrent rendering
features and automatic batching improvements.

BREAKING CHANGE: React 18 requires Node.js >= 14
```

### CI/CD Change

```
ci: add automated security scanning

Integrate Snyk to scan for vulnerabilities on every PR.
Build fails if high-severity issues are detected.
```

### Revert

```
revert: revert "feat(search): add fuzzy matching"

This reverts commit a1b2c3d4e5f6.

Fuzzy matching caused performance degradation on large datasets.
Will reimplement with optimized algorithm in future PR.

Refs #789
```

## Commit Message Best Practices

### 1. Atomic Commits

**One logical change per commit**:

✅ **Good** (atomic):
```
fix(auth): resolve login redirect loop
feat(profile): add avatar upload
test(auth): add login flow tests
```

❌ **Bad** (mixed changes):
```
feat(profile): add avatar upload, fix login bug, update tests
```

### 2. Imperative Mood

**Use present tense, imperative mood**:

✅ **Good**:
```
add user authentication
fix memory leak
update dependencies
remove deprecated method
```

❌ **Bad**:
```
added user authentication  (past tense)
fixes memory leak          (present tense)
updating dependencies      (gerund)
removed deprecated method  (past tense)
```

**Why imperative?** It matches Git's own convention:
- `git merge` → "Merge branch 'feature'"
- `git revert` → "Revert 'commit message'"

### 3. Describe WHAT and WHY, Not HOW

✅ **Good**:
```
perf(api): optimize user query performance

Reduce average response time from 800ms to 50ms by adding
database indexes on frequently queried fields.
```

❌ **Bad**:
```
perf(api): add indexes to users table on email and created_at columns

(Focuses on HOW, not WHAT/WHY)
```

### 4. Length Guidelines

**Description**:
- 50-72 characters (hard limit: 72)
- One line summary

**Body**:
- Wrap at 72 characters
- Explain context and motivation
- Multiple paragraphs allowed

**Example**:
```
feat(auth): add OAuth 2.0 support                    <- 38 chars

Integrate OAuth 2.0 for third-party authentication   <- 72 chars
enabling users to log in with Google, GitHub, and    <- 72 chars
Microsoft accounts.                                   <- 72 chars
```

### 5. Scope Consistency

**Define scopes upfront**:

Create a `.commitlintrc.js` with allowed scopes:
```javascript
module.exports = {
  rules: {
    'scope-enum': [
      2,
      'always',
      [
        'auth',
        'api',
        'ui',
        'db',
        'deps',
        'config'
      ]
    ]
  }
}
```

**Benefits**:
- Consistent scopes across team
- Easier to filter/search commits
- Better changelog organization

### 6. When to Use Each Type

| Use Case | Type | Example |
|----------|------|---------|
| Add new functionality | `feat` | `feat(api): add user export endpoint` |
| Fix a bug | `fix` | `fix(auth): resolve token expiration bug` |
| Improve performance | `perf` | `perf(db): add index for faster queries` |
| Refactor code | `refactor` | `refactor(api): extract validation logic` |
| Change code style | `style` | `style: format with prettier` |
| Add/update tests | `test` | `test(auth): add login flow tests` |
| Update documentation | `docs` | `docs: update API reference` |
| Change build/deps | `build` | `build: upgrade webpack to v5` |
| Change CI/CD | `ci` | `ci: add deployment workflow` |
| Maintenance | `chore` | `chore: update copyright year` |

## Tooling Setup

### commitlint

**Purpose**: Lint commit messages to enforce Conventional Commits.

#### Installation

```bash
npm install --save-dev @commitlint/{cli,config-conventional}
```

#### Configuration

```javascript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',
        'fix',
        'docs',
        'style',
        'refactor',
        'perf',
        'test',
        'build',
        'ci',
        'chore',
        'revert'
      ]
    ],
    'scope-enum': [
      2,
      'always',
      [
        'auth',
        'api',
        'ui',
        'db',
        'deps'
      ]
    ],
    'scope-empty': [2, 'never'], // Require scope
    'subject-case': [2, 'always', 'lower-case'],
    'subject-max-length': [2, 'always', 72],
    'body-max-line-length': [2, 'always', 100]
  }
}
```

#### Custom Rules

```javascript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  
  rules: {
    // Require scope for certain types
    'scope-empty': [2, 'never'],
    
    // Custom subject pattern
    'subject-exclamation-mark': [2, 'never'],
    
    // Require body for breaking changes
    'body-min-length': [
      2,
      'always',
      (parsed) => parsed.header.includes('!') ? 20 : 0
    ]
  }
}
```

### Husky + commitlint

**Purpose**: Run commitlint on every commit.

#### Installation

```bash
npm install --save-dev husky
npx husky install
npx husky add .husky/commit-msg 'npx --no -- commitlint --edit $1'
```

#### Add to package.json

```json
{
  "scripts": {
    "prepare": "husky install"
  }
}
```

**Now every commit will be linted!**

### Commitizen

**Purpose**: Interactive CLI for writing conventional commits.

#### Installation

```bash
npm install --save-dev commitizen cz-conventional-changelog
npx commitizen init cz-conventional-changelog --save-dev --save-exact
```

#### Configuration

```json
// package.json
{
  "scripts": {
    "commit": "cz"
  },
  "config": {
    "commitizen": {
      "path": "cz-conventional-changelog"
    }
  }
}
```

#### Usage

```bash
git add .
npm run commit
```

**Interactive prompts**:
```
? Select the type of change: (Use arrow keys)
❯ feat:     A new feature
  fix:      A bug fix
  docs:     Documentation only changes
  ...

? What is the scope of this change: (press enter to skip)
  auth

? Write a short description:
  add two-factor authentication

? Provide a longer description: (press enter to skip)
  

? Are there any breaking changes?
  No

? Does this change affect any open issues?
  Closes #123
```

### Custom Commitizen Adapter

**For custom prompts**:

```bash
npm install --save-dev cz-customizable
```

```javascript
// .cz-config.js
module.exports = {
  types: [
    { value: 'feat', name: 'feat:     A new feature' },
    { value: 'fix', name: 'fix:      A bug fix' },
    { value: 'docs', name: 'docs:     Documentation changes' },
    { value: 'style', name: 'style:    Code style changes' },
    { value: 'refactor', name: 'refactor: Code refactoring' },
    { value: 'perf', name: 'perf:     Performance improvements' },
    { value: 'test', name: 'test:     Add or update tests' },
    { value: 'build', name: 'build:    Build system changes' },
    { value: 'ci', name: 'ci:       CI/CD changes' },
    { value: 'chore', name: 'chore:    Other changes' }
  ],

  scopes: [
    { name: 'auth' },
    { name: 'api' },
    { name: 'ui' },
    { name: 'db' },
    { name: 'deps' }
  ],

  scopeOverrides: {
    feat: [
      { name: 'auth' },
      { name: 'api' },
      { name: 'ui' }
    ]
  },

  messages: {
    type: 'Select the type of change:',
    scope: 'Select the scope:',
    subject: 'Write a short description:\n',
    body: 'Provide a longer description (optional):\n',
    breaking: 'List any breaking changes (optional):\n',
    footer: 'List any issues closed (e.g., #123, #456):\n',
    confirmCommit: 'Confirm commit?'
  },

  allowCustomScopes: true,
  allowBreakingChanges: ['feat', 'fix'],
  subjectLimit: 72
}
```

## Automated Versioning

### semantic-release

**Purpose**: Fully automated versioning and changelog generation.

#### Installation

```bash
npm install --save-dev semantic-release
```

#### Configuration

```json
// package.json
{
  "scripts": {
    "semantic-release": "semantic-release"
  },
  "release": {
    "branches": ["main"],
    "plugins": [
      "@semantic-release/commit-analyzer",
      "@semantic-release/release-notes-generator",
      "@semantic-release/changelog",
      "@semantic-release/npm",
      "@semantic-release/github",
      "@semantic-release/git"
    ]
  }
}
```

#### GitHub Actions

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    branches:
      - main

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
      pull-requests: write
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      
      - run: npm ci
      
      - run: npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

**What it does**:
1. Analyzes commits since last release
2. Determines version bump (major/minor/patch)
3. Generates changelog
4. Creates git tag
5. Publishes to npm
6. Creates GitHub release

### standard-version

**Purpose**: Manual versioning with conventional commits.

#### Installation

```bash
npm install --save-dev standard-version
```

#### Configuration

```json
// package.json
{
  "scripts": {
    "release": "standard-version",
    "release:minor": "standard-version --release-as minor",
    "release:major": "standard-version --release-as major"
  },
  "standard-version": {
    "types": [
      { "type": "feat", "section": "Features" },
      { "type": "fix", "section": "Bug Fixes" },
      { "type": "chore", "hidden": true },
      { "type": "docs", "section": "Documentation" },
      { "type": "style", "hidden": true },
      { "type": "refactor", "section": "Code Refactoring" },
      { "type": "perf", "section": "Performance Improvements" },
      { "type": "test", "hidden": true }
    ]
  }
}
```

#### Usage

```bash
# Automatic version bump
npm run release

# Specific version bump
npm run release:minor
npm run release:major

# Preview without committing
npm run release -- --dry-run

# Push release
git push --follow-tags origin main
```

**What it does**:
1. Bumps version in package.json
2. Generates CHANGELOG.md
3. Commits changes
4. Creates git tag

### Version Bump Rules

**Based on commit types**:

| Commit Type | Version Bump | Example |
|-------------|--------------|---------|
| `feat` | MINOR (0.x.0) | 1.2.0 → 1.3.0 |
| `fix` | PATCH (0.0.x) | 1.2.0 → 1.2.1 |
| `perf` | PATCH (0.0.x) | 1.2.0 → 1.2.1 |
| `!` or `BREAKING CHANGE` | MAJOR (x.0.0) | 1.2.0 → 2.0.0 |
| `docs`, `style`, `refactor`, `test`, `chore` | No bump* | - |

*Configurable based on tool settings

**Pre-1.0.0 versions**:
- BREAKING CHANGE → MINOR (0.x.0)
- feat → MINOR (0.x.0)
- fix → PATCH (0.0.x)

## Changelog Generation

### Automatic Generation

**With semantic-release**:

Changelog generated automatically on release:

```markdown
# Changelog

## [2.0.0](https://github.com/user/repo/compare/v1.2.0...v2.0.0) (2025-02-14)

### ⚠ BREAKING CHANGES

* **api:** Response format changed to JSON:API spec

### Features

* **api:** add user search endpoint ([a1b2c3d](link))
* **auth:** add OAuth 2.0 support ([e4f5g6h](link))

### Bug Fixes

* **ui:** resolve button alignment issue ([i7j8k9l](link))
```

### Manual Generation

**With conventional-changelog-cli**:

```bash
npm install --save-dev conventional-changelog-cli
```

```json
// package.json
{
  "scripts": {
    "changelog": "conventional-changelog -p angular -i CHANGELOG.md -s"
  }
}
```

Generate changelog:
```bash
npm run changelog
```

## Git Hooks Integration

### Complete Husky Setup

```bash
# Install
npm install --save-dev husky lint-staged

# Initialize
npx husky install
```

#### Pre-commit: Lint Staged Files

```bash
npx husky add .husky/pre-commit 'npx lint-staged'
```

```json
// package.json
{
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md,yml,yaml}": ["prettier --write"]
  }
}
```

#### Commit-msg: Lint Commit Message

```bash
npx husky add .husky/commit-msg 'npx --no -- commitlint --edit $1'
```

#### Prepare-commit-msg: Add Ticket Number

```bash
npx husky add .husky/prepare-commit-msg
```

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

# Extract ticket number from branch name
BRANCH_NAME=$(git symbolic-ref --short HEAD)
TICKET=$(echo $BRANCH_NAME | grep -oE '[A-Z]+-[0-9]+')

if [ -n "$TICKET" ]; then
  # Check if ticket number already in commit message
  if ! grep -q "$TICKET" "$1"; then
    # Append ticket number to commit message
    echo "\n\nRefs $TICKET" >> "$1"
  fi
fi
```

## Team Adoption Strategies

### 1. Gradual Rollout

**Phase 1: Education**
- Share specification with team
- Explain benefits
- Provide examples

**Phase 2: Soft Enforcement**
- Add commitlint (warnings only)
- Encourage Commitizen usage
- Review commits in PRs

**Phase 3: Hard Enforcement**
- Enable commitlint errors
- Required git hooks
- CI checks for commit format

### 2. Documentation

Create `.github/COMMIT_CONVENTION.md`:

```markdown
# Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/).

## Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

## Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style
- `refactor`: Code refactoring
- `perf`: Performance
- `test`: Tests
- `build`: Build system
- `ci`: CI/CD
- `chore`: Maintenance

## Scopes

- `auth`: Authentication
- `api`: API endpoints
- `ui`: User interface
- `db`: Database

## Examples

```
feat(auth): add two-factor authentication
fix(api): resolve race condition in user creation
docs: update README with setup instructions
```

## Tools

Use Commitizen for interactive commit creation:
```bash
npm run commit
```

See [full specification](https://www.conventionalcommits.org/).
```

### 3. PR Template

`.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Description

<!-- Describe your changes -->

## Type of Change

- [ ] feat: New feature
- [ ] fix: Bug fix
- [ ] docs: Documentation
- [ ] refactor: Code refactoring
- [ ] test: Tests

## Breaking Changes

- [ ] This PR introduces breaking changes

If yes, describe migration path:

## Checklist

- [ ] Commits follow Conventional Commits
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if not automated)
```

## Common Pitfalls

### ❌ Mistakes to Avoid

| Mistake | Problem | Fix |
|---------|---------|-----|
| `Fix bug` | Too vague | `fix(auth): resolve login redirect loop` |
| `feat(api): Updated endpoint` | Wrong tense | `feat(api): update endpoint response format` |
| `Added new feature.` | Period, past tense | `feat: add user profile page` |
| `fix: Fixed issue #123` | Redundant "issue" | `fix: resolve memory leak (#123)` |
| `feat: lots of changes` | Too vague | Multiple atomic commits |
| `WIP: work in progress` | Not conventional | Use draft PR, squash before merge |
| `asdf` | Not descriptive | Follow format |

### ✅ Best Practices

| Practice | Benefit | Example |
|----------|---------|---------|
| **Atomic commits** | Clear history | One logical change per commit |
| **Descriptive scopes** | Easy filtering | `feat(auth): ...` |
| **Imperative mood** | Consistency | `add` not `added` |
| **Reference issues** | Traceability | `Closes #123` |
| **Explain breaking changes** | Clear migration | `BREAKING CHANGE: ...` |
| **Use body for context** | Better understanding | Why the change was made |
| **Test before commit** | Quality | Ensure code works |

## Advanced Patterns

### Monorepo Commits

**Use package name as scope**:

```
feat(web): add landing page
fix(mobile): resolve Android crash
chore(shared): update dependencies
```

**Or workspace prefix**:

```
feat(@org/web): add landing page
fix(@org/mobile): resolve Android crash
```

### Multiple Scopes

**When change affects multiple areas**:

```
feat(api,ui): add user search functionality
```

### Long Descriptions

**Use body for details**:

```
feat(api): add pagination support

Implement cursor-based pagination for better performance
with large datasets. Uses base64-encoded cursors for
secure, opaque pagination tokens.

API changes:
- Add `cursor` query parameter
- Add `nextCursor` and `prevCursor` in response
- Deprecated `offset` parameter (still supported)

Closes #456
```

### Co-authored Commits

**Credit multiple authors**:

```
feat(auth): implement SSO integration

Co-authored-by: Jane Doe <jane@example.com>
Co-authored-by: John Smith <john@example.com>
```

### Revert Commits

**Always reference original commit**:

```
revert: revert "feat(search): add fuzzy matching"

This reverts commit a1b2c3d4e5f6.

Fuzzy matching caused 50% performance degradation.
Will reimplement with optimized algorithm.

Refs #789
```

## Troubleshooting

### commitlint Fails

**Error**: `subject must not be sentence-case`

**Fix**:
```
# Bad
feat(api): Add new endpoint

# Good
feat(api): add new endpoint
```

**Error**: `type must be one of [feat, fix, ...]`

**Fix**: Use standard type or configure custom types in `.commitlintrc.js`.

### Hook Not Running

**Check hook is executable**:
```bash
chmod +x .husky/commit-msg
```

**Verify Husky installed**:
```bash
npx husky install
```

### Commitizen Not Found

**Error**: `cz: command not found`

**Fix**:
```bash
npm install --save-dev commitizen
npx cz  # Or npm run commit
```

## Rules

- **ALWAYS use imperative mood** - "add" not "added" or "adds".
- **ALWAYS use lowercase** for type, scope, and description (unless proper noun).
- **NEVER end description with period** - Keep it concise.
- **ALWAYS use `!` for breaking changes** - And explain in footer.
- **ALWAYS make atomic commits** - One logical change per commit.
- **NEVER mix multiple changes** - Separate feat, fix, refactor into different commits.
- **ALWAYS reference issues** - Use `Closes #123` in footer.
- **ALWAYS explain breaking changes** - Include migration path.
- **Use `feat` for new features** - Even small ones.
- **Use `fix` for bug fixes** - No matter how small.
- **Use `docs` for documentation only** - No code changes.
- **Use `chore` for maintenance** - Build, dependencies, etc.
- **Keep description under 72 chars** - One-line summary.
- **Use body for complex changes** - Explain WHY not just WHAT.

## Quick Reference

### Commit Template

```bash
# Configure git to use template
git config commit.template .gitmessage
```

```
# .gitmessage
# <type>(<scope>): <description>
# 
# [optional body]
# 
# [optional footer(s)]
#
# Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
# Scope: module, component, or area of codebase
# Description: imperative mood, lowercase, no period, <72 chars
#
# Body: explain WHAT and WHY (not HOW), wrap at 72 chars
#
# Footer: BREAKING CHANGE, Closes #123, Refs #456
```

### Alias for Quick Commits

```bash
# ~/.gitconfig or run git config --global alias.*

[alias]
  c = commit
  cm = commit -m
  cma = commit -am
  ca = commit --amend
  can = commit --amend --no-edit
```

**Usage**:
```bash
git cm "feat(api): add new endpoint"
git ca  # Amend last commit
```

## Resources

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [commitlint Documentation](https://commitlint.js.org/)
- [Commitizen Documentation](https://github.com/commitizen/cz-cli)
- [semantic-release Documentation](https://semantic-release.gitbook.io/)
- [Angular Commit Guidelines](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit)
- [Conventional Changelog](https://github.com/conventional-changelog/conventional-changelog)
