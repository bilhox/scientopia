import pygame
import scene
import pygame_gui

from pygame_gui.elements import UIButton, UILabel, UIPanel
from pygame_gui.ui_manager import UIManager


class StartMenu(scene.Scene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.ui_manager = UIManager(pygame.display.get_window_size())

        self.game_title = UILabel(
            relative_rect=pygame.Rect(0, 100, 400, 200),
            manager=self.ui_manager,
            text="Scientopia",
            anchors={"centerx": "centerx"},
        )

        self.play_button = UIButton(
            relative_rect=pygame.Rect(0, 400, 100, 75),
            manager=self.ui_manager,
            text="play",
            anchors={"centerx": "centerx"},
        )

    def events(self, event: pygame.Event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self.scene_manager.set_scene("game")

        self.ui_manager.process_events(event)

    def update(self, clock: pygame.Clock):
        self.screen.fill("black")

        dt = clock.tick() / 1000

        self.ui_manager.update(dt)
        self.ui_manager.draw_ui(self.screen)
