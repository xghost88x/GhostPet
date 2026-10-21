"""Species-specific desktop sprites; the approved Founder mouse is not modified."""
from __future__ import annotations
from PySide6.QtGui import QColor

COLORS = {
    "Ghost": ("#d5c1f4", "#8d80c7", "#ffadca"),
    "Cat": ("#eab77e", "#a87653", "#e6a1ad"),
    "Dog": ("#cda27b", "#92694e", "#eda3b4"),
    "Bunny": ("#f2e6d9", "#b9aaa2", "#e9a9be"),
    "Fox": ("#ed955f", "#b8634d", "#eda7a6"),
    "Dragon": ("#87cf9c", "#538d75", "#e7a4b8"),
}


def draw_adopted_pet(painter, width, height, pet, frame, scale=4, facing=1):
    species = pet.get("species", "Ghost")
    bright, shaded, blush = (QColor(x) for x in COLORS.get(species, COLORS["Ghost"]))
    dark = QColor("#334143")
    light = QColor("#fff7e9")
    painter.save()
    if facing < 0:
        painter.translate(width, 0)
        painter.scale(-1, 1)
    ox = (width - 20*scale)//2
    oy = (height - 21*scale)//2 + (frame%2 if not pet.get("sleeping") else 0)
    def pix(x,y,w,h,color):
        painter.fillRect(ox+x*scale,oy+y*scale,w*scale,h*scale,color)
    # Species silhouettes are built before the rounded face.
    if species == "Cat":
        pix(2,3,5,7,dark);pix(13,3,5,7,dark)
        pix(3,4,3,5,bright);pix(14,4,3,5,bright)
        pix(4,6,2,2,blush);pix(14,6,2,2,blush)
        pix(17,13,2,5,dark);pix(18,11,1,4,bright)
    elif species == "Dog":
        pix(2,6,4,7,dark);pix(14,6,4,7,dark)
        pix(3,7,2,6,shaded);pix(15,7,2,6,shaded)
        pix(17,14,3,3,shaded)
    elif species == "Bunny":
        pix(4,0,5,9,dark);pix(12,0,5,9,dark)
        pix(5,1,3,7,bright);pix(13,1,3,7,bright)
        pix(6,2,1,5,blush);pix(14,2,1,5,blush)
        pix(17,16,3,3,light)
    elif species == "Fox":
        pix(3,4,5,5,dark);pix(12,4,5,5,dark)
        pix(4,3,3,6,bright);pix(13,3,3,6,bright)
        pix(16,14,3,5,shaded);pix(18,12,2,3,bright)
        pix(17,12,2,2,light)
    elif species == "Dragon":
        pix(3,8,5,7,dark);pix(12,8,5,7,dark)
        pix(2,9,4,6,shaded);pix(14,9,4,6,shaded)
        pix(7,3,2,5,dark);pix(12,3,2,5,dark)
        pix(8,3,1,4,light);pix(12,3,1,4,light)
        pix(17,12,3,6,shaded)
    else:
        # Little floating ghost with scalloped hem.
        pix(3,14,14,4,light)
        pix(4,17,4,3,bright);pix(9,17,4,3,bright);pix(14,17,3,3,bright)
    # Small compact body. Avoid the oversized shoulder/arm silhouette.
    pix(5,7,10,12,dark)
    pix(4,10,12,7,dark)
    pix(6,8,8,10,bright)
    pix(5,11,10,6,bright)
    if species == "Fox":
        pix(7,13,6,4,light)
    elif species == "Dog":
        pix(8,13,4,3,shaded)
    else:
        pix(8,15,4,2,light)
    pix(6,18,3,2,dark);pix(11,18,3,2,dark)
    pix(7,18,2,1,shaded);pix(11,18,2,1,shaded)
    if pet.get("sleeping",False) or frame%52 == 0:
        pix(7,11,2,1,dark);pix(12,11,2,1,dark)
    else:
        pix(7,10,2,2,dark);pix(12,10,2,2,dark)
        pix(7,10,1,1,light);pix(12,10,1,1,light)
    pix(5,13,2,1,blush);pix(14,13,2,1,blush)
    pix(9,13,2,1,dark)
    painter.restore()
