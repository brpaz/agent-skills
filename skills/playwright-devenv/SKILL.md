---
name: playwright-devenv
version: "1.0.0"
description: "Set up Playwright browser automation in devenv.sh on NixOS, including browser installation, version pinning, and troubleshooting."
tags: [playwright, devenv, nix, nixos, testing, browser-automation]
---

# Playwright with devenv.sh - NixOS Setup

Use this skill when setting up Playwright browser automation in a devenv.sh project on NixOS. This handles browser installation, version pinning, environment configuration, and common troubleshooting.

## When to Use

- Adding Playwright to a project that uses devenv.sh on NixOS
- Resolving browser launch failures caused by missing Nix store library paths
- Pinning or updating Playwright versions in both `devenv.yaml` and `package.json`
- Configuring CI to run Playwright tests inside a Nix environment

## The Problem with Playwright on NixOS

Playwright's default `playwright install` command downloads browsers that expect dependencies in standard Linux paths. NixOS stores dependencies in unique `/nix/store/` paths, causing browsers to fail with missing library errors.

**Solution:** Use nixpkgs' `playwright-driver.browsers` package and set environment variables to tell Playwright where to find the Nix-provided browsers.

## Critical Rule: Version Synchronization

**MANDATORY:** Playwright versions in `devenv.yaml` (nixpkgs input) and `package.json` MUST match exactly, or browsers won't work.

```
Nix: playwright@1.52.0
npm: @playwright/test@1.52.0
✅ Versions match - browsers work

Nix: playwright@1.52.0
npm: @playwright/test@1.48.0
❌ Version mismatch - browsers fail
```

## Quick Start Configuration

### Step 1: Find the Right Playwright Version

Visit [NixOS Package Search](https://search.nixos.org/packages?channel=unstable&query=playwright) to find:
- Latest available Playwright version
- The nixpkgs commit hash for that version

Example:
```
Package: playwright-driver 1.52.0
Channel: nixos-unstable
Commit: 979daf34c8cacebcd917d540070b52a3c2b9b16e
```

### Step 2: Configure devenv.yaml

Pin the nixpkgs-playwright input to the exact commit from Step 1:

```yaml
# yaml-language-server: $schema=https://devenv.sh/devenv.schema.json
inputs:
  nixpkgs:
    url: github:NixOS/nixpkgs/nixos-unstable
  
  # Pin to specific Playwright version commit
  # Update commit hash from: https://search.nixos.org/packages?channel=unstable&query=playwright
  nixpkgs-playwright:
    url: github:NixOS/nixpkgs/979daf34c8cacebcd917d540070b52a3c2b9b16e
```

### Step 3: Configure devenv.nix

```nix
{ pkgs, lib, config, inputs, ... }:

let
  # Import the pinned playwright nixpkgs
  pkgs-playwright = import inputs.nixpkgs-playwright { 
    system = pkgs.stdenv.system; 
  };
  
  # Extract chromium revision for executable path
  browsers = (builtins.fromJSON (builtins.readFile "${pkgs-playwright.playwright-driver}/browsers.json")).browsers;
  chromium-rev = (builtins.head (builtins.filter (x: x.name == "chromium") browsers)).revision;
in
{
  # Environment variables for Playwright
  env = {
    PLAYWRIGHT_BROWSERS_PATH = "${pkgs-playwright.playwright.browsers}";
    PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS = true;
    PLAYWRIGHT_NODEJS_PATH = "${pkgs.nodejs}/bin/node";
    PLAYWRIGHT_LAUNCH_OPTIONS_EXECUTABLE_PATH = "${pkgs-playwright.playwright.browsers}/chromium-${chromium-rev}/chrome-linux/chrome";
  };

  # Add Node.js and other required packages
  packages = with pkgs; [
    nodejs
  ];

  # Enable JavaScript language support
  languages.javascript.enable = true;

  # Optional: Add npm/pnpm auto-install
  # languages.javascript.pnpm.enable = true;
  # languages.javascript.pnpm.install.enable = true;

  # Optional: Startup message to verify versions
  scripts.intro.exec = ''
    playwrightNpmVersion="$(npm view ./. devDependencies'[@playwright/test]')"
    echo "❄️ Playwright nix version: ${pkgs-playwright.playwright.version}"
    echo "📦 Playwright npm version: $playwrightNpmVersion"

    if [ "${pkgs-playwright.playwright.version}" != "$playwrightNpmVersion" ]; then
        echo "❌ Playwright versions in nix (in devenv.yaml) and npm (in package.json) are not the same!"
        echo "   Update devenv.yaml nixpkgs-playwright commit to match package.json version."
    else
        echo "✅ Playwright versions in nix and npm are the same"
    fi

    echo
    env | grep ^PLAYWRIGHT
  '';

  enterShell = ''
    intro
  '';
}
```

### Step 4: Configure package.json

Use the **exact same version** as in your pinned nixpkgs:

```json
{
  "name": "e2e-tests",
  "version": "1.0.0",
  "devDependencies": {
    "@playwright/test": "1.52.0"
  },
  "scripts": {
    "test": "playwright test",
    "test:ui": "playwright test --ui",
    "test:headed": "playwright test --headed"
  }
}
```

### Step 5: Install and Verify

```bash
# Enter devenv shell
devenv shell

# Install dependencies
npm install  # or pnpm install

# Verify setup (should show matching versions)
# The intro script will automatically run and show version comparison

# Run tests
npm run test
```

## Environment Variables Reference

| Variable | Purpose | Required |
|----------|---------|----------|
| `PLAYWRIGHT_BROWSERS_PATH` | Path to Nix-provided browser binaries | Yes |
| `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS` | Skip Playwright's host validation (NixOS has different paths) | Yes |
| `PLAYWRIGHT_NODEJS_PATH` | Path to Node.js binary (for Playwright server) | Recommended |
| `PLAYWRIGHT_LAUNCH_OPTIONS_EXECUTABLE_PATH` | Direct path to browser executable (Chromium) | Optional |

## Advanced Configurations

### Multiple Browser Support

By default, the configuration uses Chromium. To support Firefox, WebKit, or all browsers:

```nix
{
  env = {
    PLAYWRIGHT_BROWSERS_PATH = "${pkgs-playwright.playwright.browsers}";
    PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS = true;
    
    # Firefox
    # PLAYWRIGHT_FIREFOX_EXECUTABLE_PATH = "${pkgs-playwright.playwright.browsers}/firefox-${firefox-rev}/firefox/firefox";
    
    # WebKit
    # PLAYWRIGHT_WEBKIT_EXECUTABLE_PATH = "${pkgs-playwright.playwright.browsers}/webkit-${webkit-rev}/...";
  };
}
```

Extract revisions from `browsers.json` the same way as `chromium-rev` in the base config.

## Troubleshooting

### Error: "Executable doesn't exist at ..."

**Cause:** Version mismatch between nix and npm.

**Fix:**
1. Check versions: the `intro` script shows both
2. Update `devenv.yaml` nixpkgs-playwright commit to match npm version
3. Run `devenv update` to update lock file
4. Exit and re-enter shell: `exit` then `devenv shell`

### Error: "browserType.launch: Host system is missing dependencies"

**Cause:** `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS` not set.

**Fix:** Ensure env var is set in `devenv.nix` (see Step 3 above).

### Error: "Failed to launch browser ... cannot open shared object file"

**Cause:** Browser trying to use system libraries instead of Nix libraries.

**Fix:** Verify `PLAYWRIGHT_BROWSERS_PATH` points to Nix store path:
```bash
echo $PLAYWRIGHT_BROWSERS_PATH
# Should output: /nix/store/...-playwright-browsers/...
```

### Tests pass locally but fail in CI

**Cause:** CI environment may not have the same Nix setup.

**Fix Options:**
1. Use the Docker remote approach (works anywhere)
2. Set up Nix in CI with cachix for binary caching
3. Use Playwright's official Docker images in CI

### Browsers take up too much disk space

**Cause:** All browsers installed by default (Chromium + Firefox + WebKit ≈ 1GB).

**Fix:** Use selective browser installation (see "Selective Browser Installation" above).

### Updating Playwright Version

**Process:**
1. Update `package.json`: `"@playwright/test": "1.53.0"`
2. Find new nixpkgs commit: [search.nixos.org](https://search.nixos.org/packages?channel=unstable&query=playwright)
3. Update `devenv.yaml` nixpkgs-playwright URL with new commit
4. Run `devenv update` to update lock
5. Exit shell and re-enter: `exit` then `devenv shell`
6. Verify versions match: the `intro` script will confirm

## Testing the Setup

Create `tests/example.spec.ts`:

```typescript
import { test, expect } from '@playwright/test';

test('basic test', async ({ page }) => {
  await page.goto('https://playwright.dev/');
  await expect(page).toHaveTitle(/Playwright/);
});
```

Create `playwright.config.ts`:

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
```

Run:
```bash
npm run test
```

## Integration with devenv Processes

Run tests as a long-running process during development:

```nix
{
  processes.playwright-watch = {
    exec = "playwright test --ui";
  };
}
```

Start: `devenv up`

## Integration with devenv Tasks

Run tests as a cacheable task:

```nix
{
  tasks."test:e2e" = {
    exec = "playwright test";
    before = [ "devenv:enterShell" ];
  };
}
```

Run: `devenv tasks run test:e2e`

## Integration with Git Hooks

Run Playwright tests on pre-push:

```nix
{
  git-hooks.hooks = {
    playwright-test = {
      enable = true;
      name = "playwright";
      entry = "npm run test";
      language = "system";
      stages = [ "pre-push" ];
    };
  };
}
```

## Complete Working Example

Minimal working setup:

**Directory structure:**
```
.
├── devenv.nix
├── devenv.yaml
├── package.json
├── playwright.config.ts
└── tests/
    └── example.spec.ts
```

**devenv.yaml:**
```yaml
inputs:
  nixpkgs:
    url: github:NixOS/nixpkgs/nixos-unstable
  nixpkgs-playwright:
    url: github:NixOS/nixpkgs/979daf34c8cacebcd917d540070b52a3c2b9b16e
```

**devenv.nix:**
```nix
{ pkgs, lib, config, inputs, ... }:

let
  pkgs-playwright = import inputs.nixpkgs-playwright { system = pkgs.stdenv.system; };
  browsers = (builtins.fromJSON (builtins.readFile "${pkgs-playwright.playwright-driver}/browsers.json")).browsers;
  chromium-rev = (builtins.head (builtins.filter (x: x.name == "chromium") browsers)).revision;
in
{
  env = {
    PLAYWRIGHT_BROWSERS_PATH = "${pkgs-playwright.playwright.browsers}";
    PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS = true;
    PLAYWRIGHT_NODEJS_PATH = "${pkgs.nodejs}/bin/node";
    PLAYWRIGHT_LAUNCH_OPTIONS_EXECUTABLE_PATH = "${pkgs-playwright.playwright.browsers}/chromium-${chromium-rev}/chrome-linux/chrome";
  };

  packages = [ pkgs.nodejs ];
  languages.javascript.enable = true;
}
```

**package.json:**
```json
{
  "devDependencies": {
    "@playwright/test": "1.52.0"
  },
  "scripts": {
    "test": "playwright test"
  }
}
```

**playwright.config.ts:**
```typescript
import { defineConfig } from '@playwright/test';
export default defineConfig({ testDir: './tests' });
```

**tests/example.spec.ts:**
```typescript
import { test, expect } from '@playwright/test';
test('basic', async ({ page }) => {
  await page.goto('https://playwright.dev/');
  await expect(page).toHaveTitle(/Playwright/);
});
```

**Run:**
```bash
devenv shell
npm install
npm run test
```

## Rules

- **ALWAYS verify Playwright version match** between `devenv.yaml` (nixpkgs commit) and `package.json` before troubleshooting other issues.
- **NEVER run `playwright install`** - it downloads incompatible binaries. Use `playwright-driver.browsers` from nixpkgs.
- **ALWAYS set `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true`** - Playwright's host checks don't understand NixOS paths.
- **ALWAYS pin the nixpkgs-playwright input** - don't use `nixos-unstable` directly, pin to a specific commit for reproducibility.
- **Use the `intro` script pattern** to verify version synchronization on every shell entry.
- **When updating Playwright**, update BOTH `devenv.yaml` commit hash AND `package.json` version together.
- **For CI/CD**, prefer the Docker remote browser approach for consistency across environments.
- **Test the setup with a simple test** before writing complex test suites.
- **Check `$PLAYWRIGHT_BROWSERS_PATH`** first when debugging browser launch issues.

## Common Pitfalls

1. **Forgetting to update `devenv.lock`**: After changing `devenv.yaml`, run `devenv update` and restart shell.
2. **Version drift**: npm/pnpm updating `@playwright/test` without updating nix config.
3. **Missing Node.js**: Playwright requires Node.js - ensure it's in `packages` or via `languages.javascript.enable = true`.
4. **CI failures**: CI doesn't inherit devenv shell - either setup Nix in CI or use Docker approach.
5. **Disk space**: All three browsers consume ~1GB - use selective installation if space-constrained.

## References

- [NixOS Wiki - Playwright](https://wiki.nixos.org/wiki/Playwright)
- [Playwright Documentation](https://playwright.dev/)
- [devenv.sh Documentation](https://devenv.sh/)
- [NixOS Package Search](https://search.nixos.org/packages)

## Inputs

- `devenv.nix` and `devenv.yaml` for the project
- Desired Playwright version (must match in both Nix and npm)
- Target browsers (chromium, firefox, webkit)

## Outputs

- Updated `devenv.nix` with `playwright-driver.browsers` package and required env vars (`PLAYWRIGHT_BROWSERS_PATH`, `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS`)
- `devenv.yaml` with the correct nixpkgs revision for the matching Playwright version

## Examples

```nix
# devenv.nix — Playwright on NixOS
{ pkgs, ... }: {
  packages = [ pkgs.playwright-driver.browsers ];
  env = {
    PLAYWRIGHT_BROWSERS_PATH = "${pkgs.playwright-driver.browsers}";
    PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS = "true";
  };
}
```
