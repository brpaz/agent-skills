---
name: project-webapp
description: "Bootstrap a production-ready Nuxt 4 web application with Drizzle ORM (SQLite), Nuxt UI, Tailwind CSS, Docker deployment, GitHub Actions CI/CD, Release Drafter, and Renovate. USE WHEN creating a new full-stack webapp from scratch with modern tooling, type safety, automated migrations, containerization, and automated dependency management."
---

# Project Webapp - Production-Ready Nuxt 4 Stack

Use this skill when bootstrapping a new full-stack web application with: Nuxt 4, Drizzle ORM + SQLite, Nuxt UI + Tailwind CSS, Docker Compose for local dev, GitHub Actions for CI/CD, Release Drafter for automated release notes, and Renovate for dependency updates.

## Philosophy

This stack prioritizes:

- **Type safety** - End-to-end TypeScript with Drizzle's type-safe queries
- **Modern tooling** - Nuxt 4 (edge), Tailwind v4, Docker, GitHub Actions
- **Developer experience** - Hot reload, automatic migrations, component library
- **Production-ready** - Docker deployment, CI/CD, automated releases, dependency updates
- **Simplicity** - SQLite (no separate DB server for small-medium apps)

## Tech Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | Nuxt 4 | Full-stack Vue 3 framework |
| **UI** | Nuxt UI + Tailwind CSS | Component library + utility CSS |
| **Database** | SQLite + Drizzle ORM | Embedded database with type-safe queries |
| **Migrations** | drizzle-kit | Schema migrations and introspection |
| **Container** | Docker + Docker Compose | Local dev and production deployment |
| **CI/CD** | GitHub Actions | Automated testing and deployment |
| **Releases** | Release Drafter | Automated changelog generation |
| **Dependencies** | Renovate | Automated dependency updates |

## Project Structure

```
my-webapp/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                    # CI pipeline
│   │   └── release.yml               # Release automation
│   ├── release-drafter.yml           # Release notes template
│   └── renovate.json                 # Dependency update config
├── server/
│   ├── api/                          # API routes
│   ├── db/
│   │   ├── schema.ts                 # Drizzle schema
│   │   ├── index.ts                  # DB connection
│   │   └── migrations/               # Generated migrations
│   └── utils/                        # Server utilities
├── app/
│   ├── components/                   # Vue components
│   ├── pages/                        # Nuxt pages
│   ├── layouts/                      # Layouts
│   └── app.vue                       # Root component
├── public/                           # Static assets
├── docker/
│   ├── Dockerfile                    # Production image
│   └── Dockerfile.dev                # Development image
├── compose.yaml                      # Docker Compose config
├── compose.override.yaml             # Local dev overrides
├── drizzle.config.ts                 # drizzle-kit config
├── nuxt.config.ts                    # Nuxt config
├── tailwind.config.ts                # Tailwind config (if needed)
├── app.css                           # Global styles + Tailwind
├── package.json
├── tsconfig.json
└── .env.example                      # Environment template
```

## Step-by-Step Bootstrap

### 1. Initialize Nuxt 4 Project

```bash
npx nuxi@latest init my-webapp
cd my-webapp
```

When prompted, choose:
- Package manager: `pnpm` (recommended)
- Initialize git: Yes

### 2. Install Dependencies

```bash
# Core dependencies
pnpm add drizzle-orm better-sqlite3
pnpm add -D drizzle-kit @types/better-sqlite3

# Nuxt UI (includes Tailwind CSS)
pnpm add @nuxt/ui

# Additional utilities
pnpm add zod  # For validation
```

### 3. Configure Nuxt

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  compatibilityDate: '2025-02-14',
  
  modules: ['@nuxt/ui'],
  
  // Enable server API
  nitro: {
    experimental: {
      openAPI: true
    }
  },
  
  // Type safety
  typescript: {
    strict: true,
    typeCheck: true
  },
  
  // Development
  devtools: { enabled: true },
  
  // Runtime config
  runtimeConfig: {
    // Private keys (server-only)
    databaseUrl: 'sqlite.db',
    
    public: {
      // Public keys (client-accessible)
      apiBase: '/api'
    }
  }
})
```

### 4. Set Up Drizzle ORM

#### Create Schema

```ts
// server/db/schema.ts
import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core'
import { createId } from '@paralleldrive/cuid2'

export const users = sqliteTable('users', {
  id: text('id').primaryKey().$defaultFn(() => createId()),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  createdAt: integer('created_at', { mode: 'timestamp' })
    .notNull()
    .$defaultFn(() => new Date()),
  updatedAt: integer('updated_at', { mode: 'timestamp' })
    .notNull()
    .$defaultFn(() => new Date())
})

export const posts = sqliteTable('posts', {
  id: text('id').primaryKey().$defaultFn(() => createId()),
  title: text('title').notNull(),
  content: text('content').notNull(),
  authorId: text('author_id')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
  published: integer('published', { mode: 'boolean' }).notNull().default(false),
  createdAt: integer('created_at', { mode: 'timestamp' })
    .notNull()
    .$defaultFn(() => new Date()),
  updatedAt: integer('updated_at', { mode: 'timestamp' })
    .notNull()
    .$defaultFn(() => new Date())
})
```

**Install cuid2 for IDs**:
```bash
pnpm add @paralleldrive/cuid2
```

#### Create DB Connection

```ts
// server/db/index.ts
import { drizzle } from 'drizzle-orm/better-sqlite3'
import Database from 'better-sqlite3'
import * as schema from './schema'

const sqlite = new Database(process.env.DATABASE_URL || 'sqlite.db')

// Enable WAL mode for better concurrency
sqlite.pragma('journal_mode = WAL')

export const db = drizzle(sqlite, { schema })
```

#### Configure drizzle-kit

```ts
// drizzle.config.ts
import { defineConfig } from 'drizzle-kit'

export default defineConfig({
  schema: './server/db/schema.ts',
  out: './server/db/migrations',
  dialect: 'sqlite',
  dbCredentials: {
    url: process.env.DATABASE_URL || 'sqlite.db'
  }
})
```

#### Add Migration Scripts

```json
// package.json
{
  "scripts": {
    "dev": "nuxt dev",
    "build": "nuxt build",
    "generate": "nuxt generate",
    "preview": "nuxt preview",
    "postinstall": "nuxt prepare",
    "db:generate": "drizzle-kit generate",
    "db:migrate": "drizzle-kit migrate",
    "db:push": "drizzle-kit push",
    "db:studio": "drizzle-kit studio"
  }
}
```

#### Generate Initial Migration

```bash
pnpm db:generate
pnpm db:migrate
```

### 5. Create API Routes

```ts
// server/api/users/index.get.ts
import { db } from '~/server/db'
import { users } from '~/server/db/schema'

export default defineEventHandler(async () => {
  return await db.select().from(users)
})
```

```ts
// server/api/users/index.post.ts
import { db } from '~/server/db'
import { users } from '~/server/db/schema'
import { z } from 'zod'

const createUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1)
})

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const data = createUserSchema.parse(body)
  
  const [user] = await db.insert(users).values(data).returning()
  return user
})
```

```ts
// server/api/users/[id].get.ts
import { db } from '~/server/db'
import { users } from '~/server/db/schema'
import { eq } from 'drizzle-orm'

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  
  const [user] = await db.select()
    .from(users)
    .where(eq(users.id, id))
    .limit(1)
  
  if (!user) {
    throw createError({
      statusCode: 404,
      message: 'User not found'
    })
  }
  
  return user
})
```

### 6. Set Up Tailwind CSS

```css
/* app.css */
@import "tailwindcss";

@theme {
  /* Add custom theme variables if needed */
  --color-primary: #0ea5e9;
}
```

```ts
// app.vue
<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<style>
@import './app.css';
</style>
```

### 7. Create Docker Setup

#### Production Dockerfile

```dockerfile
# docker/Dockerfile
# syntax=docker/dockerfile:1

# ============================================
# Build Stage
# ============================================
FROM node:20-alpine AS builder

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source
COPY . .

# Build application
RUN pnpm build

# ============================================
# Runtime Stage
# ============================================
FROM node:20-alpine AS runtime

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Security: Run as non-root
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nuxt -u 1001

WORKDIR /app

# Copy package files
COPY --chown=nuxt:nodejs package.json pnpm-lock.yaml ./

# Install production dependencies only
RUN pnpm install --prod --frozen-lockfile

# Copy built application from builder
COPY --from=builder --chown=nuxt:nodejs /app/.output ./.output
COPY --from=builder --chown=nuxt:nodejs /app/server/db/migrations ./server/db/migrations

# Create directory for SQLite database
RUN mkdir -p /app/data && chown nuxt:nodejs /app/data

# Switch to non-root user
USER nuxt

# Environment
ENV NODE_ENV=production \
    DATABASE_URL=/app/data/sqlite.db

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => r.statusCode === 200 ? process.exit(0) : process.exit(1))"

CMD ["node", ".output/server/index.mjs"]
```

#### Development Dockerfile (Optional)

```dockerfile
# docker/Dockerfile.dev
FROM node:20-alpine

RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Install dependencies
COPY package.json pnpm-lock.yaml ./
RUN pnpm install

# Copy source
COPY . .

EXPOSE 3000 24678

CMD ["pnpm", "dev"]
```

#### Docker Compose

```yaml
# compose.yaml
services:
  app:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=/app/data/sqlite.db
    volumes:
      - app-data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "node", "-e", "require('http').get('http://localhost:3000/api/health', (r) => r.statusCode === 200 ? process.exit(0) : process.exit(1))"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  app-data:
```

```yaml
# compose.override.yaml (local dev)
services:
  app:
    build:
      dockerfile: docker/Dockerfile.dev
    volumes:
      - .:/app
      - /app/node_modules
      - /app/.nuxt
    environment:
      - NODE_ENV=development
    ports:
      - "3000:3000"
      - "24678:24678"  # Nuxt DevTools
```

### 8. Add Health Check Endpoint

```ts
// server/api/health.get.ts
export default defineEventHandler(() => {
  return { status: 'ok', timestamp: new Date().toISOString() }
})
```

### 9. Set Up GitHub Actions

#### CI Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
      
      - name: Install dependencies
        run: pnpm install --frozen-lockfile
      
      - name: Type check
        run: pnpm nuxt typecheck
      
      - name: Build
        run: pnpm build

  docker:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: docker/Dockerfile
          push: false
          tags: ${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

#### Deployment Workflow (Example)

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=semver,pattern={{major}}
            type=sha
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: docker/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### 10. Set Up Release Drafter

```yaml
# .github/release-drafter.yml
name-template: 'v$RESOLVED_VERSION'
tag-template: 'v$RESOLVED_VERSION'

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
  - title: '🧰 Maintenance'
    labels:
      - 'chore'
      - 'dependencies'

change-template: '- $TITLE @$AUTHOR (#$NUMBER)'

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

autolabeler:
  - label: 'chore'
    files:
      - '*.md'
  - label: 'bug'
    branch:
      - '/fix\/.+/'
    title:
      - '/fix/i'
  - label: 'enhancement'
    branch:
      - '/feature\/.+/'
    title:
      - '/feat/i'

template: |
  ## Changes
  
  $CHANGES
```

```yaml
# .github/workflows/release-drafter.yml
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

### 11. Set Up Renovate

```json
// .github/renovate.json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "config:best-practices",
    "default:automergeDigest"
  ],
  
  "timezone": "UTC",
  "schedule": [
    "* 0-4,22-23 * * 1-5",
    "* * * * 0,6"
  ],
  
  "osvVulnerabilityAlerts": true,
  "vulnerabilityAlerts": {
    "labels": ["security"],
    "automerge": false
  },
  
  "lockFileMaintenance": {
    "enabled": true,
    "automerge": true,
    "schedule": ["before 5am on Monday"]
  },
  
  "packageRules": [
    {
      "description": "Group npm patch updates",
      "matchManagers": ["npm"],
      "matchUpdateTypes": ["patch"],
      "groupName": "npm patch updates",
      "automerge": true
    },
    {
      "description": "Group npm minor updates",
      "matchManagers": ["npm"],
      "matchUpdateTypes": ["minor"],
      "groupName": "npm minor updates"
    },
    {
      "description": "Group npm major updates",
      "matchManagers": ["npm"],
      "matchUpdateTypes": ["major"],
      "groupName": "npm major updates"
    },
    {
      "description": "Automerge npm devDependency non-major updates",
      "matchManagers": ["npm"],
      "matchDepTypes": ["devDependencies"],
      "matchUpdateTypes": ["patch", "minor"],
      "matchCurrentVersion": "!/^0/",
      "automerge": true
    },
    {
      "description": "Enable Docker major updates",
      "matchDatasources": ["docker"],
      "matchUpdateTypes": ["major"],
      "enabled": true
    },
    {
      "description": "Group GitHub Actions updates",
      "matchManagers": ["github-actions"],
      "groupName": "GitHub Actions"
    }
  ]
}
```

**Enable Renovate**:
1. Install Renovate GitHub App: https://github.com/apps/renovate
2. Grant access to your repository
3. Renovate will create an onboarding PR

### 12. Environment Variables

```bash
# .env.example
# Database
DATABASE_URL=sqlite.db

# Application
NODE_ENV=development
NUXT_PUBLIC_API_BASE=/api

# Copy to .env and customize
```

```bash
# .gitignore additions
.env
sqlite.db
sqlite.db-shm
sqlite.db-wal
data/
```

## Development Workflow

### Daily Development

```bash
# Start dev server
pnpm dev

# Open Drizzle Studio (database GUI)
pnpm db:studio
```

### Making Schema Changes

```bash
# 1. Edit server/db/schema.ts

# 2. Generate migration
pnpm db:generate

# 3. Review migration in server/db/migrations/

# 4. Apply migration
pnpm db:migrate
```

### Docker Development

```bash
# Start with Docker Compose
docker compose up

# Rebuild after changes
docker compose up --build

# View logs
docker compose logs -f

# Stop
docker compose down
```

## Production Deployment

### Build and Deploy

```bash
# Build Docker image
docker build -f docker/Dockerfile -t myapp:latest .

# Run
docker run -p 3000:3000 -v $(pwd)/data:/app/data myapp:latest
```

### Database Backups

SQLite backups:

```bash
# Backup (online backup with WAL mode)
sqlite3 data/sqlite.db ".backup data/backup-$(date +%Y%m%d).db"

# Restore
cp data/backup-20250214.db data/sqlite.db
```

**Automate backups** in production with cron or your cloud provider's backup system.

### Migrations in Production

**Option 1**: Run migrations in container startup

```dockerfile
# Add to Dockerfile CMD
CMD ["sh", "-c", "pnpm db:migrate && node .output/server/index.mjs"]
```

**Option 2**: Run migrations as separate job before deployment

```yaml
# In GitHub Actions
- name: Run migrations
  run: |
    docker run --rm \
      -v ${{ secrets.DATABASE_PATH }}:/app/data \
      myapp:latest \
      pnpm db:migrate
```

## Drizzle ORM Patterns

### Queries

```ts
// Select all
const allUsers = await db.select().from(users)

// Select with where
import { eq, and, or, like, gt } from 'drizzle-orm'

const user = await db.select()
  .from(users)
  .where(eq(users.id, userId))
  .limit(1)

// Complex where
const recentPosts = await db.select()
  .from(posts)
  .where(
    and(
      eq(posts.published, true),
      gt(posts.createdAt, new Date('2025-01-01'))
    )
  )
  .orderBy(posts.createdAt)

// Joins
const postsWithAuthors = await db.select()
  .from(posts)
  .leftJoin(users, eq(posts.authorId, users.id))
```

### Inserts

```ts
// Insert one
const [newUser] = await db.insert(users)
  .values({ email: 'user@example.com', name: 'User' })
  .returning()

// Insert many
await db.insert(posts).values([
  { title: 'Post 1', content: '...' },
  { title: 'Post 2', content: '...' }
])
```

### Updates

```ts
await db.update(users)
  .set({ name: 'New Name', updatedAt: new Date() })
  .where(eq(users.id, userId))
```

### Deletes

```ts
await db.delete(posts)
  .where(eq(posts.id, postId))
```

### Transactions

```ts
await db.transaction(async (tx) => {
  const [user] = await tx.insert(users)
    .values({ email: 'user@example.com', name: 'User' })
    .returning()
  
  await tx.insert(posts)
    .values({ title: 'First Post', authorId: user.id })
})
```

## Nuxt UI Patterns

### Using Components

```vue
<template>
  <UContainer>
    <UCard>
      <template #header>
        <h3 class="text-lg font-semibold">Users</h3>
      </template>
      
      <UTable :rows="users" :columns="columns" />
      
      <template #footer>
        <UButton @click="createUser">Add User</UButton>
      </template>
    </UCard>
  </UContainer>
</template>

<script setup lang="ts">
const { data: users } = await useFetch('/api/users')

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'email', label: 'Email' }
]

const createUser = () => {
  // Navigate to create page or open modal
}
</script>
```

### Forms

```vue
<template>
  <UForm :schema="schema" :state="state" @submit="onSubmit">
    <UFormGroup label="Email" name="email">
      <UInput v-model="state.email" type="email" />
    </UFormGroup>
    
    <UFormGroup label="Name" name="name">
      <UInput v-model="state.name" />
    </UFormGroup>
    
    <UButton type="submit">Create User</UButton>
  </UForm>
</template>

<script setup lang="ts">
import { z } from 'zod'

const schema = z.object({
  email: z.string().email(),
  name: z.string().min(1)
})

const state = reactive({
  email: '',
  name: ''
})

const onSubmit = async (data: any) => {
  await $fetch('/api/users', {
    method: 'POST',
    body: data
  })
}
</script>
```

## Troubleshooting

### Database Locked Error

```
database is locked
```

**Solution**: Enable WAL mode (already in `server/db/index.ts`):

```ts
sqlite.pragma('journal_mode = WAL')
```

### Migrations Not Running

```bash
# Check migration status
pnpm db:push --verbose

# Force regenerate
pnpm db:generate --force
```

### Docker Build Fails

```
ERROR: failed to solve: failed to compute cache key
```

**Solution**: Check `.dockerignore`:

```
# .dockerignore
node_modules
.nuxt
.output
.env
sqlite.db
data/
```

### Type Errors After Schema Changes

```bash
# Regenerate Nuxt types
pnpm nuxt prepare

# Restart TypeScript server in IDE
```

## Rules

- **ALWAYS use drizzle-kit for migrations** - Never manually edit migration files.
- **ALWAYS enable WAL mode** for SQLite in production - Better concurrency.
- **NEVER commit `.env` or `sqlite.db`** - Use `.env.example` as template.
- **ALWAYS use transactions** for multi-step operations that must succeed/fail together.
- **Use volume mounts** for SQLite database in Docker - Data persists across container restarts.
- **ALWAYS run type checking** in CI - `pnpm nuxt typecheck`.
- **Pin Docker base images** by digest in production for reproducibility.
- **Use zod** for runtime validation of API inputs.
- **ALWAYS add health check endpoint** for monitoring and orchestration.
- **Back up SQLite database** regularly in production.
- **Use cuid2 or nanoid** for IDs instead of auto-increment integers (better for distributed systems).

## Quick Reference

```bash
# Development
pnpm dev                    # Start dev server
pnpm db:studio             # Open Drizzle Studio

# Database
pnpm db:generate           # Generate migration from schema
pnpm db:migrate            # Apply migrations
pnpm db:push               # Push schema directly (dev only)

# Docker
docker compose up          # Start services
docker compose build       # Rebuild images
docker compose down -v     # Stop and remove volumes

# GitHub Actions
git push                   # Triggers CI
git tag v1.0.0 && git push --tags  # Triggers deployment
```

## Resources

- [Nuxt 4 Documentation](https://nuxt.com/docs)
- [Drizzle ORM Documentation](https://orm.drizzle.team/docs/overview)
- [Nuxt UI Documentation](https://ui.nuxt.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Release Drafter](https://github.com/release-drafter/release-drafter)
- [Renovate Documentation](https://docs.renovatebot.com/)
