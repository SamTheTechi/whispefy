# Architecture

Whispefy is a small pipeline with one control loop:

`trigger -> record -> silence stop -> transcribe -> clean -> insert`

## Core Pieces

<div class="whispefy-grid">
<div class="whispefy-card">

<b>Capture</b><br>

<p>
<a href="https://github.com/SamTheTechi/whispefy/blob/master/whispefy/audio.py">whispefy/audio.py</a> reads mic input, tracks RMS levels, and stops the session when silence lasts long enough.
</p>

</div>
<div class="whispefy-card">

<b>Processing</b><br>

<p>
<a href="https://github.com/SamTheTechi/whispefy/blob/master/whispefy/groq_pipeline.py">whispefy/groq_pipeline.py</a> sends the WAV file to Groq Whisper and then runs a small LangChain cleanup pass with <code>ChatGroq</code>.
</p>

</div>
<div class="whispefy-card">

<b>Insert</b><br>

<p>
<a href="https://github.com/SamTheTechi/whispefy/blob/master/whispefy/insertion.py">whispefy/insertion.py</a> types text directly with <code>wtype</code>, then falls back to clipboard paste if direct typing fails.
</p>

</div>
<div class="whispefy-card">

<b>Control</b><br>

<p>
<a href="https://github.com/SamTheTechi/whispefy/blob/master/whispefy/app.py">whispefy/app.py</a> owns the session state, while
<a href="https://github.com/SamTheTechi/whispefy/blob/master/whispefy/server.py">whispefy/server.py</a> exposes the local FastAPI trigger endpoints.
</p>

</div>
</div>

## Config

The app reads runtime settings from `.env` through [`whispefy/config.py`](https://github.com/SamTheTechi/whispefy/blob/master/whispefy/config.py).

Important values:

- `HTTP_PORT` controls the local server port
- `SILENCE_MS` controls how long silence ends a session
- `TRANSCRIPTION_BASE_URL` should stay on Groq's OpenAI-compatible base
- `TRANSCRIPTION_MODEL` defaults to `whisper-large-v3-turbo`
- `LLM_MODEL` controls the cleanup model

## API Endpoints

The FastAPI server lives in [`whispefy/server.py`](https://github.com/SamTheTechi/whispefy/blob/master/whispefy/server.py) and binds to `127.0.0.1`.

- `GET /health` checks that the local server is alive
- `POST /toggle` starts recording when idle, or stops the current session when active
- `POST /stop` forces the current session to stop

Use `HTTP_PORT` if you need to change the local port. The default is `8764`.

## Session Behavior

The app does not keep a long-running audio stream open forever.
It starts recording on `POST /toggle` or the Hyprland bind, then:

1. buffers frames locally
2. watches for speech
3. stops on silence
4. skips transcription if no speech was detected
5. logs and inserts only after the full pipeline succeeds

Expected no-speech cases are treated as a normal cancel path, not a crash.

## Launch Paths

There are three practical ways to run it:

- `uv run whispefy` for terminal testing
- `exec-once = sh -c '/path/to/whispefy/start.sh >> /tmp/whispefy.log 2>&1'` for Hyprland autostart
- `systemd --user` for a background service

## Wayland Notes

Whispefy is designed for Hyprland on Wayland.
The insertion path relies on `wtype`, and clipboard fallback relies on `wl-copy`.
If those tools are missing, text insertion will fail even if transcription succeeds.

## Failure Modes

These are the main failure points to know about when debugging:

- `No speech detected` is a normal cancel path from [`whispefy/audio.py`](https://github.com/SamTheTechi/whispefy/blob/master/whispefy/audio.py), not a crash.
- A wrong `TRANSCRIPTION_BASE_URL` will break Groq chat calls if it does not resolve to the OpenAI-compatible base.
- Missing `wtype` or `wl-copy` will break insertion, even if transcription succeeds.
- `systemd --user` launches need the Wayland env imported, or the service may start without access to the desktop session.
- The local FastAPI server binds to `127.0.0.1`, so it is meant for local triggers only.

Treat these as operational guardrails, not app bugs, unless the app mishandles them.
