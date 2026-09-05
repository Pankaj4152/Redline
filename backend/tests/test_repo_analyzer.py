import os
import pytest
from app.services.repo_analyzer import (
    is_safe_path,
    is_secret_or_forbidden_file,
    is_whitelisted_extension,
    RepoAnalyzerService,
    repo_analyzer_service
)
from app.core.config import settings

def test_is_safe_path_valid():
    base = os.path.realpath(settings.BACKEND_DIR)
    target = os.path.join(base, "app", "main.py")
    assert is_safe_path(base, target) is True

def test_is_safe_path_traversal_attack():
    base = os.path.realpath(os.path.join(settings.BACKEND_DIR, "app"))
    traversal_target = os.path.join(base, "..", "..", "etc", "passwd")
    assert is_safe_path(base, traversal_target) is False

def test_secret_file_filtering():
    assert is_secret_or_forbidden_file(".env") is True
    assert is_secret_or_forbidden_file(".env.local") is True
    assert is_secret_or_forbidden_file("server.pem") is True
    assert is_secret_or_forbidden_file("id_rsa") is True
    assert is_secret_or_forbidden_file("credentials") is True
    assert is_secret_or_forbidden_file("app.py") is False
    assert is_secret_or_forbidden_file("schemas.py") is False

def test_whitelisted_extensions():
    assert is_whitelisted_extension("main.py") is True
    assert is_whitelisted_extension("index.ts") is True
    assert is_whitelisted_extension("component.jsx") is True
    assert is_whitelisted_extension("binary.exe") is False
    assert is_whitelisted_extension("lib.dll") is False

def test_python_ast_static_route_parsing():
    content = '''
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/v1/users")
async def get_users():
    return []

class UserResponse:
    pass
'''
    syms, routes = RepoAnalyzerService.extract_python_ast_symbols("api/users.py", content)
    
    # Verify symbols extracted statically
    sym_names = [s.name for s in syms]
    assert "get_users" in sym_names
    assert "UserResponse" in sym_names
    
    # Verify FastAPI route extracted statically
    assert len(routes) == 1
    assert "GET /api/v1/users" in routes[0]

def test_analyze_local_backend_directory():
    summary = repo_analyzer_service.analyze_repository(
        repo_url=str(settings.BACKEND_DIR),
        cleanup=False
    )
    assert summary.total_files > 0
    assert "app/main.py" in summary.file_tree
    # Check that secrets like .env were NOT included in file_tree
    assert not any(".env" in f for f in summary.file_tree)
