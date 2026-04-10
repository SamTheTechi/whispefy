# Architecture

Whispefy stays intentionally small:

- `whispefy/audio.py` handles microphone capture and silence detection.
- `whispefy/groq_pipeline.py` sends audio to Groq and cleans transcripts with LangChain.
- `whispefy/insertion.py` inserts text on Wayland using `wtype` and clipboard fallback.
- `whispefy/server.py` exposes the local FastAPI trigger.
- `whispefy/app.py` ties the flow together.

The project is structured so the core logic stays shared and the desktop integration stays thin.
