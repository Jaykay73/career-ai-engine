"""
LaTeX to PDF Compiler.
Safely compiles generated .tex files using pdflatex with sandboxed temporary directories,
timeouts, and comprehensive error extraction. Fails gracefully if compiler is not installed.
"""

from typing import Optional, Tuple
from pathlib import Path
import subprocess
import shutil
import tempfile
import re
from career_ai.core.config import settings
from career_ai.core.logging import get_logger
from career_ai.core.exceptions import LaTeXCompilationError

logger = get_logger("compiler")

class LaTeXCompiler:
    """Invokes pdflatex safely via subprocess."""

    def __init__(
        self,
        compiler_cmd: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        self.compiler_cmd = compiler_cmd or settings.latex_compiler
        self.timeout = timeout or settings.latex_timeout_seconds

    def is_available(self) -> bool:
        """Checks if the configured LaTeX compiler executable is found in PATH."""
        return shutil.which(self.compiler_cmd) is not None

    def compile(self, tex_content: str, output_pdf_path: Path) -> Tuple[bool, str]:
        """
        Compiles LaTeX string to a target PDF path.
        Returns (success: bool, message_or_log: str).
        Does NOT crash if compiler is unavailable.
        """
        output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.is_available():
            msg = (
                f"LaTeX compiler '{self.compiler_cmd}' is not found in system PATH. "
                f"Generated .tex file is preserved at {output_pdf_path.with_suffix('.tex')}. "
                f"To enable direct PDF compilation, install MiKTeX (Windows) or TeX Live and ensure '{self.compiler_cmd}' is on PATH."
            )
            logger.warning(msg)
            return False, msg

        # Run inside an isolated temporary directory to keep working directory clean
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            job_name = "resume"
            temp_tex = temp_path / f"{job_name}.tex"
            temp_tex.write_text(tex_content, encoding="utf-8")

            # Safe subprocess invocation with list of args (shell=False)
            cmd = [
                self.compiler_cmd,
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-jobname={job_name}",
                str(temp_tex.name)
            ]

            try:
                # Two compilation passes to ensure cross-references / layout resolve
                for run_num in [1, 2]:
                    proc = subprocess.run(
                        cmd,
                        cwd=str(temp_path),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=self.timeout
                    )
                    if proc.returncode != 0 and run_num == 2:
                        error_log = self._extract_error_log(temp_path / f"{job_name}.log", proc.stdout)
                        logger.error("LaTeX compilation failed on pass %d: %s", run_num, error_log)
                        return False, f"LaTeX Compilation Error:\n{error_log}"

                temp_pdf = temp_path / f"{job_name}.pdf"
                if temp_pdf.exists():
                    shutil.copy2(temp_pdf, output_pdf_path)
                    logger.info("PDF compiled successfully to %s", output_pdf_path)
                    return True, "PDF compiled successfully."
                else:
                    return False, "PDF was not created by the LaTeX compiler."

            except subprocess.TimeoutExpired:
                logger.error("LaTeX compilation timed out after %d seconds.", self.timeout)
                return False, f"LaTeX compilation timed out after {self.timeout}s."
            except Exception as e:
                logger.error("LaTeX execution error: %s", e)
                return False, f"Failed to execute LaTeX compiler: {e}"

    def _extract_error_log(self, log_path: Path, stdout: str) -> str:
        """Extracts relevant error lines from LaTeX log or stdout."""
        if log_path.exists():
            log_text = log_path.read_text(encoding="latin-1", errors="ignore")
            # Find lines starting with '!'
            errors = [line for line in log_text.splitlines() if line.startswith("!")]
            if errors:
                return "\n".join(errors[:5])
            return "\n".join(log_text.splitlines()[-25:])
        return stdout[-500:]

# Global compiler
latex_compiler = LaTeXCompiler()
