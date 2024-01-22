import pygame
import traceback

from scene import SceneManager
from game import Game
from start_menu import StartMenu

def main():

    pygame.init()

    # Screen related infos
    desktop_size = pygame.Vector2(pygame.display.get_desktop_sizes()[0])
    screen_size = desktop_size * 2 / 3
    pygame.display.set_mode([screen_size.x, screen_size.y], flags=pygame.RESIZABLE + pygame.SCALED, vsync=1)
    clock = pygame.Clock()

    scene_manager = SceneManager()
    scene_manager.scenes = {"game":Game(scene_manager), "start_menu":StartMenu(scene_manager)}

    scene_manager.set_scene("start_menu")

    running = True

    while running:
        try:
            scene_manager.update(clock)
        except Exception as e:
            running = False
            pygame.display.message_box("Error", traceback.format_exc(), "error")

        
        for event in pygame.event.get():
            scene_manager.events(event)

            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()

        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()