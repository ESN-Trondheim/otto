from otto.features.coverimage.generator import CoverImageFormat
from otto.utils.blocks import actions, button, section, select_input, text_input
from otto.utils.esn import EsnColor

COVERIMAGE_BLOCKS = [
    text_input(text="Title (required)", value="title"),
    text_input(text="Subtitle", value="subtitle"),
    select_input(
        text="Color (required)",
        value="color",
        options=[c.display_name() for c in EsnColor],
    ),
    select_input(
        text="Format (required)",
        value="format",
        options=[f.value for f in CoverImageFormat],
    ),
    actions(
        elements=[button(text="Generate", value="generate_coverimage", style="primary")]
    ),
]
