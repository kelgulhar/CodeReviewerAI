"""Code Statistics Tool"""
from pathlib import Path
from typing import Dict, Any, List


def get_code_statistics(repo_path: str) -> Dict[str, Any]:
    """
    Gets general code statistics for a repository.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Dictionary with code statistics
    """
    repo = Path(repo_path)
    
    stats = {
        'total_lines': 0,
        'total_files': 0,
        'files_by_type': {},
        'total_functions': 0,
        'total_classes': 0,
        'average_file_size': 0,
        'largest_files': []
    }
    
    file_extensions = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.java': 'Java',
        '.go': 'Go',
        '.rs': 'Rust'
    }
    
    file_sizes = []
    
    for ext, lang in file_extensions.items():
        files = list(repo.rglob(f"*{ext}"))
        for file in files:
            if file.is_file() and file.stat().st_size < 200_000:
                try:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                        stats['total_lines'] += lines
                        stats['total_files'] += 1
                        file_sizes.append((str(file), lines))
                        
                        if lang not in stats['files_by_type']:
                            stats['files_by_type'][lang] = {'count': 0, 'lines': 0}
                        stats['files_by_type'][lang]['count'] += 1
                        stats['files_by_type'][lang]['lines'] += lines
                except Exception:
                    pass
    
    if stats['total_files'] > 0:
        stats['average_file_size'] = round(stats['total_lines'] / stats['total_files'], 2)
    
    # Get largest files
    file_sizes.sort(key=lambda x: x[1], reverse=True)
    stats['largest_files'] = [{'file': f[0], 'lines': f[1]} for f in file_sizes[:10]]
    
    return stats
