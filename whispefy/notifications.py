from __future__ import annotations

import logging
import subprocess

logger = logging.getLogger(__name__)


def notify(text: str, duration_ms: int = 1600, urgency: str = "normal") -> None:
    cmd = [
        "notify-send",
        "--urgency",
        urgency,
        "--hint",
        f"int:expire-time:{duration_ms}",
        text,
    ]
    try:
        subprocess.run(cmd, capture_output=True, check=False)
    except FileNotFoundError:
        logger.info(text)
