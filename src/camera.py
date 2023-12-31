import pygame

class Camera():

    def __init__(self, screen_size : pygame.Vector2):

        self.rect = pygame.FRect(0, 0, screen_size.x / 2, screen_size.y / 2)
        self.display_surface = pygame.Surface(self.rect.size)
        self.position = pygame.Vector2()
    
    def clear(self, color="black"):
        self.display_surface.fill(color)

    def draw(self, surfs : list[tuple[pygame.Surface, pygame.Vector2]], special_flag = 0):
        self.display_surface.fblits(surfs, special_flag)
    
    def display_on_screen(self, screen):
        screen.blit(pygame.transform.scale_by(self.display_surface, 2), self.position)