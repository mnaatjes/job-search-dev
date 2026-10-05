---
name: unified-process-iteration
description: >-
  Guides the planning, contract-first design, architectural slice execution,
  and milestone verification for a Unified Process (UP) development iteration.
  Use when planning or building features, mitigating register risks, or advancing
  milestones (LCO, LCA, IOC, PR).
---

# Unified Process Iteration Execution Skill

This skill operationalizes the risk-driven, API-First development process defined in `docs/how-to/execute-unified-process-iteration.md`.

---

## 1. Iteration Pre-Flight Check

Before making file edits or writing code:
1. Read the active risk matrix at `docs/reference/unified-process/risk-list.md`.
2. Identify the target risk (e.g., `RSK-01` scraper breakage, `RSK-06` artifact drift, `RSK-09` schema sync).
3. Identify the driving use case in `docs/reference/unified-process/use-cases.md`.
4. Ensure the current test baseline passes:
   ```bash
   pytest
   ```

---

## 2. API-First Iteration Workflow

Execute iterations across the four engineering disciplines:

### Step A: Contract Specification (Phase 1 Discipline)
* Define/update input and output Pydantic v2 DTOs in `src/job_search_dev/models/`.
* Define abstract Use Case protocols in `src/job_search_dev/use_cases/`.
* Create or update offline mock fixtures in `tests/fixtures/`.
* **Rule:** Never write business logic before input/output DTOs are declared.

### Step B: Core Use Case & Adapter Implementation (Phase 2/3 Discipline)
* Implement core domain logic in pure Python use cases (`src/job_search_dev/use_cases/`).
* Build or update Driven Adapters (`src/job_search_dev/storage.py`, `src/job_search_dev/scrapers/`).
* If in Early Prototyping (Phase 2): Provide a standalone CLI runner in `scripts/` calling the Use Case in-process.
* If in API Integration (Phase 3/4): Expose the Use Case via FastAPI in `src/job_search_dev/api/routes/`.

### Step C: Hermetic Verification (Testing Discipline)
* Author unit and integration tests using offline fixtures.
* Run coverage benchmarks:
   ```bash
   pytest --cov=job_search_dev --cov-report=term-missing tests/
   ```
* **Enforce Thresholds:** Project total must meet $\ge 85\%$ coverage defined in `docs/reference/unified-process/test-plan.md`.

### Step D: Assessment & Milestone Sign-Off
1. Update `docs/reference/unified-process/risk-list.md`: Transition mitigated risks to `Mitigated` or `Retired`.
2. Update `docs/explanation/unified-process/software-architecture-document.md` if new ports or layers were added.
3. Validate against the Phase Milestone criteria (LCO $\rightarrow$ LCA $\rightarrow$ IOC $\rightarrow$ PR).
