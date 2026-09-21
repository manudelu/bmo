#!/usr/bin/env python3
from enum import Enum, auto
import pygame
import os
from time import sleep
from agent import OllamaAgent

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 480

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load_face(filename):
    path = os.path.join(BASE_DIR, "faces", filename)
    img = pygame.image.load(path).convert()
    return pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))

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

        # Pygame
        self.screen = None
        self.clock = None
        self.faces = {}
        self.current_face = "happy"

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
            self.current_face = state_faces[new_state]

    def run(self):
        while self.running:
            try:
                if self.screen is not None:
                    self.handle_events()
                    self.draw()

                self.run_current_state()

                if self.clock is not None:
                    self.clock.tick(30)

            except KeyboardInterrupt:
                self.transition_to(BMOState.STOPPED)    
            
            except Exception as error:
                self.last_error = error
                print(f"BMO error {error}")
                self.transition_to(BMOState.ERROR)
        
        pygame.quit()

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
        pygame.init()

        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), 
           # pygame.NOFRAME | pygame.FULLSCREEN
        )
        self.clock = pygame.time.Clock()

        self.faces = {
            "annoyed": load_face('annoyed.png'),
            "content": load_face('content.png'),
            "angry": load_face('angry.png'),
            "surprised": load_face('surprised.png'),
            "surprised_dot": load_face('surprised_dot.png'),
            "shocked": load_face('shocked.png'),
            "worried": load_face('worried.png'),
            "neutral": load_face('neutral.png'),
            "skeptical": load_face('skeptical.png'),
            "happy": load_face('happy.png'),
            "bored": load_face('bored.png'),
            "sad": load_face('sad.png'),
            "afk": load_face('afk.png'),
            "uwu": load_face('uwu.png'),
        }
        self.current_face = "happy"
        self.draw()
        pygame.event.pump()

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

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.transition_to(BMOState.STOPPED)

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.transition_to(BMOState.STOPPED)

    def draw(self):
        face = self.faces.get(self.current_face)

        if face is not None:
            self.screen.blit(face, (0, 0))

        pygame.display.flip()

if __name__ == "__main__":
    bmo = BMO()
    bmo.run()