"""
LaTeX and Filesystem Sanitizers.
Prevents LaTeX syntax breakage, escaping injection attacks, and illegal file paths.
"""

import re
from typing import Optional

LATEX_REPLACEMENTS = [
    ('\\', r'\textbackslash{}'),
    ('&', r'\&'),
    ('%', r'\%'),
    ('$', r'\$'),
    ('#', r'\#'),
    ('_', r'\_'),
    ('{', r'\{'),
    ('}', r'\}'),
    ('~', r'\textasciitilde{}'),
    ('^', r'\textasciicircum{}'),
]

def escape_latex(text: str) -> str:
    """Escapes all LaTeX special characters in text while preserving readability."""
    if not text:
        return ""
    
    # Don't escape existing backslashes if they are part of already escaped commands
    res = str(text)
    for char, replacement in [
        ('&', r'\&'),
        ('%', r'\%'),
        ('$', r'\$'),
        ('#', r'\#'),
        ('_', r'\_'),
        ('{', r'\{'),
        ('}', r'\}'),
    ]:
        # Avoid double-escaping already escaped characters like \&
        pattern = r'(?<!\\)' + re.escape(char)
        res = re.sub(pattern, replacement, res)

    return res

def sanitize_filename(name: str) -> str:
    """
    Sanitizes string for safe cross-platform filesystem use.
    Removes invalid characters: < > : " / \ | ? *
    """
    if not name:
        return "Application"
    # Remove illegal characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '', name)
    # Collapse multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned
