import pygame

if not pygame.get_init():
    pygame.init()

UI_DEFAULT_RESSOURCES = {
    "button_images":{
        "nothing":(100, 100, 100),
        "on_hover":(170, 170, 170),
        "on_click":(70, 70, 70)
    },
    "fonts":{
        "regular":pygame.Font('assets/fonts/FiraCode-Regular.ttf')
    },
    "colors":{
        "default":(20, 20, 20, 230),
        "default_border":(150, 150, 150),
        "scrollbar_bg":(120, 120, 120, 128)
    }
}

# def load_default_ressources() -> dict:
#     ressources = {}

#     for x_property_name, x_property_datas in UI_DEFAULT_RESSOURCES.items():
#         x_prop_datas = {}
#         for name, value in x_property_datas:
#             if(value.startswith("color")):
#                 color = eval(value.removeprefix("color"))
                


class UIManager():
    def __init__(self, size : list) -> None:

        self._size = size
        self.ressources = UI_DEFAULT_RESSOURCES
        self.ui_elements = []
    
    def handle_event(self, event : pygame.Event) -> None:
        for element in self.ui_elements:
            if not element.hidden:
                element.handle_event(event)
    
    def update(self, dt : float) -> None:
        for element in self.ui_elements:
            element.update(dt)
    
    def set_size(self, size : list) -> None:
        self._size = size
        for el in self.ui_elements:
            el._update_position()
    
    def prepare_drawing(self) -> list[pygame.Surface, tuple]:

        surfs = []

        for el in self.ui_elements:
            surf = el.prepare_drawing()
            if surf and not el.hidden:
                surfs.append((surf, el.get_position()))
        
        return surfs