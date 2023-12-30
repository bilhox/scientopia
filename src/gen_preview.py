import pygame
import pygame_gui
import perlin_noise
import time
import numpy

class Parameter(pygame_gui.core.UIContainer):

    def __init__(self, relative_rect, manager, p_type, *, starting_height: int = 1, is_window_root_container = False, container = None, parent_element = None, object_id = None, anchors = None, visible = 1, name = "", range_values = [], default_value = None, integer_values = False):
        super().__init__(relative_rect, manager, starting_height=starting_height, is_window_root_container=is_window_root_container, container=container, parent_element=parent_element, object_id=object_id, anchors=anchors, visible=visible)

        self.type = p_type
        self.name = name
        self.value = "-1"
        self.integer_values = integer_values

        self.ui_label = pygame_gui.elements.UILabel(pygame.Rect(0, 0, self.rect.w / 4, self.rect.h),
                                                    manager=manager,
                                                    container=self,
                                                    text=self.name)
        
        if self.type in ["detail", "ranged value"]:

            self.ui_value = pygame_gui.elements.UILabel(pygame.Rect(-self.rect.w / 4, 0, self.rect.w / 4, self.rect.h),
                                                        manager=manager,
                                                        container=self,
                                                        text=self.value,
                                                        anchors={"right":"right"})
            
            if self.type == "ranged value":

                if not range_values or len(range_values) == 1 or len(range_values) > 2:
                    raise ValueError("range value type was chosen, but range_value has incorrect number of values")
                
                self.range = range_values
                self.range_value = default_value if default_value else (self.range[0] + self.range[1]) / 2
                self.ui_value.set_text(str(self.range_value))

                self.ui_range = pygame_gui.elements.UIHorizontalSlider(pygame.Rect(self.rect.w / 4, 0, self.rect.w / 2, self.rect.h),
                                                                       manager=manager,
                                                                       container=self,
                                                                       value_range=self.range,
                                                                       start_value=self.range_value)
    
    def process_event(self, event: pygame.Event) -> bool:
        
        if self.type == "ranged value":
            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == self.ui_range:
                    val = int(self.ui_range.get_current_value()) if self.integer_values else round(self.ui_range.get_current_value(), 2)
                    self.set_value(str(val))
        
        return super().process_event(event)
    
    def set_name(self, name : str):
        self.ui_label.set_text(name)
        self.name = name

    def set_value(self, value : str):
        self.value = value
        self.ui_value.set_text(value)



noise = perlin_noise.PerlinNoise(2)

def generate_texture(size : int, octaves : int, offset : tuple[int, int]) -> pygame.Surface:

    t_a = time.time()
    noise.octaves = octaves
    surf = pygame.Surface([size, size])
    pixels = pygame.surfarray.pixels3d(surf)

    for j in range(size):
        for i in range(size):
            noise_value = noise([(offset[0] + i)/size, (offset[1] + j)/size])
            color = [int(pygame.math.clamp((noise_value + 0.5) * 255, 0, 255))]*3
            pixels[i, j] = color

    del pixels
    return surf, round(time.time() - t_a, 3)


pygame.init()

pygame.display.set_caption('Quick Start')
window_surface = pygame.display.set_mode((1000, 600), vsync=60)

manager = pygame_gui.UIManager((1000, 600))

Parameter(pygame.Rect(0, 100, 450, 30), manager=manager, p_type="ranged value", name="haya", range_values=[0, 100], integer_values=True)

is_running = True
clock = pygame.Clock()

settings = {
    "seed":{"type":"detail", "text":f"{noise.seed}"},
    "generation dur.":{"type":"detail", "text":""},
    "size":{"range":[16, 256], "default":256, "value":256, "type":"ranged value"},
    "octave":{"range":[1, 32], "default":2, "value":2, "type":"ranged value"},
    "offsetx":{"range":[-200, 200], "default":0, "value":0, "type":"ranged value"},
    "offsety":{"range":[-200, 200], "default":0, "value":0, "type":"ranged value"},
    "threshold":{"range":[0.0, 1.0], "default":0.5, "value":0, "type":"ranged value"}
}

ui_settings = {}

# settings
result, time_taken = generate_texture(
                          settings["size"]["value"], 
                          settings["octave"]["value"],
                          [settings["offsetx"]["value"], settings["offsety"]["value"]])

settings["generation dur."]["text"] = f"{time_taken}s"

menu = pygame_gui.elements.UIPanel(pygame.Rect(500, 0, 500, 600), manager=manager)

components = []
i = 0
for setting in settings:

    if settings[setting]["type"] == "ranged value":
        bar = pygame_gui.elements.UIHorizontalSlider(pygame.Rect(150, 10 + i * 32, 200, 30), 
                                                    start_value=settings[setting]["range"][0], 
                                                    value_range=settings[setting]["range"], 
                                                    manager=manager, 
                                                    container=menu
                                                    )
        
        bar.set_current_value(settings[setting]["default"])
        
        bar_value = pygame_gui.elements.UILabel(pygame.Rect(350, 10 + i * 32, 100, 30), 
                                                text=f"{settings[setting]['default']}", 
                                                manager=manager, 
                                                container=menu
                                                )
        
        
        value_name = pygame_gui.elements.UILabel(pygame.Rect(0, 10 + i * 32, 150, 30), 
                                                text=setting, 
                                                manager=manager, 
                                                container=menu
                                                )

        bar.linked = bar_value
        bar.parameter = setting

    elif settings[setting]["type"] == "detail":

        value_name = pygame_gui.elements.UILabel(pygame.Rect(0, 10 + i * 32, 150, 30), 
                                                text=setting, 
                                                manager=manager, 
                                                container=menu
                                                )

        value = pygame_gui.elements.UILabel(pygame.Rect(350, 10 + i * 32, 100, 30), 
                                                text=settings[setting]["text"], 
                                                manager=manager, 
                                                container=menu
                                                )
        
        settings[setting]["ui"] = value
    
    i+=1

generate_button = pygame_gui.elements.UIButton(pygame.Rect(20, 20, 200, 40),
                                               text="generate",
                                               manager=manager
                                               )

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
                result, time_taken = generate_texture(
                                          settings["size"]["value"], 
                                          settings["octave"]["value"],
                                          [settings["offsetx"]["value"], settings["offsety"]["value"]])
                
                settings["generation dur."]["ui"].set_text(f"{time_taken}s")
        
        manager.process_events(event)

    manager.update(dt)

    window_surface.fill("black")

    window_surface.blit(result, pygame.Vector2(250, 300) - pygame.Vector2(result.get_size())/2)

    manager.draw_ui(window_surface)

    pygame.display.flip()
