---
name: bspec-prd-discovery
description: "Discovery skill for Bruno's personal spec workflow. Shapes project-level or feature-level product requirements directly in the PRD with a single question-driven loop."
---

# PRD Discovery

Use this skill when shaping product requirements directly in `prd_document`.

## Purpose

Handle both:

- project-level discovery
- feature-level refinement

using one discovery loop and one product artifact.

`prd_document` is the working and canonical product artifact.

It may be:

- one file, or
- a PRD index plus feature section files

## Modes

### Project Mode

Use when the request is broad, early, or shapes the overall product.

Focus on:

- project scope
- target users
- user problems
- product goals
- success measures
- major constraints
- candidate features
- sequencing and priorities at a product level

### Feature Mode

Use when the request targets one feature or feature-sized slice.

Focus on:

- user value
- scope
- acceptance criteria
- non-goals
- UX notes
- assumptions
- constraints
- open questions

## Discovery Method

- read the relevant parts of `prd_document` first
- decide whether the request is project mode or feature mode
- ask one question at a time
- ask only questions that materially change scope, priority, user value, acceptance criteria, or non-goals
- update the relevant PRD file inside `prd_document` after each meaningful clarification
- prefer the smallest clarification that unlocks forward progress
- stop when the relevant scope is clear enough for issue decomposition or architecture follow-up

In multi-file mode:

- keep project-level content in the PRD index
- create or update one feature file when the request is feature-sized
- avoid scattering one feature across many PRD files

## Avoid

- technical architecture
- implementation plans
- story decomposition
- issue labels or GitHub workflow
- line-by-line wording polish that does not change product clarity

## Recommended Project Structure

```md
# Product Requirements Document

## Overview

## Goals

## Target Audience

## Success Metrics

## Features
- Feature A
- Feature B

## Constraints

## Open Questions
- ...
```

In multi-file mode, keep this structure in the PRD index and place feature-level sections in separate files under the configured PRD sections directory.

## Recommended Feature Structure

```md
### Feature: <name>

#### User Value

#### Scope

#### Acceptance Criteria
- ...

#### Non-Goals
- ...

#### UX Notes
- ...

#### Assumptions
- ...

#### Constraints
- ...

#### Additional Notes
- product notes only

#### Open Questions
- ...
```

In multi-file mode, this structure can be the entire contents of one feature file.

## Definition Of Ready

The discovered scope is ready when:

- the relevant project or feature outcome is clear
- acceptance criteria are concrete when the work is feature-sized
- non-goals prevent accidental scope creep
- the remaining open questions do not block issue decomposition
- the PRD can support issue creation without more product discovery
