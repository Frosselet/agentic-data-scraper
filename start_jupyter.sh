#!/bin/bash
# Jupyter Lab Startup Script for Agentic Data Scraper
# This ensures Jupyter runs with the UV environment

echo "🚀 Jupyter Lab Startup Options"
echo "📍 Project: Agentic Data Scraper"
echo "🐍 Using UV Python environment with NumPy 1.26.4 (compatible)"
echo ""

# Ensure we're in the project directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Not in project root directory"
    echo "   Please cd to the agentic-data-scraper directory first"
    exit 1
fi

echo "📋 Choose your preferred option:"
echo "   1. VS Code Integration (Recommended)"
echo "   2. External Jupyter Lab Server"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "🔧 Setting up VS Code + Jupyter integration..."
        python3 setup_vscode_jupyter.py
        echo ""
        echo "🎯 Next steps:"
        echo "   1. code ."
        echo "   2. Open: notebooks/mississippi_river_etkl_workflow.ipynb"
        echo "   3. Select the UV Python interpreter when prompted"
        echo ""
        echo "✅ VS Code will handle Jupyter automatically!"
        ;;
    2)
        echo ""
        echo "🔄 Syncing dependencies..."
        uv sync --all-extras
        
        echo "🚀 Launching external Jupyter Lab..."
        uv run jupyter lab --notebook-dir=notebooks --no-browser
        
        echo ""
        echo "🎯 Remember to select kernel: 'Agentic Data Scraper (UV)'"
        echo "✅ Jupyter Lab is running with UV environment integration!"
        ;;
    *)
        echo "❌ Invalid choice. Please run again and choose 1 or 2."
        exit 1
        ;;
esac
