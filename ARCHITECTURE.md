# Architecture Specification - Redline 🎯

## 1. System Architecture

Redline uses a lightweight, modular pipe-and-filter architecture designed for fast execution, low latency, and structured LLM reasoning.

```text
                                FRONTEND (React + Vite + Tailwind/Vanilla CSS)
                                 (Displays Heuristic Diagnostic Feedback & Evidence)
                                                      │
                                                      │ REST / JSON API
                                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       BACKEND (FastAPI / Async Python)                                 │
│                                                                                                        │
│   ┌─────────────────────┐       ┌──────────────────────┐       ┌──────────────────────────────────┐   │
│   │ 1. Git & Repo Ingestion│────►│ 2. Context Aggregator │────►│ 3. Assessment & Impact Analyzer │   │
│   │    & AST Extractor  │       │   & Token Budgeter   │       │      (Gemini Structured Output)   │   │
│   └─────────────────────┘       └──────────────────────┘       └──────────────────────────────────┘   │
│              │                                                                   │                     │
│  [Security Policy Engine]                                                        ▼                     │
│  (Sanitization, Whitelisting,                                  ┌──────────────────────────────────┐   │
│   Secret Filter, Data Boundary) │ 6. Report & Upgrade │◄──────│ 5. Heuristic Signal │◄──────│ 4. Candidate Strategy Simulator  │   │
│                                 │    Generator Engine │       │    Evaluation Engine │       │   (3 AI Candidate Behaviors)     │   │
│                                 │                     │       │ (Transparent Evidence│       │                              │   │
│                                 │                     │       │    Linkage Mapping)  │       │                              │   │
│                                 └─────────────────────┘       └──────────────────────┘       └──────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                      │
                                                      │ SDK Calls
                                                      ▼
                                           Google Gemini 2.5/3.6 API
```

---

## 2. Component Descriptions

### 2.1 Repository Ingestion & AST Extractor (`RepoAnalyzerService`)
- **Responsibility**: Clones or scans local/remote GitHub repositories. Extracts directory maps, file contents, language constructs (functions, classes, imports, exported routes) while filtering out vendor/build artifacts (`node_modules`, `.venv`, `.git`, binary files).
- **Security Enforcements**:
  - Enforces GitHub repository URL validation (regex filter restricting to `https://github.com/org/repo` format).
  - Enforces single-depth shallow clones (`--depth 1`) and strict repository size caps (<50MB).
  - Enforces canonical path verification (`os.path.realpath`) to block directory traversal attacks (`../`).
  - Enforces strict file extension whitelisting (`.py`, `.ts`, `.js`, etc.) and secret file exclusions (`.env*`, `*.pem`, `credentials`, etc.).
  - **Zero Execution Rule**: Analyzes code statically. Arbitrary repository scripts or build commands are **never executed**.
- **Output**: Structured tree map and sanitized symbol summaries.

### 2.2 Context Aggregator & Token Budgeter (`ContextBudgetService`)
- **Responsibility**: Truncates and formats repository summaries to fit optimal LLM prompt windows (e.g. max 15,000 tokens) without losing critical architectural interfaces or data schemas.
- **Security Policy**: Wraps all repository code, comments, READMEs, and config file snippets in explicit untrusted data block delimiters (e.g. `<untrusted_repository_data>`). Enforces system prompt boundary instructions ensuring repo contents are parsed exclusively as **passive DATA** and cannot override Redline evaluation instructions.

### 2.3 Assessment Impact Analyzer (`TaskImpactService`)
- **Responsibility**: Evaluates the candidate task against the repository context to determine which modules are touched, cross-module dependencies, and potential side effects.

### 2.4 Candidate Strategy Simulator Engine (`StrategySimulatorService`)
- **Responsibility**: Runs 3 structured LLM simulations:
  1. **AI-Dependent Engineer**: Simulates a candidate relying entirely on broad natural-language prompts.
  2. **Naive AI-Assisted Engineer**: Simulates a candidate doing basic manual edits and happy-path checks.
  3. **Strong AI-Native Engineer**: Simulates a candidate inspecting architectural constraints, writing targeted prompts, and validating non-obvious failure modes.

### 2.5 Heuristic Signal Evaluator (`SignalEvaluationService`)
- **Responsibility**: Calculates qualitative heuristic diagnostic scores across 5 key dimensions (AI Solvability, Reasoning Signal, Repo Depth, Architectural Judgment, Verification Requirement).
- **Diagnostic Transparency Rule**: Every calculated dimension MUST include an explicit list of contributing qualitative evidence statements and specific file/code references. The evaluator functions purely as a **heuristic assessment design diagnostic**, making no claims of statistical validity or predictive candidate benchmarking.

### 2.6 Report & Upgrade Generator (`UpgradeGeneratorService`)
- **Responsibility**: Generates actionable, repository-specific task tweaks that elevate the required engineering depth without inflating task duration.

---

## 3. Data Flow

1. **User Request**: User inputs GitHub Repo URL (`https://github.com/...`) and Candidate Task Prompt into the React dashboard.
2. **URL & Input Sanitization**: Backend validates GitHub URL schema and sanitizes task prompt inputs.
3. **Secure Ingestion & Parsing**: Backend clones/scans the repo, parses file tree + AST symbols into `RepoContextSummary`, ignoring secret files and executing zero code.
4. **Data Isolation Framing**: `ContextBudgetService` encapsulates repo text into untrusted data delimiters.
5. **Task Mapping**: `TaskImpactService` calls Gemini API to pinpoint affected files and architectural boundaries.
6. **Strategy Simulation**: Backend runs simulation calls for the 3 candidate profiles using structured Pydantic schemas.
7. **Diagnostic Signal Scoring**: Backend computes heuristic metric scores, attaching specific evidence quotes and file links to each dimension.
8. **Task Upgrade**: Backend prompts Gemini to formulate an upgraded task description containing hard design constraints.
9. **Response Delivery**: Full `FullAssessmentResult` object returned to the frontend for visualization.

---

## 4. API Specification

### `POST /api/v1/analyze`
**Request Payload**:
```json
{
  "repo_url": "https://github.com/example/sample-fastapi-app",
  "branch": "main",
  "task_description": "Add a CSV export endpoint for user transaction history.",
  "sample_preset_id": null
}
```

**Response Payload**:
```json
{
  "job_id": "job_987654321",
  "status": "completed",
  "diagnostic_disclaimer": "The Assessment Health Score is a heuristic design diagnostic based on static code structure and simulated AI solving strategies. It is not a statistically validated measurement or candidate prediction.",
  "summary": {
    "overall_health_score": 42,
    "verdict": "Weak Signal - Highly AI-Delegable",
    "ai_solvability": "HIGH",
    "reasoning_signal": "LOW"
  },
  "metrics": {
    "ai_solvability": {
      "score": 85,
      "contributing_evidence": [
        "Default AI prompt generates a working solution on first try without inspecting repository abstractions.",
        "Modifies only single route handler file (routes/export.py)."
      ]
    },
    "reasoning_signal": {
      "score": 30,
      "contributing_evidence": [
        "Task requires zero cross-module dependency understanding.",
        "No edge-case validation or error contract enforcement demanded."
      ]
    },
    "repo_depth": {
      "score": 25,
      "contributing_evidence": ["No interaction with underlying database connection pool or background worker queues."]
    },
    "architectural_judgment": {
      "score": 20,
      "contributing_evidence": ["Standard boilerplate pattern can be pasted without evaluating memory limits."]
    },
    "verification_requirement": {
      "score": 35,
      "contributing_evidence": ["Superficial happy-path HTTP 200 check passes without stress testing volume bounds."]
    }
  },
  "simulations": [
    {
      "profile": "AI-Dependent Engineer",
      "success_likelihood": "HIGH",
      "delegation_level": "90%",
      "missed_risks": ["Ignores memory limit on large datasets", "Bypasses existing streaming contract"]
    },
    {
      "profile": "Naive AI-Assisted Engineer",
      "success_likelihood": "HIGH",
      "delegation_level": "70%",
      "missed_risks": ["Missing error handling for empty transactions"]
    },
    {
      "profile": "Strong AI-Native Engineer",
      "success_likelihood": "HIGH",
      "delegation_level": "40%",
      "missed_risks": []
    }
  ],
  "recommendations": {
    "original_task": "Add a CSV export endpoint for user transaction history.",
    "upgraded_task": "Add a CSV export endpoint for user transaction history that streams results to stay under 50MB RAM usage and preserves existing API rate-limiting middleware.",
    "rationale": "Forces candidate to inspect memory constraints and integrate with existing custom middleware rather than pasting generic snippet."
  }
}
```

---

## 5. Database & Storage Structure

For the **Proof-of-Concept MVP**, complex external persistent database management (e.g. Postgres) is **not required**.
- **In-Memory Cache**: Python dictionary cache storing recent analysis jobs indexed by `job_id` or `hash(repo_url + task)`.
- **Local File Cache (Scratch/Temp)**: Repositories cloned into temporary working folders (`/tmp/redline_repos/` or local `backend/scratch/`) with automatic cleanup and path isolation.
- **Optional SQLite File**: SQLite DB using `SQLAlchemy` / `aiosqlite` if job persistence across server restarts is desired later.

---

## 6. Important Technical Decisions

1. **Heuristic Diagnostic Framing vs Statistical Validation**:
   - *Decision*: Treat scores purely as heuristic design feedback and mandate transparent evidence linkage for every metric score in the API response.
   - *Rationale*: Prevents misinterpretation of LLM diagnostic evaluations as objective candidate metrics or scientifically validated measurements.

2. **Untrusted Data Boundary & Anti-Prompt-Injection Rule**:
   - *Decision*: Treat all scanned repository contents (READMEs, inline comments, code files, docs) as passive data rather than instructions.
   - *Rationale*: Prevents repository authors or candidates from embedding prompt injections in code comments or READMEs to manipulate Redline's signal evaluation.

3. **Zero Code Execution**:
   - *Decision*: Never execute arbitrary repository scripts, setup scripts, or test runners.
   - *Rationale*: Eliminates code execution vulnerability vectors entirely while maintaining fast static analysis times.

4. **Structured LLM Outputs over Unstructured Parsing**:
   - *Decision*: Utilize Gemini Pydantic/JSON schema enforcement (`response_mime_type="application/json"`).
   - *Rationale*: Eliminates fragile regex string parsing for scores, profiles, and evidence arrays.

5. **Simulated Agent Behavior vs Autonomous Execution**:
   - *Decision*: Use LLM reasoning simulation rather than running actual autonomous coding agents in Docker environments.
   - *Rationale*: Running real coding agents requires heavy container orchestration, long execution times, and high API costs. Simulation provides instant, deterministic feedback in seconds.

6. **AST Symbol Summarization over Raw File Context Dumping**:
   - *Decision*: Extract language symbol outlines instead of feeding entire raw file contents into the prompt.
   - *Rationale*: Maximizes relevance, reduces noise, avoids context overflow, and keeps execution latency under 30 seconds.
