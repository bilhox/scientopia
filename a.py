import pygame

screen = pygame.display.set_mode([600, 400], vsync=1)

running = True
clock = pygame.Clock() # pygame.Clock est une alias de pygame.time.Clock dans pygame-ce

while running:

    # clock.tick retourne une valeur en milliseconde, il faut la convertir en seconde en divisant par 1000
    dt = clock.tick() / 1000 # temps écoulé entre 2 frames

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()