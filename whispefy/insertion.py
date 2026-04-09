from __future__ import annotations

import shutil
import subprocess


class WaylandInserter:
    def copy_to_clipboard(self, text: str) -> None:
        if shutil.which("wl-copy") is None:
            raise RuntimeError("wl-copy is not installed")
        print("[Whispefy] copying to clipboard", flush=True)
        subprocess.run(
            ["wl-copy", "--type", "text/plain"],
            input=text.encode("utf-8"),
            check=True,
        )

    def paste(self) -> None:
        if shutil.which("wtype") is None:
            raise RuntimeError("wtype is not installed")
        print("[Whispefy] pasting from clipboard", flush=True)
        subprocess.run(["wtype", "-M", "ctrl", "-k", "v", "-m", "ctrl"], check=True)

    def type_text(self, text: str) -> None:
        if shutil.which("wtype") is None:
            raise RuntimeError("wtype is not installed")
        print("[Whispefy] typing text directly", flush=True)
        subprocess.run(["wtype", "-"], input=text.encode("utf-8"), check=True)

    def insert(self, text: str) -> None:
        try:
            self.type_text(text)
        except Exception as exc:
            print(f"[Whispefy] direct typing failed, falling back to clipboard paste: {exc}", flush=True)
            self.copy_to_clipboard(text)
            self.paste()
