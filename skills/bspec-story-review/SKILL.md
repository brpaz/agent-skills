---
name: bspec-story-review
description: "Read-only review skill for Bruno's personal spec workflow. Reviews one implemented GitHub story against the issue, PRD, architecture document, ADRs, and validation evidence, then produces actionable feedback for the implementation loop."
---

# Story Review

Use this skill only when reviewing one implemented story in repo-read-only mode.

## Purpose

Evaluate whether a story implementation is correct, in scope, aligned with the PRD and architecture, properly validated, and ready to merge.

The review is advisory and must not change code directly, but it may update GitHub review summaries and workflow labels.

## Review Inputs

- GitHub issue
- `prd_document`
- `architecture_document`
- linked ADRs, if any
- the current issue-based `implementation_plan`, if present
- PR summary
- implementation diff, PR, or changed files
- validation evidence
- CI or check results
- latest structured implementation summary, if present

## Review Focus

- correctness
- scope alignment
- architecture alignment
- regression risk
- test quality and coverage
- validation completeness
- CI or check status
- maintainability and clarity

## Outcomes

- `approved`
- `approved-with-follow-ups`
- `needs-fixes`

Use:

- `approved` when the story meets its intent with no meaningful corrective work left and is ready to merge
- `approved-with-follow-ups` when the story is acceptable now but has small explicit follow-ups
- `needs-fixes` when correctness, scope, architecture, validation, or required CI issues still block completion

## Finding Severity

- `high`: likely bug, broken acceptance criteria, strong architecture mismatch, missing critical validation, failing required CI, or clear regression risk
- `medium`: important but non-blocking weakness, unclear edge case handling, incomplete test coverage, or maintainability concern
- `low`: polish, clarity, or small cleanup suggestion

## Feedback Loop Rules

- produce concrete findings tied to the story, not generic code review advice
- reference the relevant issue, PRD, architecture, ADR, test, plan, or file context when possible
- if fixes are needed, make it obvious what the implementation stage should do next
- preserve a clean loop: review -> fix -> review again if needed
- do not silently expand scope during review
- write the review back using the shared review marker when updating GitHub

## Definition Of Review Ready

The implementation is review-ready when:

- the story slice is implemented
- validation has been run or the lack of validation is clearly disclosed
- the current CI or required-check state is known
- the implementer has stated whether the definition of done was met
- architecture or ADR references are linked when relevant

## Review Checklist

- does the delivered slice satisfy the intended acceptance criteria?
- does it stay within story scope?
- does it follow the current architecture and ADR guidance when relevant?
- is the implementation plan reflected honestly in what shipped?
- are tests or validation appropriate for the change?
- are required PR checks passing or clearly explained?
- are there obvious regressions or missing edge cases?
- is any follow-up clearly separated from the accepted slice?

## Output Format

Use this structure:

```md
<!-- bspec:review -->

## Review Outcome
approved | approved-with-follow-ups | needs-fixes

## Findings
- [high] ...
- [medium] ...
- [low] ...

## Validation Notes
- ...

## Next Step For Implementation
- ...
```

## Rules

- stay read-only
- be specific and actionable
- prefer a small number of high-signal findings over broad commentary
- do not require unnecessary rewrites when a focused fix is enough
- treat unresolved failing required checks as blocking unless clearly unrelated and explicitly explained
- focus on architecture, scope, correctness, and validation over style or preference. Anything that can be easily detected and fixed by a linter tool should not be a review finding.
