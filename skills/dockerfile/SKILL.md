---
name: dockerfile
version: "1.0.0"
description: "Create and improve Dockerfiles with multi-stage builds, caching, security hardening, and debugging guidance."
tags: [docker, dockerfile, containers, ci-cd, security]
---

# Dockerfile - Production-Ready Container Images

Use this skill when writing, optimizing, or debugging Dockerfiles. Covers multi-stage builds, layer caching, security guidance, and language-specific patterns.

## When to Use

- Creating a new `Dockerfile` for any language or framework
- Optimising an existing Dockerfile for smaller image size or faster builds
- Adding multi-stage builds, security hardening, or non-root user configuration
- Debugging build failures or unexpected image behavior

## Dockerfile Fundamentals

### Basic Structure

```dockerfile
# Syntax version (enables BuildKit features)
# syntax=docker/dockerfile:1

# Base image
FROM node:20-alpine

# Metadata
LABEL maintainer="team@example.com"
LABEL version="1.0"

# Working directory
WORKDIR /app

# Copy files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Default command
CMD ["node", "index.js"]
```

### Instruction Reference

| Instruction | Purpose | Usage |
|-------------|---------|-------|
| `FROM` | Base image | `FROM node:20-alpine` |
| `WORKDIR` | Set working directory | `WORKDIR /app` |
| `COPY` | Copy files from build context | `COPY src/ ./src/` |
| `ADD` | Copy + extract archives (avoid unless needed) | `ADD archive.tar.gz /app/` |
| `RUN` | Execute command in build | `RUN apt-get update && apt-get install -y curl` |
| `CMD` | Default command (overridable) | `CMD ["python", "app.py"]` |
| `ENTRYPOINT` | Main executable (not overridable) | `ENTRYPOINT ["docker-entrypoint.sh"]` |
| `ENV` | Set environment variable | `ENV NODE_ENV=production` |
| `ARG` | Build-time variable | `ARG VERSION=1.0` |
| `EXPOSE` | Document port (metadata only) | `EXPOSE 8080` |
| `VOLUME` | Define mount point | `VOLUME /data` |
| `USER` | Switch user | `USER node` |
| `HEALTHCHECK` | Container health check | `HEALTHCHECK CMD curl -f http://localhost/ || exit 1` |

## Multi-Stage Builds (CRITICAL for Production)

Multi-stage builds separate build dependencies from runtime dependencies, dramatically reducing image size.

### Pattern: Build Stage + Runtime Stage

```dockerfile
# syntax=docker/dockerfile:1

# ============================================
# Build Stage
# ============================================
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies (including devDependencies)
COPY package*.json ./
RUN npm ci

# Build application
COPY . .
RUN npm run build

# ============================================
# Runtime Stage
# ============================================
FROM node:20-alpine AS runtime

# Security: Run as non-root
USER node
WORKDIR /app

# Copy only production dependencies
COPY --chown=node:node package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy built artifacts from builder stage
COPY --from=builder --chown=node:node /app/dist ./dist

# Runtime configuration
ENV NODE_ENV=production
EXPOSE 3000

CMD ["node", "dist/index.js"]
```

**Why multi-stage?**
- Build stage: `npm ci` (all deps) + `npm run build` = ~500MB
- Runtime stage: `npm ci --only=production` + built artifacts = ~150MB
- **Result:** 70% smaller final image

### Pattern: Separate Dependency Stage

For better caching when dependencies change infrequently:

```dockerfile
# syntax=docker/dockerfile:1

# ============================================
# Dependencies Stage
# ============================================
FROM node:20-alpine AS deps

WORKDIR /app
COPY package*.json ./
RUN npm ci

# ============================================
# Build Stage
# ============================================
FROM node:20-alpine AS builder

WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# ============================================
# Runtime Stage
# ============================================
FROM node:20-alpine AS runtime

USER node
WORKDIR /app

COPY --chown=node:node package*.json ./
RUN npm ci --only=production && npm cache clean --force

COPY --from=builder --chown=node:node /app/dist ./dist

ENV NODE_ENV=production
EXPOSE 3000

CMD ["node", "dist/index.js"]
```

## Layer Caching Strategy

Docker caches each instruction as a layer. Order matters for build speed.

### Rule: Order by Change Frequency

```dockerfile
# ❌ BAD: Changes to code invalidate dependency cache
COPY . .
RUN npm ci

# ✅ GOOD: Dependencies cached separately from code
COPY package*.json ./
RUN npm ci
COPY . .
```

### Optimal Ordering

1. **Base image** (changes rarely)
2. **System dependencies** (changes rarely)
3. **Language/framework dependencies** (changes occasionally)
4. **Application code** (changes frequently)

```dockerfile
FROM python:3.12-slim              # 1. Base (rarely changes)

RUN apt-get update && \            # 2. System deps (rarely changes)
    apt-get install -y --no-install-recommends \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .            # 3. Language deps (occasionally changes)
RUN pip install --no-cache-dir -r requirements.txt

COPY . .                           # 4. Code (frequently changes)
```

### BuildKit Cache Mounts

Enable BuildKit for advanced caching:

```bash
export DOCKER_BUILDKIT=1
docker build .
```

Use cache mounts for package managers:

```dockerfile
# syntax=docker/dockerfile:1

FROM node:20-alpine

WORKDIR /app
COPY package*.json ./

# Cache npm cache across builds
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production

COPY . .
CMD ["node", "index.js"]
```

**Python example:**

```dockerfile
# syntax=docker/dockerfile:1

FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .

# Cache pip cache across builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . .
CMD ["python", "app.py"]
```

## Security Guidance

### 1. Use Specific Base Image Versions

```dockerfile
# ❌ BAD: Uses latest, unpredictable
FROM node:alpine

# ⚠️ BETTER: Version pinned, but still updates
FROM node:20-alpine

# ✅ Fully pinned and reproducible
FROM node:20.11.0-alpine3.19
```

### 2. Run as Non-Root User

```dockerfile
# ❌ BAD: Runs as root (default)
FROM node:20-alpine
COPY . /app
CMD ["node", "index.js"]

# ✅ GOOD: Switches to non-root user
FROM node:20-alpine

# Create user if base doesn't provide one
# RUN addgroup -g 1001 -S nodejs && \
#     adduser -S nodejs -u 1001

USER node
WORKDIR /home/node/app

COPY --chown=node:node . .
CMD ["node", "index.js"]
```

### 3. Minimize Attack Surface

```dockerfile
# ❌ BAD: Full OS with unnecessary tools
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    python3 python3-pip curl wget git vim sudo

# ✅ GOOD: Minimal distroless or alpine
FROM python:3.12-slim
# Only install what's needed for runtime

# ✅ Distroless base image (no shell, no package manager)
FROM gcr.io/distroless/python3-debian12
COPY --from=builder /app /app
CMD ["/app/main.py"]
```

### 4. Scan for Vulnerabilities

```bash
# Use Docker Scout (built into Docker Desktop)
docker scout cves myimage:latest

# Or Trivy
trivy image myimage:latest

# Or Snyk
snyk container test myimage:latest
```

Integrate into CI:

```dockerfile
# In your CI pipeline (e.g., GitHub Actions)
- name: Build image
  run: docker build -t myapp:${{ github.sha }} .

- name: Scan for vulnerabilities
  run: docker scout cves myapp:${{ github.sha }} --exit-code
```

### 5. Don't Embed Secrets

```dockerfile
# ❌ BAD: Secret in layer
ENV DATABASE_PASSWORD=supersecret

# ❌ BAD: Secret in build arg (visible in history)
ARG API_KEY
RUN curl -H "Authorization: Bearer $API_KEY" ...

# ✅ GOOD: Use BuildKit secrets
# docker build --secret id=apikey,src=.apikey .
RUN --mount=type=secret,id=apikey \
    curl -H "Authorization: Bearer $(cat /run/secrets/apikey)" ...

# ✅ GOOD: Pass secrets at runtime
# docker run -e API_KEY=$API_KEY myapp
```

### 6. Use .dockerignore

Prevent sensitive files from entering build context:

```
# .dockerignore
.git
.env
.env.*
*.md
node_modules
npm-debug.log
Dockerfile
.dockerignore
.gitignore
README.md
tests/
*.test.js
coverage/
.vscode/
.idea/
*.pem
*.key
secrets/
```

## Language-Specific Patterns

### Node.js / JavaScript / TypeScript

```dockerfile
# syntax=docker/dockerfile:1

# ============================================
# Dependencies Stage
# ============================================
FROM node:20-alpine AS deps

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install all dependencies (including dev)
RUN npm ci

# ============================================
# Build Stage
# ============================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy source code
COPY . .

# Build (TypeScript, bundling, etc.)
RUN npm run build

# ============================================
# Runtime Stage
# ============================================
FROM node:20-alpine AS runtime

# Run as non-root
USER node
WORKDIR /app

# Copy package files
COPY --chown=node:node package.json package-lock.json ./

# Install only production dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy built artifacts
COPY --from=builder --chown=node:node /app/dist ./dist

# Environment
ENV NODE_ENV=production
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

CMD ["node", "dist/index.js"]
```

### Python

```dockerfile
# syntax=docker/dockerfile:1

# ============================================
# Build Stage
# ============================================
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install to /install directory
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ============================================
# Runtime Stage
# ============================================
FROM python:3.12-slim AS runtime

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1001 appuser

USER appuser
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder --chown=appuser:appuser /install /usr/local

# Copy application code
COPY --chown=appuser:appuser . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["python", "app.py"]
```

**With Poetry:**

```dockerfile
# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder

# Install poetry
RUN pip install poetry

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies to system (not venv)
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# ============================================
# Runtime Stage
# ============================================
FROM python:3.12-slim

RUN useradd -m -u 1001 appuser
USER appuser
WORKDIR /app

COPY --from=builder --chown=appuser:appuser /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --chown=appuser:appuser . .

ENV PYTHONUNBUFFERED=1
CMD ["python", "app.py"]
```

### Go

```dockerfile
# syntax=docker/dockerfile:1

# ============================================
# Build Stage
# ============================================
FROM golang:1.22-alpine AS builder

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies (cached layer)
RUN go mod download

# Copy source code
COPY . .

# Build binary
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# ============================================
# Runtime Stage (Scratch or Distroless)
# ============================================
FROM gcr.io/distroless/static-debian12

WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/main .

USER nonroot:nonroot

EXPOSE 8080

CMD ["./main"]
```

**Alternative with scratch:**

```dockerfile
FROM scratch

# Copy SSL certificates for HTTPS
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Copy binary
COPY --from=builder /app/main /main

EXPOSE 8080
CMD ["/main"]
```

### Rust

```dockerfile
# syntax=docker/dockerfile:1

# ============================================
# Build Stage
# ============================================
FROM rust:1.76-slim AS builder

WORKDIR /app

# Copy manifests
COPY Cargo.toml Cargo.lock ./

# Create dummy main to cache dependencies
RUN mkdir src && \
    echo "fn main() {}" > src/main.rs && \
    cargo build --release && \
    rm -rf src

# Copy real source code
COPY src ./src

# Build for release (triggers rebuild due to source change)
RUN touch src/main.rs && \
    cargo build --release

# ============================================
# Runtime Stage
# ============================================
FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1001 appuser
USER appuser

WORKDIR /app

# Copy binary from builder
COPY --from=builder --chown=appuser:appuser /app/target/release/myapp ./myapp

EXPOSE 8080

CMD ["./myapp"]
```

### Java / Maven

```dockerfile
# syntax=docker/dockerfile:1

# ============================================
# Build Stage
# ============================================
FROM maven:3.9-eclipse-temurin-21 AS builder

WORKDIR /app

# Copy pom.xml and download dependencies (cached layer)
COPY pom.xml .
RUN mvn dependency:go-offline

# Copy source and build
COPY src ./src
RUN mvn package -DskipTests

# ============================================
# Runtime Stage
# ============================================
FROM eclipse-temurin:21-jre-jammy

# Create non-root user
RUN useradd -m -u 1001 appuser
USER appuser

WORKDIR /app

# Copy jar from builder
COPY --from=builder --chown=appuser:appuser /app/target/*.jar app.jar

EXPOSE 8080

CMD ["java", "-jar", "app.jar"]
```

### Static Sites (Nginx)

```dockerfile
# syntax=docker/dockerfile:1

# ============================================
# Build Stage
# ============================================
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# ============================================
# Runtime Stage
# ============================================
FROM nginx:1.25-alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/

# Copy built static files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Run as non-root (nginx user)
USER nginx

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
```

**nginx.conf:**

```nginx
server {
    listen 8080;
    server_name _;
    
    root /usr/share/nginx/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

## Advanced Patterns

### Health Checks

```dockerfile
# HTTP health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# TCP health check (when curl not available)
HEALTHCHECK CMD nc -z localhost 8080 || exit 1

# Custom script
HEALTHCHECK CMD /app/healthcheck.sh || exit 1
```

### Conditional Builds (Build Args)

```dockerfile
# syntax=docker/dockerfile:1

ARG ENVIRONMENT=production

FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

# Install dependencies based on environment
RUN if [ "$ENVIRONMENT" = "production" ]; then \
        npm ci --only=production; \
    else \
        npm ci; \
    fi

COPY . .

CMD ["node", "index.js"]
```

Build:
```bash
# Production build
docker build --build-arg ENVIRONMENT=production -t myapp:prod .

# Development build
docker build --build-arg ENVIRONMENT=development -t myapp:dev .
```

### Dynamic Version Injection

```dockerfile
# syntax=docker/dockerfile:1

ARG VERSION=dev
ARG COMMIT_SHA=unknown

FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

# Inject version info
ENV APP_VERSION=${VERSION}
ENV APP_COMMIT=${COMMIT_SHA}

CMD ["node", "index.js"]
```

Build:
```bash
docker build \
    --build-arg VERSION=$(git describe --tags) \
    --build-arg COMMIT_SHA=$(git rev-parse HEAD) \
    -t myapp:latest .
```

### BuildKit Secrets for Private Packages

**Private npm packages:**

```dockerfile
# syntax=docker/dockerfile:1

FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

# Mount .npmrc as secret
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci --only=production

COPY . .
CMD ["node", "index.js"]
```

Build:
```bash
docker build --secret id=npmrc,src=$HOME/.npmrc -t myapp .
```

**Private git repos:**

```dockerfile
# syntax=docker/dockerfile:1

FROM golang:1.22-alpine

WORKDIR /app

# Mount SSH key as secret
RUN apk add --no-cache git openssh-client && \
    mkdir -p /root/.ssh && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts

COPY go.mod go.sum ./

RUN --mount=type=ssh \
    go mod download

COPY . .
RUN go build -o main .

CMD ["./main"]
```

Build:
```bash
docker build --ssh default -t myapp .
```

### Debugging Containers

Add a debug stage for troubleshooting:

```dockerfile
# syntax=docker/dockerfile:1

# ... (build stages)

# ============================================
# Runtime Stage
# ============================================
FROM node:20-alpine AS runtime
# ... (production setup)

# ============================================
# Debug Stage
# ============================================
FROM runtime AS debug

USER root

# Install debugging tools
RUN apk add --no-cache \
    curl \
    wget \
    busybox-extras \
    bind-tools \
    strace \
    tcpdump

USER node

CMD ["node", "--inspect=0.0.0.0:9229", "dist/index.js"]
```

Build debug image:
```bash
docker build --target debug -t myapp:debug .
docker run -p 9229:9229 myapp:debug
```

## Optimization Techniques

### Reduce Image Size

**1. Use Alpine Linux**
```dockerfile
# Standard: ~900MB
FROM node:20
# Alpine: ~120MB
FROM node:20-alpine
```

**2. Use Distroless**
```dockerfile
# Alpine: ~120MB
FROM node:20-alpine
# Distroless: ~80MB
FROM gcr.io/distroless/nodejs20-debian12
```

**3. Multi-stage builds (already covered)**

**4. Remove unnecessary files**
```dockerfile
# Remove cache and temp files
RUN npm ci --only=production && \
    npm cache clean --force

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*
```

**5. Optimize COPY operations**
```dockerfile
# ❌ BAD: Copies everything
COPY . .

# ✅ GOOD: Copy only what's needed
COPY src ./src
COPY package.json ./
```

### Build Speed

**1. Order matters** (already covered)

**2. Use cache mounts** (already covered)

**3. Parallelize independent stages**
```dockerfile
FROM base AS stage1
RUN long-running-task-1

FROM base AS stage2
RUN long-running-task-2

# Both stages build in parallel
FROM alpine
COPY --from=stage1 /output1 ./
COPY --from=stage2 /output2 ./
```

**4. Use BuildKit features**
```bash
export DOCKER_BUILDKIT=1
```

### Reproducible Builds

**1. Pin all versions**
```dockerfile
FROM node:20.11.0-alpine3.19

# Pin system packages
RUN apk add --no-cache \
    curl=8.5.0-r0 \
    ca-certificates=20240226-r0
```

**2. Use lock files**
```dockerfile
# Node.js: package-lock.json or pnpm-lock.yaml
COPY package.json package-lock.json ./
RUN npm ci

# Python: requirements.txt with pinned versions or poetry.lock
COPY requirements.txt .
RUN pip install -r requirements.txt

# Go: go.sum
COPY go.mod go.sum ./
RUN go mod download
```

## Common Pitfalls

### 1. Running as Root

```dockerfile
# ❌ DANGER: Runs as root
FROM node:20-alpine
COPY . /app
CMD ["node", "index.js"]

# ✅ SAFE: Switches to non-root
FROM node:20-alpine
USER node
COPY --chown=node:node . /home/node/app
CMD ["node", "index.js"]
```

### 2. Installing Unnecessary Dependencies

```dockerfile
# ❌ BAD: Installs dev dependencies in production
RUN npm install

# ✅ GOOD: Production only
RUN npm ci --only=production
```

### 3. Not Using .dockerignore

Without `.dockerignore`, every file change triggers rebuild:

```bash
# .dockerignore saves you
.git/          # Don't copy version control
node_modules/  # Don't copy local deps
*.md           # Don't copy docs
.env*          # Don't copy secrets
```

### 4. apt-get Issues

```dockerfile
# ❌ BAD: Stale package lists, leftover cache
RUN apt-get install -y curl

# ✅ GOOD: Update, install, cleanup in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*
```

### 5. Exposing Secrets in Layers

```dockerfile
# ❌ BAD: Secret visible in image history
RUN echo "API_KEY=secret123" > .env

# ✅ GOOD: Use BuildKit secrets or runtime env vars
RUN --mount=type=secret,id=apikey \
    export API_KEY=$(cat /run/secrets/apikey) && \
    ./configure.sh
```

### 6. Using ADD Instead of COPY

```dockerfile
# ❌ BAD: ADD has implicit behavior (URL fetch, tar extraction)
ADD https://example.com/file.tar.gz /app/

# ✅ GOOD: Use COPY (explicit) or RUN + curl
COPY file.tar.gz /app/
# OR
RUN curl -o file.tar.gz https://example.com/file.tar.gz
```

### 7. Not Cleaning Package Manager Caches

```dockerfile
# ❌ BAD: npm cache left in image
RUN npm ci

# ✅ GOOD: Clean cache
RUN npm ci && npm cache clean --force
```

### 8. Multiple EXPOSE Instructions

```dockerfile
# ❌ Confusing: Multiple EXPOSE
EXPOSE 3000
EXPOSE 8080

# ✅ Clear: Single EXPOSE for primary port
EXPOSE 3000
# Document other ports in README
```

## Testing Dockerfiles

### Local Testing

```bash
# Build
docker build -t myapp:test .

# Run
docker run -p 3000:3000 myapp:test

# Check size
docker images myapp:test

# Inspect layers
docker history myapp:test

# Scan for vulnerabilities
docker scout cves myapp:test
```

### Automated Testing

**hadolint** (Dockerfile linter):

```bash
# Install
brew install hadolint  # macOS
# or
docker pull hadolint/hadolint

# Lint
hadolint Dockerfile

# In CI
docker run --rm -i hadolint/hadolint < Dockerfile
```

Create `.hadolint.yaml`:
```yaml
ignored:
  - DL3008  # Pin versions in apt-get install (if you prefer not to)

trustedRegistries:
  - docker.io
  - gcr.io
```

**Container Structure Test:**

```yaml
# container-test.yaml
schemaVersion: 2.0.0

fileExistenceTests:
  - name: 'app binary'
    path: '/app/main'
    shouldExist: true

commandTests:
  - name: 'healthcheck'
    command: 'curl'
    args: ['-f', 'http://localhost:8080/health']
    expectedOutput: ['OK']

metadataTest:
  user: 'node'
  exposedPorts: ['3000']
  env:
    - key: 'NODE_ENV'
      value: 'production'
```

Run:
```bash
container-structure-test test \
    --image myapp:test \
    --config container-test.yaml
```

## Docker Compose Integration

When developing locally, use `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: debug  # Use debug stage locally
    ports:
      - "3000:3000"
      - "9229:9229"  # Debug port
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgres://postgres:postgres@db:5432/myapp
    volumes:
      - ./src:/app/src  # Hot reload
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: myapp
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  pgdata:
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: myorg/myapp
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=myorg/myapp:buildcache
          cache-to: type=registry,ref=myorg/myapp:buildcache,mode=max
          build-args: |
            VERSION=${{ github.ref_name }}
            COMMIT_SHA=${{ github.sha }}

      - name: Scan image
        run: |
          docker scout cves myorg/myapp:${{ github.sha }} --exit-code
```

## Rules

- **ALWAYS use multi-stage builds** for compiled languages or build processes - reduces image size by 50-80%.
- **ALWAYS run as non-root user** in final stage - critical security practice.
- **ALWAYS pin base image versions** with full tags (e.g., `node:20.11.0-alpine3.19`) for reproducibility.
- **ALWAYS create and use .dockerignore** - prevents copying unnecessary files and exposing secrets.
- **ALWAYS clean package manager caches** in the same RUN instruction (`npm cache clean --force`, `--no-cache-dir` for pip).
- **ALWAYS combine apt-get update + install + cleanup** in a single RUN instruction.
- **NEVER use `latest` tag** for base images - breaks reproducibility.
- **NEVER copy secrets into image layers** - use BuildKit secrets or runtime environment variables.
- **NEVER use ADD unless you need tar extraction** - COPY is explicit and safer.
- **Order COPY/RUN by change frequency** - dependencies first, code last, for optimal caching.
- **Use `# syntax=docker/dockerfile:1`** at the top to enable BuildKit features.
- **Scan images for vulnerabilities** before deploying to production.
- **Test Dockerfiles with hadolint** to catch common issues early.
- **Use health checks** to enable container orchestration platforms to monitor application health.
- **Prefer alpine or distroless base images** for smaller attack surface and image size.

## Quick Reference

### Minimal Production Dockerfile Template

```dockerfile
# syntax=docker/dockerfile:1

# ============================================
# Build Stage
# ============================================
FROM <language>:<version>-alpine AS builder

WORKDIR /app

# Copy dependency manifests
COPY <package-files> ./

# Install dependencies
RUN <install-command>

# Copy source code
COPY . .

# Build application
RUN <build-command>

# ============================================
# Runtime Stage
# ============================================
FROM <language>:<version>-alpine AS runtime

# Run as non-root
USER <non-root-user>
WORKDIR /app

# Copy only production dependencies
COPY --chown=<user>:<user> <package-files> ./
RUN <install-prod-command>

# Copy built artifacts from builder
COPY --from=builder --chown=<user>:<user> /app/<output> ./<output>

# Set production environment
ENV <ENV_VAR>=production

# Expose port
EXPOSE <port>

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD <healthcheck-command> || exit 1

# Start application
CMD ["<entrypoint>", "<args>"]
```

### Common Commands

```bash
# Build
docker build -t myapp:latest .

# Build with BuildKit
DOCKER_BUILDKIT=1 docker build -t myapp:latest .

# Build specific stage
docker build --target debug -t myapp:debug .

# Build with args
docker build --build-arg VERSION=1.0 -t myapp:1.0 .

# Build with secrets
docker build --secret id=npmrc,src=$HOME/.npmrc -t myapp .

# Build with cache
docker build --cache-from myapp:latest -t myapp:new .

# Lint
hadolint Dockerfile

# Scan vulnerabilities
docker scout cves myapp:latest

# Check size
docker images myapp:latest

# Inspect layers
docker history myapp:latest

# Dive into layers (detailed)
dive myapp:latest
```

## Resources

- [Dockerfile guidance (Docker Docs)](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [BuildKit Documentation](https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/reference.md)
- [hadolint](https://github.com/hadolint/hadolint) - Dockerfile linter
- [dive](https://github.com/wagoodman/dive) - Layer analysis tool
- [Docker Scout](https://docs.docker.com/scout/) - Vulnerability scanning
- [Distroless Images](https://github.com/GoogleContainerTools/distroless)

## Inputs

- Application source directory with build tool config (`package.json`, `go.mod`, `Pipfile`, etc.)
- Target runtime requirements: language version, exposed ports, run command

## Outputs

- A production-ready `Dockerfile` using multi-stage builds, a minimal base image, non-root user, and optimised layer caching

## Examples

```dockerfile
# Multi-stage Node.js build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine
RUN addgroup -S app && adduser -S app -G app
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
USER app
EXPOSE 3000
CMD ["node", "server.js"]
```
