# Installation

## Install

```bash
git clone -b master https://github.com/SamTheTechi/whispefy.git
cd whispefy
uv sync
cp example.env .env
```

Edit `.env` and set `GROQ_API_KEY`.

Useful defaults to review:

- `HTTP_PORT=8764`
- `TRANSCRIPTION_BASE_URL=https://api.groq.com/openai/v1`
- `SILENCE_MS=900` or higher if you pause between words
- `LLM_MODEL=llama-3.1-8b-instant`

On the first start, Whispefy also warms up its local embedding model
(`BAAI/bge-small-en-v1.5`) so the first cleanup check does not stall on a
download.

## Run

### Quick Run

```bash
uv run whispefy
```

Use this while testing changes from a terminal.

### On Hyprland Start

If you want Whispefy to start with Hyprland without a service, place this line in your `hyprland.conf` file:

```conf
exec-once = sh -c '/path/to/whispefy/start.sh >> /tmp/whispefy.log 2>&1'
```

If your Hyprland config is split across files, add it to the main file that gets sourced at session start.

The script is just a thin wrapper around `uv run whispefy`.

### Systemd Service

This is the cleaner background setup.

Create the service file:

```bash
nano ~/.config/systemd/user/whispefy.service
```

Paste this content:

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

If Wayland env vars are missing in the service, import them from Hyprland:

```conf
exec-once = systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP XDG_SESSION_TYPE XDG_RUNTIME_DIR
exec-once = dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP XDG_SESSION_TYPE XDG_RUNTIME_DIR
```

## Trigger

Bind a Hyprland key to the local toggle endpoint:

```conf
bind = Super, E, exec, curl -X POST http://127.0.0.1:8764/toggle
```

`/toggle` starts recording when idle and stops the current session when active.

## Check Dependencies

Run the checker before first use:

```bash
./scripts/check-deps.sh
```

It verifies the shell tools, Python packages, and Wayland session bits the app needs.

## Logs

- Terminal run: logs print in the terminal
- Hyprland launch: check `/tmp/whispefy.log`
- Systemd service: use `journalctl --user -u whispefy.service -f`

## Tuning

If it stops too quickly on pauses, increase `SILENCE_MS`.
If it keeps missing your voice, increase the gain in your input device settings first, then lower the threshold only if needed.
