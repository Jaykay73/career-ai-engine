"""
CLI Script to compile a LaTeX resume or cover letter into PDF.
Usage:
    python scripts/compile_resume.py path/to/file.tex [output.pdf]
"""

import sys
import argparse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from career_ai.latex.compiler import latex_compiler

def main():
    parser = argparse.ArgumentParser(description="Compile a LaTeX source file to PDF.")
    parser.add_argument("tex_file", help="Path to .tex file to compile")
    parser.add_argument("--output", "-o", help="Optional path for output PDF", default=None)
    args = parser.parse_args()

    tex_path = Path(args.tex_file)
    if not tex_path.exists():
        print(f"Error: File not found at '{tex_path}'")
        sys.exit(1)

    pdf_out = Path(args.output) if args.output else tex_path.with_suffix(".pdf")
    print(f"Compiling '{tex_path}' -> '{pdf_out}'...")

    content = tex_path.read_text(encoding="utf-8")
    success, msg = latex_compiler.compile(content, pdf_out)

    if success:
        print(f"Compilation SUCCESSFUL! PDF created at: {pdf_out}")
    else:
        print(f"Compilation failed: {msg}")
        if not latex_compiler.is_available():
            print("\nNote: pdflatex or latexmk is not on your PATH.")
            print("You can install MiKTeX on Windows with:")
            print("    winget install MiKTeX.MiKTeX")
            print("Or compile directly for free on Overleaf (https://www.overleaf.com).")
        sys.exit(1)

if __name__ == "__main__":
    main()
