# Implementation Plan - Redline 🎯

**Redline** is an AI-powered pre-flight testing and red-teaming tool for AI-native coding assessments. It analyzes a GitHub repository and a candidate task, simulates AI-assisted solving strategies across 3 candidate profiles, evaluates signal strength vs AI solvability, and provides evidence-backed task upgrades.

---

## 📊 Diagnostic Nature & Non-Statistical Disclaimer

> **Core Product Principle**: The Assessment Health Score is a **heuristic diagnostic**, NOT a scientifically validated or statistically predictive measurement.

1. **Evidence First**: The system prioritizes concrete, repository-specific qualitative evidence and architectural reasoning over arbitrary numeric metrics.
2. **Transparent Scoring Rationale**: Every sub-score and dimension (AI Solvability, Reasoning Signal, Repo Depth, etc.) must explicitly link to the specific repository structures, file paths, and simulation evidence that contributed to it.
3. **No Validity Claims**: Redline makes **no claims of statistical validity or objective candidate performance prediction**. It functions purely as an assessment-design heuristic and red-teaming tool for engineering managers and interview designers.

---

## 🛡️ Security Requirements & Data Boundaries

> **Core Principle**: All GitHub repository contents must be treated strictly as **untrusted DATA**, never as system or operational instructions.

The system enforces the following security boundaries across all components:
1. **Instruction Boundary Isolation**: System prompts explicitly treat repository code, READMEs, docs, comments, and config files as inert passive data. Content inside repositories must never override Redline's system instructions or evaluation prompt boundaries (Prompt Injection Protection).
2. **Zero Code Execution**: Redline performs static code structure & AST analysis only. Arbitrary repository code, scripts, build steps, or tests are **never executed**.
3. **Path Traversal Prevention**: Strict canonical path validation on cloned/scanned directory paths prevents reading files outside the isolated repository temporary folder.
4. **Clone & Scan Guardrails**:
   - Limit clone depth (`--depth 1`).
   - Repository size limit enforcement (< 50 MB total context scan limit).
   - Strict URL schema and format validation (allow only valid `https://github.com/org/repo` patterns).
5. **File Type Whitelisting**: Analyzes source code files only (`.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.go`, `.java`, `.rs`, `.cpp`, `.c`, `.h`, `.cs`, `.json`, `.md`).
6. **Secret Exclusion & Redaction**: Automatically excludes sensitive file patterns (`.env`, `.env.*`, `*.pem`, `*.key`, `credentials`, `id_rsa`, `secrets.*`) and strips detected API key string patterns prior to prompt aggregation.

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
│ Phase 2: Secure Repository Context Extractor            │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 3: Assessment Analysis & Strategy Simulation Engine│
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 4: Signal Scoring & Task Recommendation Generator │
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
- [ ] **Task 1.1: Environment & Project Bootstrap**
  - Setup Python backend directory structure (`backend/app/{api,core,services,models}`) and Frontend Vite React TypeScript application (`frontend/`).
  - Configure `.env` management (Gemini API Key, CORS origins, file size limits).
  - *Dependencies*: None
  - *Acceptance Criteria*: Backend initializes with FastAPI (`/health` returns status OK); Frontend compiles with clean UI shell.

- [ ] **Task 1.2: Pydantic Data Contracts & Validation Schemas**
  - Define input schemas (`AnalysisRequest`, `RepoSource`) with strict URL regex validation for GitHub repositories.
  - Define output schemas (`RepoContextSummary`, `SimulationProfileResult`, `SignalHealthReport`, `TaskRecommendation`, `FullAssessmentResult`). Include evidence linkage fields for each metric score.
  - *Dependencies*: Task 1.1
  - *Acceptance Criteria*: Invalid URLs or malformed payloads fail Pydantic validation cleanly.

---

### Phase 2: Secure Repository Analyzer & Context Extractor
- [ ] **Task 2.1: Secure Ingestion, Path Sanitation & AST File Parsing**
  - Build helper to clone GitHub repos securely (`--depth 1`, target directory path traversal protection via `os.path.realpath` checks).
  - Implement file extension whitelisting (`.py`, `.ts`, `.js`, etc.) and explicit exclusion of secret files (`.env*`, `*.pem`, `credentials`, etc.).
  - Ensure **zero code execution** during file traversal.
  - Implement language-specific lightweight AST / structure extractors.
  - *Dependencies*: Task 1.2
  - *Acceptance Criteria*: Correctly constructs file tree map and extracts API routes while ignoring secret files and binary assets.

- [ ] **Task 2.2: Context Summarizer, Prompt Framing & Token Budgeter**
  - Implement token-budgeting logic to build concise LLM context.
  - Wrap repository snippets in explicit DATA framing delimiters (e.g. `<untrusted_repository_data>`) with system instructions stating repository contents are passive data only.
  - *Dependencies*: Task 2.1
  - *Acceptance Criteria*: Context payload stays under target token budget and isolates untrusted repo code from system prompts.

---

### Phase 3: Assessment Analyzer & Strategy Simulator
- [ ] **Task 3.1: Task Impact Analyzer**
  - Implement LLM prompt pipeline to map the candidate task against repo context, determining impacted modules, touched files, and architectural depth required.
  - *Dependencies*: Task 2.2
  - *Acceptance Criteria*: Returns structured JSON listing affected modules and potential side effects.

- [ ] **Task 3.2: Strategy Simulator (3 Candidate Profiles)**
  - Implement LLM-based structured simulation prompts for:
    1. **AI-Dependent Engineer**: Broad delegation, zero context verification, happy-path reliance.
    2. **Naive AI-Assisted Engineer**: Partial context inspection, superficial testing, misses non-obvious failure modes.
    3. **Strong AI-Native Engineer**: Deep architectural context inspection, targeted AI prompts, rigorous edge-case verification.
  - *Dependencies*: Task 3.1
  - *Acceptance Criteria*: Produces distinct simulation steps, probable bugs/misses, and execution likelihood for each profile.

---

### Phase 4: Transparent Diagnostic Evaluator & Task Upgrade Generator
- [ ] **Task 4.1: Heuristic Assessment Signal Evaluator**
  - Evaluate 5 core metrics: AI Solvability, Reasoning Signal, Repo Depth, Architectural Judgment, Verification Requirement.
  - Ensure each score includes mandatory **contributing evidence quotes/references** explaining *why* the score was assigned.
  - Explicitly frame results as heuristic diagnostic feedback.
  - *Dependencies*: Task 3.2
  - *Acceptance Criteria*: Computes transparent scores backed by specific repository file links and simulation arguments.

- [ ] **Task 4.2: Recommendation & Upgrade Generator**
  - Generate upgraded task descriptions with explicit constraints (e.g. streaming memory limits, error handling contracts, interface reuse requirements) that prevent lazy AI delegation.
  - *Dependencies*: Task 4.1
  - *Acceptance Criteria*: Outputs original vs upgraded task with rationale and risk mitigation details.

---

### Phase 5: API Layer & Async Execution
- [ ] **Task 5.1: REST Endpoints & Async Pipeline Orchestrator**
  - Implement `/api/v1/analyze` (POST) to trigger background analysis pipeline.
  - Implement `/api/v1/analysis/{job_id}` (GET) for status polling or WebSockets for real-time progress updates.
  - *Dependencies*: Task 4.2
  - *Acceptance Criteria*: End-to-end API execution completes in < 30 seconds for typical sample repositories.

---

### Phase 6: Frontend Visual Dashboard
- [ ] **Task 6.1: Dashboard UI Components & Assessment Form**
  - Build GitHub Repo input field, task description text area, and sample preset loader.
  - Build Diagnostic Health Score Card (Radar/Bar charts, evidence breakdown accordions, diagnostic disclaimer badge).
  - Build Candidate Profile Simulator comparison view.
  - Build Task Upgrade comparison card (Original vs Recommended Task with copy action).
  - *Dependencies*: Task 5.1
  - *Acceptance Criteria*: Responsive, sleek dark-mode interface with clear visual hierarchy, transparent score evidence linkages, and working demo presets.

---

## ⚡ Edge Cases & Handling Strategies

| Edge Case | Potential Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **User Misinterpreting Score as Scientific Truth** | Over-reliance on numerical metric | UI disclaimer badge clearly marking scores as "Heuristic Diagnostic Feedback", emphasizing qualitative evidence. |
| **Prompt Injection in Repo (README/Code)** | LLM instruction hijacking | Strict separation of System instructions and Untrusted Data blocks in prompt templates. |
| **Secrets in Repo (`.env`, keys)** | Sensitive data leaked to LLM | Mandatory regex filter & filename exclusion list before string context aggregation. |
| **Malicious Path Traversal (`../../`)** | File system exposure | Validate absolute path canonicalization (`realpath`) within sandboxed temp dir. |
| **Large Repository (>10k files)** | LLM context window overflow, slow processing | Strict file whitelist, depth 1 clone, ignore vendor/build dirs, symbol extraction only. |
| **Invalid / Private Repo URL** | Pipeline failure / command injection | URL schema validation (HTTPS only, github.com regex), no shell parameter injection in git commands. |
| **Gemini API Rate Limiting / Timeout** | Pipeline execution failure | Implement retries with exponential backoff, prompt response caching for repo context summaries. |

---

## 🧪 Verification Plan

### Automated Tests
- **Backend Security & Unit Tests (`pytest`)**:
  - Test evidence-attribution mapping for all calculated heuristic metrics.
  - Test URL sanitizer and validator against invalid/malicious GitHub URLs.
  - Test secret exclusion filter on repositories containing `.env`, `.pem`, and dummy API keys.
  - Test path traversal protection helper against synthetic `../../` path inputs.
  - Test repository tree crawler and AST parser on sample mock repos.
  - Test Pydantic schema validation for LLM structured output parsing.

### Manual Verification
- Test with 3 real GitHub repositories:
  1. *Small Python FastAPI project* (Simple endpoint modification task vs complex async stream task).
  2. *TypeScript/Node.js backend* (Database migration/middleware task).
  3. *Monorepo / Multi-module app* (Cross-module dependency refactoring task).
- Validate UI rendering, transparent evidence linkage display, and real-time step progress feedback on the frontend dashboard.
