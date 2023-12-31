import pygame
import pygame_gui


class DetailParameter(pygame_gui.core.UIContainer):
    def __init__(self, relative_rect, manager, *, starting_height: int = 1, is_window_root_container = False, container = None, parent_element = None, object_id = None, anchors = None, visible = 1, name = "", text = ""):
        super().__init__(relative_rect, manager, starting_height=starting_height, is_window_root_container=is_window_root_container, container=container, parent_element=parent_element, object_id=object_id, anchors=anchors, visible=visible)

        self.name = name
        self.value = text

        self.ui_label = pygame_gui.elements.UILabel(pygame.Rect(0, 0, self.rect.w / 4, self.rect.h),
                                                    manager=manager,
                                                    container=self,
                                                    text=self.name)


        self.ui_value = pygame_gui.elements.UILabel(pygame.Rect(-self.rect.w / 4, 0, self.rect.w / 4, self.rect.h),
                                                    manager=manager,
                                                    container=self,
                                                    text=self.value,
                                                    anchors={"right":"right"})
    
    def set_name(self, name : str):
        self.ui_label.set_text(name)
        self.name = name

    def set_value(self, value : str):
        self.value = value
        self.ui_value.set_text(value)

class RangedParameter(pygame_gui.core.UIContainer):

    def __init__(self, relative_rect, manager, range_values, *, starting_height: int = 1, is_window_root_container = False, container = None, parent_element = None, object_id = None, anchors = None, visible = 1, name = "", default_value = None, integer_values = False):
        super().__init__(relative_rect, manager, starting_height=starting_height, is_window_root_container=is_window_root_container, container=container, parent_element=parent_element, object_id=object_id, anchors=anchors, visible=visible)

        self.name = name
        self.value = "-1"
        self.integer_values = integer_values

        self.ui_label = pygame_gui.elements.UILabel(pygame.Rect(0, 0, self.rect.w / 4, self.rect.h),
                                                    manager=manager,
                                                    container=self,
                                                    text=self.name)


        self.ui_value = pygame_gui.elements.UILabel(pygame.Rect(-self.rect.w / 4, 0, self.rect.w / 4, self.rect.h),
                                                    manager=manager,
                                                    container=self,
                                                    text=self.value,
                                                    anchors={"right":"right"})


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

        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.ui_range:
                val = int(self.ui_range.get_current_value()) if self.integer_values else round(self.ui_range.get_current_value(), 2)
                self.range_value = val
                self.set_value(str(val))
        
        return super().process_event(event)
    
    def set_name(self, name : str):
        self.ui_label.set_text(name)
        self.name = name

    def set_value(self, value : str):
        self.value = value
        self.ui_value.set_text(value)

class CheckBoxParameter(pygame_gui.core.UIContainer):
    def __init__(self, relative_rect, manager, *, starting_height: int = 1, is_window_root_container = False, container = None, parent_element = None, object_id = None, anchors = None, visible = 1, name = ""):
        super().__init__(relative_rect, manager, starting_height=starting_height, is_window_root_container=is_window_root_container, container=container, parent_element=parent_element, object_id=object_id, anchors=anchors, visible=visible)

        self.name = name

        self.ui_label = pygame_gui.elements.UILabel(pygame.Rect(0, 0, self.rect.w / 4, self.rect.h),
                                                    manager=manager,
                                                    container=self,
                                                    text=self.name)


        self.ui_value = pygame_gui.elements.UI
    
    def set_name(self, name : str):
        self.ui_label.set_text(name)
        self.name = name

    def set_value(self, value : str):
        self.value = value
        self.ui_value.set_text(value)