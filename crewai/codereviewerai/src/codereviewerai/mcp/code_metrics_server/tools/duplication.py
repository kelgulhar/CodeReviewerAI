"""Code Duplication Detection Tool"""
from pathlib import Path
from typing import Dict, Any, List, Tuple
import hashlib


def detect_duplication(repo_path: str, min_lines: int = 5) -> Dict[str, Any]:
    """
    Detects code duplication in a repository.
    
    Args:
        repo_path: Path to the repository
        min_lines: Minimum number of lines for a duplicate block
        
    Returns:
        Dictionary with duplication information
    """
    repo = Path(repo_path)
    
    # Collect all code blocks
    code_blocks: Dict[str, List[Tuple[str, int]]] = {}
    
    for py_file in repo.rglob("*.py"):
        if py_file.is_file() and py_file.stat().st_size < 200_000:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                # Extract blocks of consecutive non-empty lines
                current_block = []
                current_start = 0
                
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#'):
                        if not current_block:
                            current_start = i + 1
                        current_block.append(stripped)
                    else:
                        if len(current_block) >= min_lines:
                            block_text = '\n'.join(current_block)
                            block_hash = hashlib.md5(block_text.encode()).hexdigest()
                            
                            if block_hash not in code_blocks:
                                code_blocks[block_hash] = []
                            code_blocks[block_hash].append((str(py_file), current_start))
                        current_block = []
                
                # Check last block
                if len(current_block) >= min_lines:
                    block_text = '\n'.join(current_block)
                    block_hash = hashlib.md5(block_text.encode()).hexdigest()
                    if block_hash not in code_blocks:
                        code_blocks[block_hash] = []
                    code_blocks[block_hash].append((str(py_file), current_start))
            except Exception:
                pass
    
    # Find duplicates (blocks that appear in multiple files or multiple times)
    duplicates = []
    for block_hash, locations in code_blocks.items():
        if len(locations) > 1:
            # Check if in different files
            files = set([loc[0] for loc in locations])
            if len(files) > 1 or len(locations) > 2:
                duplicates.append({
                    'hash': block_hash,
                    'occurrences': len(locations),
                    'files': list(files),
                    'locations': locations[:5]  # Limit to first 5
                })
    
    return {
        'repository': repo_path,
        'total_duplicate_blocks': len(duplicates),
        'duplicates': duplicates[:20]  # Limit to first 20
    }
