import shutil
from pathlib import Path


class TempFileManager:
    """
    Context manager that tracks temporary paths and removes them on exit.

    Usage::

        with TempFileManager() as tmp:
            path = tmp.register(some_path)
            ...
        # path is deleted here
    """

    def __init__(self) -> None:
        self._paths: list[Path] = []

    def register(self, path: Path) -> Path:
        """Track *path* for deletion; returns *path* unchanged for convenience."""
        self._paths.append(path)
        return path

    def cleanup(self) -> None:
        """Delete all registered paths (files and directories)."""
        for path in self._paths:
            try:
                if path.is_file():
                    path.unlink(missing_ok=True)
                elif path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
            except OSError:
                pass
        self._paths.clear()

    def __enter__(self) -> "TempFileManager":
        return self

    def __exit__(self, *_: object) -> None:
        self.cleanup()
