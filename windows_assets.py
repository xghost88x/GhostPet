"""Generate a Windows application icon from the existing original GhostPet SVG."""
from pathlib import Path
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer


def build_icon():
    renderer = QSvgRenderer(str(Path("assets/ghostpet.svg").resolve()))
    if not renderer.isValid():
        raise RuntimeError("Could not render the original GhostPet SVG icon.")
    image = QImage(256,256,QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter=QPainter(image)
    renderer.render(painter)
    painter.end()
    out=Path("build_icons")
    out.mkdir(exist_ok=True)
    png=out/"ghostpet.png"
    ico=out/"ghostpet.ico"
    if not image.save(str(png)):
        raise RuntimeError("Could not save PNG for Windows icon")
    icon=Image.open(png).convert("RGBA")
    icon.save(ico,format="ICO",sizes=[
        (16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)
    ])
    return ico


if __name__=="__main__":
    print(build_icon())
