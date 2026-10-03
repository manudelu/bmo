#!/usr/bin/env python3
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "agent.yaml"

def load_config(path=CONFIG_PATH):
    with Path(path).open() as config_file:
        config = yaml.safe_load(config_file)

    for section, key in (("whisper", "model"), ("piper", "voice")):
        name = config["speech"][section][key]
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", name):
            raise ValueError(f"speech.{section}.{key} must be a model name, not a path")
        
    threads = config["speech"]["whisper"]["threads"]
    if type(threads) is not int or threads < 1:
        raise ValueError("speech.whisper.threads must be a positive integer")
    
    recording = config["speech"]["recording"]
    for key in ("start_timeout_seconds", "max_seconds", "silence_ms", "min_speech_ms"):
        value = recording[key]
        if type(value) is not int or value < 1:
            raise ValueError(f"speech.recording.{key} must be a positive integer")
    for key, maximum in (("pre_roll_ms", recording["max_seconds"] * 1000), ("vad_mode", 3)):
        value = recording[key]
        if type(value) is not int or not 0 <= value <= maximum:
            raise ValueError(f"speech.recording.{key} must be between 0 and {maximum}")
        
    if recording["min_speech_ms"] > recording["max_seconds"] * 1000:
        raise ValueError("speech.recording.min_speech_ms exceeds max_seconds")
    
    return config