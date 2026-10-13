import os

from html2image import Html2Image
from jinja2 import Environment, FileSystemLoader, select_autoescape

WIDTH = 1920
HEIGHT = 460

template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets\\templates")

jinja = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=select_autoescape()
)

template = jinja.get_template("event-cover-image.html")

html = template.render(title = "Event Title Example", width = WIDTH, height = HEIGHT)

hti = Html2Image("chromium")

hti.size = (WIDTH, HEIGHT)

hti.screenshot(html_str=html, save_as='event-cover-image.png')
