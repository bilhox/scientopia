import pygame
import os
import perlin_numpy
import numpy

from tilemap import Tilemap
from player import Player
from camera import Camera

def main():

    pygame.init()

    # Screen related infos
    desktop_size = pygame.Vector2(pygame.display.get_desktop_sizes()[0])
    screen_size = desktop_size * 2 / 3
    screen = pygame.display.set_mode([screen_size.x, screen_size.y], flags=pygame.RESIZABLE + pygame.SCALED, vsync=1)
    camera = Camera(screen_size)

    # Game map
    game_map = Tilemap()
    game_map.load("./assets/tilemap/map_0.tmj")

    # Player definition
    player = Player()
    player.hitbox.topleft = pygame.Vector2(128, 128)

    numpy.random.seed(0)
    noise_values = perlin_numpy.generate_perlin_noise_2d([int(camera.rect.w), int(camera.rect.h)], (4, 4))

    surf_filter = pygame.Surface([int(camera.rect.w), int(camera.rect.h)], pygame.SRCALPHA)
    pixels = pygame.surfarray.pixels3d(surf_filter)

    for j in range(int(camera.rect.h)):
        for i in range(int(camera.rect.w)):
            pix_color = [255 * (noise_values[i, j] + 0.5)] * 3
            pixels[i, j] = pix_color
    
    del pixels

    # Working on
    # player_dest_surface = pygame.Surface([16, 16], pygame.SRCALPHA)
    # pygame.draw.circle(player_dest_surface, [255, 255, 255, 128], [8, 8], 4)

    # player_dest = pygame.Vector2(0, 0)

    pygame.mouse.set_visible(False)

    clock = pygame.Clock()

    running = True

    while running:

        dt = clock.tick() / 1000
        # draw part

        camera.clear()

        player.update(dt)
        player.collisions(game_map.object_layers["colliders"])

        camera.rect.x += (player.hitbox.centerx - camera.rect.centerx) * 3 * dt
        camera.rect.y += (player.hitbox.centery - camera.rect.centery) * 3 * dt

        camera.rect.x = pygame.math.clamp(camera.rect.x, 0, game_map.size.x - camera.rect.width)
        camera.rect.y = pygame.math.clamp(camera.rect.y, 0, game_map.size.y - camera.rect.height)

        game_map.draw(camera)
        # camera.draw([(player_dest_surface, player_dest * 16 - pygame.Vector2(camera.rect.topleft))])
        player.draw(camera)

        camera.draw([(surf_filter, pygame.Vector2(0, 0))])

        camera.display_on_screen(screen)

        pygame.display.flip()
        pygame.display.set_caption(f"FPS : {round(clock.get_fps(), 2)}")

        # event part

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_RIGHT:
                    player.keys["right"] = True
                elif event.key == pygame.K_LEFT:
                    player.keys["left"] = True
                elif event.key == pygame.K_UP:
                    player.keys["up"] = True
                elif event.key == pygame.K_DOWN:
                    player.keys["down"] = True
            
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    player.keys["right"] = False
                elif event.key == pygame.K_LEFT:
                    player.keys["left"] = False
                elif event.key == pygame.K_UP:
                    player.keys["up"] = False
                elif event.key == pygame.K_DOWN:
                    player.keys["down"] = False
            
            # elif event.type == pygame.MOUSEBUTTONDOWN:
            #     mouse_pos = pygame.Vector2(event.pos)
            #     # 2 c'est le coefficient de zoom de la caméra, 16 la taille des tuiles
            #     mouse_pos /= 2
            #     mouse_pos += pygame.Vector2(camera.rect.topleft)
            #     mouse_pos //= 16
            #     player_dest = mouse_pos


if __name__ == "__main__":
    main()