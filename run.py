import os
from pathlib import Path
import subprocess
import sys


ROOT_DIR = Path(__file__).resolve().parent
VENV_DIR = ROOT_DIR / ".venv"
REQUIREMENTS_FILE = ROOT_DIR / "requirements.txt"


def main():
    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10 or newer is required.")

    if os.name == "nt":
        venv_python = VENV_DIR / "Scripts" / "python.exe"
    else:
        venv_python = VENV_DIR / "bin" / "python"

    if not venv_python.exists():
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)

    flask_check = subprocess.run(
        [str(venv_python), "-c", "import flask"],
        cwd=ROOT_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if flask_check.returncode != 0:
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)],
            cwd=ROOT_DIR,
            check=True,
        )

    subprocess.run([str(venv_python), str(ROOT_DIR / "app.py")], cwd=ROOT_DIR, check=True)


if __name__ == "__main__":
    main()
