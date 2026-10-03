BMO - Adventure Time AI Agent
=============================

<p align="center">
  <img src="images/BMO_front.png" alt="Fusion 360 - BMO Front" width="45%">
  <img src="images/BMO_back.png" alt="Fusion 360 - BMO Back" width="48.7%">
</p>


Electronics
------------------------

* Raspberry Pi 5 (w/ active cooler)
* Freenove 5 inch touchscreen monitor
* Camera Module 3 Wide NoIR

Future Additions
------------------

* USB microphone
* Speaker
* Custom PCB for button control (using Raspberry Pi 5 GPIO)
* Raspberry Pi AI HAT+ 2 (Hailo-10H AI accelerator and 8GB of on‑board RAM)


Setup
------------

Target: Raspberry Pi 5 with 8 GB RAM and Raspberry Pi OS 64-bit.


```bash
git clone --recurse-submodules <repository-url> bmo
cd bmo
./setup.sh
```

For an existing checkout, just run `./setup.sh`. It:

- Creates or reuses `.venv/` using the system `python3`.
- Installs the Python dependencies in `requirements.txt`.
- Builds `third_party/whisper.cpp` for the current machine.
- Downloads Whisper `base.en` and Piper `en_US-lessac-medium` if missing.
- Installs Ollama if needed and downloads the model in `config/agent.yaml`.

If Ollama is not running and no systemd service is available, start
`ollama serve` in another terminal and rerun setup.

Run BMO
------------

```bash
.venv/bin/python src/fsm.py
```

Focus the BMO window and press Space. Speak within the five-second recording
window. BMO transcribes with Whisper, asks Ollama, generates speech with Piper,
and returns to idle after playback. Escape, Q, or closing the window exits.
Recording and inference run in workers so face animations remain responsive.

On the Pi, `arecord` and `aplay` use the default ALSA devices. To select a
microphone, find its card/device with `arecord -l`, then use, for example:

```bash
BMO_CAPTURE_DEVICE=plughw:2,0 .venv/bin/python src/fsm.py
```

Replace `2,0` with your microphone's actual card and device numbers.
`BMO_PLAYER` selects the playback executable; playback uses that player's
default output device.

Models and configuration
------------

- `config/agent.yaml`: Ollama model, prompt, and generation settings. Setup
  downloads this exact model. The current setting is `llama3.2:3b`; for a
  lighter Pi baseline, set it to `llama3.2:1b` and rerun setup.
- `third_party/whisper.cpp/models/ggml-base.en.bin`: current English
  speech-recognition model. Its runtime path is in `src/speech.py`.
- `models/piper/en_US-lessac-medium.onnx` and its `.onnx.json` file:
  current English voice. Its runtime path is also in `src/speech.py`.

Upstream documentation:
[Whisper](https://github.com/ggml-org/whisper.cpp),
[Piper](https://github.com/OHF-Voice/piper1-gpl),
[Ollama Linux setup](https://docs.ollama.com/linux).