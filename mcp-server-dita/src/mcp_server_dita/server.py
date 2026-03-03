import subprocess
import os
import shutil
import tempfile
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("dita")

@mcp.tool()
def md_to_pdf(input_path: str, output_path: str) -> str:
    """
    Convert a Markdown file to PDF using the DITA Open Toolkit.
    
    Args:
        input_path: The absolute path to the input Markdown file.
        output_path: The absolute path where the output PDF should be saved.
    """
    if not os.path.exists(input_path):
        return f"Error: Input file '{input_path}' does not exist."
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Run dita command
        try:
            # shell=True helps Windows find the 'dita.bat' wrapper script on the PATH.
            result = subprocess.run(
                ["dita", "--input", input_path, "--format", "pdf", "--output", temp_dir],
                check=True,
                capture_output=True,
                text=True,
                shell=True
            )
        except FileNotFoundError:
            return "Error: 'dita' executable not found. Please ensure DITA-OT is in your system PATH."
        except subprocess.CalledProcessError as e:
            # DITA outputs build errors to stdout/stderr. Return them to the user.
            return f"Error during DITA conversion (Exit code {e.returncode}):\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        
        # DITA typically generates a PDF with the exact same base name as the input file
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        generated_pdf = os.path.join(temp_dir, f"{base_name}.pdf")
        
        if os.path.exists(generated_pdf):
            # Ensure the output directory exists
            output_dir = os.path.dirname(os.path.abspath(output_path))
            os.makedirs(output_dir, exist_ok=True)
            
            shutil.copy2(generated_pdf, output_path)
            return f"Successfully converted '{input_path}' to PDF at '{output_path}'."
        else:
            files_in_dir = os.listdir(temp_dir)
            return f"Error: Conversion command succeeded, but expected PDF '{generated_pdf}' was not found. Output directory contains: {files_in_dir}"
