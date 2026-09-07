---
name: bspec-story-implementation
description: "Implementation skill for Bruno's personal spec workflow. Works one GitHub story at a time, either implementing directly or routing non-trivial work back to technical architecture while keeping delivery scoped to the smallest useful vertical slice."
---

# Story Implementation

Use this skill only when working a single GitHub story issue.

## Philosophy

- GitHub issues are the source of truth for executable stories.
- The PRD owns `what` and `why`.
- `architecture_document` owns the stable technical direction: stack, contracts, boundaries, and cross-cutting decisions.
- `implementation_plan` owns the story-specific execution detail for the active slice and lives in the GitHub issue comment.
- ADRs own durable architecture decisions that should outlive one implementation pass.
- Most issues should still go straight to implementation.
- Use the workflow state labels and structured comment markers defined by the shared workflow contract.

## Decision Policy

Classify the issue as exactly one of:

- `direct-implement`
- `needs-tech-design`
- `blocked`

### `direct-implement`

Use only when all are true:

- product intent is clear
- the smallest useful slice is obvious
- and one of the following is true:
  - the work is straightforward, with no schema or migration changes, no auth or security boundary changes, no new external integration or infrastructure change, and no broad refactor
  - `architecture_document` or linked ADRs already cover the risky technical decisions closely enough for implementation to proceed safely

### `needs-tech-design`

Use when any are true:

- schema, migration, or backfill work needs architecture clarification
- auth, roles, permissions, or secrets need architecture clarification
- external APIs, queues, webhooks, cron jobs, or infrastructure choices are not covered well enough
- a large refactor or shared abstraction change would alter module boundaries
- performance-sensitive or concurrency-sensitive work has unresolved tradeoffs
- multiple viable approaches with real tradeoffs exist
- the issue spans a larger feature or epic whose technical direction should be captured once and reused
- `architecture_document` is missing, stale, or not explicit enough for the needed decision

### `blocked`

Use when product intent is not clear enough to proceed safely.

## Implementation Planning Rules

- before coding, create or update a lightweight `implementation_plan`
- keep it in the GitHub issue comment
- include:
  - target slice
  - touched modules or files
  - contract, schema, or migration changes for this slice
  - validation plan
  - explicit out-of-scope items
- keep feature-specific execution detail here, not in `architecture_document`

## Repository Start Rules

- before starting development, ensure the repo is in a clean state
- if the working tree has unrelated staged, unstaged, or untracked changes, stop and ask the user how to proceed instead of mixing work
- fetch the latest `main` from the remote before starting implementation work
- create a fresh branch for the story from the updated `main`. 
- Use a descriptive branch name that includes the story ID or issue number when possible, and avoid long or generic names that make it hard to track the work.

Recommended branch examples:

```text
us-001-bookmark-create
issue-123-bookmark-create
```

## Pull Request Rules

- create or update a PR whenever implementation proceeds
- use `.github/PULL_REQUEST_TEMPLATE.md` if present as the default PR body template. If the template is not present or does not fit the story, use the recommended structure below instead.
- keep the PR summary short and focused on delivered work
- link the story issue explicitly in the `Linked Issues` section
- include the validation actually performed
- include current CI or required check status
- include concrete test evidence, not only a checklist
- check CI results for the related PR or branch before claiming the slice is review-ready
- if the PR only delivers part of the story, say what remains out of scope

Do not use the PR as the canonical planning source.

Recommended PR structure:

```md
## What Was Done

- brief implementation summary
- notable user-facing or architecture-impacting change

## Linked Issues

- Closes #123

## Validation

- tests run
- manual verification

## CI / Checks

- named PR checks or workflow runs reviewed
- their current conclusion

## Follow-ups / Out Of Scope

- remaining work intentionally left out of this PR
- explicit note when something remains unverified
```

## Commit Rules

- use Conventional Commits for any commits created during implementation
- prefer types like `feat`, `fix`, `refactor`, `test`, or `docs` based on the change
- prefer a short scope that matches the affected area when it is obvious
- use imperative, lowercase subjects without a trailing period

Examples:

```text
feat(bookmarks): add bookmark creation flow
fix(search): handle empty query state
refactor(storage): extract bookmark repository
test(bookmarks): cover duplicate URL validation
```

## Direct Implementation Rules

- work one issue at a time
- check the repo state before starting implementation work
- fetch `main` from the remote and branch from it before changing code
- implement the smallest useful vertical slice first
- follow `architecture_document` and linked ADRs when they cover the needed decisions
- restate the target slice, constraints, and known review feedback before changing code
- read the latest structured review summary before coding when review feedback exists
- if implementation reveals material architectural drift, stop and update or hand off updates to `architecture_document`
- minor local implementation adjustments do not require architecture updates; note them in the implementation summary instead
- reuse existing repo patterns
- avoid speculative abstractions
- run relevant validation
- check GitHub Actions or required checks after pushing the branch or updating the PR
- update GitHub with a structured implementation summary and the correct workflow state
- keep planning in the issue comment and keep the PR body focused on delivered work

## CI And Checks Rules

- do not move a story to `status/in-review` until the relevant local validation is complete and the current CI state is known
- if a PR exists, prefer checking PR checks first
- if no PR exists yet but the branch was pushed, check the latest branch workflow runs
- if checks are still running, either wait for completion or stop and report that review is pending CI
- if CI fails, inspect the failing workflow or job output and either fix the issue or stop with a clear explanation
- only treat CI as non-blocking when the failing check is clearly unrelated to the story and you explicitly report that exception

Preferred `gh` commands:

```bash
# Quick view of PR checks
gh pr checks <pr-number>

# Watch checks until completion
gh pr checks <pr-number> --watch

# List recent workflow runs for the branch
gh run list --branch <branch-name> --limit 5

# Inspect a workflow run summary
gh run view <run-id>

# Show failed job logs only
gh run view <run-id> --log-failed

# Show full logs for the run
gh run view <run-id> --log
```

How to use them:

- start with `gh pr checks <pr-number>` to see the current check state tied to the PR
- if checks are still running, use `gh pr checks <pr-number> --watch`
- if you need the underlying GitHub Actions run, use `gh run list --branch <branch-name> --limit 5` and pick the newest relevant run
- use `gh run view <run-id>` to inspect workflow names, job names, conclusions, and the GitHub Actions URL
- use `gh run view <run-id> --log-failed` to read only failing job output first
- use `gh run view <run-id> --log` when you need full job logs or more context
- when reporting validation, name the relevant check or workflow conclusion, not only "CI passed"

## Feedback Loop

- implement in small, reviewable slices
- validate after each meaningful slice, not only at the end
- if prior review feedback exists, resolve it explicitly and report what changed
- if validation fails, fix the issue or stop with a clear explanation instead of guessing
- if scope, architecture, or product intent becomes unclear, stop and route back to the right stage

## Needs-Tech-Design Rules

- do not write a substitute architecture plan in the issue
- point the work to `/bspec:arch`
- apply or preserve the needs-tech-design workflow state
- reference the stale or missing section of `architecture_document` when possible
- stop after the handoff

## Blocked Rules

- ask one targeted product question
- make it a question that changes implementation
- stop after asking

## Validation Rules

- run the narrowest relevant automated tests first
- run broader checks when the change surface warrants it
- include manual verification when user-visible behavior changes
- check the current GitHub Actions or required check status after pushing code when CI exists for the repo
- never claim success without naming the tests or checks performed
- when CI was checked, name the PR checks or workflow runs reviewed and their conclusion
- if validation cannot be run, say exactly why and what remains unverified
- move the issue into the correct workflow state when stopping

## Definition Of Done

A story slice is done only when all are true:

- the delivered slice satisfies the relevant acceptance criteria for the scope actually implemented
- the code follows existing repo patterns or justified local conventions
- relevant automated tests were added or updated when needed and are passing
- relevant manual verification was performed when the change affects user-visible behavior
- relevant CI or required PR checks were reviewed and are passing, pending with explanation, or explicitly called out as unrelated failures
- any material architecture changes are reflected in `architecture_document` or routed back to the architecture stage
- related documentation is updated or added.
- GitHub was updated with what changed, how it was validated, any remaining follow-up, and a structured implementation summary

## Rules

- default to direct implementation
- escalate to the architecture stage only on real technical risk or stale architecture
- keep scope tied to one issue
- prefer end-to-end progress over layer work
