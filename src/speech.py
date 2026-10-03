#!/usr/bin/env python3
import io
import os
import subprocess
import tempfile
import wave
from pathlib import Path

from piper import PiperVoice
from bmo_config import load_config


ROOT = Path(__file__).resolve().parent.parent

class Speech:
    def __init__(self):
        config = load_config()["speech"]
        self.record_seconds = config["record_seconds"]
        self.language = config["whisper"]["language"]
        self.threads = config["whisper"]["threads"]
        self.whisper = (
            ROOT / "third_party/whisper.cpp/build/bin/whisper-cli"
        )
        self.whisper_model = (
            ROOT / "third_party/whisper.cpp/models"
            / f"ggml-{config['whisper']['model']}.bin"
        )
        self.voice_model = (
            ROOT / "models/piper" / f"{config['piper']['voice']}.onnx"
        )

        self.capture_device = os.getenv(
            "BMO_CAPTURE_DEVICE",
            "pulse" if os.getenv("PULSE_SERVER") else "default",
        )
        self.player = os.getenv(
            "BMO_PLAYER",
            "paplay" if os.getenv("PULSE_SERVER") else "aplay",
        )
        self.voice = None

    def listen(self):
        with tempfile.TemporaryDirectory(prefix="bmo-listen-") as folder:
            folder = Path(folder)
            recording = folder / "input.wav"
            transcript = folder / "transcript"

            print(f"Listening for {self.record_seconds} seconds...")
            subprocess.run(
                [
                    "arecord",
                    "-D", self.capture_device,
                    "-f", "S16_LE",
                    "-r", "16000",
                    "-c", "1",
                    "-d", str(self.record_seconds),
                    str(recording),
                ],
                check=True,
                timeout=self.record_seconds + 5,
            )

            print("Transcribing...")
            result = subprocess.run(
                [
                    str(self.whisper),
                    "-m", str(self.whisper_model),
                    "-f", str(recording),
                    "-l", self.language,
                    "-t", str(self.threads),
                    "-ng",
                    "-otxt",
                    "-of", str(transcript),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode:
                raise RuntimeError(
                    f"Whisper failed: {result.stderr.strip()}"
                )

            text = transcript.with_suffix(".txt").read_text().strip()
            print(f"You: {text}")
            return text

    def synthesize(self, text):
        if self.voice is None:
            self.voice = PiperVoice.load(str(self.voice_model))

        audio = io.BytesIO()
        with wave.open(audio, "wb") as wav_file:
            self.voice.synthesize_wav(text, wav_file)
        return audio.getvalue()

    def play(self, audio):
        with tempfile.TemporaryDirectory(prefix="bmo-speak-") as folder:
            recording = Path(folder) / "reply.wav"
            recording.write_bytes(audio)
            subprocess.run(
                [self.player, str(recording)],
                check=True,
                timeout=120,
            )
