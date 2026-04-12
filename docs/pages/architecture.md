# Architecture

Whispefy is a small pipeline with one control loop:

`trigger -> record -> silence stop -> transcribe -> clean -> insert`

The cleanup path warms up its local embedding model at startup so the first
real session does not pay the download cost.

## Core Pieces

<div class="whispefy-grid">
<div class="whispefy-card">

<b>Capture</b><br>

<p>
<a href="https://github.com/SamTheTechi/whispefy/blob/master/whispefy/audio.py">whispefy/audio.py</a> reads mic input, tracks RMS levels, and stops the session when silence lasts long enough.
</p>

</div>
<div class="whispefy-card">

<b>Guardrails</b><br>

<p>
The app checks the recorded clip before transcription. If it is too short or too quiet, it skips Whisper and ends the session early.
</p>

</div>
<div class="whispefy-card">

<b>Transcribe</b><br>

<p>
<a href="https://github.com/SamTheTechi/whispefy/blob/master/whispefy/groq_pipeline.py">whispefy/groq_pipeline.py</a> sends the WAV file to Groq Whisper and returns plain transcript text.
</p>

</div>
<div class="whispefy-card">

<b>Clean</b><br>

<p>
The pipeline cleans the text with <code>ChatGroq</code>.
Then it compares the new text with the old text using local embeddings.
If the new text looks too different, Whispefy keeps the original.
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
The app also preloads the embedding model during startup.
</p>

</div>
</div>

## Guardrails

Whispefy has two simple checks.

1. Before Whisper, the clip must be long enough and loud enough.
2. Before cleanup, the text must be worth cleaning.
3. After cleanup, the new text must stay close to the old text.

The pre-Whisper gate is plain:

- minimum duration: `1.0s`
- minimum voiced content: `0.25s`
- minimum peak level: `max(40.0, noise_floor * 1.2)`

If a clip fails those checks, Whispefy skips Whisper and calls it too short or
too quiet.

The cleanup text filter is simple too. If the transcript is empty, too short,
or looks like junk, Whispefy keeps it as-is and skips the cleanup model.

The cleanup gate uses local embeddings from `BAAI/bge-small-en-v1.5`.
Whispefy compares the old text with the new text and checks cosine similarity.
The cutoff is `0.8`.

If the score is below `0.8`, Whispefy keeps the original text.

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

## Launch Paths

There are three practical ways to run it:

- `uv run whispefy` for terminal testing
- `exec-once = sh -c '/path/to/whispefy/start.sh >> /tmp/whispefy.log 2>&1'` for Hyprland autostart
- `systemd --user` for a background service

## Wayland Notes

Whispefy is designed for Hyprland on Wayland.
The insertion path relies on `wtype`, and clipboard fallback relies on `wl-copy`.
If those tools are missing, text insertion will fail even if transcription succeeds.

## Session Behavior

Whispefy does not keep mic open forever.
It starts on `POST /toggle` or the Hyprland bind.

Then it does this:

1. take audio frames
2. watch for speech
3. stop when silence comes
4. skip Whisper if the clip is too short or too quiet
5. clean the text
6. check if the new text looks too far from the old text
7. only insert if the whole thing looks good

The first check saves Groq calls.
The second check stops bad cleanup from going through.

## Failure Modes

These are the main failure points to know about when debugging:

- A too-short or too-quiet clip is filtered before Whisper by the pre-Whisper gate.
- A wrong `TRANSCRIPTION_BASE_URL` will break Groq chat calls if it does not resolve to the OpenAI-compatible base.
- Missing `wtype` or `wl-copy` will break insertion, even if transcription succeeds.
- `systemd --user` launches need the Wayland env imported, or the service may start without access to the desktop session.
- The local FastAPI server binds to `127.0.0.1`, so it is meant for local triggers only.

Treat these as operational guardrails, not app bugs, unless the app mishandles them.
