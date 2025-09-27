#!/usr/bin/env python3
"""
Sequential Notebook Execution Test
Tests the notebook as it would actually run in Jupyter - cell by cell with state preservation
"""

import json
import sys
import traceback
import warnings
from pathlib import Path

# Suppress warnings for cleaner testing
warnings.filterwarnings("ignore")

def test_sequential_execution():
    """Test notebook by executing cells sequentially with state preservation"""
    print("🧪 SEQUENTIAL NOTEBOOK EXECUTION TEST")
    print("=" * 50)

    # Load notebook
    with open('semantic_knowledge_graph_experiments.ipynb', 'r') as f:
        nb = json.load(f)

    # Get code cells only
    code_cells = []
    for i, cell in enumerate(nb['cells']):
        if cell.get('cell_type') == 'code' and ''.join(cell.get('source', [])).strip():
            code_cells.append((i, cell))

    print(f"📊 Found {len(code_cells)} code cells to execute sequentially")

    # Execute cells in sequence (like Jupyter does)
    global_namespace = {}
    results = []

    for cell_num, (original_index, cell) in enumerate(code_cells):
        source = ''.join(cell.get('source', []))

        print(f"\n📝 Executing cell {original_index} ({cell_num + 1}/{len(code_cells)})")
        print(f"   Source preview: {source[:60]}...")

        try:
            # Execute in persistent global namespace (like Jupyter)
            exec(source, global_namespace)
            print("✅ SUCCESS")
            results.append((original_index, True, "Success"))

        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            print(f"❌ FAILED: {error_msg}")
            results.append((original_index, False, error_msg))

            # For critical initialization failures, stop execution
            if 'import' in source.lower() or 'class ' in source:
                print("🚨 Critical cell failed - stopping execution")
                break

    # Results summary
    print("\n" + "=" * 50)
    print("📊 SEQUENTIAL EXECUTION RESULTS")
    print("=" * 50)

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    print(f"✅ Passed: {passed}/{total} cells ({passed/total*100:.1f}%)")

    if passed < total:
        print(f"\n❌ Failed cells:")
        for original_index, success, message in results:
            if not success:
                print(f"  Cell {original_index}: {message}")

    # Check what variables are available in final state
    print(f"\n🔍 Final namespace contains {len(global_namespace)} variables:")
    key_vars = ['kg', 'pd', 'widgets', 'nx', 'go']
    for var in key_vars:
        if var in global_namespace:
            print(f"  ✅ {var}: {type(global_namespace[var])}")
        else:
            print(f"  ❌ {var}: Not defined")

    return passed == total

def quick_fix_remaining_imports():
    """Fix remaining import issues"""
    print("\n🔧 QUICK FIX: Adding missing type imports")

    with open('semantic_knowledge_graph_experiments.ipynb', 'r') as f:
        nb = json.load(f)

    # Find imports cell and add missing types
    for cell in nb['cells']:
        if cell.get('cell_type') == 'code' and 'source' in cell:
            source_lines = cell['source']
            if 'import pandas as pd' in ''.join(source_lines):
                # Add missing typing imports
                typing_import = 'from typing import Dict, Any, List, Optional\n'

                # Check if already present
                if 'from typing import' not in ''.join(source_lines):
                    # Insert after pandas import
                    for i, line in enumerate(source_lines):
                        if 'import pandas as pd' in line:
                            source_lines.insert(i + 1, typing_import)
                            print("✅ Added typing imports")
                            break
                break

    # Save the updated notebook
    with open('semantic_knowledge_graph_experiments.ipynb', 'w') as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # First fix remaining imports
    quick_fix_remaining_imports()

    # Then test sequential execution
    success = test_sequential_execution()

    if success:
        print("\n🎉 NOTEBOOK SEQUENTIAL EXECUTION: SUCCESS!")
        print("✅ All cells execute properly in sequence")
        print("✅ Notebook is ready for normal Jupyter use")
    else:
        print("\n⚠️ NOTEBOOK SEQUENTIAL EXECUTION: ISSUES REMAIN")
        print("🔧 Review failed cells above for remaining issues")

    sys.exit(0 if success else 1)