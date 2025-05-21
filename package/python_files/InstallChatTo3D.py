from pathlib import Path
import git
from git.exc import GitCommandError
import shutil
import subprocess
import os
import platform
import logging
import re

# Set up logging for get_conda_python_path and general use
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# GitHub repository URL
gHubURL = 'https://github.com/anmaurya001/chat-to-3d.git'

# Get the directory two levels up from the current script (C:\VGAI_BP\3d-guided-genai-rtx\package)
output_path = Path(__file__).resolve().parent.parent
target_dir = output_path / 'chat-to-3d'

def clone_repository(url: str, target_dir: Path) -> bool:
    """Clone a Git repository with --recursive to the target directory."""
    try:
        git.Repo.clone_from(
            url=url,
            to_path=target_dir,
            multi_options=['--recursive']
        )
        print(f"Successfully cloned repository to {target_dir}")
        return True
    except GitCommandError as e:
        if e.status == 128:
            print(f"Repository not cloned: Target directory '{target_dir}' already exists.")
        else:
            print(f"Error cloning repository: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error cloning repository: {e}")
        return False

def replace_file(target_file: Path, patch_file: Path) -> bool:
    """Replace target_file with patch_file if both exist."""
    if target_file.exists():
        print(f"Target file '{target_file}' exists.")
        if patch_file.exists():
            try:
                shutil.copy2(patch_file, target_file)
                print(f"Successfully replaced '{target_file}' with '{patch_file}'.")
                return True
            except Exception as e:
                print(f"Error replacing file: {e}")
                return False
        else:
            print(f"Patch file '{patch_file}' does not exist. No replacement performed.")
            return False
    else:
        print(f"Target file '{target_file}' does not exist. No replacement performed.")
        return False

def get_conda_python_path() -> str | None:
    """Attempt to find the Conda 'trellis' environment's Python executable."""
    conda_base = os.environ.get("CONDA_PREFIX")
    if conda_base:
        logger.debug("Using CONDA_PREFIX: %s", conda_base)
        if os.path.basename(conda_base) == "trellis" and os.path.basename(os.path.dirname(conda_base)) == "envs":
            conda_base = os.path.dirname(os.path.dirname(conda_base))
            logger.debug("Adjusted Conda base from CONDA_PREFIX: %s", conda_base)
    else:
        try:
            result = subprocess.run(
                ["conda", "info", "--base"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout:
                conda_base = result.stdout.strip()
                logger.debug("Found Conda base using 'conda info --base': %s", conda_base)
            else:
                logger.warning("Could not locate Conda base using 'conda info --base': %s", result.stderr)
                conda_base = os.path.expanduser("~/Miniconda3")
                logger.debug("Falling back to default Conda base: %s", conda_base)
        except subprocess.SubprocessError as e:
            logger.error("Failed to locate Conda base using 'conda info --base': %s", str(e))
            conda_base = os.path.expanduser("~/Miniconda3")
            logger.debug("Falling back to default Conda base: %s", conda_base)

    if platform.system() == "Windows":
        python_path = os.path.join(conda_base, "envs", "trellis", "python.exe")
    else:
        python_path = os.path.join(conda_base, "envs", "trellis", "bin", "python")
    
    if os.path.isfile(python_path):
        try:
            result = subprocess.run(
                [python_path, "-c", "import sys; print(sys.version)"],
                capture_output=True,
                text=True,
                timeout=5
            )
            logger.debug("Conda Python version: %s", result.stdout.strip())
            return python_path
        except subprocess.SubprocessError as e:
            logger.error("Failed to verify Conda Python: %s", str(e))
            return None
    logger.warning("Conda Python not found at %s", python_path)
    return None

def check_conda_installed() -> bool:
    """Check if Conda is installed by running 'conda --version'."""
    try:
        result = subprocess.run(
            ['conda', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        print(f"Conda is installed: {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print("Conda is not installed or not found in PATH.")
        logger.error("Conda check failed: %s", str(e))
        return False

def check_trellis_environment() -> bool:
    """Check if a Conda environment named 'trellis' exists."""
    python_path = get_conda_python_path()
    if python_path:
        print(f"Conda environment 'trellis' exists. Python executable: {python_path}")
        return True
    else:
        print("Conda environment 'trellis' does not exist.")
        return False

def install_trellis_conda_packages() -> bool:
    """Install nvidia::cuda-runtime and nvidia::cuda-nvcc in the trellis environment."""
    print("Installing packages in 'trellis' environment...")
    try:
        result = subprocess.run(
            [
                'conda', 'install', '-n', 'trellis', '-c', 'nvidia',
                'cuda-runtime', 'cuda-nvcc', '-y'
            ],
            capture_output=True,
            text=True,
            check=True
        )
        print("Successfully installed nvidia::cuda-runtime and nvidia::cuda-nvcc.")
        logger.info("Conda install output: %s", result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e.stderr}")
        logger.error("Failed to install packages: %s", e.stderr)
        return False
    except FileNotFoundError:
        print("Conda is not installed or not found in PATH.")
        logger.error("Conda not found during package installation")
        return False

def main():
    """Main function to execute Git clone, file replacement, Conda checks, and package installation."""
    # Step 1: Clone the repository
    print("Cloning repository...")
    clone_success = clone_repository(gHubURL, target_dir)

    # Step 2: Replace the file if applicable
    print("\nChecking and replacing file...")
    target_file = target_dir / 'trellis' / 'trellis' / 'representations' / 'mesh' / 'flexicubes' / 'flexicubes.py'
    patch_file = target_dir / 'patchfiles' / 'flexicubes.py'
    replace_file(target_file, patch_file)

    # Step 3: Check Conda and trellis environment
    print("\nChecking for Conda installation...")
    conda_installed = check_conda_installed()
    if conda_installed:
        print("\nChecking for 'trellis' environment...")
        trellis_exists = check_trellis_environment()

        # Step 4: If conda trellis environment does not exist, create it
        if not trellis_exists:
            print("\nCreating 'trellis' environment...")
            try:
                subprocess.run(['conda', 'create', '-n', 'trellis', 'python=3.8', '-y'], check=True)
                print("Successfully created 'trellis' environment.")
            except subprocess.CalledProcessError as e:
                print(f"Error creating 'trellis' environment: {e.stderr}")
                logger.error("Failed to create trellis environment: %s", e.stderr)
                return

        # Step 5: Install packages in trellis environment
        print("\nInstalling packages in trellis environment...")
        install_trellis_conda_packages()

if __name__ == "__main__":
    main()