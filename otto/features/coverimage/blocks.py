from otto.features.coverimage.generator import CoverImageFormat
from otto.utils.blocks import actions, button, section, select_input, text_input
from otto.utils.esn import EsnColor

COVERIMAGE_BLOCKS = [
    section(text="Alright! Let's make a cover image :esnstar:"),
    text_input(text="Title", value="title"),
    text_input(text="Subtitle", value="subtitle"),
    text_input(text="Subsubtitle", value="subsubtitle"),
    select_input(
        text="Color", value="color", options=[c.display_name() for c in EsnColor]
    ),
    select_input(
        text="Format",
        value="format",
        options=[f.value for f in CoverImageFormat],
        initial_option=CoverImageFormat.ESN_ACTIVITIES.value,
    ),
    actions(elements=[button(text="Generate", value="generate_coverimage")]),
]
