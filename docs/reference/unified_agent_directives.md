---
title: "Unified Agent Directives and Documentation Standards"
tags: ["reference", "diataxis", "adr", "token_efficiency", "response_format"]
created_at: "2026-09-17"
last_updated_at: "2026-09-17"
desc: Authoritative directives on token efficiency, response formatting, Diátaxis compliance, and ADR authoring
---

# Unified Agent Directives and Documentation Standards

This document consolidates system directives, documentation standards, and operational guidelines governing agent interaction, token efficiency, response formatting, and Architectural Decision Record (ADR) authoring within the project framework.

---

## 1. Diátaxis Framework Adherence

All technical documentation must align strictly with the **Diátaxis** framework structure to maintain a clear division between different document intents:

* **Tutorials (`docs/tutorials/`):** Learning-oriented hands-on guides for beginners.
* **How-To Guides (`docs/how-to/`):** Problem-oriented, step-by-step instructions to accomplish specific operational goals or workarounds.
* **Reference (`docs/reference/`):** Information-oriented, precise technical descriptions, APIs, schemas, configurations, and specs.
* **Explanation (`docs/explanation/`):** Understanding-oriented, high-level architecture decisions, design rationale, context, and theoretical discussions (includes ADRs).

---

## 2. Documentation Frontmatter Configuration

Every markdown document created or maintained under `docs/` must include standard YAML frontmatter at the top of the file:

```yaml
---
title: "Document Title"
tags: ["tag1", "tag2"]
created_at: "YYYY-MM-DD"
last_updated_at: "YYYY-MM-DD"
---
```

When creating or modifying documents:
* **`title`:** Clear, descriptive title of the document.
* **`tags`:** Relevant metadata tags matching category and scope.
* **`created_at`:** ISO date when document was initially authored.
* **`last_updated_at`:** Agents must update this field whenever modifications are made.

---

## 3. Architectural Decision Record (ADR) Authoring Guidelines

### 3.1 File Placement & Naming Conventions
* **Directory Location:** `docs/explanation/adr/`
* **File Naming Format:** `NNNN_short_descriptive_title.md` (e.g., `0008_integrate_external_dns_sync.md`).

### 3.2 Standard ADR Structure
Every ADR must include the YAML frontmatter and contain the following six sections:

1. **Title:** `# ADR NNNN: [Descriptive Title]`
2. **Status:** `Proposed`, `Accepted`, `Rejected`, `Superseded by [ADR NNNN](...)`, or `Deprecated`.
3. **Context:** Background, limitations, and problems explaining *why* the change is required.
4. **Decision:** The active path of action or architectural standard chosen to resolve the context.
5. **Consequences:** Objective analysis of positive benefits, negative trade-offs, and neutral impacts.
6. **Procedure & Implementation:** Chronological checklist of execution steps to implement the decision.

---

## 4. agy/Gemini Token Efficiency Guidelines & Directives

To maximize execution speed and eliminate unnecessary token consumption, agents must adhere to the following rules:

* **Eradicate Conversational Filler:** Never use pleasantries, greetings, sign-offs, or apologies. Begin responses immediately with technical answers or action items.
* **Strictly Enforce File-Based Code Edits:** Avoid outputting modified code blocks directly in chat output. Strictly use filesystem tools (`replace_file_content`, `write_to_file`). Limit chat output regarding code updates to a bulleted list of modified absolute filepaths and a 1-sentence summary.
* **Minimal Execution Reporting:** Report execution steps in minimal, bullet-point declarative statements displaying absolute filepaths of files read, written, or commands run.
* **Targeted File Reading:** Avoid viewing large files in full. Use `grep_search` to locate target line numbers first and restrict `view_file` to narrow line ranges.

---

## 5. agy/Gemini Response Format & Content Guidelines

Agents must strictly structure responses according to the task context:

### 5.1 Dry-Run Verification Rule
For complex tasks, output a numbered list of exact filepaths intended for modification along with a 1-sentence summary of each change. Halt and wait for explicit user approval (`Proceed`) before executing file writes.

### 5.2 Technical Troubleshooting & Analysis Format
All technical analysis and troubleshooting responses must adhere to the following sequence:

* **Diagnostic:** Identify the root cause or core question.
* **Theory:** Explain the underlying mechanism or conflict.
* **Analysis:** Break down the specific options, hardware, code, or logs involved.
* **Remediation:** Provide prioritized solution paths or exact execution steps.
