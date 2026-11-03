"""File path behavior for the traversal training lab."""

from pathlib import Path


def resolve_training_file(
    files_dir: str, project_dir: str, requested: str, secure: bool = False
) -> Path:
    """Resolve a file path, optionally restricting it to the download directory."""
    # VULN[traversal]
    base = Path(files_dir if secure else project_dir).resolve()
    path = (Path(files_dir) / requested).resolve()
    if path != base and base not in path.parents:
        raise ValueError("Path di luar direktori proyek tidak diizinkan")
    return path
