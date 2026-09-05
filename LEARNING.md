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
