from enum import Enum
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from otto.utils import EsnColor


class CoverImageFormat(Enum):
    ESN_ACTIVITIES = "activites"
    FACEBOOK = "facebook"


class CoverImageDimension(Enum):
    ESN_ACTIVITIES = (1920, 460)
    FACEBOOK = (1568, 588)

    def size(self) -> tuple[int]:
        return self.value

    def width(self) -> int:
        return self.value[0]

    def height(self) -> int:
        return self.value[1]


class CoverImageOverlay(Enum):
    ESN_ACTIVITIES = Image.open(
        Path.cwd().joinpath("assets", "overlays", "coverimage-activities.png")
    )
    FACEBOOK = Image.open(
        Path.cwd().joinpath("assets", "overlays", "coverimage-facebook.png")
    )


class CoverImageTextOffsets(Enum):
    ESN_ACTIVITIES = (19, -6, 116, 178)
    FACEBOOK = (19, -6, 90, 152)

    def solotitle_offset(self) -> int:
        return self.value[0]

    def title_offset(self) -> int:
        return self.value[1]

    def subtitle_offset(self) -> int:
        return self.value[2]

    def subsubtitle_offset(self) -> int:
        return self.value[3]


class CoverImageTextFont(Enum):
    TITLE = ImageFont.truetype(
        str(Path.cwd().joinpath("assets", "fonts", "kelson-sans-bold.otf")), 90
    )
    SUBTITLE = ImageFont.truetype(
        str(Path.cwd().joinpath("assets", "fonts", "kelson-sans-bold.otf")), 50
    )


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

    dimension = CoverImageDimension[format.name]
    cover = resize_and_crop_to_dimension(cover, dimension)

    cover = add_color_layer(cover, color)

    overlay = CoverImageOverlay[format.name]
    cover = add_overlay_layer(cover, overlay)

    text_offsets = CoverImageTextOffsets[format.name]
    cover = add_text_layer(cover, text_offsets, title, subtitle, subsubtitle)

    return cover


def resize_and_crop_to_dimension(
    image: Image.Image, target_dimension: CoverImageDimension
):
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


def add_overlay_layer(image: Image.Image, overlay: CoverImageOverlay):
    image.paste(overlay.value, (0, 0), overlay.value)
    return image


def add_text_layer(
    image: Image.Image,
    text_offsets: CoverImageTextOffsets,
    title: str,
    subtitle: str,
    subsubtitle: str,
):
    if subtitle or subsubtitle:
        image = add_title(image, text_offsets, title)
        image = add_subtitle(image, text_offsets, subtitle)
        image = add_subsubtitle(image, text_offsets, subsubtitle)
    else:
        image = add_solo_title(image, text_offsets, title)

    return image


def add_title(image: Image.Image, text_offsets: CoverImageTextOffsets, text: str):
    return add_text(
        image, CoverImageTextFont.TITLE.value, text_offsets.title_offset(), text
    )


def add_subtitle(image: Image.Image, text_offsets: CoverImageTextOffsets, text: str):
    return add_text(
        image, CoverImageTextFont.SUBTITLE.value, text_offsets.subtitle_offset(), text
    )


def add_subsubtitle(image: Image.Image, text_offsets: CoverImageTextOffsets, text: str):
    return add_text(
        image,
        CoverImageTextFont.SUBTITLE.value,
        text_offsets.subsubtitle_offset(),
        text,
    )


def add_solo_title(image: Image.Image, text_offsets: CoverImageTextOffsets, text: str):
    return add_text(
        image, CoverImageTextFont.TITLE.value, text_offsets.solotitle_offset(), text
    )


def add_text(
    image: Image.Image, font: ImageFont.FreeTypeFont, text_offset: int, text: str
):
    draw = ImageDraw.Draw(image)

    left, top, right, bottom = draw.textbbox((0, 0), text=text, font=font)
    width = right - left
    height = bottom - top
    draw.text(
        ((image.size[0] - width) / 2, (image.size[1] - height) / 2 + text_offset),
        text,
        font=font,
    )

    return image
