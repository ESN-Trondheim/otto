from enum import Enum

from PIL.ImageColor import getcolor


class EsnColor(Enum):
    CYAN = ("Cyan", "#00AEEF")
    MAGENTA = ("Magenta", "#EC008C")
    GREEN =("Green", "#7AC143") 
    ORANGE = ("Orange", "#F47B20")
    DARK_BLUE = ("Dark Blue", "#2E3192")

    def display_name(self):
        return self.value[0]
    
    def hex(self):
        return self.value[1]

    def rgb(self):
        return getcolor(self.value[1], "RGB")
    
    @staticmethod
    def from_display_name(name: str):
        for c in EsnColor:
            if c.display_name() == name:
                return c