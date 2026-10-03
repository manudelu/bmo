#!/usr/bin/env python3
from enum import Enum, auto
from queue import Empty, Queue
from threading import Thread
import pygame

from agent import OllamaAgent
from display import Display
from speech import Speech

class BMOState(Enum):
    START = auto()
    IDLE = auto()
    LISTEN = auto()
    THINK = auto()
    SPEAK = auto()
    ERROR = auto()
    STOPPED = auto()

class BMO:
    def __init__(self):
        self.state = BMOState.START
        self.running = True

        self.input = None
        self.reply = None
        self.last_error = None

        self.display = Display()
        self.agent = OllamaAgent()
        self.speech = Speech()

        self.results = Queue()
        self.input_thread = None
        self.reply_thread = None
        self.speech_thread = None
        self.audio = None

    def transition_to(self, new_state):
        self.state = new_state

        state_faces = {
            BMOState.IDLE: "idle",
            BMOState.LISTEN: "listening",
            BMOState.THINK: "thinking",
            BMOState.SPEAK: "speaking",
            BMOState.ERROR: "error",
        }

        if new_state in state_faces:
            self.display.show(state_faces[new_state])
        if new_state == BMOState.STOPPED:
            self.running = False

    def run(self):
        try:
            self.start()
            while self.running:
                try:
                    self.handle_events()
                    if not self.running:
                        break
                    self.process_results()
                    if not self.running:
                        break
                    self.run_current_state()
                    if self.running:
                        self.display.update()

                except KeyboardInterrupt:
                    self.transition_to(BMOState.STOPPED)

                except Exception as error:
                    self.last_error = error
                    print(f"BMO error {error}")
                    self.transition_to(BMOState.ERROR)
        finally:
            self.speech.close()
            if self.input_thread is not None:
                self.input_thread.join(timeout=2)
            self.display.close()

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN
                and event.key in (pygame.K_ESCAPE, pygame.K_q)
            ):
                self.transition_to(BMOState.STOPPED)
                return

        # TODO: Substitute SPACE with buttons once the PCB arrives
        for event in events:
            if (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_SPACE
                    and self.state == BMOState.IDLE):
                self.transition_to(BMOState.LISTEN)

    def process_results(self):
        try:
            kind, value = self.results.get_nowait()
        except Empty:
            return

        if kind == "input":
            self.input_thread = None
            self.input = value.strip()
            if self.input.lower() in ("exit", "quit"):
                self.transition_to(BMOState.STOPPED)
            elif self.input:
                self.transition_to(BMOState.THINK)
            else:
                self.transition_to(BMOState.IDLE)
        elif kind == "reply":
            self.reply_thread = None
            self.reply, self.audio = value
            self.transition_to(BMOState.SPEAK)
        elif kind == "spoken":
            self.speech_thread = None
            self.input = None
            self.reply = None
            self.audio = None
            self.transition_to(BMOState.IDLE)
        elif kind == "eof":
            self.transition_to(BMOState.STOPPED)
        elif kind == "error":
            self.last_error = value
            self.transition_to(BMOState.ERROR)

    def run_current_state(self):
        if self.state == BMOState.START:
            self.start()
        elif self.state == BMOState.LISTEN:
            self.listen()
        elif self.state == BMOState.THINK:
            self.think()
        elif self.state == BMOState.SPEAK:
            self.speak()
        elif self.state == BMOState.ERROR:
            self.error()
        elif self.state == BMOState.STOPPED:
            self.running = False

    def start(self):
        print(f"Using {self.agent.model}. Press Space in the BMO window, then speak.")
        self.transition_to(BMOState.IDLE)

    def read_input(self):
        try:
            text = self.speech.listen()
            self.results.put(("input", text))
        except Exception as error:
            self.results.put(("error", error))

    def wait_for_user(self):
        if self.input_thread is None:
            self.input_thread = Thread(target=self.read_input, daemon=True)
            self.input_thread.start()

    def listen(self):
        self.wait_for_user()

    def get_reply(self):
        try:
            reply = self.agent.reply(input=self.input)
            audio = self.speech.synthesize(reply)
            self.results.put(("reply", (reply, audio)))
        except Exception as error:
            self.results.put(("error", error))

    def think(self):
        if self.reply_thread is None:
            self.reply_thread = Thread(target=self.get_reply, daemon=True)
            self.reply_thread.start()

    def speak(self):
        if self.speech_thread is None:
            print(f"BMO: {self.reply}")
            self.speech_thread = Thread(target=self.play_reply, daemon=True)
            self.speech_thread.start()

    def play_reply(self):
        try:
            self.speech.play(self.audio)
            self.results.put(("spoken", None))
        except Exception as error:
            self.results.put(("error", error))

    def error(self):
        print(f"Recovering from error: {self.last_error}")

        self.input = None
        self.reply = None
        self.last_error = None
        self.input_thread = None
        self.reply_thread = None
        self.speech_thread = None
        self.audio = None

        self.transition_to(BMOState.IDLE)

if __name__ == "__main__":
    bmo = BMO()
    bmo.run()