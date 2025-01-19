from enum import Enum
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from otto.utils.esn import EsnColor


class CoverImageFont(Enum):
    TITLE = ImageFont.truetype(
        str(Path.cwd().joinpath("assets", "fonts", "kelson-sans-bold.otf")), 90
    )
    SUBTITLE = ImageFont.truetype(
        str(Path.cwd().joinpath("assets", "fonts", "kelson-sans-bold.otf")), 50
    )


class CoverImageFormat(Enum):
    ESN_ACTIVITIES = (
        "Activities",
        (1920, 460),
        (19, -6, 116, 178),
        Image.open(
            Path.cwd().joinpath("assets", "overlays", "coverimage-activities.png")
        ),
    )
    FACEBOOK = (
        "Facebook",
        (1568, 588),
        (19, -6, 90, 152),
        Image.open(
            Path.cwd().joinpath("assets", "overlays", "coverimage-facebook.png")
        ),
    )

    def __new__(
        cls, value: str, size: tuple[int], offset: tuple[int], overlay: Image.Image
    ):
        """This override allows multi-value enum objects"""
        obj = object.__new__(cls)

        obj._value_ = value
        obj.size = size
        obj.overlay = overlay
        obj.offset = offset

        return obj

    @property
    def target_width(self) -> tuple:
        return self.size[0]

    @property
    def target_height(self) -> tuple:
        return self.size[1]

    @property
    def solotitle_offset(self) -> int:
        return self.offset[0]

    @property
    def title_offset(self) -> int:
        return self.offset[1]

    @property
    def subtitle_offset(self) -> int:
        return self.offset[2]

    @property
    def subsubtitle_offset(self) -> int:
        return self.offset[3]

    @staticmethod
    def from_value(value: str):
        for f in CoverImageFormat:
            if f.value == value:
                return f


default_subtitle = None
default_subsubtitle = None
default_color = EsnColor.DARK_BLUE
default_format = CoverImageFormat.ESN_ACTIVITIES
default_background = Image.open(
    Path.cwd().joinpath("assets", "backgrounds", "coverimage-default.png")
)


def create_cover_image(
    title: str,
    subtitle: str = default_subtitle,
    subsubtitle: str = default_subsubtitle,
    color: EsnColor = default_color,
    format: CoverImageFormat = default_format,
    background: Image.Image = default_background,
):
    cover = background.convert(mode="RGB")
    cover = resize_and_crop_to_dimension(
        cover, format.target_width, format.target_height
    )
    cover = add_color_layer(cover, color)
    cover = add_overlay_layer(cover, format.overlay)

    cover = add_text_layer(
        cover,
        format.solotitle_offset,
        format.title_offset,
        format.subtitle_offset,
        format.subsubtitle_offset,
        title,
        subtitle,
        subsubtitle,
    )

    return cover


def resize_and_crop_to_dimension(
    image: Image.Image, target_width: int, target_height: int
):
    if image.height == target_height and image.width == target_width:
        return image

    background_aspect_ratio = image.width / image.height
    target_aspect_ratio = target_width / target_height

    # If background height is too big
    if background_aspect_ratio <= target_aspect_ratio:
        # Resize the image so the height reaches the target width (while maintaining original aspect ratio)
        resize_ratio = image.width / target_width
        new_height = int(image.height / resize_ratio)
        image = image.resize((target_width, new_height), Image.Resampling.LANCZOS)

        # Crop away the excessive height if neccessary
        if image.height > target_height:
            padding = (image.height - target_height) / 2
            coords = (0, padding, target_width, image.height - padding)
            image = image.crop(coords)
    else:  # If background width is too big
        # Resize the image so the height reaches the target height (while maintaining original aspect ratio)
        resize_ratio = image.height / target_height
        new_width = int(image.width / resize_ratio)
        image = image.resize((new_width, target_height), Image.Resampling.LANCZOS)

        # Crop away the excessive width if neccessary
        if image.width > target_width:
            padding = (image.width - target_width) / 2
            coords = (padding, 0, image.width - padding, target_height)
            image = image.crop(coords)

    return image


def add_color_layer(image: Image.Image, color: EsnColor):
    color_layer = Image.new(image.mode, image.size, color.rgb())
    return Image.blend(image, color_layer, 0.60)


def add_overlay_layer(image: Image.Image, overlay: Image.Image):
    image.paste(overlay, (0, 0), overlay)
    return image


def add_text_layer(
    image: Image.Image,
    solo_title_offset: int,
    title_offset: int,
    subtitle_offset: int,
    subsubtitle_offset: int,
    title: str,
    subtitle: str,
    subsubtitle: str,
):
    if subtitle or subsubtitle:
        image = add_text(image, CoverImageFont.TITLE, title_offset, title)
        if subtitle:
            image = add_text(image, CoverImageFont.SUBTITLE, subtitle_offset, subtitle)
        if subsubtitle:
            image = add_text(
                image,
                CoverImageFont.SUBTITLE,
                subsubtitle_offset,
                subsubtitle,
            )
    else:
        image = add_text(image, CoverImageFont.TITLE, solo_title_offset, title)

    return image


def add_text(image: Image.Image, font: CoverImageFont, text_offset: int, text: str):
    draw = ImageDraw.Draw(image)

    left, top, right, bottom = draw.textbbox((0, 0), text=text, font=font.value)
    width = right - left
    height = bottom - top
    draw.text(
        ((image.size[0] - width) / 2, (image.size[1] - height) / 2 + text_offset),
        text,
        font=font.value,
    )

    return image
