import pygame
import scene

from tilemap import Tilemap
from player import Player
from camera import Camera
from menu import Inventory
import gui

class Game(scene.Scene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)

        self.camera = Camera(pygame.Vector2(pygame.display.get_window_size()))
        self.game_map = Tilemap()
        self.player = Player()

        self.draw_map = True
        ui_manager_size = pygame.Vector2(self.camera.rect.size) * 2
        self.ui_manager = gui.UIManager(ui_manager_size)

        self.ui_inventory = Inventory(ui_manager_size, self.ui_manager)

    def start(self):

        self.game_map.player = self.player
        self.game_map.layers["foreground"].value_based_tiles.append(1)

        self.game_map.load_tileset("./assets/tilesets/tileset_1.tsj")

        self.game_map.layers["foreground"].add_threshold(0, 5)
        self.game_map.layers["foreground"].add_threshold(0.1, 1)
        self.game_map.layers["foreground"].add_threshold(0.25, 4)

        self.game_map.generate(seed=1)

        # Working on
        # player_dest_surface = pygame.Surface([16, 16], pygame.SRCALPHA)
        # pygame.draw.circle(player_dest_surface, [255, 255, 255, 128], [8, 8], 4)

        # player_dest = pygame.Vector2(0, 0)

        pygame.mouse.set_visible(False)

    def events(self, event: pygame.Event):
        if event.type == pygame.KEYDOWN:
            if self.ui_inventory.hidden:
                if event.key == pygame.K_RIGHT:
                    self.player.keys["right"] = True
                elif event.key == pygame.K_LEFT:
                    self.player.keys["left"] = True
                elif event.key == pygame.K_UP:
                    self.player.keys["up"] = True
                elif event.key == pygame.K_DOWN:
                    self.player.keys["down"] = True

        elif event.type == pygame.KEYUP:
            if self.ui_inventory.hidden:
                if event.key == pygame.K_RIGHT:
                    self.player.keys["right"] = False
                elif event.key == pygame.K_LEFT:
                    self.player.keys["left"] = False
                elif event.key == pygame.K_UP:
                    self.player.keys["up"] = False
                elif event.key == pygame.K_DOWN:
                    self.player.keys["down"] = False
            if event.key == pygame.K_m and not self.ui_inventory.current_animation:
                self.ui_inventory.set_hidden(not self.ui_inventory.hidden)
                self.player.keys = {"left":False, "right":False, "up":False, "down":False}
        elif event.type == gui.UI_ANIMATIONENDED:
            if event.ui_element == self.ui_inventory:
                pygame.mouse.set_visible(not self.ui_inventory.hidden)

        self.ui_manager.handle_event(event)

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

        self.camera.rect.x += (
            (self.player.hitbox.centerx - self.camera.rect.centerx) * 3 * dt
        )
        self.camera.rect.y += (
            (self.player.hitbox.centery - self.camera.rect.centery) * 3 * dt
        )

        self.ui_manager.update(dt)

        self.game_map.draw(self.camera)
        # camera.draw([(player_dest_surface, player_dest * 16 - pygame.Vector2(camera.rect.topleft))])
        self.player.draw(self.camera)
        self.camera.display_on_screen()
        self.camera.draw(self.ui_manager.prepare_drawing(), on_screen=True)
        pygame.display.set_caption(f"FPS : {round(clock.get_fps(), 2)}")
