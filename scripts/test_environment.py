#!/usr/bin/env python3
"""
Test script to verify all dependencies are installed correctly
"""

def test_imports():
    """Test importing all required packages"""
    packages = [
        ('pandas', 'pd'),
        ('numpy', 'np'), 
        ('matplotlib.pyplot', 'plt'),
        ('seaborn', 'sns'),
        ('kuzu', None),
        ('rdflib', None),
        ('httpx', None),
        ('pydantic', None)
    ]
    
    print("🧪 Testing Package Imports...")
    print("=" * 40)
    
    success_count = 0
    total_count = len(packages)
    
    for package, alias in packages:
        try:
            if alias:
                exec(f"import {package} as {alias}")
            else:
                exec(f"import {package}")
            print(f"✅ {package} - OK")
            success_count += 1
        except ImportError as e:
            print(f"❌ {package} - MISSING ({e})")
    
    print("\n📊 Results:")
    print(f"   Success: {success_count}/{total_count}")
    print(f"   Success Rate: {(success_count/total_count)*100:.1f}%")
    
    if success_count == total_count:
        print("🎉 All packages imported successfully!")
        print("✅ Environment is ready for the notebook")
        
        # Test some basic functionality
        print("\n🔧 Testing Basic Functionality...")
        try:
            import pandas as pd
            import numpy as np
            
            # Create test data
            df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
            arr = np.array([1, 2, 3])
            
            print("✅ Pandas DataFrame creation works")
            print("✅ NumPy array creation works")
            
        except Exception as e:
            print(f"❌ Basic functionality test failed: {e}")
    else:
        print("\n⚠️  Some packages are missing. Run:")
        print("   uv sync --all-extras")
    
    return success_count == total_count

if __name__ == "__main__":
    import sys
    print(f"🐍 Python Version: {sys.version}")
    print(f"📍 Python Path: {sys.executable}")
    print()
    
    success = test_imports()
    
    if success:
        print("\n🚀 Ready to run the Mississippi River ET(K)L notebook!")
    else:
        print("\n🛑 Please fix the missing dependencies first.")
        sys.exit(1)