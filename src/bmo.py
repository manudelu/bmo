import pygame

pygame.init()

# Freenove 5-inch resolution
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

faces = {
    "annoyed": pygame.image.load('faces/annoyed.png').convert(),
    "content": pygame.image.load('faces/content.png').convert(),
    "angry": pygame.image.load('faces/angry.png').convert(),
    "surprised": pygame.image.load('faces/surprised.png').convert(),
    "surprised_dot": pygame.image.load('faces/surprised_dot.png').convert(),
    "shocked": pygame.image.load('faces/shocked.png').convert(),
    "worried": pygame.image.load('faces/worried.png').convert(),
    "neutral": pygame.image.load('faces/neutral.png').convert(),
    "skeptical": pygame.image.load('faces/skeptical.png').convert(),
    "happy": pygame.image.load('faces/happy.png').convert(),
    "bored": pygame.image.load('faces/bored.png').convert(),
    "sad": pygame.image.load('faces/sad.png').convert(),
    "afk": pygame.image.load('faces/afk.png').convert(),
    "uwu": pygame.image.load('faces/uwu.png').convert(),
}
current_face = "uwu"

clock = pygame.optim = pygame.time.Clock()

running = True
while running:
    screen.blit(faces[current_face])
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
