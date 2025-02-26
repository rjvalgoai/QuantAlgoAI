import os
from pathlib import Path
from typing import List, Set

def generate_structure(
    root_dir: str,
    exclude_dirs: Set[str] = {'__pycache__', 'node_modules', '.venv', '.git'},
    exclude_files: Set[str] = {'.pyc', '.pyo', '.pyd', '.DS_Store'}
) -> str:
    """Generate a clean project structure"""
    
    structure = []
    root = Path(root_dir)
    
    for path in sorted(root.rglob('*')):
        # Skip excluded directories and files
        if any(excluded in path.parts for excluded in exclude_dirs):
            continue
        if path.suffix in exclude_files:
            continue
            
        # Calculate relative path and depth
        rel_path = path.relative_to(root)
        depth = len(rel_path.parts) - 1
        
        # Add to structure
        prefix = '    ' * depth + '|-- '
        structure.append(f"{prefix}{path.name}")
    
    return '\n'.join(structure)

if __name__ == '__main__':
    # Generate structure from project root
    project_root = Path(__file__).parent.parent
    structure = generate_structure(project_root)
    
    # Write to Project Structure.txt
    with open(project_root / 'Project Structure.txt', 'w') as f:
        f.write('Project Structure\n')
        f.write('=' * 50 + '\n\n')
        f.write(structure) 