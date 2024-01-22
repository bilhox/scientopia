import pygame
import scene

from tilemap import Tilemap
from player import Player
from camera import Camera

class Game(scene.Scene):

    def __init__(self, scene_manager):
        super().__init__(scene_manager)

        self.camera = Camera(pygame.Vector2(pygame.display.get_window_size()))
        self.game_map = Tilemap()
        self.debug_map = Tilemap()
        self.player = Player()

        self.draw_map = True
        

    def start(self):
        
        self.game_map.layers["foreground"].value_based_tiles.append(1)
        self.game_map.layers["grass"].based_layer = self.game_map.layers["foreground"]
        self.game_map.layers["flowers"].based_layer = self.game_map.layers["foreground"]
        self.game_map.layers["grass"].threshold_on_layer = 0.3
        self.game_map.layers["flowers"].threshold_on_layer = 0.4
        
        self.game_map.load_tileset("./assets/tilesets/tileset_0.tsj")
        self.debug_map.load_tileset("./assets/tilesets/tileset_0.tsj")

        self.game_map.layers["foreground"].add_threshold(0, 2)
        self.game_map.layers["foreground"].add_threshold(0.2, 0)
        self.game_map.layers["grass"].add_threshold(0, 10)
        self.game_map.layers["grass"].add_threshold(0.5, 1)
        self.game_map.layers["flowers"].add_threshold(0, 10)
        self.game_map.layers["flowers"].add_threshold(0.7, 7)

        # self.debug_map.layers["foreground"].add_threshold(0, 2)
        # self.debug_map.layers["foreground"].add_threshold(0.2, 0)
        # self.debug_map.layers["foreground"].add_threshold(0.35, 1)

        self.game_map.generate(pygame.Vector2(62, 62), 1)
        # self.debug_map.generate(pygame.Vector2(124, 124), 1)

        self.player.hitbox.topleft = pygame.Vector2(64, 64)

        # Working on
        # player_dest_surface = pygame.Surface([16, 16], pygame.SRCALPHA)
        # pygame.draw.circle(player_dest_surface, [255, 255, 255, 128], [8, 8], 4)

        # player_dest = pygame.Vector2(0, 0)

        # pygame.mouse.set_visible(False)
    
    def events(self, event: pygame.Event):
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.player.keys["right"] = True
            elif event.key == pygame.K_LEFT:
                self.player.keys["left"] = True
            elif event.key == pygame.K_UP:
                self.player.keys["up"] = True
            elif event.key == pygame.K_DOWN:
                self.player.keys["down"] = True
        
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                self.player.keys["right"] = False
            elif event.key == pygame.K_LEFT:
                self.player.keys["left"] = False
            elif event.key == pygame.K_UP:
                self.player.keys["up"] = False
            elif event.key == pygame.K_DOWN:
                self.player.keys["down"] = False
            elif event.key == pygame.K_s:
                self.draw_map = not self.draw_map
        
        # elif event.type == pygame.MOUSEBUTTONDOWN:
        #     mouse_pos = pygame.Vector2(event.pos)
        #     # 2 c'est le coefficient de zoom de la caméra, 16 la taille des tuiles
        #     mouse_pos /= 2
        #     mouse_pos += pygame.Vector2(camera.rect.topleft)
        #     mouse_pos //= 16
        #     player_dest = mouse_pos

    def update(self, clock: pygame.Clock):
        
        dt = clock.tick() / 1000
        # draw part

        self.camera.clear()

        self.player.update(dt)
        self.player.collisions([])

        self.camera.rect.x += (self.player.hitbox.centerx - self.camera.rect.centerx) * 3 * dt
        self.camera.rect.y += (self.player.hitbox.centery - self.camera.rect.centery) * 3 * dt

        self.camera.rect.x = pygame.math.clamp(self.camera.rect.x, 0, self.game_map.size.x - self.camera.rect.width)
        self.camera.rect.y = pygame.math.clamp(self.camera.rect.y, 0, self.game_map.size.y - self.camera.rect.height)

        if self.draw_map:
            self.game_map.draw(self.camera)
        else:
            self.debug_map.draw(self.camera)
        # camera.draw([(player_dest_surface, player_dest * 16 - pygame.Vector2(camera.rect.topleft))])
        self.player.draw(self.camera)

        self.camera.display_on_screen(self.screen)

        pygame.display.set_caption(f"FPS : {round(clock.get_fps(), 2)}")