---
name: direnv
version: "1.0.0"
description: "Set up per-directory environments with direnv for `.envrc` loading, variable management, and nix/devenv/asdf integration."
tags: [direnv, environment, dotenv, nix, shell]
---

# direnv - Environment Variable Manager

Use this skill when working with `.envrc` files, project-specific environment configuration, or integrating development tools that need automatic environment activation.

## When to Use

- Creating or updating a `.envrc` file for a project
- Setting up automatic environment activation for nix, devenv, asdf, or mise
- Troubleshooting environment variable loading or `direnv allow` issues
- Optimising `.envrc` performance with caching or watch files

## Philosophy

**direnv** automatically loads and unloads environment variables based on your current directory. Core benefits:

- **Automatic activation** - No manual sourcing required
- **Secure by default** - Requires explicit approval before executing `.envrc`
- **Shell-agnostic** - Works with bash, zsh, fish, etc.
- **Language-neutral** - Integrates with nix, asdf, mise, devenv, etc.
- **Per-directory isolation** - Each project has its own environment

## Quick Start

### Installation

```bash
# macOS
brew install direnv

# Ubuntu/Debian
apt install direnv

# Nix
nix-env -i direnv
```

### Shell Integration (REQUIRED)

Add to your shell config:

```bash
# ~/.bashrc or ~/.bash_profile
eval "$(direnv hook bash)"

# ~/.zshrc
eval "$(direnv hook zsh)"

# ~/.config/fish/config.fish
direnv hook fish | source
```

**CRITICAL**: Restart your shell after adding the hook.

### Basic .envrc

```bash
# .envrc
export DATABASE_URL="postgres://localhost:5432/myapp"
export API_KEY="dev-key-12345"
export NODE_ENV="development"
```

### Allow the .envrc

```bash
cd /path/to/project
direnv allow
```

The environment is now loaded. When you `cd` away, it's automatically unloaded.

## .envrc Patterns

### Loading .env files

```bash
# .envrc
dotenv
```

Loads `.env` file in the same directory (dotenv format: `KEY=value`).

```bash
# Load from custom path
dotenv .env.local
dotenv config/.env.production
```

### Extending PATH

```bash
# .envrc
PATH_add bin
PATH_add node_modules/.bin
PATH_add scripts
```

Prepends directories to PATH. Automatically creates absolute paths.

### Layout Commands (Language Tools)

direnv provides "layouts" for common language environments:

```bash
# .envrc

# Node.js (uses project's node_modules)
layout node

# Python virtualenv
layout python
layout python python3.11

# Ruby
layout ruby

# Go
layout go

# Perl
layout perl
```

### Custom Layout Functions

```bash
# .envrc
layout_custom() {
  export PROJECT_ROOT="$PWD"
  export TEMP_DIR="$PWD/.tmp"
  mkdir -p "$TEMP_DIR"
  PATH_add "$PROJECT_ROOT/bin"
}

layout custom
```

### Nix Integration

```bash
# .envrc
use nix
```

Loads packages from `shell.nix` or `default.nix` in current directory.

**With flakes:**

```bash
# .envrc
use flake
```

Loads from `flake.nix`.

**Specific flake output:**

```bash
# .envrc
use flake .#devShell
```

### devenv Integration

```bash
# .envrc
eval "$(devenv direnvrc)"
use devenv
```

Integrates with devenv.sh (see devenv skill for details).

### asdf Integration

```bash
# .envrc
use asdf
```

Loads tool versions from `.tool-versions`.

**Specific tools:**

```bash
# .envrc
use asdf nodejs 20.11.0
use asdf python 3.12.1
```

### mise (rtx) Integration

```bash
# .envrc
use mise
```

Loads from `.mise.toml` or `.tool-versions`.

### Conditional Logic

```bash
# .envrc

# OS-specific
if [[ "$OSTYPE" == "darwin"* ]]; then
  export BROWSER="open"
else
  export BROWSER="xdg-open"
fi

# Check file existence
if [ -f .env.local ]; then
  dotenv .env.local
fi

# Check command availability
if has docker; then
  export DOCKER_AVAILABLE=true
fi
```

### Source Other Files

```bash
# .envrc
source ./scripts/env-setup.sh
source_env ../shared/.envrc  # Relative to current dir
source_env_if_exists .envrc.local  # Won't fail if missing
```

### Watching Files (Auto-reload on Change)

```bash
# .envrc
watch_file config/settings.yaml
watch_file .env.production

# Reload .envrc when these files change
```

### Secrets Management

```bash
# .envrc

# Load secrets from 1Password
export OP_SERVICE_ACCOUNT_TOKEN=$(cat ~/.op-token)
export API_KEY=$(op read "op://dev/api-key/password")

# Load from pass (password store)
export DB_PASSWORD=$(pass show myapp/db)

# Load from vault
export VAULT_TOKEN=$(vault print token)
```

**Rule**: Never commit secrets to `.envrc` - load from secure stores or use `.envrc.local` (gitignored).

### Working with Multiple Environments

```bash
# .envrc
ENV="${ENV:-development}"

case "$ENV" in
  production)
    source_env .envrc.production
    ;;
  staging)
    source_env .envrc.staging
    ;;
  *)
    source_env .envrc.development
    ;;
esac
```

Usage: `ENV=staging direnv allow`

### Project Root Detection

```bash
# .envrc
export PROJECT_ROOT="$PWD"
export SRC_ROOT="$PROJECT_ROOT/src"
export BUILD_DIR="$PROJECT_ROOT/build"
```

### Strict Mode

```bash
# .envrc
strict_env  # Exit on errors in .envrc
set -euo pipefail
```

### Logging and Debugging

```bash
# .envrc
log_status "Loading project environment..."
log_error "Failed to load secrets"

# Debug mode
export DIRENV_LOG_FORMAT="$(date) - %s"
```

## stdlib Reference

direnv provides built-in functions in `.envrc`:

| Function | Purpose |
|----------|---------|
| `dotenv [path]` | Load .env file (default: `.env`) |
| `PATH_add <dir>` | Prepend directory to PATH |
| `path_add <var> <dir>` | Prepend to any PATH-like variable |
| `load_prefix <prefix>` | Load include/ lib/ from prefix |
| `layout <name>` | Load predefined layout |
| `use <integration>` | Load integration (nix, asdf, etc.) |
| `watch_file <path>` | Reload .envrc when file changes |
| `source_env <path>` | Source another .envrc |
| `source_env_if_exists <path>` | Source if exists |
| `source_up [path]` | Load parent directory .envrc |
| `has <cmd>` | Check if command exists |
| `log_status <msg>` | Print info message |
| `log_error <msg>` | Print error message |
| `expand_path <path>` | Convert to absolute path |
| `find_up <filename>` | Search up directory tree |
| `direnv_layout_dir` | Get layout dir path (`.direnv/`) |
| `user_rel_path <path>` | Get path relative to `$HOME` |
| `strict_env` | Enable strict error handling |

## Security Model

### Approval Required

direnv requires explicit approval before executing `.envrc`:

```bash
direnv allow          # Approve current .envrc
direnv allow /path    # Approve specific path
direnv deny           # Revoke approval
```

**After editing `.envrc`, you MUST re-approve with `direnv allow`.**

### What Gets Checked

- SHA256 hash of `.envrc` contents
- Stored in `~/.config/direnv/allow/`
- Approval is per-directory + content hash

### Allowed Paths

```bash
# ~/.config/direnv/direnv.toml
[whitelist]
prefix = [ "/home/user/projects" ]
exact = [ "/opt/project" ]
```

Auto-approve paths matching these patterns.

### Block List

```bash
# ~/.config/direnv/direnv.toml
[global]
hide_env_diff = true
disable_stdin = true

[whitelist]
prefix = []  # Block everything except explicit allows
```

## Configuration

Global config: `~/.config/direnv/direnv.toml`

```toml
[global]
# Hide environment diff output
hide_env_diff = false

# Disable reading stdin (security)
disable_stdin = false

# Timeout for direnv execution
load_dotenv = true

# Warn if .envrc takes longer than X seconds
warn_timeout = "5s"

[whitelist]
# Auto-approve these paths
prefix = [ "/home/user/projects", "/opt/work" ]
exact = [ "/etc/myapp" ]
```

## Performance Optimization

### Cache Layout Directories

```bash
# .envrc
layout_dir=$(direnv_layout_dir)
export VENV_DIR="$layout_dir/venv"

if [ ! -d "$VENV_DIR" ]; then
  python -m venv "$VENV_DIR"
fi
```

Layout dir: `.direnv/` (gitignored, persistent across .envrc reloads)

### Lazy Loading

```bash
# .envrc

# Don't run expensive operations on every load
if [ ! -f .direnv/initialized ]; then
  log_status "First-time setup..."
  pnpm install
  touch .direnv/initialized
fi
```

### Conditional Activation

```bash
# .envrc

# Skip activation in CI
if [ -n "$CI" ]; then
  return
fi

# Skip in containers
if [ -f /.dockerenv ]; then
  return
fi
```

### watch_file for Cache Invalidation

```bash
# .envrc
layout_dir=$(direnv_layout_dir)
watch_file package.json

if [ ! -f "$layout_dir/.deps-installed" ] || \
   [ package.json -nt "$layout_dir/.deps-installed" ]; then
  pnpm install
  touch "$layout_dir/.deps-installed"
fi
```

Reinstalls only when `package.json` changes.

## Integration Examples

### With Docker Compose

```bash
# .envrc
export COMPOSE_PROJECT_NAME="myapp"
export COMPOSE_FILE="docker-compose.yml:docker-compose.dev.yml"
```

### With Terraform

```bash
# .envrc
export TF_VAR_environment="dev"
export TF_DATA_DIR="$PWD/.terraform"
export AWS_PROFILE="dev-account"
```

### With Kubernetes

```bash
# .envrc
export KUBECONFIG="$PWD/kubeconfig.yaml"
export KUBECTL_CONTEXT="dev-cluster"
```

### With Make

```bash
# .envrc
export MAKEFLAGS="-j$(nproc)"
export BUILD_TYPE="debug"
```

### With Homebrew

```bash
# .envrc
if [[ "$OSTYPE" == "darwin"* ]] && has brew; then
  eval "$(brew shellenv)"
  PATH_add "$(brew --prefix)/opt/postgresql@15/bin"
fi
```

## Monorepo Patterns

### Root .envrc

```bash
# /project/.envrc
export PROJECT_ROOT="$PWD"
export WORKSPACE="monorepo"

# Load global deps
PATH_add "$PROJECT_ROOT/bin"
```

### Service .envrc

```bash
# /project/services/api/.envrc
source_up  # Load parent .envrc first

export SERVICE_NAME="api"
export SERVICE_PORT=3001

# Service-specific PATH
PATH_add "$PWD/scripts"

# Load service env
dotenv .env.api
```

### Workspace .envrc

```bash
# /project/.envrc
export WORKSPACE_ROOT="$PWD"

# Detect current service
if [[ "$PWD" == *"/services/"* ]]; then
  SERVICE=$(basename "$PWD")
  export SERVICE_NAME="$SERVICE"
fi
```

## Troubleshooting

### Check direnv status

```bash
direnv status
```

Shows:
- Current allowed paths
- Found .envrc files
- Whether environment is loaded

### Debug mode

```bash
direnv exec . env | grep -v '^_'  # Show exported vars
direnv export json                # JSON output
```

### Force reload

```bash
direnv reload
```

### Clear all approvals

```bash
rm -rf ~/.config/direnv/allow/
```

### Check hook installation

```bash
echo $DIRENV_DIR  # Should be set when in project
type direnv       # Should show function, not binary
```

If `direnv` is a binary (not a shell function), the hook is not installed.

### Performance profiling

```bash
time direnv exec . true
```

If > 1 second, optimize your `.envrc`:
- Remove expensive commands
- Use layout directories for caching
- Add conditional checks to skip unnecessary work

## Common Issues

| Problem | Solution |
|---------|----------|
| Changes not applied | Run `direnv allow` after editing `.envrc` |
| "Command not found" after cd | Check shell hook is installed |
| Slow activation | Profile with `time direnv exec . true`, optimize .envrc |
| Variables remain loaded | Check for conflicting shell configs setting same vars |
| .envrc not found | Ensure no typos, check `direnv status` |
| Permission denied | Check file permissions, run `direnv allow` |

## Rules

- **ALWAYS commit `.envrc`** to version control (but NOT `.envrc.local` if it contains secrets).
- **ALWAYS gitignore `.direnv/`** - it's a cache directory.
- **NEVER put secrets directly in `.envrc`** - load from secure stores or use `.envrc.local`.
- **ALWAYS run `direnv allow`** after editing `.envrc` - it won't activate without approval.
- **ALWAYS test `.envrc` changes** by cd-ing in/out of the directory.
- **Use `source_up`** in nested directories to inherit parent environment before extending.
- **Use `layout` commands** instead of manual PATH manipulation when available.
- **Use `watch_file`** for cache invalidation based on file changes.
- **Use `.envrc.local`** (gitignored) for personal/secret overrides.
- **Profile slow `.envrc` files** with `time direnv exec . true` and optimize.
- **Document non-obvious .envrc logic** with comments - future you will thank you.
- **Use `has` to check command existence** before using tools that might not be installed.

## Quick Reference

```bash
# Approve .envrc
direnv allow

# Deny/revoke
direnv deny

# Force reload
direnv reload

# Check status
direnv status

# Edit safely (auto-reloads)
direnv edit [path]

# Show current environment diff
direnv export json

# Execute command in environment
direnv exec <path> <cmd>
```

## Resources

- [Official Documentation](https://direnv.net/)
- [stdlib Reference](https://direnv.net/man/direnv-stdlib.1.html)
- [GitHub Repository](https://github.com/direnv/direnv)
- [Wiki](https://github.com/direnv/direnv/wiki)

## Inputs

- Project root directory with an existing or new `.envrc` file
- Integration target (nix flake, devenv, asdf, mise, or plain env vars)

## Outputs

- A `.envrc` file (and optionally a `.envrc.local` for personal overrides) that automatically loads the project environment on directory entry

## Examples

```bash
# .envrc — use a devenv environment
use devenv

# .envrc — load env vars and add local bin to PATH
dotenv .env
PATH_add bin
```
