#!/usr/bin/env python
"""
Import Fixer for Streamlit

This script adds a simple import fix to the dashboard files to ensure
they can be run directly with streamlit.
"""

import os
import sys
from pathlib import Path

def fix_imports():
    """
    Adds import fixes to Python files to ensure they work with Streamlit.
    """
    # Get project root
    project_root = Path(__file__).resolve().parent
    
    # Files to fix
    dashboard_files = [
        project_root / "src" / "dashboard" / "app.py",
        project_root / "src" / "dashboard" / "components" / "analytics.py",
        project_root / "src" / "dashboard" / "components" / "filters.py",
        project_root / "src" / "dashboard" / "components" / "layout.py",
        project_root / "src" / "dashboard" / "components" / "maps.py",
        project_root / "src" / "dashboard" / "components" / "tables.py",
        project_root / "src" / "dashboard" / "utils" / "data_processing.py",
        project_root / "src" / "dashboard" / "utils" / "responsive.py"
    ]
    
    # Import fix to add at the top of each file
    import_fix = """
# --- Import Fix for Streamlit ---
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).resolve().parents[{parent_level}])
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# ---------------------------
"""
    
    # Fix each file
    for file_path in dashboard_files:
        if not file_path.exists():
            print(f"Skipping {file_path.name}: File not found")
            continue
        
        print(f"Fixing imports in {file_path.name}...")
        
        # Determine parent level (how many directories up to reach project root)
        parent_level = len(file_path.relative_to(project_root).parts) - 1
        current_fix = import_fix.format(parent_level=parent_level)
        
        # Read file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Skip if file already has the fix
        if "# --- Import Fix for Streamlit ---" in content:
            print(f"  Already fixed, skipping")
            continue
        
        # Find position to insert import fix (after docstring if present)
        lines = content.split('\n')
        insert_pos = 0
        
        # Skip shebang if present
        if lines and lines[0].startswith('#!'):
            insert_pos = 1
        
        # Skip docstring if present
        in_docstring = False
        for i, line in enumerate(lines[insert_pos:], insert_pos):
            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                if not in_docstring:
                    in_docstring = True
                else:
                    in_docstring = False
                    insert_pos = i + 1
                    break
            elif not line.strip() and not in_docstring:
                # Skip blank lines before docstring
                insert_pos = i
        
        # Insert import fix
        lines.insert(insert_pos, current_fix)
        
        # Write updated content
        with open(file_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"  Fixed imports in {file_path.name}")
    
    print("\nAll imports fixed. You can now run the dashboard with:")
    print("  streamlit run src/dashboard/app.py")

if __name__ == "__main__":
    fix_imports()