#!/usr/bin/env python3
"""
Setup VS Code Jupyter Integration with UV Environment
Configures VS Code to use the UV environment for Jupyter notebooks
"""

import json
import subprocess
import sys
from pathlib import Path

def setup_vscode_jupyter():
    """Configure VS Code to use UV environment for Jupyter"""
    
    print("🔧 Setting up VS Code + Jupyter + UV Integration")
    print("=" * 50)
    
    # Ensure we're in project root
    if not Path("pyproject.toml").exists():
        print("❌ Not in project root. Please cd to agentic-data-scraper first.")
        return False
    
    project_root = Path.cwd()
    
    # Step 1: Sync UV dependencies
    print("🔄 Syncing UV dependencies...")
    try:
        subprocess.run(["uv", "sync", "--all-extras"], check=True)
        print("✅ Dependencies synced")
    except subprocess.CalledProcessError:
        print("❌ UV sync failed")
        return False
    
    # Step 2: Get UV Python path
    try:
        result = subprocess.run(["uv", "run", "python", "-c", "import sys; print(sys.executable)"], 
                               capture_output=True, text=True, check=True)
        uv_python_path = result.stdout.strip()
        print(f"🐍 UV Python: {uv_python_path}")
    except subprocess.CalledProcessError:
        print("❌ Failed to get UV Python path")
        return False
    
    # Step 3: Create VS Code workspace settings
    vscode_dir = project_root / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    
    settings_file = vscode_dir / "settings.json"
    
    # VS Code settings for Jupyter + UV
    settings = {
        "python.pythonPath": uv_python_path,
        "python.defaultInterpreterPath": uv_python_path,
        "jupyter.notebookFileRoot": "${workspaceFolder}",
        "jupyter.interactiveWindow.textEditor.executeSelection": True,
        "python.terminal.activateEnvironment": False,  # UV handles this
        "files.associations": {
            "*.ipynb": "jupyter-notebook"
        },
        "notebook.cellToolbarLocation": {
            "default": "right",
            "jupyter-notebook": "left"
        }
    }
    
    # Merge with existing settings if they exist
    if settings_file.exists():
        with open(settings_file, 'r') as f:
            try:
                existing_settings = json.load(f)
                existing_settings.update(settings)
                settings = existing_settings
            except json.JSONDecodeError:
                pass  # Use new settings if file is corrupted
    
    # Write settings
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)
    
    print(f"✅ Created VS Code settings: {settings_file}")
    
    # Step 4: Create launch configuration for Jupyter debugging
    launch_file = vscode_dir / "launch.json"
    
    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Current File",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "python": uv_python_path
            }
        ]
    }
    
    with open(launch_file, 'w') as f:
        json.dump(launch_config, f, indent=2)
    
    print(f"✅ Created launch configuration: {launch_file}")
    
    # Step 5: Install ipykernel in UV environment
    print("\n🔧 Installing ipykernel in UV environment...")
    try:
        subprocess.run(["uv", "add", "ipykernel"], check=True)
        print("✅ ipykernel installed")
    except subprocess.CalledProcessError:
        print("⚠️  ipykernel installation failed (might already be installed)")
    
    # Step 6: Create a quick verification file
    verification_py = project_root / "verify_vscode_setup.py"
    verification_code = '''#!/usr/bin/env python3
"""
VS Code + UV Environment Verification
Run this to verify your setup is working correctly
"""

import sys
from pathlib import Path

def verify_setup():
    print("🔍 VS Code + UV Environment Verification")
    print("=" * 45)
    
    print(f"🐍 Python executable: {sys.executable}")
    
    # Check if using UV environment
    in_uv = ".venv" in sys.executable or "agentic-data-scraper" in sys.executable
    print(f"🏗️  UV Environment: {'✅ Active' if in_uv else '❌ Not active'}")
    
    # Check working directory
    print(f"📁 Working directory: {Path.cwd()}")
    print(f"📋 Project root detected: {'✅ Yes' if Path('pyproject.toml').exists() else '❌ No'}")
    
    # Check key packages
    packages = ["numpy", "pandas", "kuzu", "httpx"]
    for pkg in packages:
        try:
            module = __import__(pkg)
            version = getattr(module, '__version__', 'unknown')
            print(f"📦 {pkg}: {version}")
        except ImportError:
            print(f"❌ {pkg}: Not available")
    
    if in_uv:
        print("\\n🎉 Perfect! VS Code is using the UV environment correctly.")
        print("✅ Ready to run Jupyter notebooks in VS Code")
    else:
        print("\\n⚠️  Not using UV environment in VS Code")
        print("   Make sure you selected the correct Python interpreter")

if __name__ == "__main__":
    verify_setup()
'''
    
    with open(verification_py, 'w') as f:
        f.write(verification_code)
    
    print(f"✅ Created verification script: {verification_py}")
    
    # Step 7: Instructions
    print("\n🎯 VS Code Setup Complete!")
    print("=" * 25)
    print("1. Open VS Code in this project:")
    print(f"   code .")
    print("")
    print("2. Open the notebook:")
    print("   code notebooks/mississippi_river_etkl_workflow.ipynb")
    print("")
    print("3. If VS Code asks to select a kernel, choose:")
    print(f"   {uv_python_path}")
    print("")
    print("4. Verify setup by running:")
    print("   python verify_vscode_setup.py")
    print("")
    print("✅ VS Code will now use the UV environment automatically!")
    print("🎉 No need to run external Jupyter server!")
    
    return True

if __name__ == "__main__":
    success = setup_vscode_jupyter()
    sys.exit(0 if success else 1)