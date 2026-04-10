# Whispefy

Whispefy is a small Linux voice-dictation app for Hyprland.
It works like a Whisperflow-style flow:

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
git clone https://github.com/SamTheTechi/whispefy.git
cd whispefy
uv sync
cp example.env .env
```

Edit `.env` and set `GROQ_API_KEY`.

### Quick Run

```bash
uv run whispefy
```

## Hotkey Setup

Bind a Hyprland key on your hyprland config file to toggle the local endpoint:

```conf
bind = Super, E, exec, curl -X POST http://127.0.0.1:8764/toggle
```

## Start on Hyprland Launch

If you want to start Whispefy directly from Hyprland without a systemd service, use the bundled launcher:

```conf
exec-once = sh -c '/<PATH>/whispefy/scripts/start.sh >> /tmp/whispefy.log 2>&1'
```

The start script is just a thin wrapper around `uv run whispefy`.


## Start as Systemd Service

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

## Notes

- Clipboard insertion uses `wl-copy`.
- Paste injection uses `wtype`.
- Notifications use `notify-send`.
- Silence detection uses an adaptive RMS threshold, not WebRTC VAD.
- The app is targeted at Python 3.13.
- You can inspect logs using cat /tmp/whispefy.log

## License

GPL-3.0-or-later. See [LICENSE].
