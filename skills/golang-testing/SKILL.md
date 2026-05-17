---
name: golang-testing
version: "1.0.0"
description: "Write idiomatic Go tests."
tags: [go, golang, testing]
---

# Golang Testing

Use this skill when writing, reviewing, or refactoring Go tests.

## When to Use

- Writing new unit, integration, or package-level tests for Go code
- Refactoring tests toward idiomatic Go structure and stronger signal
- Reviewing Go test suites for maintainability, determinism, and coverage gaps
- Designing fakes, mocks, or test seams around external dependencies

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

When an integration test gives stronger confidence with similar complexity, prefer it over elaborate mocking.

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

## Review Checklist

When reviewing Go tests, check for:

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
