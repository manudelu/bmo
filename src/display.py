#!/usr/bin/env python3
from pathlib import Path
import pygame

BASE_DIR = Path(__file__).resolve().parent.parent
faces_path = BASE_DIR / "faces"

class Display:
    def __init__(self, width: int = 800, height: int = 400):
        pygame.init()

        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            # pygame.NOFRAME | pygame.FULLSCREEN
        )
        self.clock = pygame.time.Clock()

        self.faces: dict[str, list[Path]] = {}
        for folder in faces_path.iterdir():
            if folder.is_dir():
                frames = sorted(folder.glob("*.png"))
                if frames:
                    self.faces[folder.name] = frames

        self.loaded_frames: dict[Path, pygame.Surface] = {}
        self.current_face = "idle"
        self.frame_index = 0
        self.last_frame_at = pygame.time.get_ticks()
        self.frame_ms = 150

    def load_face(self, path: Path) -> pygame.Surface:
        img = pygame.image.load(path).convert()
        return pygame.transform.scale(img, (self.width, self.height))

    def show(self, face_name: str) -> None:
        if face_name not in self.faces:
            raise ValueError(f"Unknown face: {face_name}")
        self.current_face = face_name
        self.frame_index = 0
        self.last_frame_at = pygame.time.get_ticks()

    def update(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return False

        frames = self.faces[self.current_face]
        now = pygame.time.get_ticks()
        if now - self.last_frame_at >= self.frame_ms:
            steps = (now - self.last_frame_at) // self.frame_ms
            self.frame_index = (self.frame_index + steps) % len(frames)
            self.last_frame_at += steps * self.frame_ms

        path = frames[self.frame_index]
        if path not in self.loaded_frames:
            self.loaded_frames[path] = self.load_face(path)
        self.screen.blit(self.loaded_frames[path], (0, 0))

        pygame.display.flip()
        self.clock.tick(30)
        return True

    def close(self):
        pygame.quit()