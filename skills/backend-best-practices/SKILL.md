---
name: backend-best-practices
description: Personal backend engineering principles covering API design and testing. Stack-agnostic. Load this skill when designing APIs, writing tests, reviewing backend code, or building new endpoints. Triggers on tasks involving REST API design, endpoint creation, pagination, HTTP status codes, input validation, integration testing, or test strategy decisions.
license: MIT
metadata:
  author: bruno
  version: "1.0.0"
---

# Backend Best Practices

Personal backend engineering guidelines. Stack-agnostic — applies to any language or framework.
Covers two domains: **API Design** and **Testing**.

## When to Apply

Reference these guidelines when:
- Designing or reviewing REST API endpoints
- Deciding on response shapes, status codes, or URL structure
- Writing any kind of backend tests
- Deciding what and how to test (unit vs integration, mock strategy)
- Adding pagination to list endpoints
- Handling input validation at any layer

## Domains

| Domain | Key Principles |
|--------|---------------|
| API Design | Strict REST semantics, URL versioning, boundary validation, always paginate lists |
| Testing | Behavior-focused, integration-first, minimal mocking |

## Quick Reference

### API Design
- `api-rest-semantics` — Use resource-based URLs and proper HTTP verbs
- `api-url-versioning` — Version in URL path (`/v1/`)
- `api-boundary-validation` — Validate all input at the entry point
- `api-paginate-always` — All list endpoints are paginated from day one

### Testing
- `test-behavior-not-impl` — Test what the code does, not how it does it
- `test-integration-first` — Prefer integration tests over unit tests
- `test-minimal-mocking` — Only mock at external I/O boundaries

## Full Guide

For the complete expanded guide: `AGENTS.md`
