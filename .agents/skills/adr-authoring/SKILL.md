---
name: adr-authoring
description: >-
  Standardized workflow for scaffolding, authoring, and updating Architectural
  Decision Records (ADRs) under docs/explanation/adr/ in compliance with the 6-part standard.
---

# ADR Authoring Skill

This skill guides the creation and lifecycle maintenance of Architectural Decision Records (ADRs) adhering to the standards defined in `docs/reference/unified_agent_directives.md`.

---

## 1. ADR Discovery & Numbering

1. Inspect existing ADRs under `docs/explanation/adr/`.
2. Identify the highest numerical index (`NNNN`) and increment it (e.g., `0001` $\rightarrow$ `0002`).
3. Set the target filepath: `docs/explanation/adr/NNNN_<short_descriptive_title>.md` using alphanumeric lower-case and underscores.

---

## 2. Mandatory 6-Part Structure

Every authored ADR must strictly include the following YAML frontmatter and 6 sections:

```markdown
---
title: "ADR NNNN: [Descriptive Title]"
tags: ["adr", "architecture", "<domain_tag>"]
created_at: "YYYY-MM-DD"
last_updated_at: "YYYY-MM-DD"
desc: "[Concise 1-sentence summary of the decision]"
---

# ADR NNNN: [Descriptive Title]

## 1. Status
Proposed | Accepted | Rejected | Superseded by [ADR MMMM](...) | Deprecated

## 2. Context
Explain the underlying forces, technical problems, constraints, and business requirements that necessitate a decision.

## 3. Decision
State the exact architectural choice, pattern, library, or protocol being adopted. Be precise and unambiguous.

## 4. Consequences
Evaluate the impacts of this decision:
* **Positive:** Key advantages, performance gains, or decoupled dependencies.
* **Negative:** Incurred technical debt, maintenance overhead, or constraints.
* **Neutral:** Operational shifts or tooling adjustments without negative penalty.

## 5. Procedure & Implementation
A chronological checklist of steps required to execute and verify the decision:
- [ ] Step 1: Update Pydantic schemas in `src/job_search_dev/models/`
- [ ] Step 2: Implement Use Case in `src/job_search_dev/use_cases/`
- [ ] Step 3: Add test fixtures and hermetic unit tests

---
```

---

## 3. Lifecycle Updates & Superseding

When an ADR's decision is replaced or deprecated:
1. Update the original ADR's `## 1. Status` to `Superseded by [ADR MMMM](...)`.
2. Update the `last_updated_at` frontmatter field.
3. Author the new ADR linking back to the superseded record in its Context section.
