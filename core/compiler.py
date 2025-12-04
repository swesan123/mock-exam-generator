"""Compile LaTeX documents to PDF."""
import logging
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LaTeXCompiler:
    """Compiles LaTeX documents to PDF."""

    def __init__(
        self,
        compiler: str = "latexmk",
        options: Optional[list[str]] = None,
        logs_dir: Optional[Path] = None
    ) -> None:
        """
        Initialize the compiler.

        Args:
            compiler: LaTeX compiler command (latexmk or pdflatex).
            options: Additional compiler options.
            logs_dir: Directory to save LaTeX compilation logs.
        """
        self.compiler = compiler
        self.options = options or ["-pdf", "-interaction=nonstopmode"]
        self.logs_dir = Path(logs_dir) if logs_dir else None

    def compile(self, tex_path: Path, output_dir: Path) -> Path:
        """
        Compile a LaTeX file to PDF.

        Args:
            tex_path: Path to the .tex file.
            output_dir: Directory where output files should be placed.

        Returns:
            Path to the generated PDF file.

        Raises:
            FileNotFoundError: If tex_path doesn't exist.
            subprocess.CalledProcessError: If compilation fails.
        """
        tex_path = Path(tex_path)
        output_dir = Path(output_dir)

        if not tex_path.exists():
            raise FileNotFoundError(f"LaTeX file not found: {tex_path}")

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Convert to absolute paths
        tex_path = tex_path.resolve()
        output_dir = output_dir.resolve()

        # If tex_path is in output_dir, use relative path; otherwise use absolute
        try:
            tex_path_rel = tex_path.relative_to(output_dir)
            # Use relative path when running from output_dir
            tex_path_for_cmd = str(tex_path_rel)
        except ValueError:
            # tex_path is not in output_dir, use absolute path
            tex_path_for_cmd = str(tex_path)

        # Build command
        cmd = [self.compiler] + self.options + [tex_path_for_cmd]

        logger.info(f"Compiling LaTeX: {' '.join(cmd)}")
        logger.info(f"Working directory: {output_dir}")

        try:
            # Run compilation from output directory
            result = subprocess.run(
                cmd,
                cwd=str(output_dir),
                capture_output=True,
                text=True,
                check=True
            )

            # Save logs if logs directory is configured
            if self.logs_dir:
                self._save_logs(tex_path, result, cmd, output_dir)

            # Determine output PDF path
            pdf_name = tex_path.stem + ".pdf"
            pdf_path = output_dir / pdf_name

            if pdf_path.exists():
                logger.info(f"PDF generated successfully: {pdf_path}")
                return pdf_path
            else:
                # Try alternative location (some compilers output to same dir as .tex)
                alt_path = tex_path.parent / pdf_name
                if alt_path.exists():
                    logger.info(f"PDF found at alternative location: {alt_path}")
                    return alt_path
                else:
                    raise FileNotFoundError(
                        f"PDF not found after compilation. "
                        f"Checked: {pdf_path}, {alt_path}"
                    )

        except subprocess.CalledProcessError as e:
            # Save error logs if logs directory is configured
            if self.logs_dir:
                self._save_error_logs(tex_path, e, output_dir)
            
            logger.error(f"LaTeX compilation failed: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            raise
        except FileNotFoundError:
            logger.error(f"LaTeX compiler not found: {self.compiler}")
            raise RuntimeError(
                f"LaTeX compiler '{self.compiler}' not found. "
                f"Please install it or check your PATH."
            )

    def _save_logs(
        self, 
        tex_path: Path, 
        result: subprocess.CompletedProcess,
        cmd: list[str],
        output_dir: Path
    ) -> None:
        """Save compilation logs to the logs directory."""
        if not self.logs_dir:
            return
        
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_dir / f"{tex_path.stem}_{timestamp}.log"
        
        log_content = f"=== LaTeX Compilation Log ===\n"
        log_content += f"File: {tex_path}\n"
        log_content += f"Working Directory: {output_dir}\n"
        log_content += f"Timestamp: {datetime.now().isoformat()}\n"
        log_content += f"Command: {' '.join(cmd)}\n"
        log_content += f"\n=== STDOUT ===\n{result.stdout}\n"
        log_content += f"\n=== STDERR ===\n{result.stderr}\n"
        
        log_file.write_text(log_content, encoding="utf-8")
        logger.info(f"Compilation log saved to: {log_file}")

    def _save_error_logs(
        self, 
        tex_path: Path, 
        error: subprocess.CalledProcessError,
        output_dir: Path
    ) -> None:
        """Save error logs to the logs directory."""
        if not self.logs_dir:
            return
        
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_dir / f"{tex_path.stem}_{timestamp}_ERROR.log"
        
        log_content = f"=== LaTeX Compilation Error Log ===\n"
        log_content += f"File: {tex_path}\n"
        log_content += f"Working Directory: {output_dir}\n"
        log_content += f"Timestamp: {datetime.now().isoformat()}\n"
        log_content += f"Return Code: {error.returncode}\n"
        log_content += f"Command: {' '.join(error.cmd)}\n"
        log_content += f"\n=== STDOUT ===\n{error.stdout}\n"
        log_content += f"\n=== STDERR ===\n{error.stderr}\n"
        
        log_file.write_text(log_content, encoding="utf-8")
        logger.error(f"Error log saved to: {log_file}")

