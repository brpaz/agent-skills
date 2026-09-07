---
name: bspec-workflow
description: "Shared conventions for Bruno's personal spec-driven workflow. Defines logical artifacts, issue labels, workflow states, story IDs, implementation planning, and review markers."
---

# BSpec Workflow

Use this skill at the start of every spec-driven workflow command.

## Purpose

Provide one shared workflow contract for artifact names, GitHub labels, workflow states, story IDs, implementation planning, review semantics, and structured feedback markers.

Commands should load this skill first, then load the task-specific skill.

## Optional Repo Config

If `docs/spec-workflow.yml` exists, read it first and use it to override the defaults below.

If no config file exists, use the defaults below.

`prd_document` supports two shapes:

- string form for single-file mode
- object form for index-plus-sections mode

Expected config shape:

```yaml
version: 1
artifacts:
  prd_document:
    index: docs/PRD.md
    sections_directory: docs/prd
  architecture_document: docs/ARCHITECTURE.md
  adr_directory: docs/adr
issues:
  managed_label: bspec
  story_label: story
  status_labels:
    ready: status/ready
    in_progress: status/in-progress
    in_review: status/in-review
    needs_fixes: status/needs-fixes
    blocked: status/blocked
    needs_tech_design: status/needs-tech-design
implementation:
  plan_location: issue-comment
comments:
  implementation_marker: "<!-- bspec:implementation -->"
  review_marker: "<!-- bspec:review -->"
  design_drift_marker: "<!-- bspec:design-drift -->"
```

## Logical Artifacts

Use these logical names in workflow prompts and reasoning:

- `prd_document`
- `architecture_document`
- `implementation_plan`
- `adr_directory`

## Default Artifact Locations

- `prd_document` = `docs/PRD.md` by default, or `docs/PRD.md` plus `docs/prd/*` when multi-file mode is configured
- `architecture_document` = `docs/ARCHITECTURE.md`
- `implementation_plan` = the current issue comment for the active story
- `adr_directory` = `docs/adr`

## PRD Resolution Rules

- if `prd_document` is a string, treat it as a single-file PRD
- if `prd_document` is an object, treat `index` as the project-level PRD entrypoint and `sections_directory` as the feature/detail directory
- keep project-wide goals, users, constraints, priorities, and overview content in the PRD index
- keep feature-specific product detail in section files when multi-file mode is enabled
- when a feature exists both inline in the index and in a section file, treat the section file as canonical
- keep the workflow logically simple: one `prd_document`, even when it spans multiple files

## Truth Model

- `prd_document` = working and canonical business/product truth during discovery and refinement, whether stored in one file or in an index plus section files
- `architecture_document` = canonical technical architecture truth
- `implementation_plan` = story-specific execution detail for the active implementation, stored in the GitHub issue comment
- GitHub issues = executable work truth
- ADRs = optional durable architecture decisions

## Stage Order

Default workflow:

1. spec discovery
2. optional technical architecture
3. GitHub issues
4. implementation
5. review

## Workflow Design Rules

- Keep business scope in `prd_document`.
- Keep technical stack, API contracts, module structure, and system boundaries in `architecture_document`.
- Keep story-specific sequencing, touched files, and slice details in `implementation_plan`.
- Do not overload `architecture_document` with story-by-story execution detail.

## Architecture Usage Rule

- `architecture_document` is optional for issue generation.
- If `architecture_document` exists and is clearly `Approved`, treat it as binding technical context for issue generation, implementation, and review.
- If `architecture_document` is missing, `Draft`, or `In Review`, `/bspec:sync` may still proceed from `prd_document` alone.
- Use `/bspec:arch` when technical risk, ambiguity, or drift justifies architecture work.

## GitHub Issue Labels

Apply these labels to every workflow-managed story issue:

- `bspec`
- `story`
- exactly one status label from the list below

Optional labels:

- `area/<name>`
- `priority:p0`
- `priority:p1`
- `priority:p2`

## Workflow Status Labels

Exactly one of:

- `status/ready`
- `status/in-progress`
- `status/in-review`
- `status/needs-fixes`
- `status/blocked`
- `status/needs-tech-design`

## Default Status Transitions

- `/bspec:sync` creates new stories as `status/ready`
- `/bspec:implement` moves `status/ready` or `status/needs-fixes` to `status/in-progress`
- if technical architecture is missing or materially stale, move to `status/needs-tech-design`
- `/bspec:arch` updates `architecture_document` and can move blocked issues back to `status/ready`
- once implementation is validated and review-ready, move to `status/in-review`
- review feedback that blocks completion moves to `status/needs-fixes`
- blocked execution moves to `status/blocked`
- closing the issue marks the story done

## Implementation Plan Rule

- The canonical `implementation_plan` lives in the GitHub issue comment, not in the PR.
- The PR body explains what was delivered, how it was validated, the CI or check state, and any follow-up or out-of-scope items.
- Do not treat PR comments or PR descriptions as the planning source of truth.

## Review Semantics

- `/bspec:review` is read-only for repo files and code.
- `/bspec:review` may still update GitHub comments and workflow labels.
- An `approved` or `approved-with-follow-ups` review means the PR is ready to merge.
- The issue remains `status/in-review` until the PR is merged or the issue is otherwise closed.

## Story ID Convention

Use stable IDs in this form:

```text
US-001
US-002
US-003
```

Issue title format:

```text
[US-001] User can create a project
```

## PRD Linkback Convention

When a story issue exists, write the issue reference back into the PRD file that owns the relevant section of `prd_document` using a compact subsection such as:

```md
#### GitHub Issues
- [US-001 / #123](https://github.com/example/repo/issues/123) User can create a project
```

Use path-aware traces when helpful, for example:

```md
## PRD Trace
- prd_document: docs/prd/project-setup.md :: Feature: Project Setup
```

## Structured Comment Markers

Use these markers for durable machine-readable workflow summaries:

- `<!-- bspec:implementation -->`
- `<!-- bspec:review -->`
- `<!-- bspec:design-drift -->`

## Review Targeting Rule

Do not guess at the review target.

- If the user gives an issue, PR, or URL, use that.
- If exactly one current story is unambiguous, use it.
- Otherwise ask for a target.

## Rules

- Keep the workflow simple and single-file by default, and split feature sections only when the PRD becomes painful.
- Put repo-specific conventions here, not in every skill.
- Let task skills own policy, not paths.
- Let commands own orchestration, not duplicated workflow contracts.
