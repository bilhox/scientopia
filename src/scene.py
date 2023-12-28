import pygame

class Scene():

    def __init__(self, scene_manager):

        self.screen = pygame.display.get_surface()
        self.scene_manager : "SceneManager" = scene_manager

    def start(self):
        pass

    def events(self, event : pygame.Event):
        pass

    def update(self, clock : pygame.Clock):
        pass


class SceneManager():

    def __init__(self):
        self.scenes : dict[str, Scene] = {}
        self.current_scene : Scene = None
    
    def set_scene(self, name : str):
        self.current_scene = self.scenes[name]
        self.current_scene.start()

    def events(self, event : pygame.Event):
        if self.current_scene:
            self.current_scene.events(event)
    
    def update(self, clock : pygame.Clock):
        if self.current_scene:
            self.current_scene.update(clock)
