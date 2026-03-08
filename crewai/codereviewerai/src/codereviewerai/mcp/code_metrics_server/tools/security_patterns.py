"""Security Pattern Detection Tool"""
from pathlib import Path
from typing import Dict, Any, List
import re


def scan_security_patterns(repo_path: str) -> Dict[str, Any]:
    """
    Scans code for known security patterns and vulnerabilities.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Dictionary with security findings
    """
    repo = Path(repo_path)
    
    security_patterns = {
        'hardcoded_secrets': [
            (r'password\s*=\s*["\']([^"\']+)["\']', 'Hardcoded password'),
            (r'api_key\s*=\s*["\']([^"\']+)["\']', 'Hardcoded API key'),
            (r'secret\s*=\s*["\']([^"\']+)["\']', 'Hardcoded secret'),
            (r'PASSWORD\s*=\s*["\']([^"\']+)["\']', 'Hardcoded password (constant)'),
        ],
        'sql_injection': [
            (r'execute\s*\(\s*["\']([^"\']*\%[sd])', 'Potential SQL injection (string formatting)'),
            (r'query\s*\(\s*f["\']([^"\']*\+)', 'Potential SQL injection (string concatenation)'),
        ],
        'xss': [
            (r'innerHTML\s*=\s*([^;]+)', 'Potential XSS (innerHTML assignment)'),
            (r'document\.write\s*\(', 'Potential XSS (document.write)'),
        ],
        'insecure_random': [
            (r'random\.random\s*\(', 'Insecure random (use secrets module)'),
            (r'random\.randint\s*\(', 'Insecure random (use secrets module)'),
        ],
        'eval_usage': [
            (r'eval\s*\(', 'Dangerous eval() usage'),
            (r'exec\s*\(', 'Dangerous exec() usage'),
        ]
    }
    
    findings = []
    
    for py_file in repo.rglob("*.py"):
        if py_file.is_file() and py_file.stat().st_size < 200_000:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                for category, patterns in security_patterns.items():
                    for pattern, description in patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            findings.append({
                                'file': str(py_file),
                                'line': line_num,
                                'category': category,
                                'issue': description,
                                'code_snippet': lines[line_num - 1].strip()[:100] if line_num <= len(lines) else ''
                            })
            except Exception:
                pass
    
    # Group by category
    by_category = {}
    for finding in findings:
        cat = finding['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(finding)
    
    return {
        'repository': repo_path,
        'total_findings': len(findings),
        'findings_by_category': {k: len(v) for k, v in by_category.items()},
        'findings': findings[:50]  # Limit to first 50
    }
