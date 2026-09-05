# Implementation Plan - Redline 🎯

**Redline** is an AI-powered pre-flight testing and red-teaming tool for AI-native coding assessments. It analyzes a GitHub repository and a candidate task, simulates AI-assisted solving strategies across 3 candidate profiles, evaluates signal strength vs AI solvability, and provides evidence-backed task upgrades.

---

## 🔍 Repository Evidence Grounding & Anti-Hallucination Policy

> **Core Product Principle**: Every assessment health score, diagnostic metric, and task recommendation MUST be strictly grounded in empirical evidence extracted directly from the repository code structure. Redline must NEVER hallucinate unsupported architectural constraints (e.g. recommending non-existent rate-limiting middleware or streaming abstractions).

1. **Repository Fact Extraction**: The pipeline first constructs an explicit Repository Fact Matrix (Detected vs Absent abstractions/patterns).
2. **Evidence → Recommendation Chain**: Upgraded task suggestions are validated against the Fact Matrix. If an abstraction does NOT exist in the repository (e.g. streaming, rate-limiting, Redis caching), Redline will NOT recommend requiring it unless explicitly flagging it as an unsupported assumption.
3. **Artificial Complexity Penalty**: Tasks that introduce artificial, ungrounded complexity (e.g. adding microservices or distributed locks to a simple monolith) are flagged with **High Complexity / Low-to-Medium Signal**, discouraging bloated assessments.
4. **Transparent Scoring Rationale**: Every metric explicitly links to specific repository file paths, symbol signatures, and candidate inspection trajectories.

---

## 📊 Diagnostic Nature & Non-Statistical Disclaimer

> **Core Principle**: The Assessment Health Score is a **heuristic diagnostic**, NOT a scientifically validated or statistically predictive measurement.

1. **Evidence First**: The system prioritizes concrete, repository-specific qualitative evidence and architectural reasoning over arbitrary numeric metrics.
2. **No Validity Claims**: Redline makes **no claims of statistical validity or objective candidate performance prediction**. It functions purely as an assessment-design heuristic tool for engineering managers and interview designers.

---

## 🛡️ Security Requirements & Data Boundaries

> **Core Principle**: All GitHub repository contents must be treated strictly as **untrusted DATA**, never as system or operational instructions.

1. **Instruction Boundary Isolation**: System prompts explicitly treat repository code, READMEs, docs, comments, and config files as inert passive data. Content inside repositories must never override Redline's system instructions (Prompt Injection Protection).
2. **Zero Code Execution**: Redline performs static code structure & AST analysis only. Arbitrary repository code, scripts, build steps, or tests are **never executed**.
3. **Path Traversal & Scan Guardrails**: Strict canonical path validation (`os.path.realpath`), `--depth 1` clones, size caps (<50MB), and file whitelisting (`.py`, `.ts`, `.js`, etc.).
4. **Secret Exclusion & Redaction**: Excludes sensitive files (`.env*`, `*.pem`, `credentials`) and redacts API key patterns.

---

## 🎯 MVP Goal

Build a functional proof-of-concept system where a user inputs a **GitHub Repository URL** (or local repo path) and a **Proposed Coding Assessment Task description**, resulting in a comprehensive **Assessment Health & Signal Report** with concrete evidence and task upgrade suggestions.

---

## 📅 Implementation Phases

```
┌─────────────────────────────────────────────────────────┐
│ Phase 1: Foundation, Core Models & Security Policies    │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 2: Secure Repo Context & Fact Matrix Extractor    │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 3: Evidence-Grounded Simulator Engine             │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 4: Grounded Signal Evaluator & Upgrade Generator │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 5: FastAPI Integration & API Layer               │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 6: Frontend Visual Dashboard & Interactive UI     │
└───────────────────────────┴─────────────────────────────┘
```

---

## 📋 Tasks Breakdown & Dependencies

### Phase 1: Project Setup & Core Models
- [x] **Task 1.1: Environment & Project Bootstrap**
  - Setup Python backend directory structure (`backend/app/{api,core,services,models}`) and Frontend Vite React TypeScript application (`frontend/`).
  - Configure `.env` management (Gemini API Key, CORS origins, file size limits).
  - *Dependencies*: None
  - *Acceptance Criteria*: Backend initializes with FastAPI (`/health` returns status OK); Frontend compiles with clean UI shell.

- [x] **Task 1.2: Pydantic Data Contracts & Validation Schemas**
  - Define input schemas (`AnalysisRequest`, `RepoSource`).
  - Define schema for `RepositoryFactMatrix` (Observed abstractions vs Absent abstractions).
  - Define `EvidenceGroundingChain` schema (Repo Facts → Task Implications → Allowed/Forbidden Upgrades → Confidence score).
  - Define `CandidateInspectionTrajectory` (Files inspected, abstractions reused, edge-case tests written per profile).
  - *Dependencies*: Task 1.1
  - *Acceptance Criteria*: All Pydantic models validate sample payload objects cleanly.

---

### Phase 2: Secure Repository Analyzer & Fact Extractor
- [x] **Task 2.1: Secure Ingestion, Path Sanitation & AST File Parsing**
  - Build helper to clone GitHub repos securely (`--depth 1`, path traversal protection via `os.path.realpath` / `is_subpath`, `--` argument separator).
  - Implement file extension whitelisting and secret file exclusions (`.env*`, `*.pem`, etc.).
  - **Zero code execution** during file traversal.
  - Implement language-specific AST / symbol extractors (Python AST + JS/TS regex for interfaces, types, classes, default exports).
  - *Dependencies*: Task 1.2
  - *Acceptance Criteria*: Extracts AST symbols, imports, classes, and API routes cleanly.

- [x] **Task 2.2: Repository Fact Matrix Extractor & Token Budgeter**
  - Analyze extracted AST data to compile `RepositoryFactMatrix`:
    - List active abstractions (e.g. SQLModel, Pydantic, FastAPI pagination, custom Auth).
    - List explicitly absent abstractions (e.g. NO streaming helpers, NO rate limiting middleware, NO Redis).
  - Wrap repository snippets in untrusted data delimiters (`<untrusted_repository_data>`).
  - *Dependencies*: Task 2.1
  - *Acceptance Criteria*: Generates an accurate, empirical Fact Matrix for target repositories.

---

### Phase 3: Assessment Analyzer & Trajectory Simulator
- [x] **Task 3.1: Task Impact & Fact Matching Analyzer**
  - Map the candidate task against the `RepositoryFactMatrix` to identify existing code patterns the task touches vs new patterns it requires.
  - *Dependencies*: Task 2.2
  - *Acceptance Criteria*: Pinpoints touched modules and highlights any missing abstractions required by the task.

- [x] **Task 3.2: Differentiated Candidate Strategy Simulator**
  - Implement LLM simulation prompts generating detailed inspection trajectories:
    1. **AI-Dependent Engineer**: Inspects minimal files (e.g. 1 file), relies on default AI generation, misses existing repository abstractions/contracts.
    2. **Naive AI-Assisted Engineer**: Inspects route handlers, tests happy-path, misses non-obvious failure modes.
    3. **Strong AI-Native Engineer**: Inspects full route + model + CRUD layer, reuses existing repository abstractions, explicitly writes edge-case tests.
  - *Dependencies*: Task 3.1
  - *Acceptance Criteria*: Simulator outputs granular, file-level inspection trajectories for each candidate profile.

---

### Phase 4: Grounded Diagnostic Evaluator & Task Upgrade Engine
- [x] **Task 4.1: Evidence-Grounded Signal Evaluator**
  - Evaluate 5 core metrics with mandatory evidence linkages.
  - Detect **Artificial Complexity**: If a task introduces technologies/constraints ungrounded in the repo (e.g., Redis + Elasticsearch on a simple app), flag as **High Complexity / Low-Medium Signal**.
  - *Dependencies*: Task 3.2
  - *Acceptance Criteria*: Accurately scores task signal while penalizing ungrounded artificial complexity.

- [x] **Task 4.2: Evidence-Grounded Task Upgrade Generator**
  - Generate task recommendations constrained strictly by the `RepositoryFactMatrix`.
  - Validate upgrade suggestions against the "Forbidden Recommendations" list.
  - Output explicit `EvidenceGroundingChain` (Repository Facts → Task Implications → Recommendation Rationale).
  - *Dependencies*: Task 4.1
  - *Acceptance Criteria*: Upgraded tasks leverage *actual* existing codebase conventions (e.g. existing pagination helpers) and never hallucinate non-existent middleware or architecture.

---

### Phase 5: API Layer & Async Execution
- [x] **Task 5.1: REST Endpoints & Async Pipeline Orchestrator**
  - Implement `/api/v1/analyze` (POST) to trigger background analysis pipeline.
  - Implement `/api/v1/health` (GET) for system health check.
  - *Dependencies*: Task 4.2
  - *Acceptance Criteria*: Pipeline execution returns complete `EvidenceGroundingChain` and candidate trajectories in < 30 seconds.

---

### Phase 6: Frontend Visual Dashboard
- [x] **Task 6.1: Visual Dashboard & Grounded Evidence UI**
  - Build GitHub Repo input field, task description text area, and sample preset loader.
  - Build **Repository Evidence & Grounding Card** (Observed Facts vs Task Implications).
  - Build **Candidate Inspection Trajectory Viewer** (comparing file-by-file inspection steps of AI-Dependent vs Strong AI-Native engineers).
  - Build **Evidence-Backed Task Upgrade View** with Grounding Confidence rating.
  - *Dependencies*: Task 5.1
  - *Acceptance Criteria*: Responsive dark-mode dashboard displaying transparent repository evidence and inspection trajectories.

---

## ⚡ Edge Cases & Handling Strategies

| Edge Case | Potential Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **LLM Hallucinating Non-Existent Repo Constraints** | Invalid / misleading task recommendation | Enforce Repository Fact Matrix verification step prior to outputting recommendations. Reject ungrounded abstractions. |
| **Artificial Task Complexity (e.g., Microservices on Monolith)** | Misleading high score | Explicit Artificial Complexity detector that penalizes tasks introducing ungrounded architectural bloat. |
| **User Misinterpreting Score as Scientific Truth** | Over-reliance on numerical metric | UI disclaimer badge marking scores as "Heuristic Diagnostic Feedback", emphasizing qualitative evidence. |
| **Prompt Injection in Repo (README/Code)** | LLM instruction hijacking | Strict separation of System instructions and Untrusted Data blocks in prompt templates. |
| **Secrets in Repo (`.env`, keys)** | Sensitive data leaked to LLM | Mandatory regex filter & filename exclusion list before string context aggregation. |
| **Malicious Path Traversal (`../../`)** | File system exposure | Validate absolute path canonicalization (`realpath`) within sandboxed temp dir. |

---

## 🧪 Verification Plan

### Automated Tests
- **Backend Security & Unit Tests (`pytest`)**:
  - Test `RepositoryFactMatrix` extractor on mock repos with and without specific abstractions (e.g., verify it correctly identifies absence of rate-limiting middleware).
  - Test anti-hallucination guardrail on recommendation generator.
  - Test evidence-attribution mapping for all calculated heuristic metrics.
  - Test URL sanitizer, path traversal protection, and secret exclusion filters.

### Manual Verification
- Test with 3 real GitHub repositories:
  1. *Small Python FastAPI project* (Verify recommendation uses existing SQLModel pagination rather than hallucinating streaming/rate-limiting).
  2. *TypeScript/Node.js backend*.
  3. *Monorepo / Multi-module app*.
- Validate UI rendering of the Evidence Grounding Card and Candidate Inspection Trajectories.
