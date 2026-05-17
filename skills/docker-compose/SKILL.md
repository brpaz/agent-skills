---
name: docker-compose
description: "Multi-container Docker orchestration with docker-compose. USE WHEN working with docker-compose.yml, compose.yaml, service definitions, networks, volumes, or local development environments. Covers v2 compose spec, profiles, extends, secrets, health checks, and production patterns."
---

# Docker Compose - Multi-Container Orchestration

Use this skill when defining multi-container applications, orchestrating services locally, or managing development environments with Docker.

## Philosophy

**Docker Compose** defines multi-container applications in YAML. Core benefits:

- **Single command** - Start entire stack with `docker compose up`
- **Declarative** - Infrastructure as code
- **Reproducible** - Same environment everywhere
- **Isolated** - Project-specific networks and volumes
- **Composable** - Extend and override configurations

## Version Note

This skill covers **Compose V2** (docker compose, not docker-compose). V2 is built into Docker CLI.

```bash
# V2 (recommended)
docker compose up

# V1 (deprecated)
docker-compose up
```

## Quick Start

### Basic compose.yaml

```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html
    
  api:
    build: ./api
    environment:
      - DATABASE_URL=postgres://db:5432/myapp
    depends_on:
      - db
    
  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_PASSWORD=secret
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```

### Common Commands

```bash
# Start services
docker compose up

# Start in background
docker compose up -d

# Stop services
docker compose down

# Rebuild and start
docker compose up --build

# View logs
docker compose logs -f

# Execute command in service
docker compose exec web sh

# List running services
docker compose ps

# Remove volumes
docker compose down -v
```

## Service Configuration

### Image vs Build

```yaml
services:
  # Use pre-built image
  nginx:
    image: nginx:1.25-alpine
  
  # Build from Dockerfile
  app:
    build: .
  
  # Build with options
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
      args:
        - NODE_ENV=development
      target: development
      cache_from:
        - myregistry/api:cache
```

### Container Name

```yaml
services:
  web:
    container_name: myapp-web  # Explicit name
```

**Default**: `<project>-<service>-<replica>` (e.g., `myapp-web-1`)

### Ports

```yaml
services:
  web:
    ports:
      - "8080:80"              # host:container
      - "127.0.0.1:3000:3000"  # bind to localhost only
      - "8000-8010:8000-8010"  # port range
      
    # Long syntax
    ports:
      - target: 80             # Container port
        published: 8080        # Host port
        protocol: tcp
        mode: host
```

### Expose (Internal Only)

```yaml
services:
  api:
    expose:
      - "3000"  # Accessible to other services, NOT host
```

### Environment Variables

```yaml
services:
  app:
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgres://db:5432/myapp
    
    # Or object syntax
    environment:
      NODE_ENV: production
      DEBUG: "true"
    
    # Load from file
    env_file:
      - .env
      - .env.local
```

### Volumes

```yaml
services:
  app:
    volumes:
      # Bind mount (host path:container path)
      - ./src:/app/src
      - ./config:/app/config:ro  # Read-only
      
      # Named volume
      - db-data:/var/lib/postgresql/data
      
      # Anonymous volume (auto-generated)
      - /app/node_modules
      
      # tmpfs mount (memory)
      - type: tmpfs
        target: /tmp

volumes:
  db-data:  # Define named volume
```

### Networks

```yaml
services:
  web:
    networks:
      - frontend
      - backend
  
  api:
    networks:
      - backend
  
  db:
    networks:
      - backend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access
```

**Default**: All services join a default network and can reach each other by service name.

### Depends On

```yaml
services:
  web:
    depends_on:
      - api
  
  api:
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started

  db:
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 5s
      timeout: 3s
      retries: 5
```

**Conditions**:
- `service_started` - Container started (default)
- `service_healthy` - Health check passed
- `service_completed_successfully` - Container exited with 0

### Health Checks

```yaml
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
  
  # Alternative: shell form
  db:
    healthcheck:
      test: pg_isready -U postgres
      interval: 10s
```

### Restart Policy

```yaml
services:
  app:
    restart: unless-stopped
```

**Options**:
- `no` - Never restart (default)
- `always` - Always restart
- `on-failure` - Restart on non-zero exit
- `unless-stopped` - Always restart unless manually stopped

### Resource Limits

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### Labels

```yaml
services:
  web:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.web.rule=Host(`example.com`)"
      - "com.example.description=Frontend service"
```

### Commands

```yaml
services:
  app:
    command: npm run dev
  
  # Array syntax
  worker:
    command: ["node", "worker.js", "--verbose"]
  
  # Override entrypoint
  debug:
    entrypoint: ["sh", "-c"]
    command: "sleep infinity"
```

## Advanced Patterns

### Profiles (Selective Services)

```yaml
services:
  web:
    image: nginx
  
  api:
    image: myapi
  
  # Only start with --profile debug
  debug:
    profiles: ["debug"]
    image: alpine
    command: sleep infinity

  # Start with --profile test or --profile ci
  test-runner:
    profiles: ["test", "ci"]
    image: cypress
```

```bash
docker compose up              # Starts web, api
docker compose --profile debug up  # Also starts debug
docker compose --profile test up   # Also starts test-runner
```

### Extends (Reuse Configuration)

```yaml
# common.yaml
services:
  base-app:
    environment:
      - LOG_LEVEL=info
    restart: unless-stopped
```

```yaml
# compose.yaml
services:
  api:
    extends:
      file: common.yaml
      service: base-app
    image: myapi
  
  worker:
    extends:
      file: common.yaml
      service: base-app
    image: myworker
```

### Multiple Compose Files

```bash
# Load base + override
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Default behavior: compose.yaml + compose.override.yaml
docker compose up
```

**compose.yaml** (base):
```yaml
services:
  web:
    image: nginx
    volumes:
      - ./html:/usr/share/nginx/html
```

**compose.override.yaml** (local dev):
```yaml
services:
  web:
    ports:
      - "8080:80"
    environment:
      - NGINX_DEBUG=true
```

**compose.prod.yaml** (production):
```yaml
services:
  web:
    restart: always
    deploy:
      resources:
        limits:
          memory: 512M
```

### Secrets (Swarm Mode or File-Based)

```yaml
services:
  app:
    secrets:
      - db_password
      - api_key

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    environment: "API_KEY"  # From env var
```

Access in container: `/run/secrets/db_password`

### Configs (Similar to Secrets, Not Encrypted)

```yaml
services:
  app:
    configs:
      - source: app_config
        target: /etc/app/config.yaml

configs:
  app_config:
    file: ./config.yaml
```

### Init Containers Pattern

```yaml
services:
  # Run migrations before starting app
  migrate:
    image: myapp
    command: npm run migrate
    depends_on:
      db:
        condition: service_healthy
  
  app:
    image: myapp
    depends_on:
      migrate:
        condition: service_completed_successfully
```

### Sidecar Pattern

```yaml
services:
  app:
    image: myapp
  
  # Logging sidecar
  fluentd:
    image: fluentd
    volumes:
      - /var/log/app:/var/log/app:ro
```

## Development Patterns

### Hot Reload Setup

```yaml
services:
  frontend:
    build: ./frontend
    volumes:
      - ./frontend/src:/app/src      # Source code
      - /app/node_modules            # Persist deps
    environment:
      - CHOKIDAR_USEPOLLING=true     # For Docker on Windows
    command: npm run dev

  api:
    build: ./api
    volumes:
      - ./api:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
    command: npm run dev
```

### Database Seeding

```yaml
services:
  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_PASSWORD=secret
    volumes:
      - ./db/init:/docker-entrypoint-initdb.d  # Auto-run .sql scripts
```

### Local Registry Cache

```yaml
services:
  registry:
    image: registry:2
    ports:
      - "5000:5000"
    volumes:
      - registry-data:/var/lib/registry

volumes:
  registry-data:
```

### Test Environment

```yaml
# compose.test.yaml
services:
  test-runner:
    build: .
    command: npm test
    depends_on:
      db:
        condition: service_healthy
    environment:
      - NODE_ENV=test
      - DATABASE_URL=postgres://db:5432/test
  
  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=test
    tmpfs:
      - /var/lib/postgresql/data  # In-memory for speed
```

Run: `docker compose -f compose.test.yaml up --abort-on-container-exit`

## Production Patterns

### Production Compose File

```yaml
services:
  web:
    image: myregistry/web:${TAG:-latest}
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Rolling Updates

```yaml
services:
  app:
    image: myapp:${VERSION}
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
```

### Logging

```yaml
services:
  app:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "5"
  
  # Send to syslog
  worker:
    logging:
      driver: syslog
      options:
        syslog-address: "tcp://logs.example.com:514"
```

### External Networks (Pre-existing)

```yaml
services:
  app:
    networks:
      - existing-network

networks:
  existing-network:
    external: true
```

### Named Volumes with Options

```yaml
volumes:
  db-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /mnt/data/db
```

## Integration Examples

### Nginx + App + Database

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app
  
  app:
    build: .
    expose:
      - "3000"
    environment:
      - DATABASE_URL=postgres://db:5432/myapp
    depends_on:
      db:
        condition: service_healthy
  
  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    volumes:
      - db-data:/var/lib/postgresql/data
    secrets:
      - db_password
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 5s

volumes:
  db-data:

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

### Traefik Reverse Proxy

```yaml
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
    ports:
      - "80:80"
      - "8080:8080"  # Dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
  
  app:
    image: myapp
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`app.localhost`)"
      - "traefik.http.routers.app.entrypoints=web"
```

### Redis + Worker Queue

```yaml
services:
  api:
    build: ./api
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
  
  worker:
    build: ./api
    command: node worker.js
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    deploy:
      replicas: 3
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s

volumes:
  redis-data:
```

### Elasticsearch + Kibana

```yaml
services:
  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - xpack.security.enabled=false
    volumes:
      - es-data:/usr/share/elasticsearch/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9200"]
      interval: 10s
  
  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
    depends_on:
      elasticsearch:
        condition: service_healthy
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200

volumes:
  es-data:
```

## Project Layout

```
project/
├── compose.yaml              # Main compose file
├── compose.override.yaml     # Local dev overrides (optional)
├── compose.prod.yaml         # Production config
├── compose.test.yaml         # Test environment
├── .env                      # Environment variables
├── .env.example              # Template
├── docker/
│   ├── nginx/
│   │   └── nginx.conf
│   └── postgres/
│       └── init.sql
├── services/
│   ├── api/
│   │   ├── Dockerfile
│   │   └── src/
│   └── frontend/
│       ├── Dockerfile
│       └── src/
└── volumes/                  # Mount points (gitignored)
```

## Environment Variables

### In compose.yaml

```yaml
services:
  app:
    image: myapp:${TAG:-latest}
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - API_KEY=${API_KEY}
```

### .env file

```bash
# .env
TAG=v1.2.3
DATABASE_URL=postgres://localhost:5432/myapp
API_KEY=dev-key-12345
COMPOSE_PROJECT_NAME=myapp
COMPOSE_FILE=compose.yaml:compose.override.yaml
```

### Special Variables

| Variable | Purpose |
|----------|---------|
| `COMPOSE_PROJECT_NAME` | Project name (default: directory name) |
| `COMPOSE_FILE` | Compose files to load (colon-separated) |
| `COMPOSE_PROFILES` | Active profiles (comma-separated) |
| `COMPOSE_PATH_SEPARATOR` | Path separator (default: `:`) |
| `DOCKER_HOST` | Docker daemon socket |

## Networking

### Service Discovery

Services can reach each other by service name:

```yaml
services:
  api:
    image: myapi
    environment:
      - DB_HOST=db  # Resolves to db service
  
  db:
    image: postgres
```

### Custom Network

```yaml
services:
  app:
    networks:
      backend:
        ipv4_address: 172.20.0.5

networks:
  backend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Host Network Mode

```yaml
services:
  app:
    network_mode: host  # Use host's network stack
```

### Container Network Mode

```yaml
services:
  app:
    image: myapp
  
  sidecar:
    image: sidecar
    network_mode: "service:app"  # Share app's network
```

## Troubleshooting

### View logs

```bash
docker compose logs
docker compose logs -f              # Follow
docker compose logs -f api          # Specific service
docker compose logs --tail=100      # Last 100 lines
docker compose logs --since 5m      # Last 5 minutes
```

### Inspect service

```bash
docker compose ps
docker compose ps --format json
docker compose top                  # Running processes
```

### Execute commands

```bash
docker compose exec api sh
docker compose exec -it db psql -U postgres
docker compose run --rm api npm test
```

### Rebuild

```bash
docker compose build
docker compose build --no-cache
docker compose up --build
```

### Remove everything

```bash
docker compose down              # Stop and remove containers
docker compose down -v           # Also remove volumes
docker compose down --rmi all    # Also remove images
```

### Validate compose file

```bash
docker compose config            # Show resolved config
docker compose config --quiet    # Validate only
```

### Network debugging

```bash
docker compose exec api ping db
docker compose exec api curl http://web:80
docker network inspect <project>_default
```

## Common Issues

| Problem | Solution |
|---------|----------|
| "Network not found" | Run `docker compose up` again, or `docker network create <name>` |
| Port already in use | Change host port in ports config, or stop conflicting service |
| Volume permission denied | Check user in Dockerfile, or use `user: "1000:1000"` in compose |
| Service can't reach another | Ensure both on same network, check service name spelling |
| Changes not applied | Run `docker compose up --build`, or `docker compose build --no-cache` |
| "No such file or directory" | Check paths are relative to compose file location |
| Slow startup | Add health checks, optimize depends_on conditions |

## Rules

- **ALWAYS use `compose.yaml`** as the primary filename (not `docker-compose.yml` unless V1 compat required).
- **ALWAYS gitignore volumes/**, `.env` (use `.env.example` instead), and service-specific `.env.*` files with secrets.
- **NEVER put secrets in compose.yaml** - use environment files, secrets, or external secret managers.
- **ALWAYS use health checks** for critical services like databases.
- **ALWAYS use `depends_on` with conditions** when startup order matters.
- **Use named volumes** for persistent data, bind mounts for development hot-reload.
- **Use profiles** to separate concerns (dev tools, debugging, test runners).
- **Use multiple compose files** for environment-specific config (dev/staging/prod).
- **Pin image versions** in production (never `:latest`).
- **ALWAYS validate** with `docker compose config` before deploying.
- **Use resource limits** in production to prevent resource exhaustion.
- **Configure logging** to prevent disk space issues.
- **Use restart policies** for resilience (except in test environments).

## Quick Reference

```bash
# Lifecycle
docker compose up                 # Start services
docker compose up -d              # Start in background
docker compose down               # Stop and remove
docker compose down -v            # Also remove volumes
docker compose restart            # Restart services

# Building
docker compose build              # Build services
docker compose build --no-cache   # Rebuild from scratch
docker compose up --build         # Rebuild and start

# Logs and debugging
docker compose logs -f            # Follow logs
docker compose ps                 # List services
docker compose top                # Running processes
docker compose exec <svc> <cmd>   # Execute command

# Config
docker compose config             # Show resolved config
docker compose config --services  # List services
docker compose config --volumes   # List volumes

# Profiles
docker compose --profile <name> up

# Multiple files
docker compose -f compose.yaml -f compose.prod.yaml up
```

## Resources

- [Compose Specification](https://compose-spec.io/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Compose File Reference](https://docs.docker.com/compose/compose-file/)
- [Awesome Compose](https://github.com/docker/awesome-compose) - Sample compose files
