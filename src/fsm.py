#!/usr/bin/env python3
from enum import Enum, auto
from time import sleep # temporary
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

    def transition_to(self, new_state):
        #print(f"Transitioning from {self.state.name} to {new_state.name}")
        self.state = new_state

        state_faces = {
            BMOState.IDLE: "happy",
            BMOState.LISTEN: "surprised_dot",
            BMOState.THINK: "skeptical",
            BMOState.SPEAK: "surprised",
            BMOState.ERROR: "worried",
        }

        if new_state in state_faces:
            self.display.show(state_faces[new_state])

    def run(self):
        while self.running:
            try:
                if not self.display.update():
                    self.transition_to(BMOState.STOPPED)

                self.run_current_state()

            except KeyboardInterrupt:
                self.transition_to(BMOState.STOPPED)    
            
            except Exception as error:
                self.last_error = error
                print(f"BMO error {error}")
                self.transition_to(BMOState.ERROR)
        
    def run_current_state(self):
        if self.state == BMOState.START:
            self.start()

        elif self.state == BMOState.IDLE:
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

    def wait_for_user(self):
        self.input = input("You: ").strip()

        if self.input.lower() in ["exit", "quit"]:
            self.transition_to(BMOState.STOPPED)
        elif self.input:
            self.transition_to(BMOState.THINK)

    def listen(self):
        pass

    def think(self):
        self.reply = self.agent.reply(input=self.input)
        self.transition_to(BMOState.SPEAK)

    def speak(self):
        print(f"BMO: {self.reply}")
        sleep(5)
        self.transition_to(BMOState.IDLE)

    def error(self):
        print(f"Recovering from error: {self.last_error}")

        self.input = None
        self.reply = None
        self.last_error = None

        self.transition_to(BMOState.IDLE)

if __name__ == "__main__":
    bmo = BMO()
    bmo.run()