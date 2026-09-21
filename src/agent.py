#!/usr/bin/env python3
import ollama
import yaml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
config_path = BASE_DIR / "config" / "agent.yaml"

class OllamaAgent:
    def __init__(self, model: str = None, prompt: str = None):
        with open(config_path, 'r') as f:
            self.data = yaml.safe_load(f)

        ollama_config = self.data["ollama"]
        
        self.model = model or ollama_config["model"]
        sys_prompt = prompt or ollama_config["prompt"]

        self.options = ollama_config.get("options", {})
        self.keep_alive = ollama_config.get("keep_alive", -1)

        self.history = [{"role": "system", "content": sys_prompt}]

    def reply(self, input: str) -> str:
        self.history.append({"role": "user", "content": input})

        response = ollama.chat(
            model=self.model,
            messages=self.history,
            options=self.options,
            keep_alive=self.keep_alive,
        )

        reply = response['message']['content']
        self.history.append({"role": "assistant", "content": reply})
        self.history = [self.history[0], *self.history[-6:]]
        return reply