#!/usr/bin/env python3
"""
Quick test of first few critical cells to verify basic functionality
"""

import json
import sys

def test_critical_cells():
    """Test only the first few critical cells"""
    print("🚀 QUICK CRITICAL CELLS TEST")
    print("=" * 40)

    with open('semantic_knowledge_graph_experiments.ipynb', 'r') as f:
        nb = json.load(f)

    # Test cells 0-5 only (critical setup cells)
    test_cells = []
    for i in range(min(6, len(nb['cells']))):
        cell = nb['cells'][i]
        if cell.get('cell_type') == 'code' and ''.join(cell.get('source', [])).strip():
            test_cells.append((i, cell))

    print(f"📊 Testing first {len(test_cells)} critical cells")

    global_namespace = {}

    for cell_index, cell in test_cells:
        source = ''.join(cell.get('source', []))
        print(f"\n📝 Cell {cell_index}: {source[:50]}...")

        try:
            exec(source, global_namespace)
            print("✅ SUCCESS")

            # Check what key variables are now available
            key_vars = ['pd', 'nx', 'go', 'kg', 'SemanticKnowledgeGraph']
            available = [var for var in key_vars if var in global_namespace]
            if available:
                print(f"   Variables: {', '.join(available)}")

        except Exception as e:
            print(f"❌ FAILED: {type(e).__name__}: {e}")
            # Continue testing other cells

    # Final state check
    print(f"\n🔍 Final state - available variables:")
    key_vars = ['pd', 'nx', 'go', 'kg', 'SemanticKnowledgeGraph']
    for var in key_vars:
        if var in global_namespace:
            print(f"  ✅ {var}: {type(global_namespace[var])}")
        else:
            print(f"  ❌ {var}: Not available")

    return True

if __name__ == "__main__":
    test_critical_cells()
    print("\n🎯 Quick test complete!")