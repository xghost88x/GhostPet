"""Species-specific desktop sprites; the approved Founder mouse is not modified."""
from __future__ import annotations
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QPolygon, QPen

COLORS = {
    "Ghost": ("#d5c1f4", "#8d80c7", "#ffadca"),
    "Cat": ("#eab77e", "#a87653", "#e6a1ad"),
    "Dog": ("#cda27b", "#92694e", "#eda3b4"),
    "Bunny": ("#f2e6d9", "#b9aaa2", "#e9a9be"),
    "Fox": ("#ed955f", "#b8634d", "#eda7a6"),
    "Dragon": ("#87cf9c", "#538d75", "#e7a4b8"),
}



def draw_cat(p, width, height, pet, frame, scale=4, facing=1):
    """Distinct 28px-wide chibi cat: triangular ears, cheeks, whiskers and curled tail.

    Kept separate from the generic species body so new shading cannot bury
    the ears or turn the face into a featureless square.
    """
    fur = QColor("#edb06d")
    shadow = QColor("#ae734d")
    ink = QColor("#4c453e")
    pink = QColor("#efaeb9")
    cream = QColor("#fff0d9")
    p.save()
    if facing < 0:
        p.translate(width, 0)
        p.scale(-1, 1)
    p.translate((width - 28 * scale) // 2, (height - 28 * scale) // 2
                + (frame % 2 if not pet.get("sleeping", False) else 0))
    p.scale(scale, scale)
    def pix(x,y,w,h,c):
        p.fillRect(x,y,w,h,c)
    def polygon(points, color):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        p.drawPolygon(QPolygon([QPoint(x,y) for x,y in points]))

    # A striped upward-curled tail clearly separated from the body.
    pix(22,18,3,6,ink)
    pix(24,14,3,6,ink)
    pix(24,12,4,4,ink)
    pix(25,13,2,4,fur)
    pix(24,17,2,3,fur)
    pix(23,21,2,3,fur)
    pix(25,15,2,2,shadow)

    # Tiny seated body, belly and two separate paws.
    p.setPen(ink)
    p.setBrush(ink)
    p.drawRoundedRect(7,15,17,12,6,6)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(fur)
    p.drawRoundedRect(8,16,15,10,5,5)
    p.setBrush(cream)
    p.drawEllipse(11,18,9,7)
    pix(8,24,6,4,ink);pix(17,24,6,4,ink)
    pix(9,24,4,3,fur);pix(18,24,4,3,fur)
    for xx in (10,12,19,21):
        pix(xx,26,1,1,shadow)

    # Ears come BEFORE the oversized, softly rounded head.
    polygon([(3,12),(4,1),(13,9)],ink)
    polygon([(15,9),(24,1),(25,12)],ink)
    polygon([(5,10),(6,4),(12,10)],fur)
    polygon([(17,10),(22,4),(23,10)],fur)
    polygon([(7,9),(7,6),(11,10)],pink)
    polygon([(19,10),(22,6),(22,9)],pink)

    p.setPen(ink)
    p.setBrush(ink)
    p.drawRoundedRect(3,8,23,15,8,8)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(fur)
    p.drawRoundedRect(4,9,21,13,7,7)
    # Wide cheek tufts, soft white muzzle and tabby forehead stripes.
    pix(3,17,4,4,fur);pix(22,17,4,4,fur)
    p.setBrush(cream)
    p.drawEllipse(9,17,11,5)
    pix(11,10,2,3,shadow);pix(15,10,2,3,shadow)
    pix(13,9,2,3,shadow)

    if pet.get("sleeping", False) or frame % 50 == 0:
        pix(8,15,4,1,ink);pix(18,15,4,1,ink)
    else:
        pix(9,14,3,3,ink);pix(18,14,3,3,ink)
        pix(9,14,1,1,cream);pix(18,14,1,1,cream)
    pix(6,18,3,2,pink);pix(21,18,3,2,pink)
    polygon([(13,18),(17,18),(15,20)],pink)
    pix(15,20,1,2,ink)
    pix(13,21,2,1,ink);pix(16,21,2,1,ink)

    # Long, symmetric whiskers are a defining cat feature at this scale.
    p.setPen(QPen(ink,1))
    for x1,y1,x2,y2 in ((2,17,0,16),(3,19,0,19),(3,21,0,22),
                        (25,17,27,16),(25,19,27,19),(25,21,27,22)):
        p.drawLine(x1,y1,x2,y2)
    p.restore()

def draw_adopted_pet(painter, width, height, pet, frame, scale=4, facing=1):
    species = pet.get("species", "Ghost")
    if species == "Cat":
        draw_cat(painter, width, height, pet, frame, scale, facing)
        return
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
