"""Filesystem boundaries for repository writers (no dependencies)."""

import os
import tempfile
from pathlib import Path


def check_paths(root, paths):
    root = Path(root).absolute()
    for path in paths:
        path = Path(path).absolute()
        if not path.is_relative_to(root) or ".." in path.relative_to(root).parts:
            raise ValueError(f"path escapes repository: {path}")
        current = root
        for part in ("", *path.relative_to(root).parts):
            current = current / part
            if current.is_symlink():
                raise ValueError(f"symlink forbidden for repository operation: {current}")


def write_bytes(root, path, data, mode=0o644):
    """Replace a checked file atomically rather than following a leaf symlink."""
    check_paths(root, [path])
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        os.chmod(temporary, mode)
        check_paths(root, [path])
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def write_text(root, path, text):
    write_bytes(root, path, text.encode("utf-8"))
