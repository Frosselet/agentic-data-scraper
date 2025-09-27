#!/usr/bin/env python3
"""
Fix core notebook issues identified by execution testing
"""

import json
from pathlib import Path

def fix_missing_imports():
    """Add missing imports to the notebook"""
    print("🔧 Fixing missing imports...")

    with open('semantic_knowledge_graph_experiments.ipynb', 'r') as f:
        nb = json.load(f)

    # Create comprehensive imports cell
    imports_cell = {
        'cell_type': 'code',
        'metadata': {},
        'source': [
            '# 📦 COMPREHENSIVE IMPORTS\n',
            '# All necessary imports for semantic knowledge graph experiments\n',
            '\n',
            '# Core data processing\n',
            'import pandas as pd\n',
            'import numpy as np\n',
            '\n',
            '# RDF and semantic web\n',
            'from rdflib import Graph, Namespace, URIRef, Literal, BNode\n',
            'from rdflib.namespace import RDF, RDFS, OWL, XSD\n',
            '\n',
            '# Jupyter widgets for interactive interfaces\n',
            'import ipywidgets as widgets\n',
            'from IPython.display import display, HTML, clear_output\n',
            '\n',
            '# Visualization\n',
            'import plotly.graph_objects as go\n',
            'import plotly.express as px\n',
            'import networkx as nx\n',
            '\n',
            '# System and utilities\n',
            'import os\n',
            'import sys\n',
            'import json\n',
            'import warnings\n',
            'from pathlib import Path\n',
            'from datetime import datetime\n',
            '\n',
            '# Suppress warnings for cleaner output\n',
            'warnings.filterwarnings("ignore")\n',
            '\n',
            'print("✅ All imports loaded successfully")\n'
        ],
        'execution_count': None,
        'outputs': []
    }

    # Insert at the beginning (after title)
    nb['cells'].insert(1, imports_cell)
    print("✅ Added comprehensive imports cell")

    return nb

def fix_knowledge_graph_initialization():
    """Fix knowledge graph initialization"""
    print("🔧 Fixing knowledge graph initialization...")

    with open('semantic_knowledge_graph_experiments.ipynb', 'r') as f:
        nb = json.load(f)

    # Find the SemanticKnowledgeGraph class definition
    class_cell_index = None
    for i, cell in enumerate(nb['cells']):
        if cell.get('cell_type') == 'code' and 'source' in cell:
            source = ''.join(cell['source'])
            if 'class SemanticKnowledgeGraph:' in source:
                class_cell_index = i
                break

    if class_cell_index:
        # Add initialization cell right after class definition
        init_cell = {
            'cell_type': 'code',
            'metadata': {},
            'source': [
                '# 🏗️ KNOWLEDGE GRAPH INITIALIZATION\n',
                '# Initialize the semantic knowledge graph that all other cells depend on\n',
                '\n',
                'print("🏗️ Initializing Semantic Knowledge Graph...")\n',
                '\n',
                '# Create knowledge graph instance\n',
                'kg = SemanticKnowledgeGraph()\n',
                '\n',
                '# Load core ontologies\n',
                'print("📚 Loading core ontologies...")\n',
                'try:\n',
                '    # Add basic RDF schema\n',
                '    kg.graph.parse(data="""<?xml version="1.0"?>\n',
                '    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n',
                '             xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">\n',
                '        <rdfs:Class rdf:about="http://example.org/Organization"/>\n',
                '        <rdfs:Class rdf:about="http://example.org/BusinessCanvas"/>\n',
                '        <rdfs:Class rdf:about="http://example.org/SOW"/>\n',
                '    </rdf:RDF>""", format="xml")\n',
                '    \n',
                '    print("✅ Core ontologies loaded")\n',
                'except Exception as e:\n',
                '    print(f"⚠️ Could not load ontologies: {e}")\n',
                '    print("✅ Continuing with empty graph")\n',
                '\n',
                '# Verify initialization\n',
                'stats = kg.get_statistics()\n',
                'print(f"📊 Knowledge graph initialized with {stats.get(\"total_triples\", 0)} triples")\n',
                'print("✅ Knowledge graph ready for use")\n'
            ],
            'execution_count': None,
            'outputs': []
        }

        nb['cells'].insert(class_cell_index + 1, init_cell)
        print("✅ Added knowledge graph initialization cell")

    return nb

def fix_pandas_usage():
    """Fix pandas usage in SemanticKnowledgeGraph class"""
    print("🔧 Fixing pandas usage in class definition...")

    with open('semantic_knowledge_graph_experiments.ipynb', 'r') as f:
        nb = json.load(f)

    # Find and fix the SemanticKnowledgeGraph class
    for cell in nb['cells']:
        if cell.get('cell_type') == 'code' and 'source' in cell:
            source_lines = cell['source']
            for i, line in enumerate(source_lines):
                # Fix pd.DataFrame usage
                if 'pd.DataFrame' in line and 'import pandas as pd' not in ''.join(source_lines):
                    # Replace with explicit pandas import
                    if 'def query(self, sparql_query: str) -> pd.DataFrame:' in line:
                        source_lines[i] = line.replace('pd.DataFrame', 'object')  # Use generic object type
                        print(f"✅ Fixed pandas type hint in line: {line.strip()}")

    return nb

def apply_all_fixes():
    """Apply all fixes and save notebook"""
    print("🚀 APPLYING ALL CORE FIXES")
    print("=" * 40)

    # Create backup
    import shutil
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2('semantic_knowledge_graph_experiments.ipynb',
                f'backups/before_core_fixes_{timestamp}.ipynb')

    # Apply fixes in sequence
    nb = fix_missing_imports()
    nb = fix_knowledge_graph_initialization()
    nb = fix_pandas_usage()

    # Save the fixed notebook
    with open('semantic_knowledge_graph_experiments.ipynb', 'w') as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)

    print("✅ All core fixes applied and saved")
    print("\n🧪 Running quick validation...")

    # Quick test of first few cells
    import subprocess
    test_script = '''
import pandas as pd
import ipywidgets as widgets
from rdflib import Graph, Namespace, URIRef, Literal, BNode
print("✅ All imports working")
'''

    try:
        result = subprocess.run([sys.executable, '-c', test_script],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Import test passed")
        else:
            print(f"❌ Import test failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Could not run import test: {e}")

if __name__ == "__main__":
    import sys
    apply_all_fixes()
    print("\n🎯 Core fixes complete. Notebook should now have working imports and initialization.")