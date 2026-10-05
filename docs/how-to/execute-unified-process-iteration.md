---
title: "How-To: Execute a Unified Process Iteration Cycle"
created_at: 2026-09-17T12:42:15-04:00
updated_at: 2026-09-17T12:42:15-04:00
tags:
  - unified-process
  - workflow
  - how-to
desc: Step-by-step procedural guide for planning, executing, and evaluating a development iteration under the Unified Process
---

# How to Execute a Unified Process Iteration Cycle

This guide outlines the procedural workflow for executing a disciplined, risk-driven iteration cycle within any phase of the Unified Process.

---

## 1. Prerequisites

Before starting an iteration:
1. Ensure the active phase (Inception, Elaboration, Construction, Transition) is defined.
2. Ensure the Risk Register (`docs/reference/unified-process/risk-list.md`) is up-to-date.
3. Verify that the previous iteration's baseline passes automated tests (`pytest`).

---

## 2. Iteration Workflow Steps

```text
[ Step 1: Select Scope & Top Risk ]
                 │
                 ▼
[ Step 2: Formalize Contract / Use Case ]
                 │
                 ▼
[ Step 3: Implement Architectural Slice ]
                 │
                 ▼
[ Step 4: Verify with Hermetic Tests ]
                 │
                 ▼
[ Step 5: Assess & Milestone Gating ]
```

### Step 1: Select Iteration Scope & Target Risk
1. Open [`docs/reference/unified-process/risk-list.md`](file:///home/michael/src/github.com/mnaatjes/job-search-dev/docs/reference/unified-process/risk-list.md).
2. Identify the highest active risk (e.g., `RSK-01` scraper breakage or `RSK-06` resume tailoring drift).
3. Select the corresponding use case in [`docs/reference/unified-process/use-cases.md`](file:///home/michael/src/github.com/mnaatjes/job-search-dev/docs/reference/unified-process/use-cases.md) to drive the iteration.

### Step 2: Specify the Contract (API-First Day 1)
1. Define input/output Pydantic DTOs in `src/job_search_dev/models/`.
2. Define the Use Case signature in `src/job_search_dev/use_cases/`.
3. Create offline mock fixtures in `tests/fixtures/` representing raw external inputs.

### Step 3: Implement the Thin Architectural Slice
1. Write the domain service logic within the Application Core.
2. Implement necessary Driven Adapters (e.g., storage repositories, scraper extractors).
3. If in Phase 2 (Elaboration), create a standalone developer script (e.g., `scripts/run_scrape.py`) invoking the Use Case in-process.
4. If in Phase 3/4 (Construction/Transition), expose the Use Case via FastAPI routing and update the thin CLI (`scripts/jobctl`).

### Step 4: Execute Hermetic Verification
1. Run the test suite with coverage enforcement:
   ```bash
   pytest --cov=job_search_dev --cov-report=term-missing tests/
   ```
2. Verify that coverage satisfies the thresholds in [`docs/reference/unified-process/test-plan.md`](file:///home/michael/src/github.com/mnaatjes/job-search-dev/docs/reference/unified-process/test-plan.md) ($\ge 85\%$).

### Step 5: Milestone Gating & Iteration Assessment
1. Update the Risk Register: mark mitigated risks as `Mitigated` or `Retired`.
2. Update the Software Architecture Document (SAD) with any newly introduced layers or ports.
3. Check the Phase Exit Criteria:
   * **Inception Exit (LCO):** Scope clear, baseline feasibility verified.
   * **Elaboration Exit (LCA):** Executable prototype running, top risks retired, core architecture locked.
   * **Construction Exit (IOC):** All primary features complete, test coverage satisfied.
   * **Transition Exit (PR):** Deployment automation and daemons operational in production.

---

## 3. Checklist: Iteration Sign-Off

- [ ] Use case acceptance criteria verified via automated tests.
- [ ] No live network dependencies in unit/integration test runs.
- [ ] Documentation updated to maintain Diátaxis compliance.
- [ ] Risk register status updated.
- [ ] Changes committed cleanly to version control.
