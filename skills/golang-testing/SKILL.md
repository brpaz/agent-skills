---
name: golang-testing
version: "2.0.0"
description: "Write idiomatic Go tests — unit tests, table-driven patterns, mocking, and testcontainers-go integration tests against real Postgres, Redis, and other containerised dependencies."
tags: [go, golang, testing, integration, testcontainers, docker]
---

# Golang Testing

Use this skill when writing, reviewing, or refactoring Go tests — unit tests, table-driven tests, or container-backed integration tests.

## When to Use

- Writing new unit, integration, or package-level tests for Go code
- Refactoring tests toward idiomatic Go structure and stronger signal
- Reviewing Go test suites for maintainability, determinism, and coverage gaps
- Designing fakes, mocks, or test seams around external dependencies
- Testing against a real Postgres, Redis, Kafka, NATS, or other containerised dependency with `testcontainers-go`
- Verifying SQL, migrations, indexes, transactions, locking, or driver behaviour against real infrastructure

## Default Testing Stance

Unless there is a clear reason not to, prefer these defaults:

- Use **black-box tests** with an external test package: `package mypkg_test`
- Test **public behaviour and interfaces**, not internal implementation details
- Use **one top-level test function per public function/method/behaviour**, with **subtests** for scenarios
- Call **`t.Parallel()` by default** in top-level tests and subtests unless shared state, process-wide mutation, timing, or external resources make it unsafe
- Use **`t.Run` subtests by default**, even when not using table-driven tests
- Use **table-driven tests only** when there is a finite, related set of input/output scenarios that benefits from shared structure
- Use **`testify/require`** for preconditions and fatal assertions, and **`testify/assert`** for non-fatal assertions
- Use **`testify/mock`** only for true external-system boundaries or very small/simple seams; otherwise prefer fakes or in-memory implementations
- Use **real containers via `testcontainers-go`** for integration tests that need real Postgres, Redis, or similar infrastructure, rather than mocking the dependency
- Keep tests deterministic, hermetic, and readable

## Core Principles

- **Behaviour over implementation** - Assert externally visible outcomes
- **Fast feedback** - Keep most tests cheap enough to run constantly
- **Deterministic** - Avoid sleeps, real clocks, network access, and ambient environment dependence
- **Minimal setup** - Prefer small helpers over deep fixture stacks
- **High signal** - Each failing test should point to one clear behaviour regression
- **Coverage with intent** - Cover important branches, edge cases, and error paths, not just lines

## Package and File Conventions

### Black-Box Test Packages

Prefer:

```go
package user_test

import (
    "testing"

    "github.com/stretchr/testify/require"

    "example.com/project/user"
)
```

Avoid:

```go
package user
```

Use same-package tests only when you intentionally need access to unexported helpers and there is no better public seam. Default to `_test` packages.

### File Organisation

- Group tests by public API surface or behaviour
- Keep helper functions near the tests that use them unless broadly reused
- Prefer `_test.go` files named after the subject under test, such as `service_test.go`, `handler_test.go`, `client_test.go`
- Avoid giant catch-all files once a package grows

## Preferred Test Structure

### One Top-Level Test per Behaviour, Subtests per Scenario

For a public function, prefer one top-level test and scenario subtests instead of many separate `TestXxx_Yyy` functions.

Use `t.Run` even without a table when the scenarios are clearer as explicitly written examples.

```go
func TestCreateUser(t *testing.T) {
    t.Parallel()

    t.Run("success", func(t *testing.T) {
        t.Parallel()

        got, err := user.Create("alice@example.com")
        require.NoError(t, err)
        assert.Equal(t, "alice@example.com", got.Email)
    })

    t.Run("rejects invalid email", func(t *testing.T) {
        t.Parallel()

        _, err := user.Create("not-an-email")
        require.Error(t, err)
        require.ErrorIs(t, err, user.ErrInvalidEmail)
    })
}
```

```go
func TestParseUserID(t *testing.T) {
    t.Parallel()

    tests := []struct {
        name    string
        input   string
        want    int
        wantErr string
    }{
        {name: "valid", input: "42", want: 42},
        {name: "empty", input: "", wantErr: "empty user id"},
        {name: "invalid", input: "abc", wantErr: "invalid user id"},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()

            got, err := user.ParseUserID(tt.input)

            if tt.wantErr != "" {
                require.Error(t, err)
                assert.Contains(t, err.Error(), tt.wantErr)
                return
            }

            require.NoError(t, err)
            assert.Equal(t, tt.want, got)
        })
    }
}
```

### Why This Pattern

- Keeps all scenarios for one behaviour together
- Makes it easy to add edge cases without duplicating setup
- Produces better output in `go test -run` and CI logs
- Works naturally with table-driven tests and `t.Parallel()`

## Parallel Test Execution

### Default Rule

Call `t.Parallel()` unless there is a concrete reason not to.

Good candidates:

- Pure functions
- Tests using isolated in-memory state
- Tests using `t.TempDir()`
- Tests with per-test `httptest.Server`
- Table-driven subtests with isolated fixtures

Avoid or carefully isolate parallelism when tests:

- Mutate global variables, singleton state, env vars, or process working directory
- Depend on wall-clock timing or `time.Sleep`
- Reuse shared mocks/fakes with non-thread-safe state
- Use fixed ports, shared files, or shared databases without isolation

### Parallel Subtest Safety

In Go 1.22+ modules, loop variables declared in the `for` statement are created per iteration, so rebinding like `tt := tt` is usually not needed.

Still rebind when:

- the module/package targets pre-Go-1.22 semantics
- the variable is declared outside the loop and reused
- you intentionally want compatibility with older Go module targets

For modern Go:

```go
for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) {
        t.Parallel()
        // use tt safely in Go 1.22+
    })
}
```

For older module targets:

```go
for _, tt := range tests {
    tt := tt
    t.Run(tt.name, func(t *testing.T) {
        t.Parallel()
        // use tt safely
    })
}
```

## Testify Usage

Prefer Testify for clearer assertions.

```go
import (
    "testing"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)
```

### `require` vs `assert`

- Use **`require`** when the test cannot continue after failure
- Use **`assert`** when you want multiple related checks in one scenario

```go
func TestUserName(t *testing.T) {
    t.Parallel()

    u, err := user.New("alice")
    require.NoError(t, err)

    assert.Equal(t, "alice", u.Name())
    assert.True(t, u.IsActive())
}
```

Prefer semantic assertions when available:

- `require.ErrorIs`
- `assert.Equal`
- `assert.ElementsMatch`
- `assert.Len`
- `assert.Empty` / `assert.NotEmpty`
- `assert.WithinDuration`
- `assert.JSONEq`

## Error Testing

- Prefer asserting exported sentinel/type behaviour with `ErrorIs` / `ErrorAs`
- Avoid brittle full-string equality unless the exact message is part of the contract
- Assert both success and failure paths for public APIs

```go
require.ErrorIs(t, err, user.ErrNotFound)
```

## Good Coverage Practices

Aim for coverage that reflects risk and behaviour, not vanity percentages.

### Always Cover

- Happy path
- Input validation failures
- Boundary values
- Zero values and empty collections
- Domain-specific edge cases
- External dependency failures
- Serialization/parsing failures
- Context cancellation / timeout paths when relevant
- Idempotency or retry semantics when relevant

### Coverage Heuristics

- Add a test for every bug fix before or with the fix
- Cover each exported public method/function with at least one success and one failure/edge scenario where meaningful
- Prefer focused unit tests for combinatorial logic and a smaller number of integration tests for end-to-end confidence
- If a branch matters to production behaviour, it deserves an assertion
- Remove duplicate tests that do not add behavioural signal

### Coverage Commands

```bash
go test ./...
go test ./... -cover
go test ./... -coverprofile=coverage.out
go tool cover -func=coverage.out
go tool cover -html=coverage.out
```

## Integration vs Unit Tests

Use the lightest test that proves the behaviour.

### Prefer Unit Tests For

- Pure transformations and validation
- Orchestration logic with fake dependencies
- Error mapping and branching logic

### Prefer Integration Tests For

- SQL queries and repository behaviour
- HTTP handlers, middleware, and routing
- Serialization boundaries
- Interactions with real adapters that are cheap and deterministic to run locally/CI

When an integration test gives stronger confidence with similar complexity, prefer it over elaborate mocking. See **Integration Testing with Testcontainers-go** below for container-backed patterns against real Postgres, Redis, and similar services.

## Integration Testing with Testcontainers-go

Use `testcontainers-go` when an integration test needs a real Postgres, Redis, Kafka, NATS, or other containerised dependency instead of a mock — for verifying SQL, migrations, indexes, transactions, locking, driver behaviour, or cache integration against the real thing.

### Default Stance

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

### Terminology: Containers Are Not Mocks

For Postgres and Redis integration tests, prefer **real Postgres and Redis containers**.

These are not mocks.

- **Mocks/fakes** are best for unit tests and narrow seams
- **Testcontainers** are best when you want confidence in the real dependency behaviour

If the test is meant to validate SQL, migrations, transactions, Redis commands, TTL behaviour, or networked dependency behaviour, a real container is usually the right tool.

### Version and API Notes

- `github.com/testcontainers/testcontainers-go` is the main library
- Prefer modern `Run(...)` APIs
- `GenericContainer` is the older style; prefer `testcontainers.Run(...)` for new generic-container examples
- Module-level `RunContainer(ctx, opts...)` helpers are deprecated; prefer `postgres.Run(...)`, `redis.Run(...)`, etc.
- `WithReuseByName(...)` is experimental; do not make it your default CI/test strategy

### Lifecycle Scope Tradeoffs

Choose container lifetime deliberately:

| Scope | Startup cost | Isolation | Parallel friendliness | Recommended use |
|---|---|---|---|---|
| Per test | Highest | Strongest | Excellent | Small suites, destructive tests, tests that mutate process-wide server state |
| Per package | Moderate | Strong if you isolate test data | Excellent when state is isolated correctly | **Default** for Postgres, Redis, and similar services |
| Cross-package/shared reusable container | Lowest warm-start cost | Weakest | Risky | Local experimentation only; avoid as the default |

### Recommended Default

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

### Generic Container Startup

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

### Postgres Module Example

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

### Redis Module Example

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

### Package-Scoped Container Pattern

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

### Parallel Tests Need State Isolation, Not Just Container Isolation

Sharing one container does **not** make parallel tests safe by itself.

If tests run with `t.Parallel()`, they must not step on the same data.

Prefer one of these per-test isolation patterns.

#### Postgres Isolation Patterns

Preferred order:

1. **Per-test transaction + rollback** when your code can run inside an injected transaction
2. **Per-test schema** when your app can point each test at its own schema/search path
3. **Per-test database** inside the same Postgres server when schema isolation is not enough
4. **Per-test container** only when the test truly needs process-level or cluster-level isolation

**Transaction pattern**

Best when the application code can accept a `*sql.Tx`, `pgx.Tx`, or a narrow query interface.

- Fastest reset strategy
- Excellent for parallel tests
- Minimal container churn

**Per-schema pattern**

Good when each test can use a unique schema name.

- Works well with one package-level Postgres container
- Lets parallel tests run without dropping each other's tables
- Usually faster than creating a fresh container per test

**Snapshot/Restore pattern**

The Postgres module supports `Snapshot(...)` and `Restore(...)`.

Use it when:

- migrations are expensive
- you want a quick reset to a known base state
- tests are mostly serial, or you can guarantee only one restore operation at a time

Be careful:

- `Restore(...)` resets shared database state
- do **not** call it concurrently from parallel tests that share the same Postgres container/database
- for truly parallel tests, prefer per-test transactions, schemas, or databases instead

#### Redis Isolation Patterns

Preferred order:

1. **Per-test logical DB** when using standalone Redis and your client can select DB numbers
2. **Per-test key prefix/namespace** when logical DB separation is not practical
3. **Per-test container** when you need hard isolation or destructive global operations

**Per-test logical DB**

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

**Per-test key prefix**

Good when DB-number isolation is unavailable or inconvenient.

- Prefix keys with a test-unique namespace such as `t_<id>:`
- Delete only that namespace in cleanup
- Safer for parallel tests than sharing raw keys

Be careful with global Redis operations:

- `FLUSHALL` will destroy every test's state
- `FLUSHDB` is also unsafe if multiple parallel tests share the same logical DB

### Example: Package-Level Postgres + Parallel Tests

This is usually the best tradeoff for repository/service integration tests.

- Start one Postgres container in `TestMain`
- Run migrations once
- Let each parallel test use its own transaction, schema, or database

Prefer this over one-container-per-test when:

- container startup dominates runtime
- the main thing you need is data isolation, not full server-process isolation

### Example: Package-Level Redis + Parallel Tests

This is usually the best tradeoff for cache integration tests.

- Start one Redis container for the package
- Give each test its own logical DB or unique key prefix
- Never use global destructive cleanup across all tests

### Wait Strategies and Readiness

Do not assume container start means service readiness.

Prefer:

- module-provided readiness helpers when available
- `wait.ForListeningPort(...)` for services that only need the socket up
- `wait.ForLog(...)` when service logs are the most reliable readiness signal
- combined strategies for flaky services or non-Linux host setups

Postgres specifically benefits from explicit readiness checks like `postgres.BasicWaitStrategies()`.

### Ports, Addresses, and Connection Strings

Prefer runtime discovery over fixed ports:

- `ctr.ConnectionString(ctx, ...)` for Postgres
- `ctr.ConnectionString(ctx)` for Redis
- `ctr.Endpoint(ctx, "")` or `ctr.MappedPort(ctx, ...)` for generic containers

Do not hardcode `localhost:5432` or `localhost:6379`.

Parallel tests depend on Docker assigning distinct mapped host ports.

### Cleanup Guidance

In normal tests:

```go
ctr, err := postgres.Run(ctx, "postgres:16-alpine", postgres.BasicWaitStrategies())
testcontainers.CleanupContainer(t, ctr)
require.NoError(t, err)
```

In `TestMain`:

- use `testcontainers.TerminateContainer(...)` explicitly after `m.Run()`

Register cleanup immediately after startup.

### Reuse Guidance

`WithReuseByName(...)` exists, but it is experimental.

Avoid making reuse your default because it:

- weakens test hermeticity
- risks hidden state between runs
- can behave differently in local development vs CI

Prefer clean startup/teardown unless you have a deliberate local-only optimisation strategy.

### Quick Templates

**Postgres package template**

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

**Redis package template**

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

## Mocking Guidance

### Default Rule

Mock only external systems or very thin boundaries. Prefer fakes and in-memory implementations for richer domain behaviour.

Prefer:

- In-memory repositories
- `httptest.Server`
- Temporary directories
- `fstest.MapFS`
- Fixed clocks / injectable time sources

Reach for `testify/mock` when:

- The dependency is an external system boundary
- A fake would be more complex than the behaviour being tested
- You need precise call assertions on a thin collaborator

Avoid mocks for:

- Your own core domain models
- Simple data containers
- Behaviour that is easier to express with an in-memory fake
- Deep implementation-driven interaction testing

### Testify Mock Pattern

```go
type MockMailer struct {
    mock.Mock
}

func (m *MockMailer) Send(ctx context.Context, msg mail.Message) error {
    args := m.Called(ctx, msg)
    return args.Error(0)
}

func TestService_SendWelcomeEmail(t *testing.T) {
    t.Parallel()

    mailer := new(MockMailer)
    mailer.
        On("Send", mock.Anything, mail.Message{To: "alice@example.com"}).
        Return(nil).
        Once()

    svc := user.NewService(mailer)

    err := svc.SendWelcomeEmail(context.Background(), "alice@example.com")
    require.NoError(t, err)

    mailer.AssertExpectations(t)
}
```

Rules:

- One mock per external dependency seam, not everywhere
- Keep expectations minimal and behaviour-focused
- Avoid over-asserting call order unless it is part of the contract
- Do not share mock instances across parallel tests

## Filesystem Testing

Prefer standard-library-friendly seams and hermetic storage.

### Recommended Patterns

1. **Inject an `fs.FS`** for read-only filesystem behaviour
2. Use **`fstest.MapFS`** for small read scenarios
3. Use **`t.TempDir()`** for realistic file creation/update flows
4. Keep filesystem access behind a small adapter if the production code is otherwise hard to isolate

### `fstest.MapFS` Example

```go
func TestLoadConfig(t *testing.T) {
    t.Parallel()

    files := fstest.MapFS{
        "config.json": {Data: []byte(`{"env":"test"}`)},
    }

    cfg, err := config.Load(files, "config.json")
    require.NoError(t, err)
    assert.Equal(t, "test", cfg.Env)
}
```

### `t.TempDir()` Example

```go
func TestWriteReport(t *testing.T) {
    t.Parallel()

    dir := t.TempDir()
    path := filepath.Join(dir, "report.txt")

    err := report.Write(path, "hello")
    require.NoError(t, err)

    data, err := os.ReadFile(path)
    require.NoError(t, err)
    assert.Equal(t, "hello", string(data))
}
```

Avoid mocking `os` calls directly when a temp dir or `fs.FS` seam would be simpler.

## HTTP Client Testing

Prefer real HTTP semantics without real network dependencies.

### Recommended Patterns

1. Use **`httptest.Server`** to test client behaviour against realistic responses
2. Inject `*http.Client` into your code
3. For very small seams, a custom `http.RoundTripper` fake can be enough
4. Mock higher-level gateways only when HTTP itself is not the thing under test

### `httptest.Server` Example

```go
func TestClient_GetUser(t *testing.T) {
    t.Parallel()

    srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        assert.Equal(t, http.MethodGet, r.Method)
        assert.Equal(t, "/users/42", r.URL.Path)
        w.Header().Set("Content-Type", "application/json")
        _, _ = w.Write([]byte(`{"id":42,"name":"alice"}`))
    }))
    t.Cleanup(srv.Close)

    client := api.NewClient(srv.URL, srv.Client())

    got, err := client.GetUser(context.Background(), 42)
    require.NoError(t, err)
    assert.Equal(t, "alice", got.Name)
}
```

### Custom Transport Fake

For narrow client logic, prefer a tiny fake over a heavyweight mock:

```go
type roundTripFunc func(*http.Request) (*http.Response, error)

func (f roundTripFunc) RoundTrip(r *http.Request) (*http.Response, error) {
    return f(r)
}
```

Use this when you only need to simulate one request/response pair and `httptest.Server` would be unnecessary ceremony.

## Time Testing

Do not depend on real time in tests.

### Recommended Patterns

1. Inject time via a function like `now func() time.Time`
2. Or define a tiny clock interface at the boundary that needs it
3. Use fixed timestamps in tests
4. Avoid `time.Sleep` as a synchronisation mechanism
5. Prefer contexts, channels, and explicit signals over waiting for elapsed time

### Function Injection Example

```go
type Service struct {
    now func() time.Time
}

func NewService() *Service {
    return &Service{now: time.Now}
}
```

```go
func TestTokenExpired(t *testing.T) {
    t.Parallel()

    fixed := time.Date(2025, 1, 1, 12, 0, 0, 0, time.UTC)
    svc := token.NewService(func() time.Time { return fixed })

    assert.True(t, svc.IsExpired(fixed.Add(-time.Second)))
    assert.False(t, svc.IsExpired(fixed.Add(time.Second)))
}
```

If production code currently calls `time.Now()` directly in many places, first introduce a small seam at the package boundary rather than mocking time per call site.

## Table-Driven Testing Guidance

- Prefer plain `t.Run` subtests first without a table when scenarios are clearer as explicitly written examples
- Use tables when the setup is mostly the same and only inputs/expectations vary
- Name cases for behaviour, not raw input values
- Keep test case structs focused; avoid giant anonymous structs with dozens of fields
- Split unrelated behaviours into separate tests instead of massive tables

Good fit for table-driven tests:

- Parsing and validation matrices
- Boundary-value checks on the same function
- Multiple related input/output combinations for deterministic logic

Poor fit for table-driven tests:

- Scenarios with materially different setup or assertions
- Behaviour tests that read more clearly as individually named `t.Run` blocks
- Large tables that hide intent behind many mostly-empty fields

## Test Helpers

- Prefer helper functions that build valid defaults and allow explicit overrides
- Mark helpers with `t.Helper()`
- Return concrete values rather than hidden global state
- Keep helpers local to the package unless broad reuse justifies promotion

```go
func newTestUser(t *testing.T, opts ...UserOption) user.User {
    t.Helper()
    u, err := user.New("alice", opts...)
    require.NoError(t, err)
    return u
}
```

## Anti-Patterns

Avoid these unless there is a strong reason:

### General

- Same-package white-box tests by default
- Multiple top-level tests for each small scenario of one function
- Reaching for table-driven tests when explicit `t.Run` scenarios are clearer
- No `t.Parallel()` without reason
- Real sleeps, real network calls, or dependence on current wall-clock time
- Assertion on internal private fields in black-box tests
- Brittle exact error string checks for wrapped/domain errors
- Massive shared fixtures that hide what the test actually needs
- Mock-heavy tests that mirror implementation rather than behaviour
- Coverage chasing without meaningful assertions

### Testcontainers-go

- One heavy Postgres container per test when a package-scoped container plus data isolation would do
- Sharing one Postgres database across parallel tests with no transaction/schema/database isolation
- Sharing one Redis logical DB across parallel tests and calling `FLUSHDB`
- Calling `FLUSHALL` in a parallel suite
- Hardcoding `localhost:5432` or `localhost:6379`
- Relying on container startup without readiness checks
- Treating `WithSnapshotting(...)` on Redis as a test reset mechanism
- Defaulting to `WithReuseByName(...)` in CI
- Using mocks to test SQL or Redis command behaviour that should be verified against the real service

## Review Checklist

When reviewing Go tests, check for:

### General

- Black-box `_test` package usage by default
- `t.Parallel()` in top-level tests and subtests unless unsafe
- Subtests for multiple scenarios of one behaviour
- `testify/assert` and `testify/require` used appropriately
- Fakes preferred over mocks when practical
- `testify/mock` limited to external boundaries or simple seams
- No hidden global state or cross-test coupling
- Deterministic handling of filesystem, HTTP, and time
- Meaningful edge-case and error-path coverage
- Tests that read like executable specifications of public behaviour

### Testcontainers-go

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
