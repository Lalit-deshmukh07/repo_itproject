import os
import sys
from pathlib import Path


def _ensure_project_environment():
    try:
        import flask  # noqa: F401
    except ModuleNotFoundError:
        venv_python = Path(__file__).resolve().parent / '.venv' / 'bin' / 'python'
        if venv_python.exists():
            print(f'Launching with project virtual environment: {venv_python}')
            os.execv(str(venv_python), [str(venv_python), str(Path(__file__))] + sys.argv[1:])
        raise


_ensure_project_environment()

from backend.app import app


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

