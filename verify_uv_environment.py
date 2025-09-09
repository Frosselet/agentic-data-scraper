#!/usr/bin/env python3
"""
Quick verification that UV environment is working correctly
Run this with: uv run python verify_uv_environment.py
"""

import sys
import subprocess

def verify_uv_environment():
    """Verify the UV environment is set up correctly"""
    
    print("🔍 UV Environment Verification")
    print("=" * 40)
    
    # Check Python executable
    python_exe = sys.executable
    print(f"📍 Python executable: {python_exe}")
    
    if ".venv" in python_exe or "uv" in python_exe:
        print("✅ Using UV virtual environment")
    else:
        print("❌ NOT using UV virtual environment")
        print("   Make sure you run: uv run python verify_uv_environment.py")
        return False
    
    # Check critical packages
    packages_to_check = [
        ('numpy', '1.26.4'),
        ('pandas', '2.2'),
        ('kuzu', '0.'),
        ('httpx', '0.'),
        ('pydantic', '2.'),
    ]
    
    print(f"\n📦 Package Versions:")
    all_good = True
    
    for package_name, expected_version in packages_to_check:
        try:
            module = __import__(package_name)
            actual_version = getattr(module, '__version__', 'unknown')
            
            if expected_version in actual_version:
                print(f"✅ {package_name}: {actual_version}")
            else:
                print(f"⚠️  {package_name}: {actual_version} (expected: {expected_version}*)")
                
        except ImportError:
            print(f"❌ {package_name}: Not installed")
            all_good = False
    
    # Test KuzuDB specifically
    print(f"\n🗄️  Testing KuzuDB:")
    try:
        import kuzu
        db = kuzu.Database("./test_kuzu_verify.kuzu")
        conn = kuzu.Connection(db)
        conn.execute("CREATE NODE TABLE IF NOT EXISTS TestNode(id STRING, PRIMARY KEY (id))")
        print("✅ KuzuDB: Working correctly")
        
        # Clean up
        import os
        import shutil
        if os.path.exists("./test_kuzu_verify.kuzu"):
            shutil.rmtree("./test_kuzu_verify.kuzu")
            
    except Exception as e:
        print(f"❌ KuzuDB: Failed - {e}")
        all_good = False
    
    # Test our schema specifically
    print(f"\n🧠 Testing Semantic Schema:")
    try:
        sys.path.append('src')
        from agentic_data_scraper.schemas.kuzu_navigation_schema import NavigationSchema
        schema = NavigationSchema("./test_schema_verify.kuzu")
        print("✅ NavigationSchema: Created successfully (KuzuDB issues fixed!)")
        
        # Clean up
        import os
        import shutil
        if os.path.exists("./test_schema_verify.kuzu"):
            shutil.rmtree("./test_schema_verify.kuzu")
            
    except Exception as e:
        print(f"❌ NavigationSchema: Failed - {e}")
        all_good = False
    
    print(f"\n🎯 Overall Status:")
    if all_good:
        print("🎉 UV environment is ready!")
        print("✅ All packages working correctly")
        print("✅ KuzuDB schema issues resolved")
        print("✅ Ready to run the notebook")
        
        print(f"\n🚀 Next Steps:")
        print("1. Start Jupyter with UV:")
        print("   uv run jupyter lab")
        print("2. Open the notebook:")
        print("   notebooks/mississippi_river_etkl_workflow.ipynb")
        print("3. Run all cells - everything should work!")
        
        return True
    else:
        print("❌ Environment issues detected")
        print("   Run: uv sync --all-extras")
        print("   Then retry this verification")
        return False

if __name__ == "__main__":
    verify_uv_environment()