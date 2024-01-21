import pygame
import pygame_gui

from pygame_gui.core import ObjectID, UIContainer
from pygame_gui.elements import UIButton, UIHorizontalSlider, UILabel

class DetailParameter(UIContainer):
    def __init__(
        self,
        relative_rect,
        manager,
        *,
        starting_height: int = 1,
        is_window_root_container=False,
        container=None,
        parent_element=None,
        object_id=None,
        anchors=None,
        visible=1,
        name="",
        text=""
    ):
        super().__init__(
            relative_rect,
            manager,
            starting_height=starting_height,
            is_window_root_container=is_window_root_container,
            container=container,
            parent_element=parent_element,
            object_id=object_id,
            anchors=anchors,
            visible=visible,
        )

        self.name = name
        self.value = text

        self.ui_label = UILabel(
            pygame.Rect(0, 0, self.rect.w / 4, self.rect.h),
            manager=manager,
            container=self,
            text=self.name,
        )

        self.ui_value = UILabel(
            pygame.Rect(-self.rect.w / 4, 0, self.rect.w / 8, self.rect.h),
            manager=manager,
            container=self,
            text=self.value,
            anchors={"right": "right"},
        )

    def set_name(self, name: str):
        self.ui_label.set_text(name)
        self.name = name

    def set_value(self, value: str):
        self.value = value
        self.ui_value.set_text(value)


class RangedParameter(UIContainer):
    def __init__(
        self,
        relative_rect,
        manager,
        range_values,
        *,
        starting_height: int = 1,
        is_window_root_container=False,
        container=None,
        parent_element=None,
        object_id=None,
        anchors=None,
        visible=1,
        name="",
        default_value=None,
        integer_values=False,
        add_checkbox=False,
        checkbox_state=False
    ):
        super().__init__(
            relative_rect,
            manager,
            starting_height=starting_height,
            is_window_root_container=is_window_root_container,
            container=container,
            parent_element=parent_element,
            object_id=object_id,
            anchors=anchors,
            visible=visible,
        )

        self.name = name
        self.value = "-1"
        self.integer_values = integer_values
        self.add_checkbox = add_checkbox
        self.enabled = checkbox_state

        self.ui_label = UILabel(
            pygame.Rect(0, 0, self.rect.w / 4, self.rect.h),
            manager=manager,
            container=self,
            text=self.name,
        )

        self.ui_value = UILabel(
            pygame.Rect(-self.rect.w / 4, 0, self.rect.w / 8, self.rect.h),
            manager=manager,
            container=self,
            text=self.value,
            anchors={"right": "right"},
        )

        if not range_values or len(range_values) == 1 or len(range_values) > 2:
            raise ValueError(
                "range value type was chosen, but range_value has incorrect number of values"
            )

        self.range = range_values
        self.range_value = (
            default_value if default_value else (self.range[0] + self.range[1]) / 2
        )
        self.ui_value.set_text(str(self.range_value))

        self.ui_range = UIHorizontalSlider(
            pygame.Rect(self.rect.w / 4, 0, self.rect.w / 2, self.rect.h),
            manager=manager,
            container=self,
            value_range=self.range,
            start_value=self.range_value,
        )

        if add_checkbox:
            self.ui_checkbox = UIButton(
                pygame.Rect(-self.rect.w / 8, 0, self.rect.w / 8, self.rect.h),
                manager=manager,
                container=self,
                text="X" if checkbox_state else " ",
                anchors={"right": "right"},
                object_id=ObjectID("@checkbox"),
            )

    def process_event(self, event: pygame.Event) -> bool:
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.ui_range:
                val = (
                    int(self.ui_range.get_current_value())
                    if self.integer_values
                    else round(self.ui_range.get_current_value(), 2)
                )
                self.range_value = val
                self.set_value(str(val))

        elif self.add_checkbox and event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.ui_checkbox:
                self.enabled = not self.enabled
                self.ui_checkbox.set_text(" " if not self.enabled else "X")

        return super().process_event(event)

    def set_name(self, name: str):
        self.ui_label.set_text(name)
        self.name = name

    def set_value(self, value: str):
        self.value = value
        self.ui_value.set_text(value)

class CheckboxParameter(UIContainer):
    def __init__(
        self,
        relative_rect,
        manager,
        *,
        starting_height: int = 1,
        is_window_root_container=False,
        container=None,
        parent_element=None,
        object_id=None,
        anchors=None,
        visible=1,
        name="",
        state=False
    ):
        super().__init__(
            relative_rect,
            manager,
            starting_height=starting_height,
            is_window_root_container=is_window_root_container,
            container=container,
            parent_element=parent_element,
            object_id=object_id,
            anchors=anchors,
            visible=visible,
        )

        self.name = name
        self.enabled = state

        self.ui_label = UILabel(
            pygame.Rect(0, 0, self.rect.w / 4, self.rect.h),
            manager=manager,
            container=self,
            text=self.name,
        )
        
        self.ui_checkbox = UIButton(
                pygame.Rect(-self.rect.w / 8, 0, self.rect.w / 8, self.rect.h),
                manager=manager,
                container=self,
                text="X" if state else " ",
                anchors={"right": "right"},
                object_id=ObjectID("@checkbox"),
            )

    def process_event(self, event: pygame.Event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.ui_checkbox:
                self.enabled = not self.enabled
                self.ui_checkbox.set_text(" " if not self.enabled else "X")

        return super().process_event(event)