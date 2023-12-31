import pygame
import pygame_gui
import perlin_noise
import time

from perlin_numpy import (
    generate_fractal_noise_2d, generate_fractal_noise_3d,
    generate_perlin_noise_2d, generate_perlin_noise_3d
)

import perlin_numpy

from parameter import *


noise1 = perlin_noise.PerlinNoise(2)

def generate_texture(settings : dict) -> pygame.Surface:

    offset = settings["offsetx"].range_value, settings["offsety"].range_value
    size = settings["size"].range_value

    t_a = time.time()
    noise1.octaves = settings["octave"].range_value
    surf = pygame.Surface([size]*2)
    pixels = pygame.surfarray.pixels3d(surf)

    noise_values = generate_perlin_noise_2d([size, size], [settings["octave"].range_value]*2)

    for j in range(size):
        for i in range(size):
            noise_value = noise_values[i, j]
            pixels[i, j] = [pygame.math.clamp(noise_value * 510, 0, 255)] * 3

    del pixels

    settings["generation dur."].set_value(str(round(time.time() - t_a, 2)))

    return surf


pygame.init()

pygame.display.set_caption('Quick Start')
window_surface = pygame.display.set_mode((1200, 700), vsync=1)

manager = pygame_gui.UIManager((1200, 700))

# Parameter(pygame.Rect(0, 100, 450, 30), manager=manager, p_type="ranged value", name="haya", range_values=[0, 100], integer_values=True)

is_running = True
clock = pygame.Clock()

settings = {
    "seed":{"type":"detail", "text":f"{noise1.seed}"},
    "generation dur.":{"type":"detail", "text":""},
    "size":{"range":[16, 256], "default":256, "type":"ranged value"},
    "octave":{"range":[1, 32], "default":2, "type":"ranged value"},
    "offsetx":{"range":[-200, 200], "default":0, "type":"ranged value"},
    "offsety":{"range":[-200, 200], "default":0, "type":"ranged value"},
    "threshold":{"range":[0.0, 1.0], "default":0.5, "type":"ranged value"},
    "scale":{"range":[0.25, 2.0], "default":1, "type":"ranged value"}
}

ui_settings = {}

# ui
menu = pygame_gui.elements.UIPanel(pygame.Rect(600, 0, 600, 700), manager=manager)

i = 0
for setting in settings:

    if settings[setting]["type"] == "ranged value":

        ui_settings[setting] = RangedParameter(pygame.Rect(0, 10 + i * 32, 550, 30),
                                            manager=manager, 
                                            container=menu,
                                            name=setting,
                                            range_values=settings[setting]["range"],
                                            default_value=settings[setting]["default"])

    elif settings[setting]["type"] == "detail":

        ui_settings[setting] = DetailParameter(pygame.Rect(0, 10 + i * 32, 550, 30),
                                               manager=manager,
                                               container=menu,
                                               name=setting,
                                               text=settings[setting]["text"])
    
    i+=1

generate_button = pygame_gui.elements.UIButton(pygame.Rect(20, 20, 200, 40),
                                               text="generate",
                                               manager=manager
                                               )

result = generate_texture(ui_settings)

while is_running:

    dt = clock.tick() / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        
        # elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
        #     element : pygame_gui.elements.UIHorizontalSlider = event.ui_element
        #     element.linked.set_text(f"{event.value}")
        #     settings[element.parameter]["value"] = event.value
        
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == generate_button:
                result = generate_texture(ui_settings)
        
        manager.process_events(event)

    manager.update(dt)

    window_surface.fill("black")

    window_surface.blit(result, pygame.Vector2(300, 350) - pygame.Vector2(result.get_size())/2)

    manager.draw_ui(window_surface)

    pygame.display.flip()
