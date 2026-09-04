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
