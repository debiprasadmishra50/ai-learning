#!/usr/bin/env python3
"""
Environment Verification Script for RAG Evaluation Lab
Automatically installs missing packages and verifies the environment.
"""

import os
import sys
import subprocess

# Required packages for this lab
REQUIRED_PACKAGES = [
    ("chromadb", "chromadb"),
    ("sentence-transformers", "sentence_transformers"),
    ("langchain-text-splitters", "langchain_text_splitters"),
    ("numpy", "numpy"),
]

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"  [OK] Python {version.major}.{version.minor}.{version.micro}")
    return version.major >= 3 and version.minor >= 9

def check_virtual_env():
    """Check if running in virtual environment"""
    print("\nChecking Virtual Environment:")

    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print(f"  [OK] Virtual environment active: {sys.prefix}")
        return True
    else:
        print("  [X] NOT running in virtual environment!")
        print("\n" + "="*60)
        print("!!  CRITICAL: You MUST activate the virtual environment!")
        print("\nRun these commands:")
        print("   cd /home/lab-user/rag-project")
        print("   source venv/bin/activate")
        print("="*60)
        return False

def check_package_installed(import_name):
    """Check if a package can be imported"""
    try:
        __import__(import_name.split('.')[0])
        return True
    except ImportError:
        return False

def install_packages(packages):
    """Install packages using uv pip"""
    if not packages:
        return True
    
    print(f"\nInstalling {len(packages)} missing packages...")
    print(f"   Packages: {', '.join(packages)}")
    
    try:
        cmd = ["uv", "pip", "install"] + packages
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print("  [OK] All packages installed successfully!")
            return True
        else:
            print(f"  [X] Installation failed: {result.stderr}")
            return False
    except FileNotFoundError:
        # Try with pip if uv is not available
        print("  !!  uv not found, trying pip...")
        try:
            cmd = [sys.executable, "-m", "pip", "install"] + packages
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                print("  [OK] All packages installed successfully!")
                return True
            else:
                print(f"  [X] Installation failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"  [X] Error: {e}")
            return False
    except Exception as e:
        print(f"  [X] Error installing packages: {e}")
        return False

def check_and_install_packages():
    """Check all required packages and install missing ones"""
    print("\nChecking Required Packages:")
    
    missing_packages = []
    installed_packages = []
    
    for package_name, import_name in REQUIRED_PACKAGES:
        if check_package_installed(import_name):
            try:
                module = __import__(import_name.split('.')[0])
                version = getattr(module, '__version__', 'installed')
                print(f"  [OK] {package_name} (v{version})")
            except:
                print(f"  [OK] {package_name}")
            installed_packages.append(package_name)
        else:
            print(f"  [X] {package_name} - MISSING")
            missing_packages.append(package_name)
    
    # Auto-install missing packages
    if missing_packages:
        print("\n" + "-"*50)
        print("Auto-installing missing packages...")
        print("-"*50)
        
        if install_packages(missing_packages):
            # Verify installation by trying imports again
            print("\nVerifying installation...")
            still_missing = []
            for package_name, import_name in REQUIRED_PACKAGES:
                if package_name in missing_packages:
                    if check_package_installed(import_name):
                        print(f"  [OK] {package_name} - installed successfully")
                    else:
                        print(f"  [X] {package_name} - still missing")
                        still_missing.append(package_name)
            
            if still_missing:
                print(f"\n!!  Some packages could not be installed: {', '.join(still_missing)}")
                print("   Try manually: uv pip install " + " ".join(still_missing))
                return False
            return True
        else:
            return False
    
    return True

def test_imports():
    """Test if we can import all required modules"""
    print("\nTesting Module Imports:")
    
    imports = [
        ("chromadb", "Vector database"),
        ("langchain_text_splitters", "LangChain text splitter"),
        ("sentence_transformers", "Sentence transformers"),
        ("numpy", "NumPy"),
    ]
    
    all_good = True
    
    for module, description in imports:
        try:
            __import__(module)
            print(f"  [OK] {description} ({module})")
        except ImportError as e:
            print(f"  [X] {description} ({module}): {e}")
            all_good = False
    
    return all_good

def test_evaluation_imports():
    """Test if evaluation-specific modules can be imported"""
    print("\nTesting Evaluation Module Imports:")
    
    try:
        # Test numpy functions needed for metrics
        import numpy as np
        print("  [OK] NumPy array operations")
        
        # Test basic math operations
        test_arr = np.array([1, 2, 3])
        _ = np.sum(test_arr)
        print("  [OK] NumPy mathematical functions")
        
        return True
    except Exception as e:
        print(f"  [X] Evaluation imports failed: {e}")
        return False


def preload_embedding_model():
    """Pre-download the embedding model to avoid timeout during tasks"""
    print("\nPre-loading Embedding Model:")
    print("   (This may take 1-2 minutes on first run...)")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        model_name = 'all-MiniLM-L6-v2'
        print(f"  Downloading/loading {model_name}...")
        
        # This will download the model if not cached
        model = SentenceTransformer(model_name)
        
        # Quick test to ensure it works
        test_embedding = model.encode("test query")
        
        print(f"  [OK] Model loaded successfully!")
        print(f"  [OK] Embedding dimension: {len(test_embedding)}")
        
        return True
    except Exception as e:
        print(f"  [X] Failed to load model: {e}")
        print("  Tip: Check your internet connection and try again")
        return False

def main():
    """Run all environment checks"""
    print("="*60)
    print("RAG Evaluation Lab - Environment Setup")
    print("="*60)
    
    print("\nPython Version Check:")

    # CRITICAL: Check virtual environment first
    venv_active = check_virtual_env()

    if not venv_active:
        print("\n[X] STOPPING HERE - Activate virtual environment first!")
        print("   Then run this script again.")
        sys.exit(1)

    # Check Python version
    python_ok = check_python_version()

    # Check and auto-install packages
    packages_ok = check_and_install_packages()

    # Test imports
    imports_ok = test_imports()

    # Test evaluation-specific imports
    eval_imports_ok = test_evaluation_imports()

    # Pre-load embedding model (critical for avoiding timeouts in tasks)
    model_ok = preload_embedding_model()

    # Summary
    checks = {
        "Python Version": python_ok,
        "Required Packages": packages_ok,
        "Module Imports": imports_ok,
        "Evaluation Imports": eval_imports_ok,
        "Embedding Model": model_ok,
    }

    print("\n" + "="*60)
    print("Environment Check Summary")
    print("="*60)

    all_passed = True
    for check, passed in checks.items():
        status = "[OK] PASS" if passed else "[X] FAIL"
        print(f"  {check}: {status}")
        if not passed:
            all_passed = False

    # Create marker file if all checks pass
    if all_passed:
        with open("/tmp/rag_eval_environment_verified.txt", "w") as f:
            f.write("ENVIRONMENT_VERIFIED")

        print("\n" + "="*60)
        print("Environment setup completed successfully!")
        print("You're ready to start the RAG Evaluation tasks!")
        print("="*60)
        print("\nRemember: Keep the virtual environment activated")
        print("   for all upcoming tasks!")
        
        print("\nEnvironment verification completed!")
    else:
        print("\n" + "="*60)
        print("!!  Some checks failed. Please fix the issues above.")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    main()
