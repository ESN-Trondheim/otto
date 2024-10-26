from enum import Enum

from PIL.ImageColor import getcolor


class EsnColor(Enum):
    CYAN = "#00AEEF"
    MAGENTA = "#EC008C"
    GREEN = "#7AC143"
    ORANGE = "#F47B20"
    DARK_BLUE = "#2E3192"

    def rgb(self):
        return getcolor(self.value, "RGB")


class SlackMessageEvent:
    type: str
    channel: str
    user: str
    text: str
    ts: str
    event_ts: str
    channel_type: str
