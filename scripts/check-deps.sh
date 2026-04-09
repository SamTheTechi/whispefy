#!/bin/sh
set -eu

have() {
	command -v "$1" >/dev/null 2>&1
}

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
project_dir=$(CDPATH= cd -- "$script_dir/.." && pwd)

python_bin="$project_dir/.venv/bin/python"
if [ ! -x "$python_bin" ]; then
	if [ -n "${PYTHON:-}" ]; then
		python_bin="$(command -v "$PYTHON" 2>/dev/null || true)"
	else
		python_bin="$(command -v python3 2>/dev/null || true)"
	fi
fi

os_id=""
os_like=""
if [ -r /etc/os-release ]; then
	. /etc/os-release
	os_id="${ID:-}"
	os_like="${ID_LIKE:-}"
fi

case "$os_id $os_like" in
	*arch*|*endeavouros*|*manjaro*)
		install_hint="sudo pacman -S uv wl-clipboard wtype libnotify dunst"
		;;
	*fedora*)
		install_hint="sudo dnf install uv wl-clipboard wtype libnotify dunst"
		;;
	*debian*|*ubuntu*|*linuxmint*)
		install_hint="sudo apt install uv wl-clipboard wtype libnotify-bin dunst"
		;;
	*opensuse*|*suse*)
		install_hint="sudo zypper install uv wl-clipboard wtype libnotify-tools dunst"
		;;
	*nixos*|*nix*)
		install_hint="nix profile install nixpkgs#uv nixpkgs#wl-clipboard nixpkgs#wtype nixpkgs#libnotify nixpkgs#dunst"
		;;
	*)
		install_hint="Install uv, wl-clipboard, wtype, libnotify, and dunst using your distro's package manager."
		;;
esac

missing=""
for cmd in uv wl-copy wtype notify-send dunstctl; do
	if have "$cmd"; then
		printf '[ok] %s\n' "$cmd"
	else
		printf '[missing] %s\n' "$cmd"
		missing="$missing $cmd"
	fi
done

if [ -n "${WAYLAND_DISPLAY:-}" ] || [ "${XDG_SESSION_TYPE:-}" = "wayland" ]; then
	printf '[ok] wayland session detected\n'
else
	printf '[warn] no Wayland session detected\n'
fi

python_missing=""
if [ -x "$python_bin" ]; then
	for mod in fastapi uvicorn httpx langchain_groq numpy sounddevice dotenv; do
		if "$python_bin" - <<PY >/dev/null 2>&1
import importlib.util
raise SystemExit(0 if importlib.util.find_spec("$mod") else 1)
PY
		then
			printf '[ok] python module %s\n' "$mod"
		else
			printf '[missing] python module %s\n' "$mod"
			python_missing="$python_missing $mod"
		fi
	done
else
	printf '[warn] no python interpreter available for module checks\n'
fi

if [ -n "$missing" ] || [ -n "$python_missing" ]; then
	printf '\nInstall hint for %s:\n%s\n' "${os_id:-unknown distro}" "$install_hint"
	exit 1
fi

printf '\nAll dependency checks passed.\n'
