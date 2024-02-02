import pygame
import scene
import pygame_gui

from gui import *
# from pygame_gui.elements import UIButton, UILabel, UIPanel
# from pygame_gui.ui_manager import UIManager


class StartMenu(scene.Scene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.ui_manager = UIManager(pygame.display.get_window_size())

        self.game_title = UILabel(pygame.Rect(0, 100, -1, -1), self.ui_manager, "Scientopia")
        self.game_title.set_align(["centerx"])

        self.play_button = UIButton(pygame.Rect(0, 100, 200, 75), self.ui_manager, text="Play")
        self.play_button.set_align(["centerx", "centery"])

        # self.game_title = UILabel(
        #     relative_rect=pygame.Rect(0, 100, 400, 200),
        #     manager=self.ui_manager,
        #     text="Scientopia",
        #     anchors={"centerx": "centerx"},
        # )

        # self.play_button = UIButton(
        #     relative_rect=pygame.Rect(0, 400, 100, 75),
        #     manager=self.ui_manager,
        #     text="play",
        #     anchors={"centerx": "centerx"},
        # )

    def events(self, event: pygame.Event):
        if event.type == UI_BUTTONCLICKED:
            self.scene_manager.set_scene("game")

        self.ui_manager.handle_event(event)

    def update(self, clock: pygame.Clock):
        self.screen.fill("black")

        dt = clock.tick() / 1000

        self.ui_manager.update(dt)
        self.screen.blits(self.ui_manager.prepare_drawing())
