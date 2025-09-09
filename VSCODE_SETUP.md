# 🎯 VS Code + Jupyter + UV Integration

## **Option 1: Quick Manual Setup (30 seconds)**

### **Step 1: Install VS Code Jupyter Extension**
- Open VS Code
- Extensions (Cmd+Shift+X) → Search "Jupyter" → Install

### **Step 2: Select UV Python Interpreter**
- Open your notebook: `code notebooks/mississippi_river_etkl_workflow.ipynb`
- Press `Cmd+Shift+P` → "Python: Select Interpreter"
- Choose: `./.venv/bin/python` (or similar UV environment path)

### **Step 3: Run cells!**
- VS Code will automatically use the UV environment
- No external Jupyter server needed!

## **Option 2: Automated Setup**

```bash
cd "/Volumes/WD Green/dev/git/agentic-data-scraper"
python3 setup_vscode_jupyter.py
code .
```

## **🎯 Benefits of VS Code Integration:**

✅ **No External Server**: Jupyter runs directly in VS Code  
✅ **UV Environment**: Automatically uses project dependencies  
✅ **Integrated Debugging**: Full VS Code debugging capabilities  
✅ **Git Integration**: See changes, commit, etc. directly  
✅ **IntelliSense**: Auto-completion with project context  
✅ **Professional**: All-in-one development environment

## **🧪 Verification:**

In any notebook cell:
```python
import sys
print("Python:", sys.executable)
print("UV Environment:", ".venv" in sys.executable)

import numpy as np
print("NumPy:", np.__version__)  # Should be 1.26.4
```

Expected output:
```
Python: /Volumes/WD Green/dev/git/agentic-data-scraper/.venv/bin/python
UV Environment: True
NumPy: 1.26.4
```

## **🚨 If Environment is Wrong:**

1. **Cmd+Shift+P** → "Python: Select Interpreter"
2. **Choose the .venv path** (UV environment)
3. **Reload VS Code** if needed

## **🎉 Result:**

- ✅ **No NumPy 2.x issues**: Uses compatible 1.26.4
- ✅ **Real API integration**: USGS APIs work without fallbacks  
- ✅ **All dependencies**: pandas, kuzu, httpx working perfectly
- ✅ **Professional workflow**: Everything integrated in VS Code

**This is the recommended approach for development!** 🚀