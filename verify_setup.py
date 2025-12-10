"""
Quick verification script - checks setup without hanging.
"""
import sys
import os

def check_dependencies():
    """Check if required packages are installed."""
    print("Checking dependencies...")
    missing = []
    required = ['fastapi', 'uvicorn', 'sqlalchemy', 'pydantic', 'openai']
    optional = ['anthropic', 'google.generativeai', 'redis']
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING (REQUIRED)")
            missing.append(package)
    
    for package in optional:
        try:
            __import__(package)
            print(f"  ✓ {package} (optional)")
        except ImportError:
            print(f"  ⚠ {package} - not installed (optional)")
    
    if missing:
        print(f"\nMissing required packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    return True

def check_env_file():
    """Check if .env file exists."""
    print("\nChecking .env file...")
    if os.path.exists('.env'):
        print("  ✓ .env file exists")
        with open('.env', 'r') as f:
            content = f.read()
            if 'OPENAI_API_KEY' in content:
                print("  ✓ OPENAI_API_KEY found")
            if 'DATABASE_URL' in content:
                print("  ✓ DATABASE_URL found")
        return True
    else:
        print("  ✗ .env file not found")
        return False

def check_imports():
    """Check if app imports work."""
    print("\nChecking app imports...")
    try:
        from app.main import app
        print("  ✓ app.main imports OK")
        
        from app.api.v1 import router
        print("  ✓ API router imports OK")
        
        from app.services.execution_service import ExecutionService
        print("  ✓ ExecutionService imports OK")
        
        # Try to import ModelRouter (may fail if google-generativeai not installed)
        try:
            from app.llm.router import ModelRouter
            print("  ✓ ModelRouter imports OK")
        except ImportError as e:
            if 'google' in str(e).lower():
                print("  ⚠ ModelRouter import warning (google-generativeai optional)")
            else:
                raise
        
        return True
    except Exception as e:
        error_msg = str(e)
        # Filter out optional dependency errors
        if 'google' in error_msg.lower() and 'generativeai' in error_msg.lower():
            print(f"  ⚠ Import warning (optional): {error_msg[:100]}")
            return True  # Not a critical error
        print(f"  ✗ Import error: {error_msg[:200]}")
        return False

def main():
    print("=" * 60)
    print("1ne.ai Backend - Setup Verification")
    print("=" * 60)
    print()
    
    all_ok = True
    
    # Check dependencies
    if not check_dependencies():
        all_ok = False
    
    # Check .env
    if not check_env_file():
        all_ok = False
    
    # Check imports
    if not check_imports():
        all_ok = False
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✓ All checks passed! Ready to start server.")
        print("\nNext steps:")
        print("  1. Start server: python -m uvicorn app.main:app --reload")
        print("  2. Run tests: python test_api_endpoints.py")
    else:
        print("✗ Some checks failed. Fix issues above.")
    print("=" * 60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())

