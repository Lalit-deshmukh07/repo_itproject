from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DB_PATH = ROOT_DIR / 'instance'
SESSION_PATH = DB_PATH / 'sessions'
