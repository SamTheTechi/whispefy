# Whispefy

Whispefy is a small Linux voice-dictation app for Hyprland.

It works like a local Whisperflow-style flow:

1. Trigger recording from a hotkey or localhost endpoint.
2. Stop automatically on silence.
3. Transcribe audio with Groq Whisper.
4. Clean the transcript with a cheap Groq chat model.
5. Paste the final text into the focused window.

## Requirements

- Linux with a Wayland session
- Hyprland or another Wayland compositor
- `uv`
- `fastapi` and `uvicorn` are installed through `uv sync`
- `wl-copy`
- `wtype`
- `notify-send`
- `dunstctl`

## Install

```bash
git clone <repo-url>
cd whispefy
uv sync
cp .env.example .env
```

Edit `.env` and set `GROQ_API_KEY`.

## Run

```bash
uv run whispefy
```

## Hyprland Launch Script

If you want to start Whispefy directly from Hyprland without a systemd service, use the bundled launcher:

```conf
exec-once = /<PATH>/whispefy/start.sh
```

The script is just a thin wrapper around `uv run whispefy`.

## Start On Login

The recommended setup is a `systemd --user` service. It keeps Whispefy running in the background and is easier to restart or inspect than a compositor-only launch.

Create `~/.config/systemd/user/whispefy.service`:

```ini
[Unit]
Description=Whispefy desktop dictation
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
WorkingDirectory=/path/to/whispefy
ExecStart=uv run whispefy
Restart=on-failure
RestartSec=2

[Install]
WantedBy=default.target
```

Enable and start it:

```bash
systemctl --user daemon-reload
systemctl --user enable --now whispefy.service
```

If your session does not inherit the Wayland environment automatically, add this to your Hyprland config:

```conf
exec-once = systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP XDG_SESSION_TYPE XDG_RUNTIME_DIR
exec-once = dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP XDG_SESSION_TYPE XDG_RUNTIME_DIR
```

If you want the simplest possible launch path instead of a service, you can also use:

```conf
exec-once = systemctl --user start whispefy.service
```

## Check Dependencies

Use the bundled checker before first run:

```bash
./scripts/check-deps.sh
```

It checks the shell tools, the Python modules, and prints install hints for common Hyprland-capable distros.

## Hotkey Example

Bind a Hyprland key to toggle the local endpoint:

```conf
bind = CTRL, SPACE, exec, curl -s -X POST http://127.0.0.1:8764/toggle
```

## Configuration

Environment variables live in `.env`.

- `GROQ_API_KEY`: Groq API key
- `HTTP_PORT`: local HTTP port, default `8764`
- `SAMPLE_RATE`: mic sample rate, default `16000`
- `FRAME_MS`: audio frame length, default `20`
- `SILENCE_MS`: silence cutoff, default `1200`
  - Increase this if the app stops too quickly on short pauses.
  - Example: `SILENCE_MS=1500` waits longer before ending recording.
- `TRANSCRIPTION_MODEL`: Groq transcription model, default `whisper-large-v3-turbo`
- `TRANSCRIPTION_BASE_URL`: Groq API base URL for transcription, default `https://api.groq.com/openai/v1`
- `TRANSCRIPTION_TIMEOUT_SECONDS`: transcription request timeout, default `60.0`
- `TRANSCRIPTION_NAME`: label used in logs and notifications, default `groq-whisper-stt`
- `LLM_MODEL`: Groq chat model, default `llama-3.1-8b-instant`
- `LANGUAGE`: transcription language, default `en`
- `LLM_TEMPERATURE`: cleanup model temperature, default `0.0`
- `NOTIFICATION_DURATION_MS`: notification lifetime, default `1600`

## Notes

- Clipboard insertion uses `wl-copy`.
- Paste injection uses `wtype`.
- Notifications use `notify-send`.
- Silence detection uses an adaptive RMS threshold, not WebRTC VAD.
- The app is targeted at Python 3.13.

## Development

Run tests:

```bash
uv run python -m unittest discover -s tests -v
```

Check formatting/syntax:

```bash
python3 -m compileall whispefy tests
```

## License

GPL-3.0-or-later. See [LICENSE].
