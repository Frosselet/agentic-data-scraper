# Mississippi River ET(K)L Notebook Setup Guide

## 🚀 Quick Setup Instructions

Before running the Jupyter notebook, you need to install all dependencies. Follow these steps:

### 1. Install Dependencies with uv

```bash
# Navigate to project directory
cd /path/to/agentic-data-scraper

# Install all dependencies (includes dev tools, notebook support, and semantic features)
uv sync --all-extras

# Or install specific dependency groups:
uv sync --extra dev --extra semantic --extra graph_viz
```

### 2. Set Up Environment Variables (Optional)

For full functionality, set these environment variables:

```bash
# For AIS vessel tracking (get from VesselFinder)
export VESSELFINDER_API_KEY="your_vesselfinder_api_key"

# For BAML agents (get from OpenAI)
export OPENAI_API_KEY="your_openai_api_key"
```

### 3. Start Jupyter

```bash
# Start Jupyter notebook server
uv run jupyter notebook

# Or use Jupyter Lab
uv run jupyter lab
```

### 4. Open the Notebook

Navigate to `notebooks/mississippi_river_etkl_workflow.ipynb` and start with the first cell.

## 📦 What Gets Installed

The `uv sync --all-extras` command installs:

### Core Dependencies
- **Data Processing**: pandas, numpy, polars, pyarrow
- **Web Scraping**: httpx, beautifulsoup4, playwright  
- **Semantic Web**: rdflib, owlready2, sparqlwrapper
- **Graph Database**: kuzu (KuzuDB), networkx
- **AI/ML**: baml-py (for BAML agents)
- **AWS Integration**: boto3, botocore

### Development Tools
- **Jupyter**: jupyter, notebook, ipython
- **Visualization**: matplotlib, seaborn, plotly, bokeh
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Code Quality**: ruff, mypy, pre-commit

### Semantic & Graph Features
- **KuzuDB**: Primary graph database for navigation analytics
- **Interactive Viz**: dash, streamlit, plotly for web interfaces
- **4D Analytics**: holoviews, panel for spatio-temporal visualization

## 🔧 Troubleshooting

### Common Issues

**ModuleNotFoundError: No module named 'pandas'**
```bash
# Make sure you ran uv sync with extras
uv sync --all-extras
```

**KuzuDB installation issues**
```bash
# Install KuzuDB separately if needed
uv add kuzu
```

**API Key issues**
```bash
# Check environment variables
echo $VESSELFINDER_API_KEY
echo $OPENAI_API_KEY

# Set if missing
export VESSELFINDER_API_KEY="your_key_here"
```

**Jupyter kernel issues**
```bash
# Install kernel in virtual environment
uv run python -m ipykernel install --user --name agentic-scraper
```

### Minimal Installation

If you want to run just the core semantic collection features:

```bash
# Minimal semantic features only
uv sync --extra semantic

# Then install notebook support
uv add jupyter notebook matplotlib seaborn
```

## 🎯 Verification

After installation, verify everything works:

```python
# Run this in a notebook cell to verify imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import kuzu
from rdflib import Graph

# Check semantic collectors
import sys
sys.path.append('../src')
from agentic_data_scraper.collectors.usgs_collector import USGSSemanticCollector

print("✅ All dependencies installed successfully!")
```

## 📊 What the Notebook Demonstrates

The notebook walks through:

1. **Semantic Data Collection** - Real-time API integration with semantic enrichment
2. **KuzuDB Knowledge Graph** - Graph database for navigation analytics  
3. **Multi-Agent Intelligence** - BAML agents for decision support
4. **Production Architecture** - Scalable deployment patterns
5. **Real-World Scenarios** - Emergency navigation decision examples

## 🚢 Next Steps

Once setup is complete:

1. Open `notebooks/mississippi_river_etkl_workflow.ipynb`
2. Run cells sequentially to see ET(K)L in action
3. Explore the semantic collectors in `src/agentic_data_scraper/collectors/`
4. Try the BAML agents in `schemas/agents/baml_src/navigation_agents.baml`
5. Review the production architecture documentation

The key innovation: **Semantic enrichment happens during data acquisition, not after!** 🧠⚡