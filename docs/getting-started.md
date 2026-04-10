# Getting Started

## Install

```bash
git clone https://github.com/SamTheTechi/whispefy.git
cd whispefy
uv sync
cp example.env .env
```

Set `GROQ_API_KEY` in `.env`.

## Run

```bash
uv run whispefy
```

## Trigger

Bind Hyprland to the local toggle endpoint:

```conf
bind = Super, E, exec, curl -X POST http://127.0.0.1:8764/toggle
```

## Launch on Login

```conf
exec-once = sh -c '/home/Asuna/Projects/macro/whispefy/start.sh >> /tmp/whispefy.log 2>&1'
```

