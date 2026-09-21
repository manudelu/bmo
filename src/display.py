#!/usr/bin/env python3
import pygame
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
faces_path = BASE_DIR / "faces"

class Display():
    def __init__(self, width: int = 800, height: int = 400):
        pygame.init()

        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            #pygame.NOFRAME | pygame.FULLSCREEN
        )
        self.clock = pygame.time.Clock()

        self.faces = self.load_faces()
        self.current_face = "happy"

    def load_face(self, filename: str) -> pygame.Surface:
        path = faces_path / filename
        img = pygame.image.load(path).convert()
        return pygame.transform.scale(img, (self.width, self.height))

    def load_faces(self) -> dict[str, pygame.Surface]:
        return {
            "annoyed": self.load_face('annoyed.png'),
            "content": self.load_face('content.png'),
            "angry": self.load_face('angry.png'),
            "surprised": self.load_face('surprised.png'),
            "surprised_dot": self.load_face('surprised_dot.png'),
            "shocked": self.load_face('shocked.png'),
            "worried": self.load_face('worried.png'),
            "neutral": self.load_face('neutral.png'),
            "skeptical": self.load_face('skeptical.png'),
            "happy": self.load_face('happy.png'),
            "bored": self.load_face('bored.png'),
            "sad": self.load_face('sad.png'),
            "afk": self.load_face('afk.png'),
            "uwu": self.load_face('uwu.png'),
        }

    def show(self, face_name: str) -> None:
        self.current_face = face_name

    def update(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return False
                
        face = self.faces.get(self.current_face)
        if face: 
            self.screen.blit(face, (0, 0))

        pygame.display.flip()
        self.clock.tick(30)
        return True

    def close(self):
        pygame.quit()