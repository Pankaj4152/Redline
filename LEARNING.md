# Redline — Engineering Learning Log

## Step 1 — FastAPI Foundation & Environment Setup

### Concept
Asynchronous Web Server & Centralized Typed Configuration.

### Why Redline Uses It
Redline needs a high-performance backend server capable of handling multiple concurrent requests (repository cloning, static analysis, LLM strategy simulations) without blocking the thread loop. Additionally, API keys and security limits must be strictly validated before runtime execution.

### How It Works in Our Project
1. **FastAPI (`app/main.py`)**: Provides the root web framework with automatic OpenAPI documentation and CORS support.
2. **Pydantic Settings (`app/core/config.py`)**: Loads environment variables from `.env` and validates their data types (`str`, `bool`, `int`) on application startup.
3. **Health Route (`app/api/health.py`)**: Implements an HTTP `GET /api/v1/health` endpoint used by monitoring services to verify backend availability.

### Important Engineering Decisions

- **Decision**: Use `FastAPI` + `Pydantic Settings` instead of `Flask` or plain `os.environ`.
- **Why**: Redline's core pipeline relies on asynchronous I/O (network requests to GitHub, async Gemini API calls) and schema validation for LLM structured outputs. FastAPI supports `async/await` natively.
- **Alternative**: Flask (synchronous, requires external extensions for type validation) or Django (too heavy, includes unneeded database/ORM overhead for our initial lightweight pipeline).
- **Tradeoff**: Pydantic requires static type declarations upfront, but completely eliminates runtime type-casting bugs and missing config crashes.

### What I Should Know
- `async def` in FastAPI route handlers allows the server event loop to switch context while waiting for I/O bound tasks.
- `Pydantic Settings` automatically casts string environment variables (e.g. `DEBUG="True"`) into Python booleans (`True`), failing fast if a variable is missing or improperly typed.

---

## Step 1.1 — Independent Review: Security, Testing & Architecture Learnings

### Concept 1: Pytest Test Discovery & Environment Determinism
- **What Is Wrong**: Running standard `pytest` inside `backend/` failed with `ModuleNotFoundError: No module named 'app'`.
- **Why It Is Wrong**: Python resolves imports based on `sys.path`. When `pytest` runs directly, the root backend directory is not automatically added as an import root unless defined in configuration or invoked via `python -m pytest`.
- **Engineering Fix**: Add `pytest.ini` with `pythonpath = .` to guarantee environment-independent test resolution across all local environments and CI/CD pipelines.
- **Key Takeaway**: **Environment Determinism**. Test suites should run cleanly regardless of the working directory or runner entry point.

### Concept 2: CORS Security & Web Credentials Boundary
- **What Is Wrong**: Combining `allow_origins=["*"]` with `allow_credentials=True` in `CORSMiddleware`.
- **Why It Is Wrong**: W3C/MDN browser CORS security standards explicitly reject requests where wildcard `*` origins are paired with credential sharing. Furthermore, wildcard origins allow any malicious domain to make requests to the API.
- **Engineering Fix**: Define explicit origins in settings (e.g. `CORS_ORIGINS = ["http://localhost:5173"]`) and pass them to `CORSMiddleware`.
- **Key Takeaway**: **Principle of Least Privilege in Web Security**. Web APIs must specify explicit trusted origins when credentials or session data are involved.

### Concept 3: Fail-Fast Configuration vs Sentinel String Fallbacks
- **What Is Wrong**: Setting default API keys to dummy string fallbacks like `GEMINI_API_KEY = "mock_key_for_dev"`.
- **Why It Is Wrong**: Fake string fallbacks bypass Pydantic's missing-variable check and defer failures until deep inside LLM API call execution (causing confusing 401/403 runtime errors).
- **Engineering Fix**: Validate missing keys at startup and introduce an explicit `USE_MOCK_LLM: bool = True` configuration flag for offline dev and testing.
- **Key Takeaway**: **Fail-Fast Configuration**. Missing or invalid production dependencies should cause immediate server startup failure rather than delayed runtime crashes.

---

## Step 1.2 — Pydantic Data Contracts & Schemas

### Concept
Strict Input Validation & LLM Structured Output Guarantees.

### Why Redline Uses It
LLM outputs are inherently probabilistic and dynamic. Without a formal data contract, downstream components risk throwing `KeyError` or `AttributeError` exceptions when consuming LLM responses. Pydantic models define an explicit boundary for input URL validation and output report schemas.

### How It Works in Our Project
1. **`AnalysisRequest`**: Validates incoming HTTP POST requests, enforcing GitHub URL pattern matching (`https://github.com/org/repo`) and task description length boundaries.
2. **`MetricScore`**: Enforces transparent evidence linkage by mandating a non-empty `contributing_evidence: list[str]` array for every qualitative score.
3. **`FullAssessmentResult`**: Defines the unified JSON payload returned to frontend clients, aggregating candidate simulation results, metric scores, and task recommendations.

### Important Engineering Decisions
- **Decision**: Use Pydantic v2 `@field_validator` regex validation for repository URLs.
- **Why**: Prevents SSRF (Server-Side Request Forgery) and invalid URL parameters from entering git clone pipelines.
- **Alternative**: Unvalidated string inputs or simple `str.startswith("http")` checks.
- **Tradeoff**: Regex validation must explicitly permit local path prefixes (e.g. `./` or absolute paths) to support offline development testing.

### What I Should Know
- Pydantic models serve a dual purpose in Redline: **API payload validation** for HTTP handlers AND **structured output schemas** for Gemini API calls.
- Enforcing `min_length=1` on `contributing_evidence` directly bakes Redline's core product principle (*no arbitrary scores without qualitative evidence*) into our software architecture.

---

## Step 2.1 — Secure Repository Context Extractor & Static AST Parser

### Concept
Untrusted Data Boundary, Canonical Path Sanitation & Zero-Execution AST Parsing.

### Why Redline Uses It
Third-party GitHub repositories submitted by users or candidates are **UNTRUSTED DATA**. They could contain malicious directory traversal paths (`../../etc/passwd`), embedded secrets (`.env`), or executable setup scripts. Redline must safely ingest code, sanitize paths, filter secrets, and extract code symbols without executing any third-party code.

### How It Works in Our Project
1. **Shallow Cloning (`git clone --depth 1`)**: Fetches only the latest commit using a subprocess list (`shell=False` to prevent shell parameter injection).
2. **Canonical Path Check (`is_safe_path`)**: Verifies via `os.path.realpath` that every traversed file strictly resides within the target sandbox directory, blocking path traversal attacks.
3. **Secret & Binary Filter**: Excludes secret patterns (`.env*`, `*.pem`, `credentials`) and restricts analysis to whitelisted source extensions (`.py`, `.ts`, `.js`, etc.).
4. **Zero-Execution AST Parsing**: Uses Python's native `ast` module to statically inspect syntax trees (`ast.ClassDef`, `ast.FunctionDef`, `@app.get` route decorators) without running `import`, `exec()`, or setup scripts.

### Important Engineering Decisions
- **Decision**: Use static AST parsing (Python `ast` module + regex symbol matching) instead of running setup scripts or importing modules.
- **Why**: Enforces Redline's **Zero Code Execution Rule**. Importing untrusted Python modules or executing setup scripts introduces Remote Code Execution (RCE) vulnerabilities.
- **Alternative**: Running `importlib.import_module()` or executing `pytest --collect-only` inside a container.
- **Tradeoff**: Static AST analysis cannot inspect dynamically generated runtime routes or metaprogrammed classes, but provides 100% security and near-instant parsing (< 1 second).

### What I Should Know
- Always use `shell=False` when calling `subprocess.run` with untrusted string inputs to prevent shell command injection.
- `os.path.realpath` resolves symlinks and `../` paths to absolute canonical paths, making it the industry standard for preventing Directory Traversal vulnerabilities.

---

## Step 2.2 — Context Summarizer, Prompt Framing & Token Budgeter

### Concept
Prompt Injection Protection, Untrusted Data Framing & Token Budget Management.

### Why Redline Uses It
Repository text processed by Redline could contain malicious prompt injection attacks embedded inside code comments or `README.md` files attempting to override system evaluation logic. Furthermore, raw repository code can exceed LLM context window caps. Redline must strictly frame untrusted repository text and cap prompt context tokens under strict budget limits.

### How It Works in Our Project
1. **Context Structuring (`format_repository_context`)**: Formats AST symbol outlines, detected routes, and file trees in order of architectural density.
2. **Token Budgeting (`estimate_tokens`, `truncate_to_token_budget`)**: Measures context size (~4 chars/token) and caps output under `MAX_TOKEN_BUDGET` (15,000 tokens).
3. **Data Isolation Framing (`apply_untrusted_data_framing`)**: Encloses repository text strictly inside `<untrusted_repository_data>` tags and prepends a mandatory System Security Notice instructing the LLM to treat content as inert data only.

### Important Engineering Decisions
- **Decision**: Wrap all repository context inside XML delimiters (`<untrusted_repository_data>`) paired with an explicit System Boundary Notice.
- **Why**: Protects Redline against Prompt Injection attacks by instructing the LLM that content inside tag boundaries is passive data and cannot override system instructions.
- **Alternative**: Passing raw repository strings directly into LLM prompts without isolation tags.
- **Tradeoff**: Consumes a few extra tokens for XML tags and security notices, but guarantees robust data boundary isolation.

### What I Should Know
- Prompt Injection is the #1 security vulnerability in LLM applications. Always isolate user-controlled or third-party text using structural tag boundaries.
- Prioritizing high-density context (API routes and symbol outlines) over raw boilerplate code reduces LLM token consumption by 80-90% while maintaining architectural signal.

---

## Step 3.1 — Assessment Task Impact Analyzer

### Concept
LLM Structured Output Pipeline & Blast Radius Mapping.

### Why Redline Uses It
Before Redline can simulate candidate profile strategies or evaluate assessment signal health, it must determine the architectural blast radius of the candidate task. `TaskImpactService` maps which files, modules, and cross-module dependencies will be touched, and determines the architectural depth required (HIGH, MEDIUM, LOW).

### How It Works in Our Project
1. **`TaskImpactResult`**: Pydantic schema holding `impacted_files`, `impacted_modules`, `architectural_depth_required`, `cross_module_dependencies`, `potential_side_effects`, and `summary`.
2. **Dual-Mode Execution**:
   - Live Mode (`USE_MOCK_LLM=False`): Calls Google Gemini API (`google-genai` client) passing `response_mime_type="application/json"` and `response_schema=TaskImpactResult`.
   - Mock Mode (`USE_MOCK_LLM=True`): Uses `generate_mock_impact` heuristic engine to evaluate task scope dynamically based on symbol matching and keyword depth heuristics.

### Important Engineering Decisions
- **Decision**: Use `google-genai` with `response_mime_type="application/json"` and Pydantic schema validation paired with a dynamic heuristic mock engine.
- **Why**: Guarantees machine-parseable JSON responses from Gemini without string parsing errors, while providing instant, deterministic execution for offline dev and test suites.
- **Alternative**: Making live LLM calls during unit testing.
- **Tradeoff**: Mock mode requires writing domain heuristic generators, but provides 100% test reliability and zero API latency.

### What I Should Know
- Gemini API native JSON schema enforcement guarantees that LLMs return JSON matching Pydantic class fields directly.
- Mapping task prompts against static AST symbol lists allows Redline to detect potential unvalidated side effects (e.g. unbounded RAM usage or bypassing rate limiters) before running candidate simulations.

---

## Step 3.2 & 4.1 — Candidate Strategy Simulator & Heuristic Signal Evaluator

### Concept
Simulated Candidate Solving Profiles & Qualitative Evidence-Backed Metric Scoring.

### Why Redline Uses It
Redline evaluates whether a task exposes true engineering signal by comparing how 3 candidate profiles attempt the task (AI-Dependent vs Naive AI-Assisted vs Strong AI-Native), and scoring 5 core health dimensions (`ai_solvability`, `reasoning_signal`, `repo_depth`, `architectural_judgment`, `verification_requirement`).

### How It Works in Our Project
1. **`StrategySimulatorService`**: Generates structured LLM simulations comparing delegation levels (90% vs 70% vs 40%), likelihood of success, reasoning summaries, and missed failure mode risks across candidate profiles.
2. **`SignalEvaluationService`**: Computes qualitative heuristic scores (0-100) across all 5 dimensions and calculates an `overall_health_score` (weighted signal index) and qualitative `verdict`.
3. **Mandatory Evidence Linkage**: Mandates non-empty `contributing_evidence` string lists on every single score object.

### Important Engineering Decisions
- **Decision**: Represent candidate behavior via structured LLM reasoning simulation (`SimulationProfileResult`) rather than running autonomous coding agents inside Docker containers.
- **Why**: Autonomous agent execution takes >5 minutes and requires complex container orchestration. Structured LLM simulation produces instant, deterministic results in <2 seconds.
- **Alternative**: Dockerized execution of autonomous coding agents.
- **Tradeoff**: LLM reasoning simulation is an approximation, but provides instant feedback and fits Redline's proof-of-concept latency goals.

### What I Should Know
- Qualitative evidence linkage ensures Redline never presents arbitrary numbers without explicit repository-backed reasoning.
- Weighted health scoring indexes enable Redline to classify tasks as `Weak Signal - Highly AI-Delegable` vs `Strong Signal - High Architectural Judgment Demanded`.

---

## Step 4.2 — Assessment Recommendation & Task Upgrade Generator

### Concept
Constraint Elevation & Actionable Task Red-Teaming Rationale.

### Why Redline Uses It
Redline not only diagnoses weak-signal assessments, but provides concrete, repository-specific task upgrades that elevate engineering depth without inflating overall task duration.

### How It Works in Our Project
1. **`TaskRecommendation`**: Pydantic schema holding `original_task`, `upgraded_task`, `rationale`, and `added_constraints`.
2. **`UpgradeGeneratorService`**:
   - Inspects `TaskImpactResult` and `SignalHealthReport`.
   - Injects targeted architectural constraints (e.g. streaming RAM limits, custom middleware integration, explicit error contracts) into weak tasks.
   - Provides clear qualitative rationale explaining how the constraint mitigates AI delegation risks.

### Important Engineering Decisions
- **Decision**: Inject targeted architectural constraints (streaming bounds, middleware integration) rather than increasing feature scope.
- **Why**: Adding features makes assessments take hours longer without improving signal. Adding constraints forces deep architectural reasoning while keeping completion time short (<90 min).
- **Alternative**: Asking candidates to build larger multi-page applications.
- **Tradeoff**: Requires precise prompt engineering to keep constraints relevant to existing repository interfaces, but maintains optimal assessment duration.

### What I Should Know
- Red-teaming an assessment task is about finding non-obvious failure modes (e.g., RAM limits or custom middleware) and making them mandatory task constraints.

---

## Step 5.1 — REST API Integration & Async Pipeline Orchestrator

### Concept
Pipe-and-Filter Pipeline Orchestration & End-to-End REST API Layer.

### Why Redline Uses It
To turn isolated analytical micro-services into a functional web product, Redline needs a master orchestrator (`AnalysisOrchestratorService`) that chains all 6 pipeline stages together sequentially, and a REST API route (`POST /api/v1/analyze`) that accepts JSON requests and returns full report payloads.

### How It Works in Our Project
1. **`AnalysisOrchestratorService`**:
   - Receives `AnalysisRequest`.
   - Chains: `RepoAnalyzer` -> `ContextBudgeter` -> `TaskImpact` -> `StrategySimulator` -> `SignalEvaluator` -> `UpgradeGenerator`.
   - Assembles and returns `FullAssessmentResult`.
2. **`POST /api/v1/analyze`**: Route handler in `app/api/analyze.py` accepting `AnalysisRequest` and returning HTTP 200 OK with `FullAssessmentResult`.

### Important Engineering Decisions
- **Decision**: Implement a synchronous/async Pipe-and-Filter Orchestrator (`AnalysisOrchestratorService`) executing all pipeline steps sequentially per HTTP request.
- **Why**: Keeps architecture clean, latency under 3 seconds in mock mode, and eliminates external background worker queue infrastructure (Celery/Redis) for the MVP proof-of-concept.
- **Alternative**: Asynchronous background workers (Celery/Redis) with polling endpoints (`GET /job/{id}`).
- **Tradeoff**: Simplifies deployment and infrastructure dependencies, though background job queues can be introduced later if execution times exceed HTTP timeout thresholds.

### What I Should Know
- The Pipe-and-Filter pattern breaks complex multi-stage data processing into decoupled, testable transform functions.
- End-to-end integration tests using `TestClient` verify that request validation, pipeline execution, and JSON output serialization work seamlessly together.
