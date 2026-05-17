---
name: golang-testcontainers
version: "1.0.0"
description: "Write Go integration tests with testcontainers-go"
tags: [go, golang, testing, integration, testcontainers, docker]
---

# Golang Testcontainers

Use this skill when writing or reviewing Go integration tests that need real infrastructure dependencies in Docker.

Use it together with `golang-testing` for general Go test structure, `t.Parallel()` defaults, black-box package guidance, and assertion style.

## When to Use

- Testing against a real Postgres, Redis, Kafka, NATS, or other containerised dependency
- Verifying SQL, migrations, indexes, transactions, locking, or driver behaviour
- Testing cache integration against a real Redis instance
- Replacing brittle fake environments with hermetic container-based integration tests
- Designing package-scoped test infrastructure that still allows parallel tests

## Default Stance

Unless there is a clear reason not to, prefer these defaults:

- Use **real containers for integration tests**, not mocks
- Prefer **module-specific helpers** like `postgres.Run` and `redis.Run` over lower-level generic setup when a module exists
- Prefer **`testcontainers.Run`** over older `GenericContainer` patterns for generic services
- Register cleanup immediately with **`testcontainers.CleanupContainer(t, ctr)`** in normal tests
- For expensive services like Postgres and Redis, prefer **one container per package/test binary**, not one container per test
- Keep tests parallel by isolating **state inside the shared container** per test
- Use **per-test transactions, schemas, databases, logical Redis DBs, or key prefixes** instead of sharing mutable state
- Let Docker assign **random host ports**; do not hardcode host ports in tests
- Configure **wait strategies** explicitly when readiness is not guaranteed by the module
- Avoid cross-test and cross-package reuse by default; keep tests hermetic and self-contained

## Terminology: Containers Are Not Mocks

For Postgres and Redis integration tests, prefer **real Postgres and Redis containers**.

These are not mocks.

- **Mocks/fakes** are best for unit tests and narrow seams
- **Testcontainers** are best when you want confidence in the real dependency behaviour

If the test is meant to validate SQL, migrations, transactions, Redis commands, TTL behaviour, or networked dependency behaviour, a real container is usually the right tool.

## Version and API Notes

- `github.com/testcontainers/testcontainers-go` is the main library
- Prefer modern `Run(...)` APIs
- `GenericContainer` is the older style; prefer `testcontainers.Run(...)` for new generic-container examples
- Module-level `RunContainer(ctx, opts...)` helpers are deprecated; prefer `postgres.Run(...)`, `redis.Run(...)`, etc.
- `WithReuseByName(...)` is experimental; do not make it your default CI/test strategy

## Lifecycle Scope Tradeoffs

Choose container lifetime deliberately:

| Scope | Startup cost | Isolation | Parallel friendliness | Recommended use |
|---|---|---|---|---|
| Per test | Highest | Strongest | Excellent | Small suites, destructive tests, tests that mutate process-wide server state |
| Per package | Moderate | Strong if you isolate test data | Excellent when state is isolated correctly | **Default** for Postgres, Redis, and similar services |
| Cross-package/shared reusable container | Lowest warm-start cost | Weakest | Risky | Local experimentation only; avoid as the default |

## Recommended Default

For Postgres and Redis, prefer:

- **one container per package/test binary**
- **parallel tests inside that package**
- **per-test state isolation inside the container**

Why this is the usual sweet spot:

- Starting one Postgres/Redis container per test is often too slow
- Sharing one container per package keeps startup cost acceptable
- `go test` runs each package in a separate process, so package-scoped fixtures already isolate one package from another
- You still need to isolate state between tests inside that package

If most tests in the package need the dependency, `TestMain` is a good fit. If only some tests need it, a lazy package-scoped helper can be better.

## Generic Container Startup

Use generic startup when there is no higher-level module or when you need custom behaviour.

```go
package cache_test

import (
    "context"
    "testing"
    "time"

    "github.com/stretchr/testify/require"

    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/wait"
)

func TestWithGenericRedis(t *testing.T) {
    t.Parallel()

    ctx := context.Background()

    ctr, err := testcontainers.Run(ctx,
        "redis:7",
        testcontainers.WithExposedPorts("6379/tcp"),
        testcontainers.WithWaitStrategy(
            wait.ForListeningPort("6379/tcp"),
            wait.ForLog("Ready to accept connections").WithStartupTimeout(30*time.Second),
        ),
    )
    testcontainers.CleanupContainer(t, ctr)
    require.NoError(t, err)

    endpoint, err := ctr.Endpoint(ctx, "")
    require.NoError(t, err)

    _ = endpoint // pass to your client under test
}
```

Use this pattern for services without a dedicated module, or when you need full control over files, env vars, commands, or custom wait strategies.

## Postgres Module Example

Prefer the Postgres module for Postgres integration tests.

```go
package repo_test

import (
    "context"
    "path/filepath"
    "testing"

    "github.com/stretchr/testify/require"

    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/modules/postgres"
)

func TestRepositoryWithPostgres(t *testing.T) {
    t.Parallel()

    ctx := context.Background()

    ctr, err := postgres.Run(ctx,
        "postgres:16-alpine",
        postgres.WithDatabase("app_test"),
        postgres.WithUsername("postgres"),
        postgres.WithPassword("postgres"),
        postgres.WithInitScripts(filepath.Join("testdata", "init.sql")),
        postgres.BasicWaitStrategies(),
    )
    testcontainers.CleanupContainer(t, ctr)
    require.NoError(t, err)

    dsn, err := ctr.ConnectionString(ctx, "sslmode=disable")
    require.NoError(t, err)

    _ = dsn // open your DB client here
}
```

Notes:

- `postgres.BasicWaitStrategies()` is the common default for Postgres readiness
- `WithInitScripts(...)` is useful for schema setup or seed data
- `ConnectionString(...)` is usually the easiest way to build a DB client

## Redis Module Example

Prefer the Redis module for Redis integration tests.

```go
package cache_test

import (
    "context"
    "testing"

    "github.com/stretchr/testify/require"

    "github.com/testcontainers/testcontainers-go"
    tcredis "github.com/testcontainers/testcontainers-go/modules/redis"
)

func TestCacheWithRedis(t *testing.T) {
    t.Parallel()

    ctx := context.Background()

    ctr, err := tcredis.Run(ctx,
        "redis:7",
    )
    testcontainers.CleanupContainer(t, ctr)
    require.NoError(t, err)

    uri, err := ctr.ConnectionString(ctx)
    require.NoError(t, err)

    _ = uri // pass to your redis client under test
}
```

Notes:

- Use module options like `WithConfigFile(...)`, `WithTLS()`, or `WithLogLevel(...)` when relevant
- `ConnectionString(...)` returns a ready-to-use Redis URI
- `WithSnapshotting(...)` configures Redis persistence behaviour; it is **not** a per-test isolation/reset mechanism

## Package-Scoped Container Pattern

When most tests in a package need the same dependency, prefer a package-scoped container.

```go
package repo_test

import (
    "context"
    "log"
    "os"
    "testing"

    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/modules/postgres"
)

var (
    postgresDSN string
    postgresCtr *postgres.PostgresContainer
)

func TestMain(m *testing.M) {
    ctx := context.Background()

    var err error
    postgresCtr, err = postgres.Run(ctx,
        "postgres:16-alpine",
        postgres.WithDatabase("app_test"),
        postgres.WithUsername("postgres"),
        postgres.WithPassword("postgres"),
        postgres.BasicWaitStrategies(),
    )
    if err != nil {
        log.Fatal(err)
    }

    postgresDSN, err = postgresCtr.ConnectionString(ctx, "sslmode=disable")
    if err != nil {
        log.Fatal(err)
    }

    code := m.Run()

    if err := testcontainers.TerminateContainer(postgresCtr); err != nil {
        log.Printf("terminate postgres container: %v", err)
    }

    os.Exit(code)
}
```

This is a good default when:

- the container startup cost is noticeable
- most tests in the package need the dependency
- you have a clear per-test isolation strategy for data

## Parallel Tests Need State Isolation, Not Just Container Isolation

Sharing one container does **not** make parallel tests safe by itself.

If tests run with `t.Parallel()`, they must not step on the same data.

Prefer one of these per-test isolation patterns.

### Postgres Isolation Patterns

Preferred order:

1. **Per-test transaction + rollback** when your code can run inside an injected transaction
2. **Per-test schema** when your app can point each test at its own schema/search path
3. **Per-test database** inside the same Postgres server when schema isolation is not enough
4. **Per-test container** only when the test truly needs process-level or cluster-level isolation

#### Transaction pattern

Best when the application code can accept a `*sql.Tx`, `pgx.Tx`, or a narrow query interface.

- Fastest reset strategy
- Excellent for parallel tests
- Minimal container churn

#### Per-schema pattern

Good when each test can use a unique schema name.

- Works well with one package-level Postgres container
- Lets parallel tests run without dropping each other's tables
- Usually faster than creating a fresh container per test

#### Snapshot/Restore pattern

The Postgres module supports `Snapshot(...)` and `Restore(...)`.

Use it when:

- migrations are expensive
- you want a quick reset to a known base state
- tests are mostly serial, or you can guarantee only one restore operation at a time

Be careful:

- `Restore(...)` resets shared database state
- do **not** call it concurrently from parallel tests that share the same Postgres container/database
- for truly parallel tests, prefer per-test transactions, schemas, or databases instead

### Redis Isolation Patterns

Preferred order:

1. **Per-test logical DB** when using standalone Redis and your client can select DB numbers
2. **Per-test key prefix/namespace** when logical DB separation is not practical
3. **Per-test container** when you need hard isolation or destructive global operations

#### Per-test logical DB

Good when using a standard standalone Redis image.

```go
client := redis.NewClient(&redis.Options{
    Addr: redisAddr,
    DB:   testDBNumber,
})
```

Guidance:

- Give each parallel test a distinct DB number
- Clean up with `FLUSHDB` for that logical DB only
- Avoid `FLUSHALL` in tests

#### Per-test key prefix

Good when DB-number isolation is unavailable or inconvenient.

- Prefix keys with a test-unique namespace such as `t_<id>:`
- Delete only that namespace in cleanup
- Safer for parallel tests than sharing raw keys

Be careful with global Redis operations:

- `FLUSHALL` will destroy every test's state
- `FLUSHDB` is also unsafe if multiple parallel tests share the same logical DB

## Example: Package-Level Postgres + Parallel Tests

This is usually the best tradeoff for repository/service integration tests.

- Start one Postgres container in `TestMain`
- Run migrations once
- Let each parallel test use its own transaction, schema, or database

Prefer this over one-container-per-test when:

- container startup dominates runtime
- the main thing you need is data isolation, not full server-process isolation

## Example: Package-Level Redis + Parallel Tests

This is usually the best tradeoff for cache integration tests.

- Start one Redis container for the package
- Give each test its own logical DB or unique key prefix
- Never use global destructive cleanup across all tests

## Wait Strategies and Readiness

Do not assume container start means service readiness.

Prefer:

- module-provided readiness helpers when available
- `wait.ForListeningPort(...)` for services that only need the socket up
- `wait.ForLog(...)` when service logs are the most reliable readiness signal
- combined strategies for flaky services or non-Linux host setups

Postgres specifically benefits from explicit readiness checks like `postgres.BasicWaitStrategies()`.

## Ports, Addresses, and Connection Strings

Prefer runtime discovery over fixed ports:

- `ctr.ConnectionString(ctx, ...)` for Postgres
- `ctr.ConnectionString(ctx)` for Redis
- `ctr.Endpoint(ctx, "")` or `ctr.MappedPort(ctx, ...)` for generic containers

Do not hardcode `localhost:5432` or `localhost:6379`.

Parallel tests depend on Docker assigning distinct mapped host ports.

## Cleanup Guidance

In normal tests:

```go
ctr, err := postgres.Run(ctx, "postgres:16-alpine", postgres.BasicWaitStrategies())
testcontainers.CleanupContainer(t, ctr)
require.NoError(t, err)
```

In `TestMain`:

- use `testcontainers.TerminateContainer(...)` explicitly after `m.Run()`

Register cleanup immediately after startup.

## Reuse Guidance

`WithReuseByName(...)` exists, but it is experimental.

Avoid making reuse your default because it:

- weakens test hermeticity
- risks hidden state between runs
- can behave differently in local development vs CI

Prefer clean startup/teardown unless you have a deliberate local-only optimisation strategy.

## Review Checklist

When reviewing `testcontainers-go` usage, check for:

- Module helpers used where available (`postgres.Run`, `redis.Run`)
- Modern `Run(...)` APIs instead of deprecated patterns
- Cleanup registered immediately
- No fixed host ports
- Explicit readiness/wait strategy where needed
- Package-scoped lifecycle chosen deliberately
- Clear per-test isolation strategy for parallel tests
- No global destructive cleanup that breaks parallel runs
- Real Postgres/Redis containers used for integration tests instead of mocks
- Postgres snapshot/restore used only when its shared-state tradeoff is acceptable

## Anti-Patterns

Avoid these unless there is a strong reason:

- One heavy Postgres container per test when a package-scoped container plus data isolation would do
- Sharing one Postgres database across parallel tests with no transaction/schema/database isolation
- Sharing one Redis logical DB across parallel tests and calling `FLUSHDB`
- Calling `FLUSHALL` in a parallel suite
- Hardcoding `localhost:5432` or `localhost:6379`
- Relying on container startup without readiness checks
- Treating `WithSnapshotting(...)` on Redis as a test reset mechanism
- Defaulting to `WithReuseByName(...)` in CI
- Using mocks to test SQL or Redis command behaviour that should be verified against the real service

## Quick Templates

### Postgres package template

```go
var postgresDSN string

func TestMain(m *testing.M) {
    ctx := context.Background()

    ctr, err := postgres.Run(ctx,
        "postgres:16-alpine",
        postgres.WithDatabase("app_test"),
        postgres.WithUsername("postgres"),
        postgres.WithPassword("postgres"),
        postgres.BasicWaitStrategies(),
    )
    if err != nil {
        log.Fatal(err)
    }

    postgresDSN, err = ctr.ConnectionString(ctx, "sslmode=disable")
    if err != nil {
        log.Fatal(err)
    }

    code := m.Run()
    _ = testcontainers.TerminateContainer(ctr)
    os.Exit(code)
}
```

Then make each parallel test isolate its own transaction, schema, or database.

### Redis package template

```go
var redisURI string

func TestMain(m *testing.M) {
    ctx := context.Background()

    ctr, err := tcredis.Run(ctx, "redis:7")
    if err != nil {
        log.Fatal(err)
    }

    redisURI, err = ctr.ConnectionString(ctx)
    if err != nil {
        log.Fatal(err)
    }

    code := m.Run()
    _ = testcontainers.TerminateContainer(ctr)
    os.Exit(code)
}
```

Then give each parallel test its own logical DB or key prefix.
