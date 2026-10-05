# Project Guidelines & Architectural Invariants

## 1. Project Overview & Architecture
* **Repository:** `job-search-dev` — Programmatic job search intake, attribution analytics, artifact compilation, and multi-board aggregation platform.
* **Architecture:** Hexagonal (Ports & Adapters) with an API-First, Headless Service design.
* **Core Tech Stack:** Python 3.12+, Pydantic v2, SQLite (WAL mode), FastAPI, Pytest.

---

## 2. Mandatory Engineering Invariants

### 2.1 API-First & Contract Decoupling
* Always design Pydantic v2 schemas in `src/job_search_dev/models/` before implementing domain use cases or routes.
* Business logic belongs strictly in `src/job_search_dev/use_cases/` — never in CLI scripts or API endpoint functions.
* Scripts in `scripts/` serve as thin clients (or in-process Phase 2 prototypes) passing DTOs directly to Use Cases.

### 2.2 Storage & Configuration Decoupling (Twelve-Factor Factor III)
* Never hardcode absolute filesystem paths or state directories in source files.
* Storage base paths must resolve through runtime settings (`JOB_SEARCH_DATA_DIR` $\rightarrow$ `/var/lib/job-search` or fallback to `<repo_root>/data`).

### 2.3 Hermetic Testing (Zero Live Network Calls)
* CI and automated unit/integration tests must NEVER execute live requests to third-party job boards.
* All test suites must use static offline JSON/YAML mock fixtures in `tests/fixtures/`.
* Code coverage must meet the minimum thresholds ($\ge 85\%$ total) defined in `docs/reference/unified-process/test-plan.md`.

### 2.4 Documentation Standards (Diátaxis)
* Maintain strict Diátaxis directory segregation:
  * `docs/tutorials/` (Learning-oriented)
  * `docs/how-to/` (Action-oriented)
  * `docs/reference/` (Information-oriented, UP catalogs, schemas)
  * `docs/explanation/` (Understanding-oriented, architecture, ADRs)
* All markdown files must include YAML frontmatter (`title`, `created_at`, `updated_at`, `tags`, `desc`).

### 2.5 Architectural Decision Records (ADR Compliance)
* All foundational design choices, partitioning standards, storage layouts, and transport mechanisms must comply with active ADRs in `docs/explanation/adr/`.
* Whenever introducing major architectural shifts, new core dependencies, or persistent schema alterations, author a corresponding ADR under `docs/explanation/adr/` before implementation.

---

## 3. Development Process & Skills

* When planning new features, addressing register risks, or advancing project phases, activate and follow the workspace skill:
  * **`unified-process-iteration`** (`.agents/skills/unified-process-iteration/SKILL.md`)
* When authoring or revising architectural decision records, activate and follow the workspace skill:
  * **`adr-authoring`** (`.agents/skills/adr-authoring/SKILL.md`)
