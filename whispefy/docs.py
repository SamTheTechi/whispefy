from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def build_docs() -> None:
    root = Path(__file__).resolve().parent.parent
    config = root / "docs" / "mkdocs.yml"
    docs_root = config.parent
    subprocess.run(
        [sys.executable, "-m", "mkdocs", "build", "-f", "mkdocs.yml"],
        check=True,
        cwd=docs_root,
    )
