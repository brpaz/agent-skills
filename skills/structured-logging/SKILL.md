---
name: structured-logging
version: "1.0.0"
description: "Design language-agnostic structured logs with consistent fields, correlation IDs, safe context, and production-ready observability guidance."
tags: [logging, observability, structured-logging, json, monitoring]
---

# Structured Logging - Language-Agnostic Production Guidance

Use this skill when designing, implementing, reviewing, or standardising application logs. It focuses on structured, machine-parseable logs that are consistent across services, safe for production, and useful for debugging, alerting, auditing, and observability.

## When to Use

- Introducing structured logging to a service or application
- Standardising log fields across multiple services or languages
- Reviewing logs for consistency, safety, or observability quality
- Designing application, HTTP, job, worker, or integration logs
- Defining log schemas for production, staging, and local environments

## Default Logging Stance

Unless there is a clear reason not to, prefer these defaults:

- Emit **structured logs**, not free-form text logs
- Prefer **JSON logs in production** for machine parsing and ingestion
- Keep **one event per log line**
- Use a **stable field schema** across all services
- Include **core metadata on every log event**
- Use **message for the human summary**, and fields for the actual data
- Include **correlation identifiers** so events can be traced across systems
- Log **meaningful business and operational events**, not every line of execution
- Avoid secrets, tokens, passwords, and sensitive personal data

## Core Principles

- **Structured over interpolated** - Put data in fields, not in string formatting
- **Consistent over clever** - Reuse the same key names everywhere
- **Contextual over noisy** - Add the fields needed to understand the event
- **Operationally useful** - Logs should support debugging, alerting, and auditing
- **Safe by default** - Never rely on downstream systems to redact sensitive data
- **Correlatable** - Every important flow should be traceable across services
- **Low-cardinality by default** - Avoid fields that explode log volume or index cost unless they are truly needed

## Preferred Formats

### Production

- Prefer **JSON**
- Use UTF-8
- Emit one JSON object per line
- Keep keys stable and predictable

Example:

```json
{
  "timestamp": "2026-05-17T14:22:03.481Z",
  "level": "info",
  "message": "user authenticated",
  "service": "auth-api",
  "environment": "production",
  "application_version": "1.14.2",
  "application_commit": "a1b2c3d4",
  "request_id": "req_123",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "user_id": "usr_456",
  "operation": "login",
  "outcome": "success",
  "duration_ms": 42
}
```

### Local Development

- JSON is still preferred when consistency matters
- Pretty logs are acceptable locally if they preserve the same fields
- Do not let local-only formatting change the semantic schema

## Canonical Field Naming

Pick one naming style and keep it consistent across all services.

Recommended default:

- `snake_case` for portability across languages and vendors

Examples:

- `request_id`
- `trace_id`
- `application_version`
- `duration_ms`

Avoid mixing styles like `requestId`, `request_id`, and `request-id` in the same platform.

## Common Log Attributes

### Core Attributes (prefer on every event)

| Field | Purpose | Notes |
|---|---|---|
| `timestamp` | When the event happened | Use RFC3339/ISO8601 in UTC |
| `level` | Severity of the event | Prefer `debug`, `info`, `warn`, `error` |
| `message` | Human-readable event summary | Short, stable, descriptive |
| `service` | Service/application name | Stable logical service name |
| `environment` | Runtime environment | `local`, `test`, `staging`, `production` |
| `application_version` | Release or app version | Semver, release ID, or build version |
| `application_commit` | Source revision | Git SHA or equivalent |

### Correlation Attributes

Use when available so related logs can be joined:

| Field | Purpose |
|---|---|
| `request_id` | Request-scoped correlation ID |
| `correlation_id` | Cross-system correlation ID when request ID is insufficient |
| `trace_id` | Distributed trace identifier |
| `span_id` | Trace span identifier |
| `session_id` | End-user or workflow session identifier |

### Actor and Tenant Attributes

Use when relevant and permitted by privacy policy:

| Field | Purpose |
|---|---|
| `user_id` | Authenticated or subject user identifier |
| `account_id` | Account identifier |
| `tenant_id` | Multi-tenant partition identifier |
| `organization_id` | Organisation/workspace identifier |
| `actor_type` | `user`, `system`, `job`, `admin`, etc. |

### Execution Context Attributes

| Field | Purpose |
|---|---|
| `operation` | Logical operation name such as `login`, `sync_account`, `process_invoice` |
| `component` | Subsystem or module name |
| `event` | More specific event identifier if useful |
| `outcome` | `success`, `failure`, `retry`, `timeout`, etc. |
| `duration_ms` | Duration in milliseconds |
| `attempt` | Retry attempt number |

### Infrastructure Attributes

| Field | Purpose |
|---|---|
| `host` | Hostname or node name |
| `instance_id` | Runtime instance/container identifier |
| `region` | Deployment region |
| `zone` | Availability zone |
| `runtime` | Language/runtime info if helpful |
| `pid` | Process ID when relevant |

### Error Attributes

Include on warnings/errors when relevant:

| Field | Purpose |
|---|---|
| `error_kind` | Stable error class or type |
| `error_code` | Domain or platform error code |
| `error_message` | Sanitised error summary |
| `stack_trace` | Stack trace for unexpected failures |
| `cause` | High-level root cause or dependency |

### Protocol-Specific Attributes

Use only when the event involves that protocol or subsystem.

HTTP examples:

- `http_method`
- `http_route`
- `http_status_code`
- `client_ip` only if allowed and necessary
- `user_agent` only if needed and safe to store

Database examples:

- `db_system`
- `db_operation`
- `db_table`
- `rows_affected`

Messaging/job examples:

- `job_name`
- `job_id`
- `queue`
- `topic`
- `partition`
- `offset`

## Required vs Contextual Fields

Do not force every log line to contain every possible field.

Prefer this model:

- **Required everywhere**: `timestamp`, `level`, `message`, `service`, `environment`, `application_version`, `application_commit`
- **Required when available in request flows**: `request_id`, `trace_id`, `span_id`
- **Required when an authenticated actor is present**: `user_id` or equivalent actor identifier
- **Required on timed operations**: `duration_ms`
- **Required on failures**: `error_kind` and/or `error_code`, plus a safe `error_message`
- **Contextual only**: protocol, domain, infrastructure, and payload-specific fields

## Message Design

The `message` field should be short and human-readable.

Good:

- `user authenticated`
- `invoice payment failed`
- `cache refresh completed`
- `http request completed`

Bad:

- `User authenticated successfully for user usr_123 from IP 10.0.0.4 in 42ms`
- `step 4 done`
- `something happened`

Rule:

- Put the summary in `message`
- Put identifiers, durations, and details in structured fields

## Severity Levels

Prefer a small, standard level set:

- `debug` - Developer-focused diagnostic detail
- `info` - Normal lifecycle and business events
- `warn` - Unexpected but handled conditions
- `error` - Failures that need attention or impact behaviour

Use `fatal` only if the process will actually terminate immediately and that distinction matters in your platform.

Avoid inventing custom levels unless your tooling requires them.

## What to Log

### Good Candidates

- Service start/stop
- Deployment/build metadata on startup
- Request completion summaries
- Authentication and authorisation events
- Background job start/finish/failure
- Calls to external dependencies that fail or are slow
- Retries, circuit-breaker opens, and timeouts
- Domain events that matter operationally or for audit trails
- Data validation failures that matter to system behaviour

### Usually Not Worth Logging

- Every function entry/exit in production
- Large raw payloads by default
- Duplicate logs for the same failure at multiple layers
- High-frequency heartbeat noise unless aggregated or sampled
- Implementation trivia that adds no debugging or operational value

## Errors and Exceptions

Log errors as structured events.

Prefer:

```json
{
  "timestamp": "2026-05-17T14:25:10.112Z",
  "level": "error",
  "message": "invoice payment failed",
  "service": "billing-worker",
  "environment": "production",
  "application_version": "1.14.2",
  "application_commit": "a1b2c3d4",
  "job_name": "charge_invoice",
  "job_id": "job_789",
  "user_id": "usr_456",
  "operation": "charge_invoice",
  "outcome": "failure",
  "error_kind": "payment_gateway_error",
  "error_code": "card_declined",
  "error_message": "payment provider declined charge",
  "duration_ms": 812
}
```

Guidance:

- Prefer stable `error_kind` / `error_code` values for alerting and grouping
- Keep `error_message` safe and sanitised
- Include stack traces for unexpected failures, not for every handled business error
- Avoid logging the same error repeatedly at multiple layers unless each layer adds distinct context

## Correlation and Traceability

Every request, job, or workflow should be traceable.

Prefer propagating:

- `request_id`
- `correlation_id`
- `trace_id`
- `span_id`

Rules:

- Generate missing IDs at ingress boundaries
- Propagate them across service boundaries
- Add them automatically through logging context/middleware if the platform supports it
- Ensure downstream services log the same identifiers

## Privacy and Security Rules

Never log:

- Passwords
- Access tokens
- Refresh tokens
- API keys
- Private keys
- Session secrets
- Raw authentication headers
- Full payment card data
- Sensitive personal data unless explicitly required and approved

Prefer:

- Redaction over omission when the field must exist
- Hashing or tokenising identifiers when raw values are too sensitive
- Logging references or IDs instead of full payloads
- Separate audit logs when regulatory requirements differ from operational logs

If in doubt, do not log it.

## Cardinality and Cost Control

Structured logs can become expensive and hard to query when fields are too dynamic.

Avoid or minimise:

- Arbitrary dynamic field names
- Full payload dumps
- Very large arrays or nested objects
- Unique values in indexed fields unless truly necessary

Prefer:

- Stable key names
- Small, targeted fields
- Sampling for extremely noisy debug flows
- Separate verbose diagnostic logging from normal production logging

## Event Patterns

### Request Completion Log

Prefer a single summary event near the boundary:

```json
{
  "timestamp": "2026-05-17T14:30:00.000Z",
  "level": "info",
  "message": "http request completed",
  "service": "users-api",
  "environment": "production",
  "application_version": "2.3.0",
  "application_commit": "9f8e7d6c",
  "request_id": "req_abc",
  "trace_id": "trace_xyz",
  "user_id": "usr_123",
  "http_method": "GET",
  "http_route": "/users/{id}",
  "http_status_code": 200,
  "duration_ms": 18,
  "outcome": "success"
}
```

### Background Job Log

```json
{
  "timestamp": "2026-05-17T14:31:00.000Z",
  "level": "warn",
  "message": "job retry scheduled",
  "service": "sync-worker",
  "environment": "production",
  "application_version": "2.3.0",
  "application_commit": "9f8e7d6c",
  "job_name": "sync_account",
  "job_id": "job_123",
  "account_id": "acct_456",
  "attempt": 2,
  "outcome": "retry",
  "error_kind": "timeout",
  "duration_ms": 30000
}
```

## Review Checklist

When reviewing structured logging, check for:

- Structured output instead of raw string concatenation
- Stable field names across services
- Core attributes present on every event
- `service`, `application_version`, and `application_commit` consistently populated
- Correlation IDs propagated through request/job boundaries
- `user_id` or actor identifiers logged where appropriate and allowed
- Error logs with structured error fields instead of only raw stack dumps
- No secrets or sensitive payloads in logs
- Sensible levels and no excessive noise
- Query-friendly schema with bounded cardinality
- Request/job completion summaries logged at system boundaries

## Anti-Patterns

Avoid these unless there is a strong reason:

- Plain text logs with embedded values instead of fields
- Inconsistent keys for the same concept across services
- Logging and re-logging the same error at every layer
- Logging full request/response bodies by default
- Logging secrets or regulated data
- Using log messages as the only structured signal
- Missing release/build metadata in production logs
- Custom severity taxonomies nobody remembers
- Logging too little context to debug incidents
- Logging so much detail that important signals disappear

## Quick Template

Use this as a baseline event shape:

```json
{
  "timestamp": "2026-05-17T14:22:03.481Z",
  "level": "info",
  "message": "descriptive event summary",
  "service": "service-name",
  "environment": "production",
  "application_version": "1.0.0",
  "application_commit": "abcdef12",
  "request_id": "optional-request-id",
  "trace_id": "optional-trace-id",
  "span_id": "optional-span-id",
  "user_id": "optional-user-id",
  "operation": "optional-operation",
  "outcome": "optional-success-or-failure",
  "duration_ms": 0,
  "error_kind": "optional-error-kind",
  "error_code": "optional-error-code",
  "error_message": "optional-sanitised-error-message"
}
```
