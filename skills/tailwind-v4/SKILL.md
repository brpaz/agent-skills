---
name: tailwind-v4
version: "1.0.0"
description: "Configure Tailwind CSS v4 with Oxide, CSS-first directives, migration steps, and production guidance."
tags: [tailwind, css, frontend, vite, design-system]
---

# Tailwind CSS v4 - CSS-First Configuration & Oxide Engine

Use this skill when working with Tailwind CSS v4, migrating from v3, or configuring modern utility-first CSS with the Oxide engine.

## When to Use

- Starting a new project with Tailwind CSS v4
- Migrating an existing Tailwind v3 project to v4
- Configuring `@theme`, `@source`, or `@utility` directives in a CSS file
- Troubleshooting missing utilities, broken variants, or incorrect design tokens in a v4 project

## Philosophy

**Tailwind CSS v4** introduces a fundamental shift in configuration and architecture:

- **CSS-first configuration** - Design tokens defined in CSS using `@theme`
- **Oxide engine** - Rust-powered engine with Lightning CSS integration
- **Unified toolchain** - Built-in imports, vendor prefixing, nesting
- **Automatic content detection** - No manual `content: []` configuration in most cases
- **Massive performance gains** - Microsecond incremental rebuilds, up to ~10x faster full builds

**Breaking change**: v4 is NOT a drop-in replacement for v3. Migration required.

## Browser Support

**Baseline**: Safari 16.4+, Chrome 111+, Firefox 128+

If you need older browser support, stay on Tailwind v3.

## Quick Start

### Installation (New Project)

Choose your setup:

#### Vite

```bash
npm install tailwindcss@next @tailwindcss/vite@next
```

```js
// vite.config.js
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [tailwindcss()],
})
```

```css
/* app.css */
@import "tailwindcss";
```

#### PostCSS

```bash
npm install tailwindcss@next @tailwindcss/postcss@next
```

```js
// postcss.config.js
export default {
  plugins: {
    '@tailwindcss/postcss': {}
  }
}
```

```css
/* app.css */
@import "tailwindcss";
```

#### CLI

```bash
npm install tailwindcss@next @tailwindcss/cli@next
```

```json
// package.json
{
  "scripts": {
    "dev": "tailwindcss --input app.css --output dist/app.css --watch",
    "build": "tailwindcss --input app.css --output dist/app.css --minify"
  }
}
```

```css
/* app.css */
@import "tailwindcss";
```

### Minimal HTML

```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="/dist/app.css">
</head>
<body>
  <h1 class="text-4xl font-bold text-blue-600">Hello Tailwind v4!</h1>
</body>
</html>
```

## CSS-First Configuration

### The New Model: @theme

**v3 (JavaScript config):**
```js
// tailwind.config.js
export default {
  theme: {
    colors: {
      mint: '#50e3c2'
    },
    extend: {
      fontFamily: {
        poppins: ['Poppins', 'sans-serif']
      }
    }
  }
}
```

**v4 (CSS config):**
```css
/* app.css */
@import "tailwindcss";

@theme {
  --color-mint-500: oklch(0.72 0.11 178);
  --font-poppins: Poppins, sans-serif;
  --breakpoint-3xl: 120rem;
}
```

Now use: `bg-mint-500`, `font-poppins`, `3xl:hidden`

### Theme Variable Naming

Theme variables follow a structured naming convention that generates utilities:

| Variable Pattern | Generated Utilities | Example |
|------------------|---------------------|---------|
| `--color-{name}-{shade}` | `text-{name}-{shade}`, `bg-{name}-{shade}` | `--color-mint-500` → `bg-mint-500` |
| `--font-{name}` | `font-{name}` | `--font-display` → `font-display` |
| `--breakpoint-{name}` | `{name}:` variant | `--breakpoint-2xl` → `2xl:flex` |
| `--spacing-{name}` | `p-{name}`, `m-{name}`, `gap-{name}` | `--spacing-huge` → `p-huge` |
| `--width-{name}` | `w-{name}`, `min-w-{name}`, `max-w-{name}` | `--width-sidebar` → `w-sidebar` |

**Full list of theme namespaces**: See [official docs](https://tailwindcss.com/docs/theme)

### Extending the Theme

```css
@import "tailwindcss";

@theme {
  /* Add new colors */
  --color-brand-50: #f0f9ff;
  --color-brand-500: #0ea5e9;
  --color-brand-900: #0c4a6e;
  
  /* Add custom spacing */
  --spacing-18: 4.5rem;
  --spacing-22: 5.5rem;
  
  /* Add custom breakpoints */
  --breakpoint-xs: 30rem;
  --breakpoint-3xl: 96rem;
  
  /* Add custom shadows */
  --shadow-brutal: 4px 4px 0 0 currentColor;
}
```

### Overriding Default Theme

Replace an entire namespace:

```css
@theme {
  /* Remove all default colors */
  --color-*: initial;
  
  /* Define only your colors */
  --color-white: #fff;
  --color-black: #000;
  --color-primary: #0ea5e9;
  --color-secondary: #8b5cf6;
}
```

### Starting from Scratch

```css
@import "tailwindcss";

@theme {
  /* Disable ALL defaults */
  --*: initial;
  
  /* Build your entire design system */
  --color-white: #fff;
  --color-black: #000;
  --spacing-0: 0;
  --spacing-1: 0.25rem;
  --breakpoint-sm: 40rem;
  /* ... */
}
```

### Sharing Theme Files

```css
/* design-system.css */
@theme {
  --color-brand-500: #0ea5e9;
  --font-display: "Inter Display", sans-serif;
}
```

```css
/* app.css */
@import "tailwindcss";
@import "./design-system.css";
```

### Using CSS Variables in Theme

```css
@theme {
  --color-primary: var(--brand-color, #0ea5e9);
  --spacing-gutter: var(--grid-gutter, 1rem);
}
```

Reference in HTML:

```html
<div style="--brand-color: #8b5cf6;" class="bg-primary">
  <!-- Uses #8b5cf6 instead of default #0ea5e9 -->
</div>
```

## Content Detection & Sources

### Automatic Detection (Default)

**v4 automatically scans** common source directories:
- `./src/**/*.{html,js,jsx,ts,tsx,vue,svelte}`
- `./*.{html,js,jsx,ts,tsx,vue,svelte}`

No `content: []` array needed in most projects.

### Custom Source Paths

```css
@import "tailwindcss";

@source "../components";
@source "../app/**/*.tsx";
@source "../../packages/ui/src";
```

Or inline with import:

```css
@import "tailwindcss" source("../src");
```

### Multiple Sources

```css
@import "tailwindcss";

@source "../app";
@source "../components";
@source "../../packages/ui";
```

### Safelisting Utilities

```css
@import "tailwindcss";

/* Safelist specific utilities that won't be detected */
@source inline("underline line-through");

/* Safelist with variants */
@source inline("{hover:,focus:,}underline");

/* Safelist dynamic classes */
@source inline("bg-{red,blue,green}-{500,600,700}");
```

## Custom Utilities

### Basic Custom Utility

```css
@utility tab-4 {
  tab-size: 4;
}
```

Usage: `<pre class="tab-4">`

### Utility with Variants

```css
@utility hyphens-auto {
  hyphens: auto;
}
```

Usage: `<p class="hyphens-auto sm:hyphens-none">`

### Parametric Utilities

```css
@utility text-shadow-* {
  text-shadow: var(--text-shadow-*);
}

@theme {
  --text-shadow-sm: 1px 1px 2px rgba(0,0,0,0.1);
  --text-shadow-lg: 3px 3px 6px rgba(0,0,0,0.3);
}
```

Usage: `<h1 class="text-shadow-lg">`

### Custom Variants

```css
@custom-variant supports-grid {
  @supports (display: grid) {
    @slot;
  }
}
```

Usage: `<div class="supports-grid:grid">`

```css
@custom-variant nth-3 {
  &:nth-child(3) {
    @slot;
  }
}
```

Usage: `<li class="nth-3:font-bold">`

## Legacy Config Support

If you need `tailwind.config.js` (for plugins, etc.):

```css
@import "tailwindcss";
@config "./tailwind.config.js";
```

**Note**: Config files are NOT auto-detected in v4. Explicit `@config` required.

## Migration from v3 to v4

### Step 1: Upgrade Tool

```bash
npx @tailwindcss/upgrade@next
```

This automates most changes but **verify manually**.

### Step 2: Install v4 Packages

```bash
npm uninstall tailwindcss
npm install tailwindcss@next @tailwindcss/postcss@next
# or @tailwindcss/vite@next, @tailwindcss/cli@next
```

### Step 3: Update Entry CSS

**Before (v3):**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**After (v4):**
```css
@import "tailwindcss";
```

### Step 4: Migrate Configuration

**Before (v3):**
```js
// tailwind.config.js
export default {
  content: ['./src/**/*.{html,js}'],
  theme: {
    extend: {
      colors: {
        brand: '#0ea5e9'
      }
    }
  }
}
```

**After (v4):**
```css
/* app.css */
@import "tailwindcss";

@theme {
  --color-brand: #0ea5e9;
}

/* content detection is automatic */
```

**If you have complex plugins**, keep config:
```css
@import "tailwindcss";
@config "./tailwind.config.js";
```

### Step 5: Update Renamed Utilities

| v3 | v4 | Notes |
|----|----|----|
| `shadow-sm` | `shadow-xs` | Renamed |
| `shadow` | `shadow-sm` | Renamed |
| `shadow-md` | `shadow` | Renamed |
| `shadow-lg` | `shadow-md` | Renamed |
| `shadow-xl` | `shadow-lg` | Renamed |
| `shadow-2xl` | `shadow-xl` | Renamed |
| `rounded` | `rounded-sm` | Renamed |
| `rounded-md` | `rounded` | Renamed |
| `rounded-lg` | `rounded-md` | Renamed |
| `rounded-xl` | `rounded-lg` | Renamed |
| `rounded-2xl` | `rounded-xl` | Renamed |
| `rounded-3xl` | `rounded-2xl` | Renamed |
| `blur` | `blur-sm` | Renamed |
| `blur-sm` | `blur-xs` | Renamed |
| `blur-md` | `blur-sm` | Renamed |
| `blur-lg` | `blur` | Renamed |
| `blur-xl` | `blur-md` | Renamed |
| `blur-2xl` | `blur-lg` | Renamed |
| `blur-3xl` | `blur-xl` | Renamed |
| `ring` | `ring-3` | Changed default width |
| `outline-none` | `outline-hidden` | Renamed |
| `flex-shrink` | `shrink` | Removed prefix |
| `flex-grow` | `grow` | Removed prefix |

### Step 6: Update Arbitrary Values with Variables

**Before (v3):**
```html
<div class="bg-[--my-color]">
```

**After (v4):**
```html
<div class="bg-(--my-color)">
```

Changed from `[]` to `()` for CSS variables.

### Step 7: Border Color Default Changed

**v3 default**: `border-gray-200`  
**v4 default**: `currentColor`

If you relied on gray borders by default, explicitly add `border-gray-200`.

### Step 8: Ring Changes

**v3 default**: `ring` = 3px width, blue color  
**v4 default**: `ring-3` = 3px width, `currentColor`

Update classes:
- `ring` → `ring-3`
- Add explicit color: `ring-blue-500`

### Step 9: Variant Stacking Order

**v3**: Right-to-left (outer → inner)  
**v4**: Left-to-right (inner → outer)

```html
<!-- v3: hover THEN dark -->
<div class="dark:hover:bg-blue-500">

<!-- v4: dark THEN hover (same syntax, different cascade) -->
<div class="dark:hover:bg-blue-500">
```

Most projects won't notice, but check complex variant chains.

### Step 10: Remove Deprecated APIs

- `corePlugins` config option removed
- `resolveConfig()` removed
- Use CSS variables for theming instead

### Step 11: Test & Verify

```bash
npm run build
```

Check console for warnings about removed utilities.

## v3 → v4 Quick Reference

| Aspect | v3 | v4 |
|--------|----|----|
| **Entry CSS** | `@tailwind base; @tailwind components; @tailwind utilities;` | `@import "tailwindcss";` |
| **Config** | `tailwind.config.js` (required) | `@theme { }` in CSS (or optional `@config`) |
| **Content** | `content: ['./src/**/*.html']` | Automatic detection (or `@source`) |
| **Colors** | `theme.extend.colors` in JS | `@theme { --color-name: value; }` |
| **Custom utilities** | `@layer utilities { }` | `@utility name { }` |
| **Arbitrary CSS vars** | `bg-[--color]` | `bg-(--color)` |
| **Border default** | `border-gray-200` | `currentColor` |
| **Ring default** | `ring` = 3px + blue | `ring-3` + `currentColor` |
| **Package** | `tailwindcss` | `@tailwindcss/postcss`, `@tailwindcss/vite`, or `@tailwindcss/cli` |

## New Features in v4

### Container Queries

```html
<div class="@container">
  <div class="@lg:grid @lg:grid-cols-2">
    <!-- Responds to container size, not viewport -->
  </div>
</div>
```

Breakpoints: `@xs`, `@sm`, `@md`, `@lg`, `@xl`, `@2xl`, etc.

### 3D Transforms

```html
<div class="rotate-x-45 rotate-y-12 translate-z-10">
  <!-- 3D rotation and translation -->
</div>
```

New utilities:
- `rotate-x-*`, `rotate-y-*`, `rotate-z-*`
- `translate-z-*`
- `scale-z-*`

### Gradient Utilities

```html
<div class="bg-linear-to-r from-blue-500 via-purple-500 to-pink-500">
  Linear gradient
</div>

<div class="bg-radial from-red-500 to-yellow-500">
  Radial gradient
</div>

<div class="bg-conic from-green-500 via-blue-500 to-purple-500">
  Conic gradient
</div>
```

### Logical Properties (Inset)

```html
<div class="inset-inline-4 inset-block-8">
  <!-- Respects RTL/LTR automatically -->
</div>
```

New utilities:
- `inset-inline-*`, `inset-block-*`
- `start-*`, `end-*`
- `ms-*`, `me-*`, `ps-*`, `pe-*` (margin/padding start/end)

### `not-*` Variant

```html
<div class="not-last:border-b">
  <!-- All except last child -->
</div>

<input class="not-disabled:border-green-500">
```

Works with any pseudo-class: `not-first`, `not-disabled`, `not-checked`, etc.

### `starting` Variant

```html
<div class="starting:opacity-0 transition-opacity">
  <!-- Fade in on first render -->
</div>
```

Leverages `@starting-style` for entry animations.

### Dynamic Values in Arbitrary Variants

```html
<div class="min-[500px]:flex max-[800px]:hidden">
  <!-- Custom breakpoints inline -->
</div>

<div class="supports-[display:grid]:grid">
  <!-- Feature queries inline -->
</div>
```

### Field Sizing

```html
<input class="field-sizing-content" value="Auto-grows">
```

New `field-sizing` utility for auto-sizing inputs/textareas.

## Oxide Engine & Performance

### What is Oxide?

- **Rust-powered engine** for parsing and processing
- **Lightning CSS** integrated (vendor prefixing, minification, nesting)
- **Custom parser** optimized for Tailwind patterns
- **Unified toolchain** - no separate PostCSS plugins for imports/nesting

### Performance Numbers (Official Benchmarks)

- **Full builds**: Up to ~3.78x faster vs v3
- **Incremental rebuilds** (no new CSS): Microseconds (e.g., 182x improvement)
- **Example**: 1.8s → 0.01s for incremental rebuild in large project

### Built-In Features (No Extra Plugins)

✅ CSS imports (`@import`)  
✅ Nesting  
✅ Vendor prefixing  
✅ Minification  
✅ Modern CSS syntax (Lightning CSS)

**You no longer need**:
- `postcss-import`
- `postcss-nesting`
- `autoprefixer`

### Implications for Build Setup

**Before (v3):**
```js
export default {
  plugins: {
    'postcss-import': {},
    'tailwindcss/nesting': {},
    tailwindcss: {},
    autoprefixer: {},
  }
}
```

**After (v4):**
```js
export default {
  plugins: {
    '@tailwindcss/postcss': {}
  }
}
```

Much simpler plugin chain.

## Production Guidance

### 1. Explicit Source Paths

For production, be explicit:

```css
@import "tailwindcss";

@source "../app";
@source "../components";
```

Avoid relying on auto-detection if directory structure might change.

### 2. Safelist Dynamic Classes

If generating classes dynamically (e.g., from CMS):

```css
@source inline("bg-{red,blue,green,yellow}-{400,500,600}");
@source inline("text-{sm,base,lg,xl}");
```

### 3. Optimize Theme

Only include colors/spacing/breakpoints you need:

```css
@theme {
  --color-*: initial;  /* Remove defaults */
  
  /* Add only your brand colors */
  --color-primary: #0ea5e9;
  --color-secondary: #8b5cf6;
  --color-gray-50: #f9fafb;
  /* ... */
}
```

### 4. Use CSS Variables for Theming

```css
@theme {
  --color-background: light-dark(#fff, #000);
  --color-text: light-dark(#000, #fff);
}
```

```html
<body class="bg-background text-text">
  <!-- Automatically switches with color-scheme -->
</body>
```

### 5. Minification

Vite/CLI handle this automatically. For PostCSS:

```js
export default {
  plugins: {
    '@tailwindcss/postcss': {},
    'cssnano': process.env.NODE_ENV === 'production' ? {} : false
  }
}
```

### 6. Content Security Policy (CSP)

v4 generates deterministic class names. No `unsafe-inline` needed for Tailwind itself (but check your framework).

### 7. Bundle Size

v4 CSS output is similar to v3 (only utilities used are included). Oxide engine doesn't affect bundle size—only build speed.

## Integration Examples

### Next.js (App Router)

```js
// next.config.js
export default {
  experimental: {
    optimizePackageImports: ['tailwindcss']
  }
}
```

```css
/* app/globals.css */
@import "tailwindcss";

@theme {
  --color-primary: #0ea5e9;
}
```

```tsx
// app/layout.tsx
import './globals.css'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>{children}</body>
    </html>
  )
}
```

### Astro

```bash
npm install tailwindcss@next @tailwindcss/vite@next
```

```js
// astro.config.mjs
import { defineConfig } from 'astro/config'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  vite: {
    plugins: [tailwindcss()]
  }
})
```

```css
/* src/styles/global.css */
@import "tailwindcss";
```

### SvelteKit

```bash
npm install tailwindcss@next @tailwindcss/vite@next
```

```js
// vite.config.js
import { sveltekit } from '@sveltejs/kit/vite'
import tailwindcss from '@tailwindcss/vite'

export default {
  plugins: [tailwindcss(), sveltekit()]
}
```

```css
/* src/app.css */
@import "tailwindcss";
```

### Vue 3

```bash
npm install tailwindcss@next @tailwindcss/vite@next
```

```js
// vite.config.js
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default {
  plugins: [vue(), tailwindcss()]
}
```

```css
/* src/main.css */
@import "tailwindcss";
```

```js
// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import './main.css'

createApp(App).mount('#app')
```

## CSS Modules & Component Styles

Use `@reference` to access Tailwind utilities in scoped CSS:

```css
/* Button.module.css */
@reference "../app.css";

.button {
  @apply rounded-lg px-4 py-2 bg-blue-500 text-white;
}

.button:hover {
  @apply bg-blue-600;
}
```

**Note**: `@apply` still works but prefer utility classes in HTML when possible.

## Troubleshooting

### Classes Not Generated

1. Check source paths: `@source` or auto-detection
2. Verify CSS import: `@import "tailwindcss";`
3. Check for typos in class names
4. Safelist if dynamically generated: `@source inline("...")`

### Build Errors

```
Error: Cannot find module '@tailwindcss/postcss'
```

Install missing package:
```bash
npm install @tailwindcss/postcss@next
```

### Styles Not Applying

1. Check CSS is imported in entry file
2. Verify build output includes Tailwind CSS
3. Check for CSS specificity conflicts
4. Inspect element in DevTools

### Migration Issues

If `npx @tailwindcss/upgrade` fails:
1. Run on a clean git state
2. Review diff carefully
3. Manually fix complex patterns
4. Check official upgrade guide for edge cases

### Performance Issues

If builds are slow:
1. Limit source paths: `@source "./src"`
2. Remove unused theme values
3. Avoid excessive `@source inline()` safelisting
4. Use Vite plugin for best performance

## Rules

- **ALWAYS use `@import "tailwindcss";`** - Do NOT use `@tailwind` directives (removed in v4).
- **ALWAYS verify browser support** - v4 requires Safari 16.4+, Chrome 111+, Firefox 128+.
- **PREFER `@theme` over `tailwind.config.js`** - Use CSS-first config unless you need complex plugins.
- **NEVER use `@tailwind base/components/utilities`** - Single `@import` replaces all three.
- **ALWAYS safelist dynamic classes** - Use `@source inline()` for runtime-generated classes.
- **Use `@reference`** for component-scoped CSS that needs Tailwind utilities.
- **Explicitly add `@config`** if using `tailwind.config.js` - not auto-detected in v4.
- **Update arbitrary CSS var syntax** - `bg-[--var]` → `bg-(--var)`.
- **Check border colors** - Default changed from gray to `currentColor`.
- **Update ring classes** - `ring` → `ring-3`, add explicit color if needed.
- **Run `npx @tailwindcss/upgrade`** first when migrating - then verify manually.
- **Remove PostCSS plugins** for imports/nesting/prefixing - Oxide handles them.

## Quick Reference

```css
/* Entry CSS */
@import "tailwindcss";

/* Theme configuration */
@theme {
  --color-brand: #0ea5e9;
  --font-display: Inter, sans-serif;
}

/* Custom sources */
@source "../components";

/* Safelist */
@source inline("bg-{red,blue}-{500,600}");

/* Custom utility */
@utility hyphens-auto {
  hyphens: auto;
}

/* Custom variant */
@custom-variant supports-grid {
  @supports (display: grid) {
    @slot;
  }
}

/* Legacy config (optional) */
@config "./tailwind.config.js";

/* Reference for CSS modules */
@reference "../app.css";
```

## Resources

- [Official v4 Documentation](https://tailwindcss.com/docs)
- [v4.0 Release Announcement](https://tailwindcss.com/blog/tailwindcss-v4)
- [Upgrade Guide (v3 → v4)](https://tailwindcss.com/docs/upgrade-guide)
- [Theme Configuration](https://tailwindcss.com/docs/theme)
- [Functions & Directives Reference](https://tailwindcss.com/docs/functions-and-directives)
- [GitHub Repository](https://github.com/tailwindlabs/tailwindcss)

## Inputs

- Existing CSS entry file (or new project) and Vite / PostCSS build configuration
- Design token requirements (colors, spacing, typography) to define in `@theme`

## Outputs

- A CSS entry file using `@import "tailwindcss"` and `@theme` block for design tokens, replacing any `tailwind.config.js`

## Examples

```css
/* app.css — v4 CSS-first config */
@import "tailwindcss";

@theme {
  --color-brand: #6366f1;
  --font-sans: "Inter", sans-serif;
  --radius-lg: 0.75rem;
}
```
