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
    seconds = config["speech"]["record_seconds"]
    if type(seconds) is not int or seconds < 1:
        raise ValueError("speech.record_seconds must be a positive integer")
    return config
