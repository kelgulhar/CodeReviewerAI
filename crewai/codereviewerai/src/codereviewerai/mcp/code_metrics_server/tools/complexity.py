"""Code Complexity Analysis Tool"""
import ast
from pathlib import Path
from typing import Dict, Any


def calculate_complexity(file_path: str) -> Dict[str, Any]:
    """
    Calculates cyclomatic complexity and other complexity metrics for a Python file.
    
    Args:
        file_path: Path to the Python file to analyze
        
    Returns:
        Dictionary with complexity metrics
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        
        tree = ast.parse(code)
        
        complexity = 1  # Base complexity
        functions = []
        max_complexity = 0
        
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 1
                self.function_name = None
                
            def visit_FunctionDef(self, node):
                old_complexity = self.complexity
                self.complexity = 1
                self.function_name = node.name
                self.generic_visit(node)
                func_complexity = self.complexity
                functions.append({
                    'name': self.function_name,
                    'complexity': func_complexity,
                    'line': node.lineno
                })
                max_complexity = max(max_complexity, func_complexity)
                self.complexity = old_complexity
                
            def visit_If(self, node):
                self.complexity += 1
                self.generic_visit(node)
                
            def visit_For(self, node):
                self.complexity += 1
                self.generic_visit(node)
                
            def visit_While(self, node):
                self.complexity += 1
                self.generic_visit(node)
                
            def visit_With(self, node):
                self.complexity += 1
                self.generic_visit(node)
                
            def visit_Try(self, node):
                self.complexity += 1
                self.generic_visit(node)
        
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        
        max_complexity = max([f['complexity'] for f in functions], default=0)
        avg_complexity = sum([f['complexity'] for f in functions]) / len(functions) if functions else 0
        
        return {
            'file': file_path,
            'total_functions': len(functions),
            'average_complexity': round(avg_complexity, 2),
            'max_complexity': max_complexity,
            'complex_functions': [f for f in functions if f['complexity'] > 10],
            'functions': functions
        }
    except Exception as e:
        return {
            'file': file_path,
            'error': str(e)
        }


def analyze_repository_complexity(repo_path: str) -> Dict[str, Any]:
    """
    Analyzes complexity for all Python files in a repository.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Dictionary with repository-wide complexity metrics
    """
    repo = Path(repo_path)
    python_files = list(repo.rglob("*.py"))
    
    all_metrics = []
    total_complexity = 0
    total_functions = 0
    max_complexity = 0
    
    for py_file in python_files[:50]:  # Limit to first 50 files
        if py_file.is_file() and py_file.stat().st_size < 200_000:
            metrics = calculate_complexity(str(py_file))
            if 'error' not in metrics:
                all_metrics.append(metrics)
                total_functions += metrics['total_functions']
                max_complexity = max(max_complexity, metrics['max_complexity'])
                total_complexity += sum([f['complexity'] for f in metrics['functions']])
    
    avg_complexity = total_complexity / total_functions if total_functions > 0 else 0
    
    return {
        'repository': repo_path,
        'files_analyzed': len(all_metrics),
        'total_functions': total_functions,
        'average_complexity': round(avg_complexity, 2),
        'max_complexity': max_complexity,
        'complex_files': [m for m in all_metrics if m['max_complexity'] > 15]
    }
