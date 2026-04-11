<div class="whispefy-hero">

<h1>Whispefy</h1>

<p>
Whispefy is a small Linux dictation app for Hyprland.
It listens from a hotkey or local HTTP trigger, stops on silence, sends audio to Groq Whisper, cleans the transcript with LangChain, and pastes the final text into the focused window.
</p>

</div>

<div class="whispefy-quickstart">

<div class="whispefy-quickstart__item">
<span>1</span>
<strong>Install</strong>
<p>`uv sync` and set `GROQ_API_KEY` in `.env`.</p>
</div>

<div class="whispefy-quickstart__item">
<span>2</span>
<strong>Launch</strong>
<p>`uv run whispefy` starts the local server and recorder.</p>
</div>

<div class="whispefy-quickstart__item">
<span>3</span>
<strong>Trigger</strong>
<p>Bind `POST /toggle` from Hyprland or call the local endpoint.</p>
</div>

</div>

## Flow

<div class="whispefy-grid">
<div class="whispefy-card">

<strong>Trigger</strong>

Use a hotkey or `POST /toggle` to start a session.

</div>
<div class="whispefy-card">

<strong>Record</strong>

Mic input runs locally until silence ends the capture.

</div>
<div class="whispefy-card">

<strong>Clean</strong>

Groq Whisper transcribes, then LangChain refines the text.

</div>
<div class="whispefy-card">

<strong>Insert</strong>

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

## What Happens

<div class="whispefy-split">
<div class="whispefy-panel">

<strong>Input</strong>

Hotkey or HTTP starts a session.

</div>
<div class="whispefy-panel">

<strong>Silence</strong>

The recorder stops when speech drops off.

</div>
<div class="whispefy-panel">

<strong>Output</strong>

The cleaned text goes straight to the cursor.

</div>
</div>
