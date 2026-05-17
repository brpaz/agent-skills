---
name: application-healthchecks
version: "1.0.0"
description: "Design web app and API health checks with RFC-style JSON responses, probe separation, and production-safe dependency policies."
tags: [healthcheck, api, web, kubernetes, observability, sre]
---

# Healthcheck - Web App and API Health Specifications

Use this skill when designing, implementing, or reviewing health endpoints for HTTP services, web applications, BFFs, and APIs.

## When to Use

- Adding or refactoring `/livez`, `/readyz`, or `/healthz` endpoints
- Standardising health response payloads across services
- Configuring Kubernetes, load balancer, or platform health probes
- Deciding which dependencies should affect liveness vs readiness
- Reviewing health endpoints for security, reliability, or operational safety

## Standards Position

- The closest IETF specification is **`draft-inadarei-api-health-check`**: *Health Check Response Format for HTTP APIs*
- It is an **expired Internet-Draft, not a published RFC**
- It is still the most widely cited structured format for HTTP API health responses
- If you want a standards-aligned JSON shape, use its field names and media type: **`application/health+json`**

## Health Check Model

Treat health checks as separate concerns:

- **Liveness** - Should this process be restarted?
- **Readiness** - Should this instance receive traffic right now?
- **Health summary** - What is the operator-facing overall state and why?

### Meaning of Each Probe

#### Liveness

Liveness should answer only: **is the process alive and able to make forward progress?**

Good liveness signals:

- Main event loop or worker threads are responsive
- The process is not deadlocked
- The app can serve a trivial in-process check

Bad liveness signals:

- Database reachability
- Redis reachability
- Third-party API reachability
- Full end-to-end business flows

**Rule:** liveness should be cheap, local, and independent of external systems.

#### Readiness

Readiness should answer: **can this instance successfully serve its current traffic?**

Good readiness signals:

- Critical request path dependencies are reachable
- Connection pools are usable
- Required configuration is loaded
- App is not draining, overloaded, or in maintenance mode

Readiness may temporarily fail without restarting the process.

## Recommended Endpoint Layout

For non-trivial services, prefer distinct endpoints:

- `GET /livez`
- `GET /readyz`
- `GET /healthz`

### Endpoint Semantics

| Endpoint | Primary consumer | Meaning | Should check external deps? |
|---|---|---|---|
| `/livez` | kubelet / runtime | process is alive | **No** |
| `/readyz` | kubelet / LB | instance can receive traffic | **Yes, critical deps only** |
| `/healthz` | operators / tooling | structured aggregate view | **Yes, as needed** |

### Path Guidance

- Use stable, memorable paths
- Avoid redirects
- Avoid HTML responses
- Avoid authentication on internal probe endpoints used by infrastructure
- If detailed health is sensitive, expose:
  - a **minimal** probe endpoint for infrastructure, and
  - a **detailed** health endpoint for operators behind auth or internal networking

If you can expose only one endpoint, use `/healthz` and document exactly whether it behaves like readiness or aggregate health.

## RFC-Style Response Format

When returning structured JSON, prefer:

- `Content-Type: application/health+json`

### Top-Level Fields

The draft defines:

- `status` **(required)** - `pass`, `warn`, or `fail`
- `version` - public service/API version
- `releaseId` - deploy/build/release identifier
- `notes` - array of human-readable notes
- `output` - error/degradation output; omit for `pass`
- `checks` - detailed dependency/sub-component checks
- `links` - related URIs
- `serviceId` - unique service identifier in application scope
- `description` - human-readable service description

### Status Values

- `pass` - healthy
- `warn` - degraded but still serving
- `fail` - unhealthy

The Internet-Draft allows aliases like `ok`, `up`, `error`, and `down` for ecosystem compatibility, but prefer the canonical values:

- **Use `pass`**
- **Use `warn`**
- **Use `fail`**

### Minimal Example

```http
HTTP/1.1 200 OK
Content-Type: application/health+json
Cache-Control: no-store

{
  "status": "pass"
}
```

### Detailed Example

```json
{
  "status": "warn",
  "version": "v1",
  "releaseId": "2026.05.17-1",
  "serviceId": "billing-api",
  "description": "Billing API health",
  "notes": [
    "running in degraded mode"
  ],
  "checks": {
    "postgres:responseTime": [
      {
        "componentId": "primary",
        "componentType": "datastore",
        "observedValue": 380,
        "observedUnit": "ms",
        "status": "warn",
        "time": "2026-05-17T12:00:00Z",
        "output": "latency above SLO"
      }
    ]
  }
}
```

## HTTP Status Code Guidance

The IETF draft ties body status to HTTP status classes:

- `pass` -> HTTP **2xx-3xx**
- `warn` -> HTTP **2xx-3xx**
- `fail` -> HTTP **4xx-5xx**

In practice, use these defaults:

- **`200 OK`** for `pass`
- **`200 OK`** for `warn` when the instance should still receive traffic
- **`503 Service Unavailable`** for `fail` when the instance must be removed from traffic

### Practical Rule

- If the platform should **keep routing traffic**, return **2xx**
- If the platform should **stop routing traffic or mark probe failed**, return **non-2xx**

### Prefer `503` for Expected Unavailability

Use `503` instead of `500` when the problem means “temporarily unable to serve traffic”, such as:

- database unavailable
- dependency timeout
- app not yet ready
- maintenance/drain mode

Avoid returning `200` with a hidden failure in the body if infrastructure must act on the failure.

## The `checks` Object

Use `checks` for dependency-level or subsystem-level detail.

### Shape

- Keys should identify the check, ideally as `componentName:measurementName`
- Values should be arrays
- For single-node dependencies, use a single-element array for consistency

### Per-Check Fields

Useful standard fields from the draft:

- `componentId`
- `componentType`
- `observedValue`
- `observedUnit`
- `status`
- `affectedEndpoints`
- `time`
- `output`
- `links`

### Good Uses of `checks`

- DB connection latency
- queue depth
- cache hit rate or connectivity
- dependency timeout state
- disk pressure or memory pressure
- partial endpoint impact via `affectedEndpoints`

### Dependency Classification

Classify dependencies before wiring them into health:

- **Hard dependency** - must work for core traffic -> affects readiness
- **Soft dependency** - degraded experience but service still works -> report `warn`, usually not readiness fail
- **Observability/admin dependency** - metrics, tracing, analytics -> do not fail readiness or liveness

## Best Practices for Dependency Checks

### Keep Probes Cheap

- Use lightweight checks (`ping`, `SELECT 1`, pool health, shallow RPC)
- Avoid full business transactions
- Avoid writes
- Avoid expensive fan-out trees

### Bound Time Aggressively

- Every dependency check needs a timeout
- Dependency timeout should be **shorter than** the platform probe timeout
- Prefer parallel checks with a global budget

### Avoid Cascading Failure

- Do not let health checks overload a failing dependency
- Consider cached or sampled dependency results for expensive checks
- Do not retry aggressively inside the health endpoint
- Fail fast rather than queueing many outbound checks under load

### Be Explicit About Partial Failure

If only part of the API is degraded:

- return `warn` if the instance can still serve traffic safely
- include `affectedEndpoints` for impacted routes when useful
- avoid failing readiness unless the degraded dependency blocks the instance's main traffic class

## Web Application Guidance

### Server-Rendered Apps / BFFs / API-Backed Web Apps

Treat them like APIs:

- `/livez` checks process health only
- `/readyz` checks critical backends needed to serve user traffic
- `/healthz` can provide detailed operator state

### Static Sites and CDN-Served Frontends

Do not treat browser rendering as a normal readiness probe.

Instead check:

- origin reachability
- edge/CDN configuration health
- deployment artifact presence
- optional synthetic monitoring outside the probe path

Synthetic browser journeys are useful for observability, but they are **not** replacements for low-cost platform health probes.

## Kubernetes and Platform Mapping

Recommended mapping:

```yaml
livenessProbe:
  httpGet:
    path: /livez
    port: 8080

readinessProbe:
  httpGet:
    path: /readyz
    port: 8080
```

### Probe Semantics

- **Liveness failure** restarts the container
- **Readiness failure** removes the instance from service traffic without killing it

### Probe Design Rules

- Do not make liveness and readiness identical unless the service is truly trivial
- Readiness may depend on critical downstream systems
- Liveness should remain local to the process

## Security and Exposure

Health endpoints often leak valuable attacker information if left unchecked.

### Public vs Internal Output

For public exposure, keep responses minimal:

```json
{ "status": "pass" }
```

For internal/operator use, add detailed `checks`, `output`, versions, links, and dependency metadata.

### Never Expose

- secrets or tokens
- connection strings
- internal hostnames unless clearly intended
- stack traces
- raw SQL errors
- detailed topology unless operationally required

### Access Control Guidance

- Infrastructure probe endpoints usually should not require end-user auth
- Detailed `/healthz` endpoints may require internal networking, auth, or RBAC
- Rate-limit or isolate public health endpoints if abuse is a concern

## Caching and Transport

The Internet-Draft discusses explicit freshness lifetimes for health responses.

Operationally:

- For **real-time probes** (`/livez`, `/readyz`, `/healthz`), prefer **`Cache-Control: no-store`**
- Do not place probe endpoints behind caches or CDNs that can hide current state
- For **operator-oriented aggregate health documents**, explicit short caching may be acceptable if the consumers understand the freshness model

Always serve health endpoints over the same trusted transport expectations as the service itself.

## Common Anti-Patterns

- Using one expensive endpoint for liveness, readiness, dashboards, and external monitoring
- Making liveness depend on the database
- Returning `200` for everything and expecting tooling to parse custom fields
- Performing writes, migrations, or side effects inside probe handlers
- Running deep dependency trees on every probe
- Exposing sensitive diagnostics to the public Internet
- Making readiness fail because a non-critical dependency is slow
- Using browser synthetic checks as the only production health signal

## Rules

- **ALWAYS separate liveness and readiness** for non-trivial services.
- **ALWAYS keep liveness local, cheap, and dependency-free.**
- **ALWAYS use `application/health+json`** when returning structured RFC-style responses.
- **ALWAYS use `pass`, `warn`, and `fail`** as the canonical body states.
- **ALWAYS return non-2xx** when you need infrastructure to stop routing traffic.
- **ALWAYS bound dependency checks with strict timeouts.**
- **ALWAYS keep public health responses minimal.**
- **NEVER make liveness depend on external systems.**
- **NEVER perform writes or side effects in a health endpoint.**
- **NEVER expose secrets, stack traces, or sensitive topology in health output.**
- **NEVER let health checks become a source of cascading failure.**

## Quick Reference

| Concern | Recommendation |
|---|---|
| Body media type | `application/health+json` |
| Body status values | `pass`, `warn`, `fail` |
| Pass HTTP code | `200` |
| Warn HTTP code | `200` if still routable |
| Fail HTTP code | `503` by default |
| Liveness dependencies | none external |
| Readiness dependencies | critical serving dependencies only |
| Public endpoint detail | minimal |
| Internal endpoint detail | rich `checks` object |

## Example Endpoint Set

### `/livez`

```json
{ "status": "pass" }
```

Checks only process-local health.

### `/readyz`

```json
{
  "status": "fail",
  "output": "database unavailable",
  "checks": {
    "postgres:connections": [
      {
        "componentType": "datastore",
        "status": "fail",
        "time": "2026-05-17T12:00:00Z",
        "output": "dial timeout"
      }
    ]
  }
}
```

Return this with **`503 Service Unavailable`**.

### `/healthz`

```json
{
  "status": "warn",
  "releaseId": "2026.05.17-1",
  "notes": ["serving traffic with elevated latency"],
  "checks": {
    "redis:responseTime": [
      {
        "componentType": "datastore",
        "observedValue": 120,
        "observedUnit": "ms",
        "status": "warn",
        "time": "2026-05-17T12:00:00Z"
      }
    ]
  }
}
```

Return this with **`200 OK`** if the instance should remain in rotation.

## Resources

- [Health Check Response Format for HTTP APIs (IETF Internet-Draft)](https://datatracker.ietf.org/doc/html/draft-inadarei-api-health-check)
- [Kubernetes: Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Kubernetes API Reference: Probe](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#probe-v1-core)

## Inputs

- Service type and traffic model (API, SSR app, BFF, static frontend, worker)
- Critical and non-critical dependencies
- Platform/orchestrator expectations (Kubernetes, ECS, load balancer, uptime monitor)
- Desired public vs internal health visibility

## Outputs

- A health endpoint design with clear liveness/readiness/aggregate-health semantics
- RFC-style JSON response schemas for minimal and detailed health responses
- Safe dependency rules and status code mappings appropriate for production
