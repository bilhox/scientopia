import pygame
import scene
import gif_pygame
import pathfinding

from tilemap import Tilemap,Layer
from player import Player
from camera import Camera
from generation import *



class Game(scene.Scene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)

        self.camera = Camera(pygame.Vector2(pygame.display.get_window_size()))
        self.game_map = Tilemap()
        self.player = Player()

        self.draw_map = True

    def start(self):
        self.game_map.player = self.player
        self.game_map.layers["foreground"].value_based_tiles.append(1)
        self.game_map.layers["foreground"].generation_type = "PATTERN MATCHING"
        self.game_map.layers["foreground"].obstacle_tiles.append(5)

        self.game_map.load_tileset("./assets/tilesets/tileset_1.tsj")

        self.game_map.generate(seed=1)

        self.game_map.layers["flowers"] = Layer()
        self.game_map.layers["flowers"].generation_type = "RANDOM"
        self.game_map.layers["flowers"].generator_function = generate2


        # Working on
        self.player_dest_surface = pygame.image.load("./assets/target_cell.png").convert_alpha()
        self.player_dest_arrow = gif_pygame.load("./assets/target_arrow.gif")
        gif_pygame.transform.convert_alpha(self.player_dest_arrow)
        self.player_dest = pygame.Vector2(0, 0)

        self.path_block = pygame.Surface([16, 16], pygame.SRCALPHA)
        self.path_block.fill((0, 0, 200, 64))
        # pygame.mouse.set_visible(False)

    def events(self, event: pygame.Event):

        if event.type == pygame.MOUSEBUTTONDOWN and self.player.reached_destination:
            mouse_pos = pygame.Vector2(event.pos)
            # 2 c'est le coefficient de zoom de la caméra, 16 la taille des tuiles
            mouse_pos /= 2
            mouse_pos += pygame.Vector2(self.camera.rect.topleft)
            mouse_pos //= 16
            self.player_dest = mouse_pos
            self.player.path = pathfinding.find_way(tuple(self.player.cell_position), tuple(mouse_pos), self.game_map.get_obstacles())
            self.player.distance_remaining = self.player.path.distance
            self.player.reached_destination = False

    def update(self, clock: pygame.Clock):
        dt = clock.tick() / 1000
        # draw part

        self.camera.clear()

        self.player.update(dt)

        self.camera.rect.x += (
            (self.player.hitbox.centerx - self.camera.rect.centerx) * 3 * dt
        )
        self.camera.rect.y += (
            (self.player.hitbox.centery - self.camera.rect.centery) * 3 * dt
        )

        self.game_map.draw(self.camera)
        if not self.player.reached_destination:
            self.camera.draw([(self.player_dest_surface, self.player_dest * 16 - pygame.Vector2(self.camera.rect.topleft))])
            self.camera.draw([(self.player_dest_arrow.blit_ready(), self.player_dest * 16 - pygame.Vector2(self.camera.rect.topleft) - pygame.Vector2(0, 8))])
        self.player.draw(self.camera)

        self.camera.display_on_screen(self.screen)

        pygame.display.set_caption(f"FPS : {round(clock.get_fps(), 2)}")
