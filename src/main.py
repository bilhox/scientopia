import pygame
from tilemap import Tilemap
from player import Player
from camera import Camera

def main():

    pygame.init()

    desktop_size = pygame.Vector2(pygame.display.get_desktop_sizes()[0])
    print(desktop_size)
    screen_size = desktop_size * 2 / 3
    screen = pygame.display.set_mode([screen_size.x, screen_size.y], flags=pygame.RESIZABLE|pygame.SCALED, vsync=1)
    camera = Camera(screen_size)

    game_map = Tilemap()
    game_map.load_tileset("./assets/maps/tilesets/tileset_0.tsj")
    game_map.generate(pygame.Vector2(100, 100))

    player = Player()
    player.hitbox.topleft = pygame.Vector2(128, 128)

    clock = pygame.Clock()

    running = True

    while running:

        dt = clock.tick() / 1000

        # draw part

        camera.clear()

        player.update(dt)
        player.collisions([])

        camera.rect.x += (player.hitbox.centerx - camera.rect.centerx) * 3 * dt
        camera.rect.y += (player.hitbox.centery - camera.rect.centery) * 3 * dt

        camera.rect.x = pygame.math.clamp(camera.rect.x, 0, game_map.size.x - camera.rect.width)
        camera.rect.y = pygame.math.clamp(camera.rect.y, 0, game_map.size.y - camera.rect.height)

        game_map.draw(camera)
        player.draw(camera)

        camera.display_on_screen(screen)

        pygame.display.flip()
        pygame.display.set_caption(f"FPS : {round(clock.get_fps(), 2)}")

        # event part

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                running = False
                break
            
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

if __name__ == "__main__":
    main()