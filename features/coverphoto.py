from enum import Enum
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageColor


class EsnColor(Enum):
    CYAN = "#00AEEF"
    MAGENTA = "#EC008C"
    GREEN = "#7AC143"
    ORANGE = "#F47B20"
    DARK_BLUE = "#2E3192"

    @classmethod
    def rgb(self):
        return ImageColor.getcolor(self.value, "RGB")
    

class ImageDimension(Enum):
    ESN_ACTIVITIES = (1920, 460)
    FACEBOOK = (1568, 588)

    @classmethod
    def size(self) -> tuple[int]:
        return self.value

    @classmethod
    def height(self) -> int:
        return self.value[0]

    @classmethod
    def width(self) -> int:
        return self.value[1]
    

class ImageOverlay(Enum):
    ESN_ACTIVITIES = Image.open(Path.cwd().joinpath("assets/esn-trondheim-color.png"))
    FACEBOOK = Image.open(Path.cwd().joinpath("assets/esn-trondheim-black.png"))


class ImageTextFont(Enum):
    TITLE = ImageFont.truetype(str(Path.cwd().joinpath("assets", "fonts", "kelson-sans-bold.otf")), 90)
    SUBTITLE = ImageFont.truetype(str(Path.cwd().joinpath("assets", "kelson-sans-bold.otf")), 50)


class ImageTextOffsets(Enum):
    ACTIVITIES = {
        "solotitle": 19,
        "title": -6,
        "subtitle": 116,
        "subsubtitle": 178,
    }
    FACEBOOK = {
        "solotitle": 19,
        "title": -6,
        "subtitle": 90,
        "subsubtitle": 152,
    }


def create_cover_image(
    dimension: ImageDimension,
    background: Image.Image,
    color: EsnColor,
    overlay: ImageOverlay,
    title: str,
    subtitle: str,
    subsubtitle: str,
):
    cover = background.convert(mode="RGB")
    cover = resize_and_crop_to_dimension(cover, dimension)
    cover = add_color_layer(cover, color)
    cover = add_overlay_layer(cover, overlay)

    if subtitle or subsubtitle:
        add_text_layer(cover, title, FONTS["title"], V_OFFFSETS[logos]["title"])
        add_text_layer(cover, subtitle, FONTS["subtitle"], V_OFFFSETS[logos]["subtitle"])
        add_text_layer(cover, subsubtitle, FONTS["subtitle"], V_OFFFSETS[logos]["subtitle2"])
    else:
        add_text_layer(cover, title, FONTS["title"], V_OFFFSETS[logos]["titleonly"])

    return cover


def resize_and_crop_to_dimension(image: Image.Image, target_dimension: ImageDimension):
    if image.size == target_dimension.size():
        return image

    background_aspect_ratio = image.width / image.height
    target_aspect_ratio = target_dimension.width() / target_dimension.height()

    # If background height is too big
    if background_aspect_ratio <= target_aspect_ratio:
        # Resize the image so the height reaches the target width (while maintaining original aspect ratio)
        resize_ratio = image.width / target_dimension.width()
        new_height = int(image.height / resize_ratio)
        image = image.resize(
            (target_dimension.width(), new_height), Image.Resampling.LANCZOS
        )

        # Crop away the excessive height if neccessary
        if image.height > target_dimension.height():
            padding = (image.height - target_dimension.height()) / 2
            coords = (0, padding, target_dimension.width(), image.height - padding)
            image = image.crop(coords)
    else:  # If background width is too big
        # Resize the image so the height reaches the target height (while maintaining original aspect ratio)
        resize_ratio = image.height / target_dimension.height()
        new_width = int(image.width / resize_ratio)
        image = image.resize(
            (new_width, target_dimension.height()), Image.Resampling.LANCZOS
        )

        # Crop away the excessive width if neccessary
        if image.width > target_dimension.width():
            padding = (image.width - target_dimension.width()) / 2
            coords = (padding, 0, image.width - padding, target_dimension.height())
            image = image.crop(coords)

    return image

def add_color_layer(image: Image.Image, color: EsnColor):
    color_layer = Image.new(image.mode, image.size, color.rgb())

    return Image.blend(image, color_layer, 0.60)

def add_overlay_layer(image: Image.Image, overlay: ImageOverlay):
    image.paste(overlay.value, (0, 0), overlay)
    return image

def add_text_layer(image: Image.Image, offsets: ImageTextOffsets, title: str, subtitle: str, subsubtitle: str):
    if subtitle or subsubtitle:
        image = add_title(image, title)
        image = add_subtitle(image, subtitle)
        image = add_subsubtitle(image, subsubtitle)
    else:
        image = add_solo_title(image, title)

def add_solo_title(image: Image.Image, offsets: ImageTextOffsets, text: str):
    draw = ImageDraw.Draw(image)
    left, top, right, bottom = draw.textbbox((0, 0), text=text, font=ImageTextFont.TITLE.value)
    width = right - left
    height = bottom - top
    draw.text(
        ((image.width - width) / 2, (image.width - height) / 2 + offsets.value["title"]),
        text,
        font=ImageTextFont.TITLE.value,
    )