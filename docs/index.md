<div class="whispefy-hero">

# Whispefy

Whispefy is a small Linux dictation app for Hyprland.

It listens from a hotkey or local HTTP trigger, stops on silence, sends audio to Groq Whisper, cleans the transcript with LangChain, and pastes the final text into the focused window.

</div>

## Flow

<div class="whispefy-grid">
<div class="whispefy-card">

### Trigger

Use a hotkey or `POST /toggle` to start a session.

</div>
<div class="whispefy-card">

### Record

Mic input runs locally until silence ends the capture.

</div>
<div class="whispefy-card">

### Clean

Groq Whisper transcribes, then LangChain refines the text.

</div>
<div class="whispefy-card">

### Insert

The final text is inserted into the focused Wayland window.

</div>
</div>

<div class="whispefy-callout">

Use this as a local desktop tool, not a cloud editor. The app keeps the control loop on your machine and only sends audio/text to Groq.

</div>

## What You Need

- Linux with Wayland
- Hyprland or another Wayland compositor
- `uv`
- `wl-copy`
- `wtype`
- `notify-send`
