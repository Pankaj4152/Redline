# Architecture Specification - Redline 🎯

## 1. System Architecture

Redline uses a lightweight, modular pipe-and-filter architecture designed for fast execution, low latency, structured LLM reasoning, and **strict repository evidence grounding**.

```text
                                FRONTEND (React + Vite + Vanilla CSS)
                     (Displays Grounding Facts, Candidate Trajectories & Upgrades)
                                                      │
                                                      │ REST / JSON API
                                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       BACKEND (FastAPI / Async Python)                                 │
│                                                                                                        │
│   ┌─────────────────────┐       ┌──────────────────────┐       ┌──────────────────────────────────┐   │
│   │ 1. Git Ingestion &  │────►│ 2. Repo Fact Matrix  │────►│ 3. Assessment & Impact Analyzer │   │
│   │    AST Extractor    │       │    Extractor Engine  │       │      (Gemini Structured Output)   │   │
│   └─────────────────────┘       └──────────────────────┘       └──────────────────────────────────┘   │
│              │                              │                                    │                     │
│  [Security Policy Engine]       [Anti-Hallucination]                             ▼                     │
│  (Sanitization, Whitelisting,   (Observed vs Absent             ┌──────────────────────────────────┐   │
│   Secret Filter, Data Boundary)  Abstractions Matrix)           │ 4. Trajectory Strategy Simulator │   │
│                                             │                  │  (File Inspection Step Comparison│   │
│                                             ▼                  └──────────────────┬───────────────┘   │
│   ┌─────────────────────┐       ┌──────────────────────┐                          │                   │
│   │ 6. Grounded Upgrade │◄──────│ 5. Grounded Signal   │◄─────────────────────────┘                   │
│   │    Generator Engine │       │    Evaluation Engine │                                              │
│   │ (Fact-Checked Upgrades)     │ (Evidence & Fact Map)│                                              │
│   └─────────────────────┘       └──────────────────────┘                                              │
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
- **Security Enforcements**: Enforces GitHub URL validation, single-depth shallow clones (`--depth 1`), canonical path verification (`os.path.realpath`), file extension whitelisting, secret file exclusions, and zero code execution.
- **Output**: Structured tree map and sanitized symbol summaries.

### 2.2 Repository Fact Matrix Extractor (`RepoFactMatrixService`)
- **Responsibility**: Analyzes AST symbols and codebase structure to generate an explicit `RepositoryFactMatrix`:
  - **Observed Abstractions**: Existing frameworks, pagination patterns, data access layers, authentication decorators, database connection pools.
  - **Absent Abstractions**: Explicitly logs abstractions that DO NOT exist in the repository (e.g., NO streaming helpers, NO rate-limiting middleware, NO Redis cache).
- **Output**: `RepositoryFactMatrix` payload used to ground recommendations and prevent LLM hallucinations.

### 2.3 Assessment Impact Analyzer (`TaskImpactService`)
- **Responsibility**: Maps candidate tasks against the `RepositoryFactMatrix` to identify touched modules and required new abstractions.

### 2.4 Candidate Strategy Simulator Engine (`StrategySimulatorService`)
- **Responsibility**: Simulates candidate solving behavior by producing file-by-file inspection trajectories:
  1. **AI-Dependent Engineer Trajectory**: Inspects 1 file -> Accepts raw AI output -> Misses existing repo abstractions/pagination contracts.
  2. **Naive AI-Assisted Engineer Trajectory**: Inspects routes -> Manually tweaks syntax -> Misses non-obvious failure modes.
  3. **Strong AI-Native Engineer Trajectory**: Inspects route + model + CRUD layers -> Reuses existing abstractions -> Explicitly writes boundary tests.

### 2.5 Grounded Heuristic Signal Evaluator (`SignalEvaluationService`)
- **Responsibility**: Evaluates signal score across 5 key dimensions with mandatory repository evidence linkages.
- **Artificial Complexity Penalty**: Automatically detects and penalizes tasks that introduce ungrounded architectural bloat (e.g. adding microservices to a simple monolith).

### 2.6 Grounded Upgrade Generator Engine (`UpgradeGeneratorService`)
- **Responsibility**: Generates upgraded tasks strictly validated against the `RepositoryFactMatrix`.
- **Anti-Hallucination Guardrail**: Rejects recommendations that require non-existent abstractions (e.g. rate-limiting middleware) unless explicitly justified.
- **Output**: `EvidenceGroundingChain` (Repository Facts -> Task Implications -> Upgraded Task Rationale).

---

## 3. Data Flow

1. **User Request**: User inputs GitHub Repo URL (`https://github.com/...`) and Candidate Task Prompt into the React dashboard.
2. **URL & Input Sanitization**: Backend validates GitHub URL schema and sanitizes task prompt inputs.
3. **Secure Ingestion & AST Extraction**: Backend scans repo, parses file tree + AST symbols into `RepoContextSummary`.
4. **Fact Matrix Compilation**: `RepoFactMatrixService` identifies active vs absent repository abstractions.
5. **Task Mapping**: `TaskImpactService` maps candidate task against the Fact Matrix.
6. **Trajectory Simulation**: Backend runs simulation producing file-by-file inspection trajectories for all 3 profiles.
7. **Signal Evaluation**: Backend calculates signal scores, penalizing ungrounded artificial complexity.
8. **Fact-Checked Upgrade**: Backend generates upgraded task description constrained strictly by the `RepositoryFactMatrix`.
9. **Response Delivery**: Full `FullAssessmentResult` object returned to the frontend for visualization.

---

## 4. API Specification

### `POST /api/v1/analyze`
**Request Payload**:
```json
{
  "repo_url": "https://github.com/example/sample-fastapi-app",
  "branch": "main",
  "task_description": "Add a /api/items/search endpoint that accepts a query and returns matching items.",
  "sample_preset_id": null
}
```

**Response Payload**:
```json
{
  "job_id": "job_987654321",
  "status": "completed",
  "diagnostic_disclaimer": "The Assessment Health Score is a heuristic design diagnostic based on static code structure and simulated AI solving strategies. It is not a statistically validated measurement.",
  "summary": {
    "overall_health_score": 30,
    "verdict": "Weak Signal - Highly AI-Delegable",
    "ai_solvability": "HIGH",
    "reasoning_signal": "LOW"
  },
  "fact_matrix": {
    "observed_abstractions": [
      "Item queries loaded via SQLModel in app/crud/items.py",
      "Existing list endpoint in app/api/routes/items.py uses page/limit pagination"
    ],
    "absent_abstractions": [
      "No streaming response implementation detected",
      "No custom rate-limiting middleware detected"
    ]
  },
  "evidence_grounding_chain": {
    "repository_facts": [
      "app/api/routes/items.py contains item retrieval logic.",
      "app/crud/items.py defines SQLModel query execution.",
      "Existing list endpoint mandates pagination parameters."
    ],
    "task_implications": [
      "Candidate task can currently be solved by copying single route handler.",
      "Candidate should be forced to reuse existing pagination abstractions."
    ],
    "forbidden_hallucinated_recommendations": [
      "Do NOT recommend streaming response memory limits (no streaming helper exists).",
      "Do NOT recommend preserving rate-limiting middleware (no rate limiter exists)."
    ],
    "grounding_confidence": "HIGH"
  },
  "metrics": {
    "ai_solvability": {
      "score": 90,
      "contributing_evidence": ["Raw AI prompt generates working endpoint in single attempt without reading CRUD abstraction."]
    },
    "reasoning_signal": {
      "score": 25,
      "contributing_evidence": ["Task requires zero cross-module architectural decisions."]
    },
    "repo_depth": {
      "score": 20,
      "contributing_evidence": ["Candidate does not need to inspect app/crud/items.py or database pool models."]
    },
    "architectural_judgment": {
      "score": 15,
      "contributing_evidence": ["Standard boilerplate pattern pasted without evaluating query constraints."]
    },
    "verification_requirement": {
      "score": 30,
      "contributing_evidence": ["Happy-path query returns HTTP 200; edge cases unexercised."]
    }
  },
  "simulations": [
    {
      "profile": "AI-Dependent Engineer",
      "success_likelihood": "HIGH",
      "delegation_level": "95%",
      "files_inspected": ["app/api/routes/items.py"],
      "missed_risks": ["Bypassed existing pagination helper", "No boundary check for empty search string"]
    },
    {
      "profile": "Naive AI-Assisted Engineer",
      "success_likelihood": "HIGH",
      "delegation_level": "70%",
      "files_inspected": ["app/api/routes/items.py", "app/models/item.py"],
      "missed_risks": ["Missed handling queries beyond available result set"]
    },
    {
      "profile": "Strong AI-Native Engineer",
      "success_likelihood": "HIGH",
      "delegation_level": "40%",
      "files_inspected": ["app/api/routes/items.py", "app/crud/items.py", "app/models/item.py"],
      "reused_abstractions": ["Reused SQLModel query pagination helper from app/crud/items.py"],
      "added_verifications": ["Added unit test covering empty query string and non-matching search term"]
    }
  ],
  "recommendations": {
    "original_task": "Add a /api/items/search endpoint that accepts a query and returns matching items.",
    "upgraded_task": "Add a /api/items/search endpoint that reuses the repository's existing pagination helper from app/crud/items.py. Handle empty search queries, non-matching terms, and request pages beyond available results with appropriate HTTP error codes and test coverage.",
    "rationale": "Grounded directly in existing repository pagination patterns. Forces candidate to inspect CRUD layers rather than pasting isolated endpoint snippet."
  }
}
```

---

## 5. Database & Storage Structure

For the **Proof-of-Concept MVP**, complex external persistent database management is **not required**.
- **In-Memory Cache**: Python dictionary cache storing recent analysis jobs indexed by `job_id` or `hash(repo_url + task)`.
- **Local File Cache**: Temporary working folders (`/tmp/redline_repos/` or local `backend/scratch/`) with automatic cleanup.

---

## 6. Important Technical Decisions

1. **Repository Fact Matrix & Anti-Hallucination Guardrail**:
   - *Decision*: Extract an explicit matrix of observed vs absent codebase abstractions prior to generating recommendations.
   - *Rationale*: Prevents LLM from inventing non-existent constraints (e.g. rate-limiting middleware, 50MB streaming limits) and congratulating itself for solving them.

2. **File-Level Candidate Inspection Trajectories**:
   - *Decision*: Model candidate profiles using specific file inspection paths (e.g., AI-dependent inspects 1 file vs Strong engineer inspects route + CRUD + model files).
   - *Rationale*: Replaces vague binary outcomes with convincing, step-by-step evidence of what strong engineers notice vs AI delegators.

3. **Artificial Complexity Detector**:
   - *Decision*: Explicitly penalize tasks that introduce ungrounded architectural complexity.
   - *Rationale*: Prevents prompt gaming where users or LLMs simply pile on random technologies (Elasticsearch, Redis) to artificially inflate assessment scores.
