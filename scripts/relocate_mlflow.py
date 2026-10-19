"""Make SQLite MLflow artifact URIs portable after moving this repository."""

import sqlite3
import sys
from pathlib import Path
from urllib.parse import quote

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE = PROJECT_ROOT / "mlflow.db"
MLRUNS_URI = "file:///" + quote(str((PROJECT_ROOT / "mlruns").resolve()).replace("\\", "/"))


def _portable_uri(old_uri: str) -> str:
    """Retain the portion below ``mlruns`` while swapping the machine prefix."""
    normalized = old_uri.replace("\\", "/")
    marker = "/mlruns/"
    suffix = normalized.split(marker, 1)[1] if marker in normalized else ""
    return f"{MLRUNS_URI}/{suffix}".rstrip("/")


def relocate(database: Path = DATABASE) -> int:
    """Rewrite known MLflow artifact locations; returns number of affected rows."""
    if not database.exists():
        raise FileNotFoundError(f"MLflow database not found: {database}")
    with sqlite3.connect(database) as connection:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        changed = 0
        for table, column in [("experiments", "artifact_location"), ("runs", "artifact_uri"),
                              ("logged_models", "artifact_location")]:
            if table not in tables:
                continue
            columns = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
            if column in columns:
                rows = connection.execute(f"SELECT rowid, {column} FROM {table}").fetchall()
                for rowid, old_uri in rows:
                    new_uri = _portable_uri(old_uri)
                    if old_uri != new_uri:
                        connection.execute(f"UPDATE {table} SET {column} = ? WHERE rowid = ?", (new_uri, rowid))
                        changed += 1
        connection.commit()
    return changed


if __name__ == "__main__":
    count = relocate()
    print(f"MLflow artifact URI set to {MLRUNS_URI} ({count} row(s) updated)")
