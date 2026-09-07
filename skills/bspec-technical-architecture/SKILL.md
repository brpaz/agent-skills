---
name: bspec-technical-architecture
description: "Technical architecture skill for Bruno's personal spec workflow. Shapes docs/ARCHITECTURE.md, drives a feedback loop, and records durable decisions via ADRs when needed."
---

# Technical Architecture

Use this skill only when shaping or updating the canonical technical architecture.

## Purpose

Create or refine a living `architecture_document` for work that is too risky, cross-cutting, or ambiguous to implement safely from the business PRD alone.

- `prd_document` = business and product truth
- `architecture_document` = canonical technical architecture truth
- `implementation_plan` = story-specific execution detail for the active implementation
- ADRs = durable architecture decisions extracted when they matter beyond one implementation pass

The architecture document should stay current as implementation evolves. If implementation materially changes architecture, the architecture document must be updated.

## When To Use

- tech stack selection or revision
- API design and contracts
- schema or persistence boundaries
- auth, security, or permission boundaries
- external integrations, queues, webhooks, cron jobs, or infrastructure choices
- module or package structure
- runtime, deployment, or operational constraints
- cross-cutting abstractions or tradeoffs that several stories will rely on

## Focus Areas

- technical goals
- non-goals
- constraints
- tech stack
- system context and boundaries
- modules and responsibilities
- interfaces and contracts
- data model and storage boundaries
- integrations and external systems
- deployment and runtime model
- security and permission boundaries
- observability and testing strategy
- risks and tradeoffs
- open technical questions
- architecture change log

## Avoid

- rewriting product requirements
- acceptance criteria duplication
- story decomposition
- vertical slice planning
- per-story implementation sequencing
- issue checklists or task tracking
- feature-specific edge-case detail that belongs in implementation planning

## Feedback Loop

- start with status `Draft`
- ask one high-leverage technical question at a time
- challenge weak assumptions and shallow tradeoff analysis
- update the same `architecture_document` after each meaningful clarification
- move to `In Review` when the architecture is coherent enough for feedback
- move to `Approved` only when the user explicitly approves it or clearly asks to issue work against it
- if implementation later discovers material architectural drift, update the same document instead of creating a parallel design doc
- while architecture work is pending, keep related issues in `status/needs-tech-design`; when architecture is stable, move them back to `status/ready`

## Recommended Structure

```md
# Technical Architecture

## Status
Draft

## Linked Artifacts
- PRD:
- ADRs:
- Relevant issues:

## Technical Goals

## Non-Goals

## Constraints

## Tech Stack

## System Context

## Module Structure

## API Design and Contracts

## Data Model and Storage Boundaries

## Integrations and External Systems

## Deployment and Runtime

## Security and Access Boundaries

## Observability and Testing Strategy

## Risks and Tradeoffs

## Open Questions

## Architecture Change Log
- YYYY-MM-DD: initial draft
```

## ADR Rules

- use `adr-writer` when the architecture includes a durable technical decision
- create or update ADRs for architecture boundaries, persistence strategy, integration strategy, auth or security boundaries, deployment decisions, and consequential tradeoffs
- link ADRs from the architecture document instead of copying them in full

## Definition Of Ready

The architecture is ready for issue generation or implementation handoff when:

- the tech stack and major dependencies are clear enough
- the main module boundaries and responsibilities are explicit
- the important APIs, contracts, and data boundaries are explicit
- the major runtime, security, and integration constraints are known
- the main risks and tradeoffs are explicit
- durable decisions are captured in ADRs when needed
- the document status is `Approved` or it has been explicitly updated to reflect accepted implementation changes

## Rules

- keep `architecture_document` cross-cutting, durable, and honest
- keep story-specific execution detail in `implementation_plan`, not here
- use this document as living technical truth for implementation and review
