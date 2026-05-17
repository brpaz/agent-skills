---
name: adr-writer
description: "Architecture decision record skill for capturing major technical decisions in an ADR directory with context, alternatives, and consequences."
---

# ADR Writer

Use this skill when the project needs a durable record of a major technical decision.

## Purpose

Capture important technical decisions in `adr_directory` so future implementation work can understand the context, tradeoffs, and consequences.

Use an ADR for decisions that are broader than one code change and likely to matter again later.

## Good ADR Candidates

- architecture or subsystem boundaries
- database or persistence strategy
- authentication or authorization approach
- external integration strategy
- deployment or infrastructure pattern
- major shared abstractions
- consequential performance or reliability tradeoffs

## Avoid

- routine implementation details
- temporary coding tactics
- decisions that only affect one tiny local change
- rewriting history to make a decision look cleaner than it was

## Output Location

Write ADRs to `adr_directory`.

File name format:

```text
<adr_directory>/0001-short-kebab-title.md
```

If ADRs already exist, continue the numbering.

## ADR Template

```md
# ADR 0001: Short Title

## Status
Proposed

## Context
What problem or pressure led to this decision?

## Decision
What are we deciding?

## Alternatives Considered
- Option A
- Option B

## Consequences
- Positive consequence
- Negative consequence
- Follow-up consequence

## Related Artifacts
- canonical PRD artifact
- related design doc, if any
- GitHub issue or PR
```

## Writing Rules

- keep it concise and durable
- explain why, not just what
- name the rejected alternatives when they matter
- record tradeoffs honestly
- prefer one ADR per major decision
- update status if a proposed decision later becomes accepted, superseded, or rejected

## Workflow Guidance

- read the related canonical PRD artifact, design doc, issue, plan, and any existing ADRs first
- avoid duplicating an existing ADR
- if a prior ADR is being changed, create a new ADR that supersedes it unless a minor edit is enough
- reference the ADR from the relevant issue or plan when appropriate
