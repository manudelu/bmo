#!/usr/bin/env bash
set -Eeuo pipefail

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly VENV_DIR="${BMO_VENV_DIR:-${SCRIPT_DIR}/.venv}"
readonly PYTHON_BIN="${PYTHON_BIN:-python3}"
readonly WHISPER_DIR="${SCRIPT_DIR}/third_party/whisper.cpp"
readonly PIPER_DIR="${SCRIPT_DIR}/models/piper"

log() { printf '\n==> %s\n' "$*"; }
fail() { printf '\n%s\n' "$*" >&2; exit 1; }

[[ "$(uname -s)" == Linux ]] || fail "Setup supports Linux only (including WSL)."
case "$(uname -m)" in
    x86_64|aarch64) ;;
    *) fail "Use a 64-bit OS: x86_64 or aarch64 (Raspberry Pi OS 64-bit)." ;;
esac
command -v apt-get >/dev/null || fail "Setup requires an apt-based distribution."

if [[ ${EUID} -eq 0 ]]; then
    SUDO=()
elif command -v sudo >/dev/null; then
    SUDO=(sudo)
else
    fail "sudo is required to install system packages."
fi

log "Installing build tools, Python, and audio utilities"
"${SUDO[@]}" apt-get update
"${SUDO[@]}" apt-get install -y \
    git build-essential cmake curl ca-certificates zstd \
    python3 python3-venv python3-dev \
    alsa-utils libasound2-plugins pulseaudio-utils

command -v "${PYTHON_BIN}" >/dev/null || fail "Python not found: ${PYTHON_BIN}"
"${PYTHON_BIN}" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' \
    || fail "BMO requires Python 3.10 or newer. Set PYTHON_BIN to a supported interpreter."

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
    log "Creating virtual environment at ${VENV_DIR}"
    "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi
readonly VENV_PYTHON="${VENV_DIR}/bin/python"
"${VENV_PYTHON}" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' \
    || fail "The existing virtual environment needs Python 3.10 or newer."

log "Installing Python dependencies"
# Pygame 2.6.1 imports pkg_resources, supplied by older setuptools.
"${VENV_PYTHON}" -m pip install --upgrade pip "setuptools<81" wheel
"${VENV_PYTHON}" -m pip install -r "${SCRIPT_DIR}/requirements.txt"

log "Initializing the pinned Whisper submodule"
git -C "${SCRIPT_DIR}" submodule update --init --recursive -- third_party/whisper.cpp

log "Building Whisper for this machine"
cmake -S "${WHISPER_DIR}" -B "${WHISPER_DIR}/build" -DCMAKE_BUILD_TYPE=Release
cmake --build "${WHISPER_DIR}/build" --parallel 4

log "Downloading Whisper base.en model"
if [[ ! -s "${WHISPER_DIR}/models/ggml-base.en.bin" ]]; then
    sh "${WHISPER_DIR}/models/download-ggml-model.sh" base.en
else
    log "Whisper model already present"
fi

log "Downloading Piper voice"
mkdir -p "${PIPER_DIR}"
if [[ ! -s "${PIPER_DIR}/en_US-lessac-medium.onnx" || \
      ! -s "${PIPER_DIR}/en_US-lessac-medium.onnx.json" ]]; then
    "${VENV_PYTHON}" -m piper.download_voices en_US-lessac-medium --data-dir "${PIPER_DIR}"
else
    log "Piper voice already present"
fi

if ! command -v ollama >/dev/null; then
    log "Installing Ollama"
    # pipefail prevents a failed download from being reported as success.
    curl --fail --show-error --silent --location https://ollama.com/install.sh | sh
fi

OLLAMA_URL="${OLLAMA_HOST:-http://127.0.0.1:11434}"
[[ "${OLLAMA_URL}" == *://* ]] || OLLAMA_URL="http://${OLLAMA_URL}"
if ! curl --fail --silent --max-time 3 "${OLLAMA_URL%/}/api/tags" >/dev/null; then
    if command -v systemctl >/dev/null && systemctl cat ollama.service >/dev/null 2>&1; then
        log "Starting Ollama service"
        "${SUDO[@]}" systemctl start ollama.service
    fi
    ollama_ready=false
    for attempt in {1..10}; do
        if curl --fail --silent --max-time 3 "${OLLAMA_URL%/}/api/tags" >/dev/null; then
            ollama_ready=true
            break
        fi
        sleep 1
    done
    if [[ "${ollama_ready}" != true ]]; then
        fail "Ollama is unreachable at ${OLLAMA_URL}. Start 'ollama serve' in another terminal, check OLLAMA_HOST, then rerun ./setup.sh."
    fi
fi

OLLAMA_MODEL="$("${VENV_PYTHON}" - "${SCRIPT_DIR}/config/agent.yaml" <<'CONFIG_PY'
import sys
import yaml
with open(sys.argv[1]) as config_file:
    print(yaml.safe_load(config_file)["ollama"]["model"])
CONFIG_PY
)"
readonly OLLAMA_MODEL
log "Downloading configured Ollama model ${OLLAMA_MODEL}"
ollama pull "${OLLAMA_MODEL}"

printf '\nSetup complete. Run BMO with:\n  %q %q\n' "${VENV_PYTHON}" "${SCRIPT_DIR}/src/fsm.py"
if [[ -n "${PULSE_SERVER:-}" ]]; then
    printf '\nFor the WSLg microphone, prefix that command with:\n  PULSE_SOURCE=RDPSource BMO_CAPTURE_DEVICE=pulse BMO_PLAYER=paplay\n'
fi