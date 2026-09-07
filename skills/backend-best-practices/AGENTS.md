# Backend Best Practices

**Version 1.0.0**
Personal Engineering Principles
February 2026

> This document is for agents and LLMs to follow when building, reviewing, or refactoring backend code.
> Principles are stack-agnostic and apply regardless of language or framework.

---

## Table of Contents

1. [API Design](#1-api-design)
   - 1.1 [Strict REST Semantics](#11-strict-rest-semantics)
   - 1.2 [URL Versioning](#12-url-versioning)
   - 1.3 [Boundary Validation](#13-boundary-validation)
   - 1.4 [Always Paginate Lists](#14-always-paginate-lists)
2. [Testing](#2-testing)
   - 2.1 [Test Behavior, Not Implementation](#21-test-behavior-not-implementation)
   - 2.2 [Integration-First Testing](#22-integration-first-testing)
   - 2.3 [Minimal Mocking](#23-minimal-mocking)

---

## 1. API Design

### 1.1 Strict REST Semantics

Use resource-based URLs and correct HTTP verbs. URLs identify resources (nouns). HTTP verbs express the action.

**Verb → Action mapping:**

| Verb | Semantics | Idempotent |
|------|-----------|------------|
| GET | Fetch resource(s) | Yes |
| POST | Create a new resource | No |
| PUT | Replace resource entirely | Yes |
| PATCH | Partially update resource | No |
| DELETE | Remove resource | Yes |

**Incorrect:**

```
POST /getUser
GET  /createPost
POST /deleteComment/42
GET  /updateProfile?name=Alice
```

**Correct:**

```
GET    /v1/users/:id
POST   /v1/posts
DELETE /v1/comments/:id
PATCH  /v1/users/:id
```

**Status codes — use them correctly:**

| Code | When to use |
|------|-------------|
| 200 | Successful GET, PATCH, PUT |
| 201 | Successful POST that created a resource |
| 204 | Successful DELETE or action with no response body |
| 400 | Client sent invalid input (malformed, missing fields) |
| 401 | Not authenticated |
| 403 | Authenticated but not authorized |
| 404 | Resource not found |
| 409 | Conflict (e.g. duplicate unique field) |
| 422 | Valid format but semantically invalid (e.g. business rule violation) |
| 429 | Rate limited |
| 500 | Unexpected server error |

**Error response shape — be consistent:**

Always return errors in a stable, machine-readable shape. Pick one and stick to it across the entire API.

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "email is required",
    "fields": {
      "email": "required"
    }
  }
}
```

- `code`: machine-readable string constant (screaming snake case)
- `message`: human-readable description
- `fields`: optional, maps field name → error when applicable

**Naming conventions:**

- URLs: lowercase, hyphen-separated (`/user-profiles`, not `/userProfiles`)
- Query params: camelCase or snake_case — pick one, never mix
- Response body keys: camelCase (JSON convention)

---

### 1.2 URL Versioning

Version the API in the URL path. This is the simplest, most explicit, and most tooling-friendly approach.

**Correct:**

```
/v1/users
/v1/posts/:id
/v2/users   ← new version when breaking changes are needed
```

**Rules:**

- Start at `/v1/` from day one, even for internal-only APIs
- Increment major version only for breaking changes (removed fields, changed types, changed semantics)
- Additive changes (new optional fields, new endpoints) do NOT require a version bump
- Keep old versions alive long enough for consumers to migrate — communicate deprecation clearly
- Do not use minor versions in the URL (`/v1.1/`) — if it's breaking, it's v2

**What counts as a breaking change:**

- Removing a field from a response
- Changing a field's type or format
- Changing the meaning of a status code
- Renaming a required request field
- Changing authentication requirements

**What is NOT a breaking change:**

- Adding a new optional field to a response
- Adding a new endpoint
- Adding a new optional query parameter
- Adding a new optional request field

---

### 1.3 Boundary Validation

Validate all incoming data at the entry point — the handler or controller layer — before it touches any business logic, service, or database.

**Why at the boundary:**

- Keeps business logic clean and free of defensive checks
- Provides a single, consistent place to look for input rules
- Fails fast with a clear 400 before wasting any downstream resources

**What to validate:**

- Required fields are present
- Types match (string, number, boolean, array)
- Format constraints (email, UUID, ISO date, URL)
- Range constraints (min/max length, min/max value)
- Enum membership (value is one of the allowed options)

**Validation must happen in the handler, not deep in a service:**

```
// Incorrect: validation buried in service layer
function createUser(data) {
  const user = userService.create(data)  // service does its own checks internally
}

// Correct: validate at the boundary, pass clean data downstream
function createUser(data) {
  const validated = validate(data, CreateUserSchema)  // throws 400 on failure
  const user = userService.create(validated)          // service trusts the input
}
```

**Never trust input from any external source:**

- HTTP request bodies
- Query parameters
- Path parameters
- Headers used as input
- Webhook payloads
- Messages from queues

**Do NOT re-validate the same data in multiple layers.** Validate once at the boundary, then pass the validated type downstream. Downstream code should trust that it received valid input — if it doesn't, that's an internal contract violation (use assertions or types, not runtime validation).

---

### 1.4 Always Paginate Lists

Any endpoint that returns a collection must be paginated from day one. Returning unbounded lists is a performance time-bomb and breaks clients when data grows.

**Why from day one:**

- Adding pagination later is a breaking change for clients
- Unbounded queries will eventually kill your database
- Clients that assume a full list will silently miss data after pagination is added

**Preferred approach — cursor-based pagination:**

Cursor pagination is stable, efficient, and works correctly when records are inserted or deleted between pages.

```json
GET /v1/posts?limit=20&cursor=eyJpZCI6IjEyMyJ9

{
  "data": [...],
  "pagination": {
    "nextCursor": "eyJpZCI6IjE0MyJ9",
    "hasMore": true
  }
}
```

- `cursor`: opaque string (base64-encoded pointer to the last seen record)
- `limit`: number of items to return (enforce a max, e.g. 100)
- `nextCursor`: null or absent when there are no more pages
- `hasMore`: boolean for convenience

**When offset pagination is acceptable:**

Use offset pagination only when the UI genuinely needs random page access (e.g. "jump to page 5") and the dataset is bounded and infrequently mutated.

```json
GET /v1/users?page=3&pageSize=25

{
  "data": [...],
  "pagination": {
    "page": 3,
    "pageSize": 25,
    "total": 312,
    "totalPages": 13
  }
}
```

**Hard rules:**

- Always enforce a maximum `limit` / `pageSize` (e.g. 100). Never allow the client to request unlimited items
- Always return pagination metadata in the response, even on the first page
- Default `limit` if not provided — never return all records as a default
- If `total` is expensive to compute (e.g. large tables), omit it and use `hasMore` instead

---

## 2. Testing

### 2.1 Test Behavior, Not Implementation

Tests should assert what the system does, not how it does it internally. A test that breaks when you refactor internals without changing behavior is a bad test.

**What "behavior" means:**

- Given this input, the output is X
- Given this state, calling Y produces side effect Z
- Given invalid input, the error response has shape W

**What "implementation" means:**

- This function calls that other function
- This private method was invoked with these arguments
- This internal variable holds this value

**Incorrect — testing implementation:**

```javascript
// Tests that a specific internal method was called
it('calls hashPassword when creating a user', async () => {
  const spy = jest.spyOn(bcrypt, 'hash')
  await createUser({ email: 'a@b.com', password: 'secret' })
  expect(spy).toHaveBeenCalledWith('secret', 10)
})
```

This test breaks if you swap bcrypt for argon2 — even if the behavior (password is hashed) is identical.

**Correct — testing behavior:**

```javascript
// Tests the observable outcome
it('stores a hashed password, not the plain text', async () => {
  await createUser({ email: 'a@b.com', password: 'secret' })
  const user = await db.users.findOne({ email: 'a@b.com' })
  expect(user.password).not.toBe('secret')
  expect(user.password).toMatch(/^\$argon2|\$2[aby]/)  // looks like a hash
})
```

**Corollaries:**

- Don't assert on private methods or internal state
- Don't test that a function was called — test what changed as a result
- If you can refactor the internals and the tests still pass, the tests are good
- If tests break on a refactor that didn't change behavior, delete or rewrite those tests

**Structure tests with AAA (Arrange-Act-Assert):**

```javascript
it('returns 404 when the user does not exist', async () => {
  // Arrange
  const nonExistentId = '00000000-0000-0000-0000-000000000000'

  // Act
  const response = await request(app).get(`/v1/users/${nonExistentId}`)

  // Assert
  expect(response.status).toBe(404)
  expect(response.body.error.code).toBe('USER_NOT_FOUND')
})
```

---

### 2.2 Integration-First Testing

Prefer integration tests over unit tests. An integration test exercises multiple real components together — the handler, service, database, and any middleware. Unit tests isolate a single function in complete isolation.

**Why integration-first:**

- Tests the thing that actually runs in production
- Catches bugs at the seams between layers (the most common failure point)
- One integration test can replace dozens of unit tests with higher confidence
- Refactoring internals doesn't break integration tests

**What an integration test looks like for a backend:**

```javascript
it('creates a user and returns 201 with the new user id', async () => {
  const response = await request(app)
    .post('/v1/users')
    .send({ email: 'alice@example.com', name: 'Alice' })

  expect(response.status).toBe(201)
  expect(response.body.data.id).toBeDefined()

  // Verify persistence — the record actually exists
  const user = await db.users.findOne({ id: response.body.data.id })
  expect(user.email).toBe('alice@example.com')
})
```

This single test exercises: routing, middleware, validation, business logic, and the database layer.

**When to write a unit test instead:**

Unit tests are appropriate for:
- Pure functions with complex logic (e.g. a pricing calculator, a parser)
- Utility functions called from many places
- Edge cases that are hard to set up via integration (e.g. clock-dependent logic)
- Logic that is too slow or side-effectful to test via integration (e.g. sending emails)

**The test pyramid — inverted for backends:**

For typical CRUD-heavy backends, the ideal split is closer to:

```
        [ E2E / Contract ]   (few — slow, high cost)
      [ Integration Tests ]   (most — real DB, real app)
    [    Unit Tests       ]   (few — pure logic only)
```

This is the opposite of the classic pyramid. For backend services, integration tests give the best return on test-writing effort.

**Database setup:**

- Use a real database (even in CI). SQLite in-memory, Postgres in Docker, or a test schema are all fine.
- Run migrations before tests. Don't manually create tables in test setup.
- Isolate tests: reset or truncate tables between tests (or use transactions that are rolled back).
- Seed only what the test needs — avoid large shared fixtures.

---

### 2.3 Minimal Mocking

Mock only at external I/O boundaries that you don't own or that cause unacceptable test slowness/side effects. Mock nothing else.

**What to mock (external boundaries):**

- Third-party HTTP APIs (Stripe, SendGrid, Twilio, etc.)
- External message queues or pub/sub systems you don't control
- Filesystem operations in tests that run in environments without disk access
- The system clock (`Date.now()`, `new Date()`) when testing time-sensitive logic
- Random number generators when testing anything that needs determinism

**What NOT to mock:**

- Your own database (use a real test database)
- Your own internal services (test them directly)
- Your own repositories or data access layer (that's exactly what integration tests should exercise)
- HTTP middleware you own
- Any code inside your own codebase

**Incorrect — over-mocking kills confidence:**

```javascript
// Mocking the database layer defeats the purpose of the test
it('creates a user', async () => {
  const mockRepo = { create: jest.fn().mockResolvedValue({ id: '123' }) }
  const service = new UserService(mockRepo)
  const user = await service.createUser({ email: 'a@b.com' })
  expect(mockRepo.create).toHaveBeenCalledWith({ email: 'a@b.com' })
})
```

This test proves nothing. It only checks that the service calls the mock you gave it.

**Correct — mock only what you can't control:**

```javascript
// Mock the external email provider, not the database
it('sends a welcome email after user creation', async () => {
  const sendEmail = jest.fn()  // mock external provider
  
  const response = await request(app)
    .post('/v1/users')
    .send({ email: 'alice@example.com', name: 'Alice' })

  expect(response.status).toBe(201)
  expect(sendEmail).toHaveBeenCalledOnce()
  expect(sendEmail).toHaveBeenCalledWith(
    expect.objectContaining({ to: 'alice@example.com', template: 'welcome' })
  )
})
```

**When you're tempted to mock your own code:**

That's often a signal the code is hard to test because of poor structure — not that mocking is the right answer. Consider:
- Is the dependency injected? If not, inject it.
- Is the function doing too much? Split it.
- Is the test trying to test a unit that's too large? Shrink the scope.

**Contract testing for external APIs:**

If you rely heavily on a third-party API, consider recording real responses and replaying them (e.g. VCR cassettes, `msw`, `nock` recordings). This gives you realistic behavior without flaky real-network calls, and alerts you when the external API changes.
