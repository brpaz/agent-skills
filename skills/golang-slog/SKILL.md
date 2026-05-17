---
name: golang-slog
version: "1.0.0"
description: "Implement structured logging in Go with log/slog, including logger setup, common attributes, context propagation, redaction, and performance-minded patterns."
tags: [go, golang, logging, slog, observability, structured-logging]
---

# Golang slog

Use this skill when implementing structured logging in Go with the standard library `log/slog` package.

Use it alongside the `structured-logging` skill:

- `structured-logging` defines the cross-language schema, field naming, safety, and observability rules
- `golang-slog` shows how to implement those rules idiomatically in Go with `log/slog`

## When to Use

- Adding structured logging to a Go service or CLI
- Replacing ad-hoc `log.Printf` calls with structured events
- Standardising common log fields across Go services
- Building request-scoped, worker-scoped, or job-scoped loggers
- Implementing redaction, log schema normalisation, or dynamic log levels

## Default Stance

Unless there is a clear reason not to, prefer these defaults:

- Use the standard library **`log/slog`** for Go 1.21+
- Prefer a **`Format` config** such as `json` or `text`, rather than a bare `JSON` boolean
- Use **`JSONHandler` in production** and **`TextHandler` locally**
- Construct the logger once during application startup
- Attach stable application metadata once with **`Logger.With(...)`**
- Keep the **schema aligned with the `structured-logging` skill**
- Prefer **typed attrs** like `slog.String`, `slog.Int`, `slog.Int64`, `slog.Duration`, `slog.Bool`
- Prefer **`InfoContext` / `ErrorContext` / `LogAttrs`** when a `context.Context` is available
- Use **`WithGroup`** or `slog.Group(...)` for nested structured context
- Use **`ReplaceAttr`** and **`LogValuer`** for schema normalisation and redaction
- Pass `*slog.Logger` as a dependency instead of hiding it in global state when possible

## Version Notes

- `log/slog` is in the Go standard library starting with **Go 1.21**
- `slog.MultiHandler` is a **newer addition**; only use it if your project's Go version supports it
- If your codebase targets older Go versions, use your existing logging stack instead of forcing `slog`

## Schema Alignment with `structured-logging`

The `structured-logging` skill recommends canonical fields like:

- `timestamp`
- `level`
- `message`
- `service`
- `environment`
- `application_version`
- `application_commit`
- `request_id`
- `trace_id`
- `span_id`
- `user_id`
- `operation`
- `outcome`
- `duration_ms`
- `error_kind`
- `error_code`
- `error_message`

By default, `slog` emits built-in keys such as:

- `time`
- `level`
- `msg`
- `source`

If you want Go logs to match the shared schema exactly, rename built-in keys with `HandlerOptions.ReplaceAttr`.

## Recommended Logger Bootstrap

Centralise logger construction in `main` or a small bootstrap package.

```go
package logging

import (
    "fmt"
    "io"
    "log/slog"
)

type Format string

const (
    FormatJSON Format = "json"
    FormatText Format = "text"
)

type config struct {
    environment        string
    service            string
    applicationVersion string
    applicationCommit  string
    format             Format
    addSource          bool
    level              slog.Leveler
    replaceAttr        func(groups []string, a slog.Attr) slog.Attr
}

type Option func(*config)

func WithEnvironment(v string) Option {
    return func(c *config) { c.environment = v }
}

func WithService(v string) Option {
    return func(c *config) { c.service = v }
}

func WithApplicationVersion(v string) Option {
    return func(c *config) { c.applicationVersion = v }
}

func WithApplicationCommit(v string) Option {
    return func(c *config) { c.applicationCommit = v }
}

func WithFormat(v Format) Option {
    return func(c *config) { c.format = v }
}

func WithAddSource(v bool) Option {
    return func(c *config) { c.addSource = v }
}

func WithLevel(v slog.Leveler) Option {
    return func(c *config) { c.level = v }
}

func WithReplaceAttr(fn func(groups []string, a slog.Attr) slog.Attr) Option {
    return func(c *config) { c.replaceAttr = fn }
}

func LevelVarFromString(v string) (*slog.LevelVar, error) {
    var level slog.LevelVar
    if err := level.UnmarshalText([]byte(v)); err != nil {
        return nil, fmt.Errorf("parse log level %q: %w", v, err)
    }
    return &level, nil
}

func New(w io.Writer, opts ...Option) (*slog.Logger, error) {
    cfg := config{
        format: FormatJSON,
        level:  slog.LevelInfo,
        replaceAttr: func(groups []string, a slog.Attr) slog.Attr {
            switch a.Key {
            case slog.TimeKey:
                a.Key = "timestamp"
            case slog.MessageKey:
                a.Key = "message"
            }
            return a
        },
    }

    for _, opt := range opts {
        opt(&cfg)
    }

    handlerOptions := &slog.HandlerOptions{
        AddSource:   cfg.addSource,
        Level:       cfg.level,
        ReplaceAttr: cfg.replaceAttr,
    }

    var handler slog.Handler
    switch cfg.format {
    case FormatJSON:
        handler = slog.NewJSONHandler(w, handlerOptions)
    case FormatText:
        handler = slog.NewTextHandler(w, handlerOptions)
    default:
        return nil, fmt.Errorf("unsupported log format: %q", cfg.format)
    }

    logger := slog.New(handler).With(
        slog.String("service", cfg.service),
        slog.String("environment", cfg.environment),
        slog.String("application_version", cfg.applicationVersion),
        slog.String("application_commit", cfg.applicationCommit),
    )

    return logger, nil
}
```

Example use:

```go
level, err := logging.LevelVarFromString("info")
if err != nil {
    return err
}

logger, err := logging.New(os.Stdout,
    logging.WithService("users-api"),
    logging.WithEnvironment("production"),
    logging.WithApplicationVersion("1.8.0"),
    logging.WithApplicationCommit("a1b2c3d4"),
    logging.WithFormat(logging.FormatJSON),
    logging.WithLevel(level),
)
if err != nil {
    return err
}
```

Guidance:

- Build one base logger at startup
- Prefer **functional options** when the bootstrap needs several optional settings
- Add `service`, `environment`, `application_version`, and `application_commit` there
- Prefer a **format enum/string** like `json` or `text` over a `JSON bool`
- Use `JSONHandler` for production ingestion
- Use `TextHandler` only when human readability is more important than strict machine parsing

## Global vs Injected Logger

Prefer:

- Constructing the logger at startup
- Injecting `*slog.Logger` into servers, services, workers, and repositories that need it

Avoid:

- Scattering calls to `slog.Default()` throughout the codebase without a reason
- Using package globals for everything

`SetDefault` is acceptable at the process boundary if you explicitly want top-level `slog.Info(...)` and legacy `log.Print(...)` calls to flow through the same handler, but keep that decision near startup.

## Common Attribute Strategy

### Stable Application Metadata

Attach these once to the base logger:

```go
baseLogger := logger.With(
    slog.String("service", "users-api"),
    slog.String("environment", "production"),
    slog.String("application_version", "1.8.0"),
    slog.String("application_commit", "a1b2c3d4"),
)
```

### Request- or Job-Scoped Metadata

Attach these at the request/job boundary:

```go
requestLogger := baseLogger.With(
    slog.String("request_id", requestID),
    slog.String("trace_id", traceID),
    slog.String("span_id", spanID),
    slog.String("user_id", userID),
)
```

Prefer deriving child loggers with `With(...)` rather than repeating the same attrs on every line.

## Context Usage

If a `context.Context` is available, prefer the `...Context` forms:

- `logger.InfoContext(ctx, ...)`
- `logger.ErrorContext(ctx, ...)`
- `logger.LogAttrs(ctx, ...)`

Why:

- custom handlers may extract trace/span metadata from the context
- it keeps logs aligned with request-scoped and tracing-aware systems

Rules:

- pass context when you already have one
- do not create fake contexts just to log
- do not treat context as a generic service locator

## HTTP Request Pattern

Derive a request logger at the boundary and reuse it for the whole flow.

```go
func (s *Server) handleGetUser(w http.ResponseWriter, r *http.Request) {
    start := time.Now()

    logger := s.logger.With(
        slog.String("request_id", requestIDFromRequest(r)),
        slog.String("trace_id", traceIDFromContext(r.Context())),
        slog.String("http_method", r.Method),
        slog.String("http_route", "/users/{id}"),
    )

    user, err := s.userService.GetByID(r.Context(), chi.URLParam(r, "id"))
    if err != nil {
        logger.ErrorContext(r.Context(), "get user failed",
            slog.String("operation", "get_user"),
            slog.String("outcome", "failure"),
            slog.String("error_kind", "user_lookup_failed"),
            slog.String("error_message", "failed to fetch user"),
            slog.Int64("duration_ms", time.Since(start).Milliseconds()),
        )
        return
    }

    logger.InfoContext(r.Context(), "http request completed",
        slog.String("operation", "get_user"),
        slog.String("outcome", "success"),
        slog.Int("http_status_code", http.StatusOK),
        slog.Int64("duration_ms", time.Since(start).Milliseconds()),
    )

    _ = user
}
```

Keep boundary logs summary-oriented. Avoid logging every internal function call in production.

## Prefer Typed Attrs

Prefer:

```go
logger.Info("user authenticated",
    slog.String("user_id", userID),
    slog.String("operation", "login"),
    slog.Int64("duration_ms", duration.Milliseconds()),
)
```

Over large alternating key/value calls when they get dense or performance-sensitive.

Notes:

- alternating key/value syntax is valid and ergonomic for small calls
- typed attrs are clearer in larger calls
- typed attrs also avoid mistakes that produce `!BADKEY`

## Hot Paths and `LogAttrs`

If profiling shows logging overhead matters, prefer `LogAttrs` with typed attrs.

```go
logger.LogAttrs(ctx, slog.LevelInfo, "cache refresh completed",
    slog.String("operation", "refresh_cache"),
    slog.String("outcome", "success"),
    slog.Int64("duration_ms", duration.Milliseconds()),
)
```

Use this especially in high-frequency code paths.

## Grouping Attributes

Use groups when nested context improves clarity or prevents key collisions.

```go
logger.Info("request finished",
    slog.Group("request",
        slog.String("method", r.Method),
        slog.String("route", "/users/{id}"),
    ),
    slog.Group("auth",
        slog.String("user_id", userID),
        slog.String("actor_type", "user"),
    ),
)
```

Use `WithGroup("http")` or `slog.Group("http", ...)` when multiple subsystems would otherwise reuse keys like `id`, `status`, or `method`.

## Error Logging

Log errors as structured events, not only as formatted strings.

Prefer:

```go
logger.ErrorContext(ctx, "invoice payment failed",
    slog.String("operation", "charge_invoice"),
    slog.String("outcome", "failure"),
    slog.String("error_kind", "payment_gateway_error"),
    slog.String("error_code", "card_declined"),
    slog.String("error_message", "payment provider declined charge"),
    slog.String("user_id", userID),
    slog.Int64("duration_ms", duration.Milliseconds()),
)
```

Guidance:

- prefer stable domain fields like `error_kind` and `error_code`
- keep `error_message` safe and sanitised
- include the raw `error` value only when useful and safe
- avoid logging the same failure at every layer

When you do need the raw error object:

```go
logger.ErrorContext(ctx, "dependency call failed",
    slog.Any("error", err),
    slog.String("dependency", "billing-api"),
)
```

`JSONHandler` formats error-valued attrs as strings.

## Redaction and Sensitive Data

Never log secrets directly.

Use `LogValuer` for type-level redaction:

```go
type Token string

func (Token) LogValue() slog.Value {
    return slog.StringValue("REDACTED")
}
```

Use `ReplaceAttr` for cross-cutting redaction or key normalisation:

```go
opts := &slog.HandlerOptions{
    ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
        if a.Key == "authorization" || a.Key == "token" {
            return slog.String(a.Key, "REDACTED")
        }
        return a
    },
}
```

Prefer type-local redaction with `LogValuer` when the data type itself is sensitive. Use `ReplaceAttr` when you need a handler-wide policy.

## Performance Guidance

- Use `Logger.With(...)` for common attrs instead of repeating them
- Prefer `LogAttrs` in hot paths
- Use typed attrs for common scalar values
- Avoid expensive string formatting before checking whether a level is enabled
- Pass values directly when possible instead of eagerly calling `.String()`
- Use `LogValuer` to defer expensive computation for debug logs

Example:

```go
if logger.Enabled(ctx, slog.LevelDebug) {
    logger.DebugContext(ctx, "computed plan",
        slog.Any("plan", buildDebugPlan(input)),
    )
}
```

Avoid:

```go
logger.DebugContext(ctx, "computed plan",
    slog.String("plan", buildDebugPlan(input).String()),
)
```

if `buildDebugPlan` is expensive and debug logging may be disabled.

## Dynamic Levels

Use `slog.LevelVar` when the level may change at runtime.

```go
var level = new(slog.LevelVar)
level.Set(slog.LevelInfo)

logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: level,
}))
```

If your level comes from config, flags, or environment variables, a small helper is reasonable:

```go
func LevelVarFromString(v string) (*slog.LevelVar, error) {
    var level slog.LevelVar
    if err := level.UnmarshalText([]byte(v)); err != nil {
        return nil, fmt.Errorf("parse log level %q: %w", v, err)
    }
    return &level, nil
}
```

This is appropriate for CLIs, services with admin-configurable verbosity, or temporary incident debugging.

## Bridging the Old `log` Package

If you still have legacy `log.Print` / `log.Printf` calls, you can centralise output with:

```go
slog.SetDefault(logger)
```

That allows the default `log` package to emit through the configured `slog` handler.

Use this only as a deliberate application-wide choice, not as a substitute for dependency injection.

## Testing Guidance

For tests around logging:

- write to a `bytes.Buffer`
- use `ReplaceAttr` to remove or normalise time/source fields
- assert on structured output, not on fragile formatting details
- prefer JSON output in tests when machine-readable assertions are easier

Example:

```go
var buf bytes.Buffer

logger := slog.New(slog.NewJSONHandler(&buf, &slog.HandlerOptions{
    ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
        if a.Key == slog.TimeKey {
            return slog.Attr{}
        }
        return a
    },
}))
```

## Review Checklist

When reviewing Go `slog` usage, check for:

- `log/slog` used consistently instead of mixed ad-hoc logging styles
- base logger created centrally at startup
- stable common attrs attached with `With(...)`
- shared schema aligned with the `structured-logging` skill
- `ReplaceAttr` used when canonical key renaming is needed
- `InfoContext` / `ErrorContext` used when context already exists
- `LogAttrs` used in hot paths where it matters
- structured error fields instead of only formatted strings
- redaction for secrets and sensitive values
- no repeated noisy logs for the same failure across layers
- JSON logs used for production ingestion

## Anti-Patterns

Avoid these unless there is a strong reason:

- logging with `fmt.Sprintf` into one giant string
- using `slog.Any` for everything when typed attrs are clearer
- eagerly computing expensive debug fields when debug is disabled
- forcing every function to call `slog.Default()`
- burying the logger in context as a universal service locator
- logging secrets, tokens, or raw auth headers
- leaving built-in keys as `time`/`msg` when the rest of the platform expects `timestamp`/`message`
- emitting text logs in production when downstream systems expect JSON
- logging every internal function call instead of boundary summaries

## Quick Template

```go
level := new(slog.LevelVar)
level.Set(slog.LevelInfo)

logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: level,
    ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
        switch a.Key {
        case slog.TimeKey:
            a.Key = "timestamp"
        case slog.MessageKey:
            a.Key = "message"
        }
        return a
    },
})).With(
    slog.String("service", "users-api"),
    slog.String("environment", "production"),
    slog.String("application_version", "1.0.0"),
    slog.String("application_commit", "abcdef12"),
)

logger.Info("user authenticated",
    slog.String("request_id", requestID),
    slog.String("trace_id", traceID),
    slog.String("user_id", userID),
    slog.String("operation", "login"),
    slog.String("outcome", "success"),
    slog.Int64("duration_ms", duration.Milliseconds()),
)
```
