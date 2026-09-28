#!/usr/bin/env python3
from enum import Enum, auto
from queue import Empty, Queue
from threading import Thread
import pygame

from agent import OllamaAgent
from display import Display

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

        self.results = Queue()
        self.input_thread = None
        self.reply_thread = None
        self.speak_until = None

    def transition_to(self, new_state):
        self.state = new_state

        state_faces = {
            BMOState.IDLE: "idle",
            BMOState.LISTEN: "curious",
            BMOState.THINK: "happy",
            BMOState.SPEAK: "surprised",
            BMOState.ERROR: "sad",
        }

        if new_state in state_faces:
            self.display.show(state_faces[new_state])

    def run(self):
        try:
            while self.running:
                try:
                    if not self.display.update():
                        self.transition_to(BMOState.STOPPED)
                        self.running = False
                    else:
                        self.process_results()
                        self.run_current_state()

                except KeyboardInterrupt:
                    self.transition_to(BMOState.STOPPED)

                except Exception as error:
                    self.last_error = error
                    print(f"BMO error {error}")
                    self.transition_to(BMOState.ERROR)
        finally:
            self.display.close()

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
        elif kind == "reply":
            self.reply_thread = None
            self.reply = value
            self.transition_to(BMOState.SPEAK)
        elif kind == "eof":
            self.transition_to(BMOState.STOPPED)
        elif kind == "error":
            self.last_error = value
            self.transition_to(BMOState.ERROR)

    def run_current_state(self):
        if self.state == BMOState.START:
            self.start()
        elif self.state == BMOState.IDLE:
            # TODO: Momentarily used for testing, later will be replace by button press or voice activation
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.transition_to(BMOState.LISTEN)
                        self.wait_for_user()
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
        print(f"Loading {self.agent.model}...")
        self.transition_to(BMOState.IDLE)

    def read_input(self):
        try:
            self.results.put(("input", input("You: ")))
        except EOFError:
            self.results.put(("eof", None))
        except Exception as error:
            self.results.put(("error", error))

    def wait_for_user(self):
        if self.input_thread is None:
            self.input_thread = Thread(target=self.read_input, daemon=True)
            self.input_thread.start()

    def listen(self):
        pass

    def get_reply(self):
        try:
            self.results.put(("reply", self.agent.reply(input=self.input)))
        except Exception as error:
            self.results.put(("error", error))

    def think(self):
        if self.reply_thread is None:
            self.reply_thread = Thread(target=self.get_reply, daemon=True)
            self.reply_thread.start()

    def speak(self):
        if self.speak_until is None:
            print(f"BMO: {self.reply}")
            self.speak_until = pygame.time.get_ticks() + 5000
        elif pygame.time.get_ticks() >= self.speak_until:
            self.speak_until = None
            self.transition_to(BMOState.IDLE)

    def error(self):
        print(f"Recovering from error: {self.last_error}")

        self.input = None
        self.reply = None
        self.last_error = None
        self.input_thread = None
        self.reply_thread = None
        self.speak_until = None

        self.transition_to(BMOState.IDLE)

if __name__ == "__main__":
    bmo = BMO()
    bmo.run()