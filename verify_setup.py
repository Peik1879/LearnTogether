#!/usr/bin/env python3
"""
StudyDuel Setup Verification

Prüft ob alles korrekt installiert ist.
Usage: python verify_setup.py
"""

import os
import sys
import subprocess
from pathlib import Path

class Setup:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def check(self, name: str, condition: bool, details: str = ""):
        """Check and print result"""
        if condition:
            print(f"✓ {name}")
            self.passed += 1
        else:
            print(f"✗ {name}")
            if details:
                print(f"  → {details}")
            self.failed += 1
    
    def warn(self, name: str, details: str = ""):
        """Warn and print result"""
        print(f"⚠ {name}")
        if details:
            print(f"  → {details}")
        self.warnings += 1
    
    def run_cmd(self, cmd: list, shell: bool = False) -> tuple:
        """Run command and return success + output"""
        try:
            result = subprocess.run(
                cmd,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)

def main():
    setup = Setup()
    root = Path(__file__).parent
    
    print("\n" + "="*60)
    print("StudyDuel Setup Verification")
    print("="*60 + "\n")
    
    # ======================================================================
    # Python Setup
    # ======================================================================
    print("Python Environment")
    print("-" * 60)
    
    setup.check(
        "Python installed",
        sys.version_info >= (3, 8),
        f"Current: {sys.version_info.major}.{sys.version_info.minor}"
    )
    
    backend_dir = root / "backend"
    setup.check(
        "Backend directory exists",
        backend_dir.exists(),
        f"Expected: {backend_dir}"
    )
    
    requirements = backend_dir / "requirements.txt"
    setup.check(
        "requirements.txt exists",
        requirements.exists(),
        f"Expected: {requirements}"
    )
    
    # Check Python packages
    try:
        import fastapi
        setup.check("FastAPI installed", True)
    except ImportError:
        setup.check("FastAPI installed", False, "Run: pip install -r backend/requirements.txt")
    
    try:
        import pydantic
        setup.check("Pydantic installed", True)
    except ImportError:
        setup.check("Pydantic installed", False, "Run: pip install -r backend/requirements.txt")
    
    try:
        import pdfplumber
        setup.check("pdfplumber installed", True)
    except ImportError:
        setup.warn("pdfplumber installed", "Optional: pip install pdfplumber")
    
    print()
    
    # ======================================================================
    # Node Setup
    # ======================================================================
    print("Node.js Environment")
    print("-" * 60)
    
    success, output = setup.run_cmd(["node", "--version"])
    setup.check("Node.js installed", success, "Install from nodejs.org")
    
    success, output = setup.run_cmd(["npm", "--version"])
    setup.check("NPM installed", success, "Install Node.js")
    
    frontend_dir = root / "frontend"
    setup.check(
        "Frontend directory exists",
        frontend_dir.exists(),
        f"Expected: {frontend_dir}"
    )
    
    package_json = frontend_dir / "package.json"
    setup.check(
        "package.json exists",
        package_json.exists(),
        f"Expected: {package_json}"
    )
    
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        setup.check("node_modules installed", True)
    else:
        setup.warn(
            "node_modules not installed",
            "Run: cd frontend && npm install"
        )
    
    print()
    
    # ======================================================================
    # File Structure
    # ======================================================================
    print("File Structure")
    print("-" * 60)
    
    files_to_check = [
        ("backend/app/main.py", backend_dir / "app" / "main.py"),
        ("backend/app/models.py", backend_dir / "app" / "models.py"),
        ("backend/app/services.py", backend_dir / "app" / "services.py"),
        ("backend/app/utils.py", backend_dir / "app" / "utils.py"),
        ("frontend/src/App.tsx", frontend_dir / "src" / "App.tsx"),
        ("frontend/src/pages/Landing.tsx", frontend_dir / "src" / "pages" / "Landing.tsx"),
        ("frontend/src/pages/LearnerPage.tsx", frontend_dir / "src" / "pages" / "LearnerPage.tsx"),
        ("frontend/src/pages/ExaminerPage.tsx", frontend_dir / "src" / "pages" / "ExaminerPage.tsx"),
        ("frontend/src/services/api.ts", frontend_dir / "src" / "services" / "api.ts"),
    ]
    
    for name, path in files_to_check:
        setup.check(f"{name}", path.exists(), f"Expected: {path}")
    
    print()
    
    # ======================================================================
    # Documentation
    # ======================================================================
    print("Documentation")
    print("-" * 60)
    
    docs_to_check = [
        ("README.md", root / "README.md"),
        ("API_REFERENCE.md", root / "API_REFERENCE.md"),
        ("TESTING.md", root / "TESTING.md"),
        ("ARCHITECTURE.md", root / "ARCHITECTURE.md"),
        ("EXTENSIONS.md", root / "EXTENSIONS.md"),
        ("QUICKREF.md", root / "QUICKREF.md"),
    ]
    
    for name, path in docs_to_check:
        setup.check(f"{name}", path.exists(), f"Expected: {path}")
    
    print()
    
    # ======================================================================
    # Ports
    # ======================================================================
    print("Network Ports")
    print("-" * 60)
    
    def is_port_available(port: int) -> bool:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return True
            except OSError:
                return False
    
    setup.check(
        "Port 8000 available (Backend)",
        is_port_available(8000),
        "Kill process using port 8000"
    )
    
    setup.check(
        "Port 5173 available (Frontend)",
        is_port_available(5173),
        "Kill process using port 5173"
    )
    
    print()
    
    # ======================================================================
    # Summary
    # ======================================================================
    print("="*60)
    print("Verification Summary")
    print("="*60)
    print(f"✓ Passed:  {setup.passed}")
    print(f"✗ Failed:  {setup.failed}")
    print(f"⚠ Warnings: {setup.warnings}")
    print()
    
    if setup.failed == 0:
        print("✓ All critical checks passed!")
        print("\nNext steps:")
        print("1. Terminal 1: cd backend && uvicorn app.main:app --reload --port 8000")
        print("2. Terminal 2: cd frontend && npm run dev")
        print("3. Browser:    http://localhost:5173")
        return 0
    else:
        print(f"✗ {setup.failed} critical check(s) failed!")
        print("\nPlease fix the issues above and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
