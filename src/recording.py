"""Bounded microphone capture with speech detection."""
from collections import deque
import math
import os
import selectors
import subprocess
import tempfile
import time

import webrtcvad

SAMPLE_RATE = 16000
FRAME_MS = 30
FRAME_BYTES = SAMPLE_RATE * FRAME_MS // 1000 * 2


class SpeechSegment:
    def __init__(self, settings):
        self.settings = settings
        self.pending = deque(maxlen=max(5, math.ceil(settings["pre_roll_ms"] / FRAME_MS)))
        self.recent = deque(maxlen=5)
        self.frames = []
        self.started = False
        self.voiced_ms = 0
        self.silence_ms = 0

    def feed(self, frame, voiced):
        """Return True when an utterance reaches silence or its size limit."""
        if not self.started:
            self.pending.append((frame, voiced))
            self.recent.append(voiced)
            if sum(self.recent) < 3:
                return False
            self.started = True
            self.frames = [audio for audio, _ in self.pending]
            self.voiced_ms = sum(speech for _, speech in self.pending) * FRAME_MS
            self.pending.clear()
        else:
            self.frames.append(frame)
            if voiced:
                self.voiced_ms += FRAME_MS

        self.silence_ms = 0 if voiced else self.silence_ms + FRAME_MS
        return (self.silence_ms >= self.settings["silence_ms"]
                or len(self.frames) * FRAME_MS >= self.settings["max_seconds"] * 1000)

    def audio(self):
        if self.voiced_ms < self.settings["min_speech_ms"]:
            return b""
        return b"".join(self.frames)


def record_pcm(device, settings, stop_event):
    """Return speech PCM, or empty bytes for silence/cancellation."""
    if stop_event.is_set():
        return b""
    vad = webrtcvad.Vad(settings["vad_mode"])
    segment = SpeechSegment(settings)
    # stderr uses a file so a noisy device cannot fill a pipe and deadlock.
    with tempfile.TemporaryFile() as errors:
        process = subprocess.Popen(
            ["arecord", "-q", "-D", device, "-t", "raw", "-f", "S16_LE",
             "-r", str(SAMPLE_RATE), "-c", "1"],
            stdout=subprocess.PIPE, stderr=errors,
        )
        try:
            os.set_blocking(process.stdout.fileno(), False)
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                pending = bytearray()
                began = last_audio = time.monotonic()
                speech_began = None
                frames_seen = 0
                while not stop_event.is_set():
                    now = time.monotonic()
                    if speech_began is None:
                        if (now - began >= settings["start_timeout_seconds"]
                                or frames_seen * FRAME_MS >= settings["start_timeout_seconds"] * 1000):
                            return b""
                    elif now - speech_began >= settings["max_seconds"]:
                        return segment.audio()
                    if now - last_audio >= 3:
                        raise RuntimeError("Microphone stopped delivering audio")
                    if not selector.select(timeout=0.1):
                        continue
                    try:
                        data = os.read(process.stdout.fileno(), FRAME_BYTES * 10)
                    except BlockingIOError:
                        continue
                    if not data:
                        if stop_event.is_set():
                            return b""
                        errors.seek(0)
                        details = errors.read().decode(errors="replace").strip()
                        raise RuntimeError(f"Microphone stream ended unexpectedly: {details}")
                    last_audio = time.monotonic()
                    pending.extend(data)
                    while len(pending) >= FRAME_BYTES:
                        if stop_event.is_set():
                            return b""
                        frame = bytes(pending[:FRAME_BYTES])
                        del pending[:FRAME_BYTES]
                        frames_seen += 1
                        done = segment.feed(frame, vad.is_speech(frame, SAMPLE_RATE))
                        if segment.started and speech_began is None:
                            speech_began = time.monotonic()
                        if done:
                            return segment.audio()
                return b""
        finally:
            if process.poll() is None:
                process.terminate()
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=1)
            process.stdout.close()