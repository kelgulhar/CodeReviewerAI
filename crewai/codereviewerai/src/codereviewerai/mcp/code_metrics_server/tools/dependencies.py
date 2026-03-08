"""Dependency Analysis Tool"""
from pathlib import Path
from typing import Dict, Any, List, Set
import re


def analyze_dependencies(repo_path: str, language: str = "python") -> Dict[str, Any]:
    """
    Analyzes dependencies between modules/components.
    
    Args:
        repo_path: Path to the repository
        language: Programming language (python, javascript, etc.)
        
    Returns:
        Dictionary with dependency information
    """
    repo = Path(repo_path)
    
    dependencies: Dict[str, Set[str]] = {}
    all_modules: Set[str] = set()
    
    if language == "python":
        # Find all Python modules
        for py_file in repo.rglob("*.py"):
            if py_file.is_file() and py_file.stat().st_size < 200_000:
                try:
                    module_name = py_file.stem
                    if module_name == "__init__":
                        module_name = str(py_file.parent.relative_to(repo))
                    all_modules.add(module_name)
                    
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Extract imports
                    imports = set()
                    import_patterns = [
                        r'^import\s+(\w+)',
                        r'^from\s+(\w+)\s+import',
                        r'^from\s+([\w.]+)\s+import'
                    ]
                    
                    for line in content.split('\n'):
                        for pattern in import_patterns:
                            match = re.match(pattern, line.strip())
                            if match:
                                import_name = match.group(1).split('.')[0]
                                imports.add(import_name)
                    
                    if imports:
                        dependencies[module_name] = imports
                except Exception:
                    pass
    
    # Calculate coupling metrics
    high_coupling_modules = []
    for module, deps in dependencies.items():
        if len(deps) > 10:  # High coupling threshold
            high_coupling_modules.append({
                'module': module,
                'dependencies': len(deps),
                'depends_on': list(deps)[:10]
            })
    
    # Find potential circular dependencies (simplified)
    circular_candidates = []
    for module, deps in dependencies.items():
        for dep in deps:
            if dep in dependencies and module in dependencies.get(dep, set()):
                circular_candidates.append({
                    'module1': module,
                    'module2': dep
                })
    
    return {
        'repository': repo_path,
        'language': language,
        'total_modules': len(all_modules),
        'modules_with_dependencies': len(dependencies),
        'high_coupling_modules': high_coupling_modules[:10],
        'potential_circular_dependencies': circular_candidates[:10],
        'dependency_graph': {k: list(v)[:5] for k, v in list(dependencies.items())[:20]}
    }
