#!/usr/bin/env python3
import pygame
import os

pygame.init()

# Freenove 5-inch resolution
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME | pygame.FULLSCREEN)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load_face(filename):
    path = os.path.join(BASE_DIR, "faces", filename)
    img = pygame.image.load(path).convert()
    return pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))

faces = {
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
current_face = "uwu"

clock = pygame.optim = pygame.time.Clock()

running = True
while running:
    screen.blit(faces[current_face], (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_1:
                current_face = "happy"
            elif event.key == pygame.K_2:
                current_face = "annoyed"
            elif event.key == pygame.K_3:
                current_face = "angry"
            elif event.key == pygame.K_4:
                current_face = "surprised"
            elif event.key == pygame.K_5:
                current_face = "shocked"

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
