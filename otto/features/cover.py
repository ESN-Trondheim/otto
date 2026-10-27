import base64
import io
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory

from html2image import Html2Image
from jinja2 import Environment, FileSystemLoader, select_autoescape
from PIL import Image, ImageFont

from otto.utils.esn import EsnColor

assets = Path.cwd().joinpath("assets")

jinja = Environment(
    loader=FileSystemLoader(assets.joinpath("templates")),
    autoescape=select_autoescape(),
)


class CoverFont(Enum):
    TITLE = ImageFont.truetype(
        str(assets.joinpath("fonts", "kelson-sans-bold.otf")), 90
    )
    SUBTITLE = ImageFont.truetype(
        str(assets.joinpath("fonts", "kelson-sans-bold.otf")), 50
    )


class CoverFormat(Enum):
    ESN_ACTIVITIES = (
        "Activities",
        (1920, 460),
        (19, -6, 116),
        "cover-activities.html",
    )
    HOOPLA = (
        "Hoopla",
        (1045, 588),
        (19, -6, 90),
        "cover-hoopla.html",
    )
    FACEBOOK = (
        "Facebook",
        (1568, 588),
        (19, -6, 90),
        "cover-facebook.html",
    )

    def __new__(cls, value: str, size: tuple[int], offset: tuple[int], template: str):
        """This override allows multi-value enum objects"""
        obj = object.__new__(cls)

        obj._value_ = value
        obj.size = size
        obj.offset = offset
        obj.template = template

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

    @staticmethod
    def from_value(value: str):
        for f in CoverFormat:
            if f.value == value:
                return f


default_subtitle = None
default_color = EsnColor.DARK_BLUE
default_format = CoverFormat.ESN_ACTIVITIES
default_background = Image.open(assets.joinpath("backgrounds", "cover-default.png"))


def create_cover(
    title: str,
    subtitle: str = default_subtitle,
    color: EsnColor = default_color,
    format: CoverFormat = default_format,
    background: Image.Image = default_background,
) -> Image.Image:
    """Creates a cover image by rendering an HTML template in a headless browser"""
    html = render_cover_html(title, subtitle, color, format, background)

    with TemporaryDirectory() as directory:
        # Running as root in Docker requires the sandbox to be disabled
        hti = Html2Image(
            browser="chromium",
            output_path=directory,
            temp_path=directory,
            size=format.size,
            custom_flags=[
                "--default-background-color=00000000",
                "--hide-scrollbars",
                "--no-sandbox",
            ],
            disable_logging=True,
        )
        (path,) = hti.screenshot(html_str=html, save_as="cover.png")

        with Image.open(path) as screenshot:
            return screenshot.convert(mode="RGB")


def render_cover_html(
    title: str,
    subtitle: str = default_subtitle,
    color: EsnColor = default_color,
    format: CoverFormat = default_format,
    background: Image.Image = default_background,
) -> str:
    # The background is cropped beforehand, so the browser only has to display it
    background = resize_and_crop_to_dimension(
        background.convert(mode="RGB"), format.target_width, format.target_height
    )

    return jinja.get_template(format.template).render(
        # Makes the relative asset paths in the template work from the temporary folder it is rendered in
        base=assets.joinpath("templates").as_uri() + "/",
        background=to_data_uri(background),
        grid_style=f"background-color: rgba{(*color.rgb(), 0.6)}",
        lines=layout_lines(format, title, subtitle),
    )


def layout_lines(format: CoverFormat, title: str, subtitle: str | None) -> list[dict]:
    """Positions each line of text the same way as the original Pillow cover generator did"""
    if subtitle:
        lines = [
            (CoverFont.TITLE, format.title_offset, title),
            (CoverFont.SUBTITLE, format.subtitle_offset, subtitle),
        ]
    else:
        lines = [(CoverFont.TITLE, format.solotitle_offset, title)]

    return [layout_line(format, *line) for line in lines]


def layout_line(format: CoverFormat, font: CoverFont, offset: int, text: str) -> dict:
    left, top, right, bottom = font.value.getbbox(text)
    ascent, descent = font.value.getmetrics()

    # Pillow places text by its ascender line, which the browser draws above the top of a line box this tight
    leading = (font.value.size - ascent - descent) / 2

    x = (format.target_width - (right - left)) / 2
    y = (format.target_height - (bottom - top)) / 2 + offset - leading

    return {
        "text": text,
        "size": font.value.size,
        "x": x,
        "y": y,
        "style": f"font-size: {font.value.size}px; left: {x}px; top: {y}px; transform: none",
    }


def to_data_uri(image: Image.Image) -> str:
    """Embeds an image in the template, as uploaded images only exist in memory"""
    content = io.BytesIO()
    image.save(content, format="PNG")

    return f"data:image/png;base64,{base64.b64encode(content.getvalue()).decode()}"


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
            padding = (image.height - target_height) // 2
            coords = (0, padding, target_width, padding + target_height)
            image = image.crop(coords)
    else:  # If background width is too big
        # Resize the image so the height reaches the target height (while maintaining original aspect ratio)
        resize_ratio = image.height / target_height
        new_width = int(image.width / resize_ratio)
        image = image.resize((new_width, target_height), Image.Resampling.LANCZOS)

        # Crop away the excessive width if neccessary
        if image.width > target_width:
            padding = (image.width - target_width) // 2
            coords = (padding, 0, padding + target_width, target_height)
            image = image.crop(coords)

    return image
