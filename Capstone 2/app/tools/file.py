# app/tools/file.py

from pathlib import Path


def read_file(path: str) -> str:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return file_path.read_text()


def write_file(path: str, content: str) -> str:
    file_path = Path(path)

    file_path.write_text(content)

    return f"File written successfully to {path}"