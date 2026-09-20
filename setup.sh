#!/usr/bin/env bash
set -Eeuo pipefail

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly VENV_DIR="${BMO_VENV_DIR:-${SCRIPT_DIR}/venv}"
readonly PYTHON_BIN="${PYTHON_BIN:-python3.10}"
readonly OLLAMA_MODEL="${OLLAMA_MODEL:-llama3.2:1b}"
readonly RVC_DIR="${SCRIPT_DIR}/rvc_models"
readonly RVC_ARCHIVE="${RVC_DIR}/BMO.zip"
readonly RVC_URL="https://huggingface.co/Freaky98/CGO-adventure-time-BMO-rvc-v2-420e/resolve/main/CGO-adventure-time-BMO-rvc-v2-420e.zip"

log() {
    printf '\n==> %s\n' "$*"
}

if [[ "$(uname -s)" != "Linux" ]]; then
    printf 'This installer currently supports Linux only.\n' >&2
    exit 1
fi

if ! command -v apt-get >/dev/null 2>&1; then
    printf 'This installer requires an apt-based distribution.\n' >&2
    exit 1
fi

if [[ ${EUID} -eq 0 ]]; then
    SUDO=()
elif command -v sudo >/dev/null 2>&1; then
    SUDO=(sudo)
else
    printf 'sudo is required to install system packages.\n' >&2
    exit 1
fi

log "Installing system dependencies"
"${SUDO[@]}" apt-get update
"${SUDO[@]}" apt-get install -y \
    software-properties-common curl unzip ffmpeg alsa-utils flac \
    portaudio19-dev python3-dev mpg321

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
    log "Installing Python 3.10"
    "${SUDO[@]}" add-apt-repository ppa:deadsnakes/ppa -y
    "${SUDO[@]}" apt-get update
    "${SUDO[@]}" apt-get install -y python3.10 python3.10-dev python3.10-venv
fi

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
    log "Creating Python virtual environment at ${VENV_DIR}"
    "${PYTHON_BIN}" -m venv "${VENV_DIR}"
else
    log "Virtual environment already exists; skipping creation"
fi
readonly VENV_PYTHON="${VENV_DIR}/bin/python"

log "Installing Python dependencies"
"${VENV_PYTHON}" -m pip install --upgrade "pip<24.1" "setuptools<81" wheel
"${VENV_PYTHON}" -m pip install \
    torch==2.5.1 torchaudio==2.5.1 \
    --index-url https://download.pytorch.org/whl/cpu
"${VENV_PYTHON}" -m pip install -r "${SCRIPT_DIR}/requirements.txt"

if ! command -v ollama >/dev/null 2>&1; then
    log "Installing Ollama"
    curl --fail --show-error --silent --location \
        https://ollama.com/install.sh | sh
fi

log "Downloading Ollama model ${OLLAMA_MODEL}"
ollama pull "${OLLAMA_MODEL}"

if [[ ! -f "${RVC_DIR}/CGO_e420_s2520.pth" ]]; then
    log "Downloading BMO voice model"
    mkdir -p "${RVC_DIR}"
    curl --fail --location --output "${RVC_ARCHIVE}" "${RVC_URL}"
    unzip -o "${RVC_ARCHIVE}" -d "${RVC_DIR}"
    rm -f -- "${RVC_ARCHIVE}"
else
    log "BMO voice model already present; skipping download"
fi

printf '\nInstallation complete.\nActivate the environment with:\n  source %q/bin/activate\n' "${VENV_DIR}"
printf 'Run BMO with:\n  python %q/src/bmo_brain.py\n' "${SCRIPT_DIR}"