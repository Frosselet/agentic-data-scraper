# 🚀 Jupyter Lab + UV Environment Setup

## The Problem
Jupyter often runs with system Python instead of project environments, causing dependency conflicts (especially NumPy 2.x issues). This defeats the purpose of using UV for consistent dependency management.

## The Solution
This setup ensures Jupyter runs **exclusively** within the UV project environment with the correct dependencies.

## 🔧 Quick Setup (2 minutes)

### Step 1: Run the setup script
```bash
cd "/Volumes/WD Green/dev/git/agentic-data-scraper"
python3 setup_jupyter.py
```

### Step 2: Start Jupyter with UV
```bash
./start_jupyter.sh
```

**OR manually:**
```bash
uv run jupyter lab --notebook-dir=notebooks
```

### Step 3: Select the correct kernel
In Jupyter Lab, make sure to select:
**Kernel: "Agentic Data Scraper (UV)"**

## ✅ Verification

Run this in any notebook cell to verify:
```python
import sys
print("Python:", sys.executable)
print("UV Environment:", ".venv" in sys.executable or "agentic-data-scraper" in sys.executable)

import numpy as np
print("NumPy version:", np.__version__)  # Should be 1.26.4, not 2.x
```

## 🎯 Expected Results

✅ **Python Path**: Should contain `.venv` or `agentic-data-scraper`  
✅ **NumPy Version**: 1.26.4 (compatible, not 2.3.1)  
✅ **All packages**: pandas, kuzu, httpx working without errors  
✅ **USGS API**: Real data collection working (no mock fallback needed)

## 🚨 Troubleshooting

### If you see "Not using UV environment"
1. Close all Jupyter tabs/windows
2. Kill any Jupyter processes: `pkill -f jupyter`
3. Restart with: `./start_jupyter.sh`
4. Select kernel: "Agentic Data Scraper (UV)"

### If kernel doesn't appear
```bash
uv run python -m ipykernel install --user --name "agentic-data-scraper-uv" --display-name "Agentic Data Scraper (UV)"
```

### If dependencies are still wrong
```bash
uv sync --all-extras  # Re-sync dependencies
uv run jupyter lab --notebook-dir=notebooks
```

## 🎉 Benefits

- **Consistent Environment**: Always uses project dependencies
- **No NumPy Issues**: Pinned to compatible 1.26.4
- **Real API Integration**: USGS API works without mock fallbacks
- **Professional Setup**: Proper project integration
- **Easy Startup**: One command starts everything correctly

This setup ensures the notebook demonstrates **real capabilities** rather than falling back to mock data due to environment issues!