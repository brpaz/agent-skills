---
name: bspec-story-sync
description: "Synchronization skill for Bruno's personal spec workflow. Decomposes the business PRD into small vertical stories and reconciles them into GitHub issues with stable labels, bodies, and safe update rules."
---

# Story Sync

Use this skill only for converting the business PRD into GitHub story issues.

## Source Of Truth

- `prd_document` = business and product truth, stored in one file or in an index plus section files
- `architecture_document` = optional approved technical architecture guidance for issue references and constraints
- GitHub issues = story truth

Do not create local story tracking files.

## Responsibilities

- extract story-ready work from the PRD
- split large features into vertical slices
- format concise executable issue bodies
- create missing issues
- update safe-to-update issues
- bootstrap labels when needed
- write issue links back into the relevant PRD file inside `prd_document`
- preserve useful architecture references on issues
- report drift on active or closed issues

## Story Rules

- prefer vertical slices over horizontal tasks
- each story should have one meaningful outcome
- each story should be small enough for one focused implementation cycle
- keep product scope anchored in `prd_document`
- use approved `architecture_document` guidance to preserve technical constraints, not to redefine product scope
- use the shared workflow contract for story IDs, managed labels, status labels, and structured markers

## Issue Template

```md
Story-ID: US-001

## Story
As a <user>, I can <action> so that <outcome>.

## Acceptance Criteria
- ...

## Non-Goals
- ...

## Notes
- concise product-facing notes

## Technical Notes
- relevant architecture constraints or references

## Testing Notes
- relevant test cases or strategies

## PRD Trace
- prd_document: <file path> :: <section reference>

## Architecture Trace
- architecture_document: <section reference>
```

## GitHub Execution Rules

- use `gh issue` for issue creation and editing
- use `gh label` when workflow labels from the shared workflow contract do not exist yet
- apply the managed label, story label, and exactly one status label from the shared workflow contract
- prefer one `area/<name>` label when the PRD clearly implies a primary area
- preserve issue discussion history when updating existing issues

### Label Bootstrap Example

Create labels from the shared workflow contract if they do not exist yet:

```bash
bash skills/bspec-story-sync/ensure-bspec-labels.sh
```

### Issue Creation Example

Use `skills/bspec-story-sync/issue-template.md` as the starting body template and rewrite the placeholders for the actual story.

```bash
gh issue create \
  --title "[US-001] User can create a project" \
  --label "bspec" \
  --label "story" \
  --label "status/ready" \
  --label "area/project-setup" \
  --body-file skills/bspec-story-sync/issue-template.md
```

### Issue Update Example

When the story already exists and is safe to update:

```bash
gh issue edit 123 \
  --title "[US-001] User can create a project" \
  --add-label "bspec" \
  --add-label "story" \
  --add-label "status/ready" \
  --add-label "area/project-setup" \
  --body-file /tmp/us-001-issue.md
```

## Issue Body Rules

- keep `Story-ID` stable
- start from `skills/bspec-story-sync/issue-template.md` and replace the example content with story-specific content before publishing
- keep acceptance criteria executable and product-facing
- include a `PRD Trace` section that points back to the canonical PRD file and section
- include an `Architecture Trace` section when relevant approved architecture guidance exists
- preserve lightweight `Architecture` and `ADRs` reference sections when updating existing issues
- if a related ADR exists, link it without copying its contents
- prefer concise issue bodies over long design documents
- ensure there is exactly one workflow status label on the issue

## Reconcile Rules

- create a new issue when the story ID does not exist
- update an issue only when it is open and not actively being implemented or reviewed
- never silently overwrite in-progress, in-review, or closed issues
- report drift clearly instead of forcing synchronization

## PRD Linkback Rules

- after creating or matching an issue, write the issue reference back into the owning PRD file inside the logical `prd_document`
- keep product intent and issue execution state separate: the PRD stores references, GitHub stores the executable story state
- place links near the relevant feature or story section inside the PRD file that owns it
- prefer a compact subsection such as `#### GitHub Issues`
- use markdown links with both story ID and issue number when available
- if the story is project-level, place the linkback in the PRD index

Example:

```md
#### GitHub Issues
- [US-001 / #123](https://github.com/example/repo/issues/123) User can create a project
```

## Rules

- preserve GitHub discussion history
- preserve existing lightweight `Architecture` and `ADRs` references on safe-to-update issues
- prefer issue state plus labels over local workflow files
- keep issue bodies concise and executable
- use the shared workflow contract as the source of truth for labels, status names, story IDs, and markers
- replace old workflow status labels when changing issue state; do not accumulate multiple status labels
- keep the PRD logically unified even when feature sections live in separate files
