#!/usr/bin/env python3
"""
Robust Notebook Management System
- Automatic saving after modifications
- Actual execution testing (not just static analysis)
- Comprehensive error detection and fixing
- State management to prevent regressions
"""

import json
import subprocess
import sys
import tempfile
import os
import shutil
from pathlib import Path
from datetime import datetime

class NotebookManager:
    def __init__(self, notebook_path):
        self.notebook_path = Path(notebook_path)
        self.backup_dir = self.notebook_path.parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)

    def backup_notebook(self):
        """Create timestamped backup before modifications"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.notebook_path.stem}_{timestamp}.ipynb"
        backup_path = self.backup_dir / backup_name
        shutil.copy2(self.notebook_path, backup_path)
        print(f"📁 Backup created: {backup_path}")
        return backup_path

    def load_notebook(self):
        """Load notebook with error handling"""
        try:
            with open(self.notebook_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading notebook: {e}")
            return None

    def save_notebook(self, notebook_data):
        """Save notebook with validation"""
        try:
            # Validate JSON structure
            json.dumps(notebook_data)

            # Create backup first
            self.backup_notebook()

            # Save with pretty formatting
            with open(self.notebook_path, 'w') as f:
                json.dump(notebook_data, f, indent=2, ensure_ascii=False)

            print(f"✅ Notebook saved successfully: {self.notebook_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving notebook: {e}")
            return False

    def execute_cell_test(self, cell_index, max_execution_time=30):
        """Execute a specific cell and capture results"""
        nb = self.load_notebook()
        if not nb or cell_index >= len(nb['cells']):
            return False, "Invalid cell index"

        cell = nb['cells'][cell_index]
        if cell.get('cell_type') != 'code':
            return True, "Markdown cell - skipped"

        source = ''.join(cell.get('source', []))
        if not source.strip():
            return True, "Empty cell - skipped"

        # Create test script
        test_script = f'''
import sys
import traceback
import warnings
warnings.filterwarnings("ignore")

try:
{chr(10).join("    " + line for line in source.split(chr(10)))}
    print("✅ CELL EXECUTION SUCCESS")
except Exception as e:
    print(f"❌ CELL EXECUTION FAILED: {{type(e).__name__}}: {{e}}")
    traceback.print_exc()
    sys.exit(1)
'''

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(test_script)
                test_file = f.name

            result = subprocess.run([sys.executable, test_file],
                                  capture_output=True, text=True,
                                  timeout=max_execution_time)

            os.unlink(test_file)

            success = result.returncode == 0
            output = result.stdout + result.stderr

            return success, output

        except subprocess.TimeoutExpired:
            return False, "Cell execution timed out"
        except Exception as e:
            return False, f"Test execution error: {e}"

    def remove_content_by_pattern(self, patterns_to_remove):
        """Remove cells or content matching specific patterns"""
        nb = self.load_notebook()
        if not nb:
            return False

        cells_removed = 0
        content_modified = 0

        # Remove entire cells that match patterns
        cells_to_keep = []
        for i, cell in enumerate(nb['cells']):
            if 'source' in cell:
                source = ''.join(cell['source'])
                should_remove = False

                for pattern in patterns_to_remove:
                    if pattern.lower() in source.lower():
                        print(f"🗑️ Removing cell {i}: matches '{pattern}'")
                        cells_removed += 1
                        should_remove = True
                        break

                if not should_remove:
                    cells_to_keep.append(cell)
            else:
                cells_to_keep.append(cell)

        nb['cells'] = cells_to_keep

        # Modify content within remaining cells
        for cell in nb['cells']:
            if 'source' in cell:
                original_source = ''.join(cell['source'])
                modified_source = original_source

                for pattern in patterns_to_remove:
                    if pattern.lower() in modified_source.lower():
                        # Remove lines containing the pattern
                        lines = modified_source.split('\n')
                        filtered_lines = [line for line in lines if pattern.lower() not in line.lower()]
                        modified_source = '\n'.join(filtered_lines)
                        content_modified += 1

                if modified_source != original_source:
                    cell['source'] = modified_source.split('\n')

        print(f"🗑️ Removed {cells_removed} cells, modified {content_modified} cells")
        return self.save_notebook(nb)

    def fix_class_execution_order(self):
        """Fix class definition and usage order issues"""
        nb = self.load_notebook()
        if not nb:
            return False

        # Find class definitions and usages
        class_definitions = {}
        class_usages = {}

        for i, cell in enumerate(nb['cells']):
            if cell.get('cell_type') == 'code' and 'source' in cell:
                source = ''.join(cell['source'])

                # Find class definitions
                if 'class KuzuSemanticGraphVisualizer' in source:
                    class_definitions['KuzuSemanticGraphVisualizer'] = i
                    print(f"📍 KuzuSemanticGraphVisualizer defined in cell {i}")

                # Find class usages (not definitions)
                if 'KuzuSemanticGraphVisualizer' in source and 'class KuzuSemanticGraphVisualizer' not in source:
                    if 'KuzuSemanticGraphVisualizer' not in class_usages:
                        class_usages['KuzuSemanticGraphVisualizer'] = []
                    class_usages['KuzuSemanticGraphVisualizer'].append(i)
                    print(f"📍 KuzuSemanticGraphVisualizer used in cell {i}")

        # Check if definition comes after usage
        if 'KuzuSemanticGraphVisualizer' in class_definitions and 'KuzuSemanticGraphVisualizer' in class_usages:
            def_cell = class_definitions['KuzuSemanticGraphVisualizer']
            usage_cells = class_usages['KuzuSemanticGraphVisualizer']

            if any(usage < def_cell for usage in usage_cells):
                print("❌ Class used before definition - fixing order")

                # Move definition before first usage
                first_usage = min(usage_cells)
                target_position = max(0, first_usage - 1)

                # Remove definition from current position
                definition_cell = nb['cells'].pop(def_cell)

                # Insert before first usage
                nb['cells'].insert(target_position, definition_cell)

                print(f"✅ Moved class definition to cell {target_position}")
                return self.save_notebook(nb)

        return True

    def comprehensive_test(self):
        """Run comprehensive notebook testing"""
        print("🧪 COMPREHENSIVE NOTEBOOK TESTING")
        print("=" * 50)

        nb = self.load_notebook()
        if not nb:
            return False

        code_cells = [(i, cell) for i, cell in enumerate(nb['cells'])
                     if cell.get('cell_type') == 'code' and
                     ''.join(cell.get('source', [])).strip()]

        print(f"📊 Testing {len(code_cells)} code cells")

        results = []
        for i, (cell_index, cell) in enumerate(code_cells):
            print(f"\n📝 Testing cell {cell_index} ({i+1}/{len(code_cells)})")
            success, output = self.execute_cell_test(cell_index)
            results.append((cell_index, success, output))

            if not success:
                print(f"❌ Cell {cell_index} failed:")
                print(output[:500] + "..." if len(output) > 500 else output)
            else:
                print(f"✅ Cell {cell_index} passed")

        # Summary
        passed = sum(1 for _, success, _ in results if success)
        total = len(results)
        success_rate = (passed / total * 100) if total > 0 else 0

        print(f"\n📊 TEST RESULTS: {passed}/{total} passed ({success_rate:.1f}%)")

        if passed < total:
            print("\n❌ FAILED CELLS:")
            for cell_index, success, output in results:
                if not success:
                    print(f"  Cell {cell_index}: {output.split(':', 1)[0] if ':' in output else 'Error'}")

        return passed == total

def main():
    """Main notebook management interface"""
    manager = NotebookManager("semantic_knowledge_graph_experiments.ipynb")

    print("🚀 NOTEBOOK MANAGEMENT SYSTEM")
    print("=" * 40)

    # Step 1: Remove data contract references as requested
    print("\n1. Removing data contract references...")
    data_contract_patterns = [
        "data contract", "Data Contract", "AWS Lambda", "lambda function",
        "Technical Specifications", "AWS Lambda Mappings", "contractual obligations"
    ]
    manager.remove_content_by_pattern(data_contract_patterns)

    # Step 2: Fix class execution order
    print("\n2. Fixing class execution order...")
    manager.fix_class_execution_order()

    # Step 3: Run comprehensive test
    print("\n3. Running comprehensive execution test...")
    test_passed = manager.comprehensive_test()

    if test_passed:
        print("\n🎉 ALL TESTS PASSED! Notebook is ready for use.")
    else:
        print("\n⚠️ Some tests failed. Manual review required.")

    return test_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)