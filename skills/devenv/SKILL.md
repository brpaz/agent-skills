---
name: devenv
version: "1.0.0"
description: "Define Nix-based development environments with devenv.sh, including packages, services, scripts, tests, and containers."
tags: [nix, devenv, development-environment, nixos, direnv]
---

# devenv.sh - Nix-powered Developer Environments

Use this skill when modifying `devenv.nix`, `devenv.yaml`, or working with devenv CLI commands. This covers the full devenv configuration surface.

## When to Use

- Creating or modifying a `devenv.nix` or `devenv.yaml` for a project
- Adding packages, language runtimes, services, or scripts to a dev environment
- Integrating devenv with direnv for automatic environment activation
- Pinning or updating devenv inputs via `devenv.lock`

## Project File Structure

| File | Purpose | Commit? |
|------|---------|---------|
| `devenv.nix` | Main configuration (Nix expression) | Yes |
| `devenv.yaml` | Inputs, imports, and settings | Yes |
| `devenv.lock` | Pinned input revisions (auto-generated) | Yes |
| `.envrc` | direnv integration (`use devenv`) | Yes |
| `devenv.local.nix` | Local overrides (not committed) | No |
| `devenv.local.yaml` | Local input overrides | No |
| `.devenv/` | Generated state directory | No (gitignored) |
| `.devenv.flake.nix` | Auto-generated flake wrapper | No (gitignored) |

## devenv.nix Structure

Every `devenv.nix` is a Nix function receiving a module argument set:

```nix
{ pkgs, lib, config, inputs, ... }:

{
  # Configuration goes here
}
```

**Key parameters:**
- `pkgs` - Nixpkgs package set
- `lib` - Nixpkgs library functions
- `config` - The resolved devenv configuration (self-referencing)
- `inputs` - Flake inputs defined in `devenv.yaml`

## devenv.yaml Structure

```yaml
inputs:
  nixpkgs:
    url: github:cachix/devenv-nixpkgs/rolling

# Optional additional inputs
# inputs:
#   nixpkgs-stable:
#     url: github:NixOS/nixpkgs/nixos-24.11

# Optional imports from local files or inputs
# imports:
#   - ./backend/devenv.nix
#   - inputs:myinput/devenv-module.nix

# Allow unfree packages
# allowUnfree: true
# permittedUnfreePackages:
#   - "terraform"

# Impure mode (access host env vars)
# impure: true
```

## Environment Variables

**Built-in variables available inside devenv shell:**
- `DEVENV_ROOT` - Project root directory
- `DEVENV_DOTFILE` - Path to `.devenv/` directory
- `DEVENV_STATE` - Persistent state directory (for services data)
- `DEVENV_RUNTIME` - Runtime directory (temp, cleared on reboot)
- `DEVENV_PROFILE` - Current Nix profile path

**Setting custom env vars:**

```nix
{
  env.DATABASE_URL = "postgres://localhost:5432/mydb";
  env.API_PORT = "3000";

  # Reference other config values
  env.GREETING = "Running in ${config.env.DEVENV_ROOT}";
}
```

## Packages

```nix
{
  # Add packages from nixpkgs
  packages = [
    pkgs.git
    pkgs.jq
    pkgs.curl
    pkgs.docker-compose
  ];
}
```

Search for packages: `devenv search <name>`

## Languages

Languages are enabled via toggle modules. Each language module provides tooling, compilers, and package managers.

```nix
{
  # Node.js
  languages.javascript = {
    enable = true;
    package = pkgs.nodejs_22;  # Override default version
    pnpm.enable = true;
    pnpm.install.enable = true;  # Auto-install on shell entry
  };

  # Python
  languages.python = {
    enable = true;
    version = "3.12";
    venv.enable = true;
    venv.requirements = ./requirements.txt;
  };

  # Rust
  languages.rust = {
    enable = true;
    channel = "stable";  # "stable", "nightly", or "beta"
  };

  # Go
  languages.go.enable = true;

  # Ruby
  languages.ruby = {
    enable = true;
    bundler.enable = true;
  };
}
```

## Scripts

Custom commands available in the devenv shell:

```nix
{
  # Simple script
  scripts.dev.exec = ''
    pnpm run dev
  '';

  # Script with extra packages in scope
  scripts.fetch-data.exec = ''
    curl -s https://api.example.com | jq '.data'
  '';
  scripts.fetch-data.packages = [ pkgs.curl pkgs.jq ];

  # Pin binaries to avoid PATH conflicts
  scripts.build.exec = ''
    ${pkgs.nodejs}/bin/node scripts/build.js
  '';

  # Use a specific interpreter
  scripts.analyze.exec = ''
    import sys
    print(sys.version)
  '';
  scripts.analyze.package = config.languages.python.package;
  scripts.analyze.binary = "python3";
}
```

## enterShell

Code that runs every time you enter the devenv shell:

```nix
{
  enterShell = ''
    echo "Welcome to the dev environment"
    echo "Node: $(node --version)"
  '';
}
```

**Prefer tasks over enterShell for anything non-trivial** - tasks support caching, dependencies, and status checks.

## Processes

Long-running processes managed by devenv (started with `devenv up`):

```nix
{
  # Simple process
  processes.api.exec = "pnpm run dev";

  # Process with working directory
  processes.frontend = {
    exec = "pnpm run dev";
    cwd = "./frontend";
  };

  # Process dependencies (start order)
  processes.api = {
    exec = "pnpm run start:api";
    after = [ "devenv:processes:db" ];
  };

  # File watching (auto-restart on changes)
  processes.worker = {
    exec = "node worker.js";
    watch.paths = [ ./src/worker ];
  };

  # Port allocation
  processes.api = {
    exec = "node server.js --port $PORT";
    ports.http.allocate = 8080;
    # Access: config.processes.api.ports.http.value
  };
}
```

## Services

Pre-built service modules (databases, caches, etc.):

```nix
{
  services.postgres = {
    enable = true;
    listen_addresses = "127.0.0.1";
    port = 5432;
    initialDatabases = [{ name = "myapp"; }];
    extensions = ext: [ ext.postgis ];
  };

  services.redis.enable = true;

  services.mysql = {
    enable = true;
    initialDatabases = [{ name = "myapp"; }];
  };

  services.minio.enable = true;

  services.elasticsearch.enable = true;
}
```

Service state is stored in `$DEVENV_STATE/<service>`. Services start with `devenv up`.

## Tasks

Cacheable, dependency-aware build tasks:

```nix/<s
{
  # Basic task
  tasks."myapp:build" = {
    exec = "pnpm run build";
    before = [ "devenv:enterShell" ];  # Runs before shell entry
  };

  # Task with status check (skip if already done)
  tasks."myapp:install" = {
    exec = "pnpm install";
    status = "test -d node_modules";
    before = [ "devenv:enterShell" ];
  };

  # Conditional re-execution on file changes
  tasks."myapp:codegen" = {
    exec = "pnpm run codegen";
    execIfModified = [ "schema/**/*.graphql" ];
    before = [ "devenv:enterShell" ];
  };

  # Task with inputs (CLI-passable)
  tasks."myapp:migrate" = {
    exec = ''
      echo "Running migration: $TASK_INPUT_NAME"
    '';
    input = {
      name = {
        description = "Migration name";
        default = "latest";
      };
    };
  };
}
```

Run tasks: `devenv tasks run myapp:build`
With inputs: `devenv tasks run myapp:migrate --input name=v2`

## Tests

```nix
{
  enterTest = ''
    echo "Running tests..."
    wait_for_port 5432    # Helper: wait for service port
    pnpm run test
  '';
}
```

Run: `devenv test` (starts processes, runs `enterTest`, then stops everything).

Use `config.devenv.isTesting` to conditionally disable things during tests:

```nix
{
  processes.heavy-worker = lib.mkIf (!config.devenv.isTesting) {
    exec = "node heavy-worker.js";
  };
}
```

## Git Hooks (pre-commit)

Integration with [git-hooks.nix](https://github.com/cachix/git-hooks.nix):

```nix
{
  git-hooks.hooks = {
    nixfmt-rfc-style.enable = true;
    prettier = {
      enable = true;
      excludes = [ "pnpm-lock.yaml" ];
    };
    eslint.enable = true;
    shellcheck.enable = true;

    # Custom hook
    check-todos = {
      enable = true;
      entry = "grep -r 'ACTION_ITEM' --include='*.ts' && exit 1 || exit 0";
      language = "system";
    };
  };
}
```

The `.pre-commit-config.yaml` is an auto-generated symlink - do not edit it directly.

## Overlays

Modify or extend the nixpkgs package set:

```nix
{
  overlays = [
    # Override an existing package
    (final: prev: {
      hello = prev.hello.overrideAttrs (old: {
        patches = (old.patches or []) ++ [ ./my-patch.patch ];
      });
    })

    # Add a custom package
    (final: prev: {
      my-tool = final.callPackage ./nix/my-tool.nix {};
    })
  ];
}
```

## Inputs & Multiple Nixpkgs

In `devenv.yaml`, add extra inputs:

```yaml
inputs:
  nixpkgs:
    url: github:cachix/devenv-nixpkgs/rolling
  nixpkgs-stable:
    url: github:NixOS/nixpkgs/nixos-24.11
```

Use in `devenv.nix`:

```nix
{ pkgs, inputs, ... }:

let
  pkgs-stable = import inputs.nixpkgs-stable {
    system = pkgs.stdenv.system;
  };
in {
  packages = [
    pkgs.nodejs_22       # From rolling
    pkgs-stable.terraform  # From stable
  ];
}
```

Update/lock inputs: `devenv update`

## Outputs (Building Artifacts)

```nix
{
  outputs = {
    my-app = config.languages.rust.import ./. {};
    container = config.containers.shell.derivation;
  };
}
```

Build: `devenv build` (all) or `devenv build outputs.my-app`

## Profiles

Named configurations for different contexts:

```nix
# devenv.nix
{
  # Shared config available to all profiles
  packages = [ pkgs.git ];
}
```

```nix
# profiles/backend.nix - referenced in devenv.yaml imports
{ pkgs, ... }: {
  languages.go.enable = true;
  services.postgres.enable = true;
}
```

Activate: `devenv --profile backend shell`

## Containers

```nix
{
  containers.shell.name = "my-app-shell";

  containers.processes = {
    name = "my-app";
    startupCommand = config.procfileScript;
  };
}
```

Build: `devenv container build shell`
Run: `devenv container run shell`
Copy to registry: `devenv container copy shell docker://registry/image:tag`

## Composing with Imports

```yaml
# devenv.yaml
imports:
  - ./backend/devenv.nix
  - ./frontend/devenv.nix
  - inputs:some-input/devenv-module.nix
```

For monorepos, use profiles or imports to compose per-service environments.

## direnv Integration

`.envrc` file:

```bash
eval "$(devenv direnvrc)"
use devenv
```

This auto-activates the devenv shell when entering the project directory.

## Dotenv Integration

```nix
{
  dotenv.enable = true;
  dotenv.filename = ".env";  # default
}
```

**Warning:** `.env` contents are copied into the Nix store (world-readable). For real secrets, use `secretspec` or inject via environment outside of Nix.

## Creating Files

```nix
{
  files."config/settings.json".text = builtins.toJSON {
    port = 3000;
    debug = true;
  };

  files.".editorconfig".text = ''
    root = true
    [*]
    indent_style = space
    indent_size = 2
  '';
}
```

## CLI Command Reference

| Command | Description |
|---------|-------------|
| `devenv init` | Initialize a new devenv project |
| `devenv shell` | Enter the development shell |
| `devenv up` | Start all processes |
| `devenv up -d` | Start processes in background (detached) |
| `devenv test` | Run tests (starts processes, runs enterTest, stops) |
| `devenv build` | Build all outputs |
| `devenv build outputs.<name>` | Build a specific output |
| `devenv search <query>` | Search available packages |
| `devenv info` | Show environment info |
| `devenv update` | Update and lock inputs |
| `devenv gc` | Garbage collect old generations |
| `devenv container build <name>` | Build a container |
| `devenv container run <name>` | Run a container |
| `devenv container copy <name> <url>` | Copy container to registry |
| `devenv tasks run <name>` | Run a specific task |
| `devenv processes up` | Start processes (alias) |

**Common flags:**
- `--profile <name>` - Use a specific profile
- `--impure` - Allow impure evaluation (access host env)
- `--option <key> <value>` - Override a Nix option

## Common Nix Patterns in devenv.nix

### let/in bindings

```nix
{ pkgs, ... }:

let
  port = "3000";
  dbName = "myapp";
in {
  env.PORT = port;
  services.postgres.initialDatabases = [{ name = dbName; }];
}
```

### Conditional configuration

```nix
{ pkgs, lib, config, ... }:

{
  # Only include when testing
  processes.seed-db = lib.mkIf config.devenv.isTesting {
    exec = "node seed.js";
  };

  # Optional attrs
  packages = [ pkgs.git ] ++
    lib.optionals pkgs.stdenv.isLinux [ pkgs.strace ];
}
```

### Module imports

```nix
{ pkgs, ... }:

{
  imports = [ ./shared.nix ];

  # This merges with shared.nix configuration
  packages = [ pkgs.curl ];
}
```

## Rules

- **ALWAYS read the existing `devenv.nix` and `devenv.yaml` before making changes** - understand the current configuration.
- **NEVER manually edit `devenv.lock`** - it is auto-generated by `devenv update`.
- **NEVER manually edit `.pre-commit-config.yaml`** - it is an auto-generated symlink from git-hooks configuration.
- **NEVER put real secrets in `devenv.nix` or `.env` with dotenv enabled** - Nix store is world-readable.
- **Use `devenv search <name>`** to find the correct package attribute before adding to `packages`.
- **Prefer tasks over enterShell** for setup steps that can be cached or have dependencies.
- **Use `lib.mkIf` for conditional configuration**, not string interpolation or `if/then/else` at the module level.
- **Pin binaries in scripts** with `${pkgs.foo}/bin/foo` when PATH conflicts are possible.
- **Use `devenv.local.nix`** for personal overrides that should not be committed.
- **Run `devenv test` to validate changes** - it exercises the full environment including processes.

## Examples

```nix
# devenv.nix — minimal Node.js environment
{ pkgs, ... }: {
  packages = [ pkgs.git ];
  languages.javascript = { enable = true; package = pkgs.nodejs_20; };
  processes.dev.exec = "npm run dev";
}
```
