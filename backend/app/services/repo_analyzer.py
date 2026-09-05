import os
import re
import ast
import shutil
import tempfile
import subprocess
from pathlib import Path
from app.core.config import settings
from app.models.schemas import RepoContextSummary, RepoSymbol

# Allowed file extensions for static analysis
WHITELISTED_EXTENSIONS = {
    ".py", ".ts", ".js", ".jsx", ".tsx",
    ".go", ".java", ".rs", ".cpp", ".c",
    ".h", ".cs", ".json", ".md"
}

# Forbidden directories and sensitive file patterns
FORBIDDEN_DIRS = {
    ".git", ".venv", "venv", "env", "node_modules",
    "__pycache__", ".pytest_cache", ".idea", ".vscode", "dist", "build"
}

FORBIDDEN_FILE_PATTERNS = [
    r"^\.env.*$",
    r".*\.pem$",
    r".*\.key$",
    r"^credentials$",
    r"^id_rsa.*$",
    r"^secrets\..*$"
]


def is_safe_path(base_dir: str, target_path: str) -> bool:
    """
    Enforces canonical path verification to prevent Directory Traversal attacks (../).
    Returns True if target_path strictly resides within base_dir.
    """
    real_base = os.path.realpath(base_dir)
    real_target = os.path.realpath(target_path)
    return real_target.startswith(real_base)


def is_secret_or_forbidden_file(filename: str) -> bool:
    """
    Returns True if the file matches forbidden secret or credential patterns.
    """
    filename_lower = filename.lower()
    for pattern in FORBIDDEN_FILE_PATTERNS:
        if re.match(pattern, filename_lower):
            return True
    return False


def is_whitelisted_extension(filename: str) -> bool:
    """
    Returns True if the file has a whitelisted source extension.
    """
    ext = Path(filename).suffix.lower()
    return ext in WHITELISTED_EXTENSIONS


class RepoAnalyzerService:
    """
    Service responsible for secure repository ingestion, path sanitation,
    secret filtering, and zero-execution static AST parsing.
    """

    @staticmethod
    def clone_repository(repo_url: str, branch: str = "main", target_dir: str | None = None) -> str:
        """
        Clones a GitHub repository securely using shallow clone (--depth 1).
        If repo_url is a local directory path, verifies canonical path safety.
        """
        # If repo_url is a local path
        if os.path.exists(repo_url):
            real_path = os.path.realpath(repo_url)
            backend_root = os.path.realpath(settings.BACKEND_DIR)
            workspace_root = os.path.realpath(os.path.join(backend_root, ".."))
            def is_subpath(child: str, parent: str) -> bool:
                try:
                    p = os.path.realpath(parent)
                    c = os.path.realpath(child)
                    return os.path.commonpath([c, p]) == p
                except ValueError:
                    return False
            if not (is_subpath(real_path, workspace_root) or is_subpath(real_path, tempfile.gettempdir())):
                raise ValueError(f"Local path traversal attempt detected outside workspace: {repo_url}")
            return real_path

        # Create temporary working directory if target_dir not provided
        if not target_dir:
            scratch_root = os.path.join(settings.BACKEND_DIR, "scratch", "repos")
            os.makedirs(scratch_root, exist_ok=True)
            target_dir = tempfile.mkdtemp(dir=scratch_root)

        # Enforce canonical path security on target_dir
        if not is_safe_path(settings.BACKEND_DIR, target_dir) and not target_dir.startswith(tempfile.gettempdir()):
            raise ValueError(f"Target directory path traversal detected: {target_dir}")

        # Execute git clone securely (shell=False prevents command injection, '--' prevents flag injection)
        cmd = ["git", "clone", "--depth", "1", "--branch", branch, "--", repo_url, target_dir]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=60  # 60s timeout limit
            )
        except subprocess.CalledProcessError as e:
            # Fallback retry without explicit branch if branch fails
            cmd_no_branch = ["git", "clone", "--depth", "1", repo_url, target_dir]
            try:
                subprocess.run(cmd_no_branch, capture_output=True, text=True, check=True, timeout=60)
            except subprocess.CalledProcessError as err:
                raise RuntimeError(f"Git clone failed for {repo_url}: {err.stderr}")

        return target_dir

    @staticmethod
    def extract_python_ast_symbols(file_path: str, content: str) -> tuple[list[RepoSymbol], list[str]]:
        """
        Parses Python code statically using ast.parse().
        Extracts classes, functions, and FastAPI/Flask route decorators.
        Guarantees ZERO code execution.
        """
        symbols: list[RepoSymbol] = []
        routes: list[str] = []

        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError:
            # Return empty if file contains syntax errors
            return symbols, routes

        for node in ast.walk(tree):
            # Extract classes
            if isinstance(node, ast.ClassDef):
                symbols.append(RepoSymbol(
                    name=node.name,
                    symbol_type="class",
                    file_path=file_path
                ))
            # Extract functions and methods
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                symbols.append(RepoSymbol(
                    name=node.name,
                    symbol_type="function",
                    file_path=file_path
                ))
                # Check for HTTP route decorators (e.g. @app.get("/path"), @router.post("/path"))
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        func = decorator.func
                        if isinstance(func, ast.Attribute) and func.attr in {"get", "post", "put", "delete", "patch"}:
                            # Extract path argument if available
                            route_path = ""
                            if decorator.args and isinstance(decorator.args[0], ast.Constant):
                                route_path = str(decorator.args[0].value)
                            method = func.attr.upper()
                            routes.append(f"{method} {route_path} ({file_path}::{node.name})")

        return symbols, routes

    @staticmethod
    def extract_js_ts_symbols(file_path: str, content: str) -> tuple[list[RepoSymbol], list[str]]:
        """
        Extracts JS/TS functions, classes, and express/fastify routes using lightweight AST regex.
        Guarantees ZERO code execution.
        """
        symbols: list[RepoSymbol] = []
        routes: list[str] = []

        # Classes
        class_matches = re.findall(r"class\s+([A-Za-z0-9_]+)", content)
        for c in class_matches:
            symbols.append(RepoSymbol(name=c, symbol_type="class", file_path=file_path))

        # Functions / Arrow functions
        func_matches = re.findall(r"(?:function\s+([A-Za-z0-9_]+)|const\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)", content)
        for f1, f2 in func_matches:
            fname = f1 or f2
            if fname:
                symbols.append(RepoSymbol(name=fname, symbol_type="function", file_path=file_path))

        # Express / Fastify routes (app.get('/path', ...), router.post('/path', ...))
        route_matches = re.findall(r"(app|router)\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]", content)
        for _, method, path in route_matches:
            routes.append(f"{method.upper()} {path} ({file_path})")

        return symbols, routes

    def analyze_repository(self, repo_url: str, branch: str = "main", cleanup: bool = True) -> RepoContextSummary:
        """
        Main entry point for repository analysis.
        1. Clones/locates repo safely.
        2. Scans files with path sanitation and secret filtering.
        3. Statically parses AST symbols.
        4. Returns RepoContextSummary.
        """
        repo_dir = self.clone_repository(repo_url, branch)
        repo_name = Path(repo_dir).name if not repo_url.startswith("http") else repo_url.rstrip("/").split("/")[-1]

        file_tree: list[str] = []
        detected_routes: list[str] = []
        key_symbols: list[RepoSymbol] = []
        total_files = 0

        try:
            for root, dirs, files in os.walk(repo_dir):
                # Filter out forbidden directories in-place
                dirs[:] = [d for d in dirs if d not in FORBIDDEN_DIRS]

                for file in files:
                    full_path = os.path.join(root, file)

                    # Security Enforcement 1: Canonical Path Check
                    if not is_safe_path(repo_dir, full_path):
                        continue

                    # Security Enforcement 2: Secret & Credential Filtering
                    if is_secret_or_forbidden_file(file):
                        continue

                    # Security Enforcement 3: Extension Whitelisting
                    if not is_whitelisted_extension(file):
                        continue

                    rel_path = os.path.relpath(full_path, repo_dir).replace("\\", "/")
                    file_tree.append(rel_path)
                    total_files += 1

                    # Read file content safely for AST parsing (limit read size to 1MB per file)
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read(1_000_000)

                        if file.endswith(".py"):
                            syms, rts = self.extract_python_ast_symbols(rel_path, content)
                            key_symbols.extend(syms)
                            detected_routes.extend(rts)
                        elif file.endswith((".js", ".ts", ".jsx", ".tsx")):
                            syms, rts = self.extract_js_ts_symbols(rel_path, content)
                            key_symbols.extend(syms)
                            detected_routes.extend(rts)
                    except Exception:
                        # Skip unreadable or broken files without failing pipeline
                        continue

            return RepoContextSummary(
                repo_name=repo_name,
                total_files=total_files,
                file_tree=file_tree[:100],  # Truncate tree list for context summary cap
                detected_routes=detected_routes,
                key_symbols=key_symbols[:50]  # Cap top symbols
            )
        finally:
            # Clean up cloned temp directory if requested and if it was cloned into scratch
            if cleanup and not os.path.exists(repo_url) and os.path.exists(repo_dir):
                shutil.rmtree(repo_dir, ignore_errors=True)


repo_analyzer_service = RepoAnalyzerService()
