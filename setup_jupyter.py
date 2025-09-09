#!/usr/bin/env python3
"""
Setup Jupyter Lab with UV Environment Integration
Ensures Jupyter uses the project's UV environment consistently
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr.strip()}")
        return False

def setup_jupyter_with_uv():
    """Set up Jupyter Lab with UV environment integration"""
    
    print("🚀 Setting up Jupyter Lab with UV Environment Integration")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Not in project root directory. Please cd to the project root first.")
        return False
    
    # Step 1: Sync UV dependencies including Jupyter
    print("🔄 This will install Jupyter Lab in the UV environment with correct dependencies...")
    if not run_command("uv sync --all-extras", "Syncing UV dependencies (including Jupyter)"):
        return False
    
    # Step 2: Install the UV environment as a Jupyter kernel
    print("\n🔧 Installing UV environment as Jupyter kernel...")
    
    # Get the UV python path
    try:
        result = subprocess.run("uv run python -c 'import sys; print(sys.executable)'", 
                              shell=True, capture_output=True, text=True, check=True)
        uv_python = result.stdout.strip()
        print(f"   UV Python path: {uv_python}")
    except subprocess.CalledProcessError:
        print("❌ Failed to get UV Python path")
        return False
    
    # Install ipykernel in the UV environment and register it
    kernel_name = "agentic-data-scraper-uv"
    display_name = "Agentic Data Scraper (UV)"
    
    install_kernel_cmd = f'uv run python -m ipykernel install --user --name "{kernel_name}" --display-name "{display_name}"'
    
    if not run_command(install_kernel_cmd, f"Installing UV kernel as '{display_name}'"):
        return False
    
    # Step 3: Create a startup script for Jupyter
    startup_script = """#!/bin/bash
# Jupyter Lab Startup Script for Agentic Data Scraper
# This ensures Jupyter runs with the UV environment

echo "🚀 Starting Jupyter Lab with UV environment..."
echo "📍 Project: Agentic Data Scraper"
echo "🐍 Using UV Python environment"
echo ""

# Start Jupyter Lab with UV
uv run jupyter lab --notebook-dir=notebooks
"""
    
    with open("start_jupyter.sh", "w") as f:
        f.write(startup_script)
    
    # Make it executable
    os.chmod("start_jupyter.sh", 0o755)
    print("✅ Created start_jupyter.sh script")
    
    # Step 4: Create a verification notebook cell
    verification_cell = '''# UV Environment Verification - Run this cell first!
import sys
import os

print("🔍 Environment Verification:")
print(f"📍 Python executable: {sys.executable}")
print(f"🐍 Python version: {sys.version.split()[0]}")

# Check if we're in UV environment
in_uv = ".venv" in sys.executable or "agentic-data-scraper" in sys.executable
print(f"🏗️  UV Environment: {'✅ Active' if in_uv else '❌ Not active'}")

# Check critical packages
packages = ["numpy", "pandas", "kuzu", "httpx"]
for pkg in packages:
    try:
        module = __import__(pkg)
        version = getattr(module, '__version__', 'unknown')
        print(f"📦 {pkg}: {version}")
    except ImportError:
        print(f"❌ {pkg}: Not installed")

if in_uv:
    print("\\n🎉 Ready! You're using the UV environment correctly.")
else:
    print("\\n⚠️  WARNING: Not using UV environment!")
    print("   Please select the 'Agentic Data Scraper (UV)' kernel.")
'''
    
    # Update the notebook with the verification cell
    print("\n📝 Updating notebook with environment verification...")
    
    try:
        import json
        notebook_path = "notebooks/mississippi_river_etkl_workflow.ipynb"
        
        if os.path.exists(notebook_path):
            with open(notebook_path, 'r') as f:
                notebook = json.load(f)
            
            # Find the environment check cell and update it
            for cell in notebook.get('cells', []):
                if cell.get('cell_type') == 'code' and 'Environment Check and Fix' in str(cell.get('source', [])):
                    cell['source'] = verification_cell.split('\n')
                    print("✅ Updated notebook verification cell")
                    break
            
            with open(notebook_path, 'w') as f:
                json.dump(notebook, f, indent=2)
        
    except Exception as e:
        print(f"⚠️  Could not update notebook: {e}")
    
    # Step 5: Final instructions
    print("\n🎯 Setup Complete! Next Steps:")
    print("=" * 30)
    print("1. Close any existing Jupyter sessions")
    print("2. Run: ./start_jupyter.sh")
    print("   OR run: uv run jupyter lab")
    print("3. When Jupyter opens, make sure to select:")
    print(f"   Kernel: '{display_name}'")
    print("4. Run the verification cell in the notebook")
    print("")
    print("🔧 Alternative quick start:")
    print("   uv run jupyter lab --notebook-dir=notebooks")
    print("")
    print("✅ Jupyter is now integrated with UV environment!")
    
    return True

if __name__ == "__main__":
    success = setup_jupyter_with_uv()
    sys.exit(0 if success else 1)