"""Original hand-painted-by-code woodland cottage artwork for Ghost Pet.

Deliberately keeps 18x12 invisible navigation grid separate from visible art.
All rendering is local QPainter shapes; no external assets or network required.
"""
from __future__ import annotations
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPen

TILE = 32
W, H = 18, 12


def box(p, x, y, w, h, color):
    p.fillRect(round(x), round(y), round(w), round(h), QColor(color))


def rug(p, x, y, w, h, edge, center):
    # Pixel-soft woven carpet with a bordered cloth and a central motif.
    box(p, x+3, y+4, w, h, "#765f4b")
    box(p, x, y, w, h, edge)
    box(p, x+5, y+5, w-10, h-10, center)
    for delta in range(10, min(w, h)//2, 11):
        box(p, x+delta, y+8, 3, 2, "#f3e3c6")
        box(p, x+delta, y+h-10, 3, 2, "#f3e3c6")
    # Light geometric rosette.
    box(p, x+w//2-8, y+h//2-8, 16, 16, edge)
    box(p, x+w//2-5, y+h//2-5, 10, 10, center)


def plant(p, x, y, size=1):
    s = size
    box(p,x+9*s,y+15*s,14*s,7*s,"#704f41")
    box(p,x+11*s,y+15*s,10*s,5*s,"#bf8566")
    box(p,x+15*s,y+4*s,3*s,14*s,"#47775c")
    for dx,dy,c in ((2,10,"#4d8261"),(8,2,"#7eaa79"),
                     (15,0,"#487f63"),(23,7,"#78a675"),(19,10,"#6c9a6f")):
        box(p,x+dx*s,y+dy*s,8*s,7*s,c)


def window(p, x, y, wide=54):
    box(p,x,y+3,wide,26,"#846950")
    box(p,x+4,y+5,wide-8,20,"#f1e5bf")
    box(p,x+8,y+7,wide-16,16,"#a1cad1")
    # Sunlight and hills outside.
    box(p,x+10,y+17,wide-20,6,"#83ab8e")
    box(p,x+12,y+9,9,6,"#fff1c7")
    box(p,x+wide//2-1,y+7,3,16,"#f6e8d1")
    box(p,x+4,y+26,wide-8,4,"#f5d8a7")
    # Sage gingham curtains.
    box(p,x+3,y+5,9,21,"#9fb59a")
    box(p,x+wide-12,y+5,9,21,"#9fb59a")
    for k in (8,15,22):
        box(p,x+5,y+k,4,2,"#d4dcc1")
        box(p,x+wide-10,y+k,4,2,"#d4dcc1")


def bookcase(p,x,y):
    box(p,x+2,y+4,52,25,"#705742")
    box(p,x+4,y+6,48,22,"#b18b61")
    for yy in (11,22):
        box(p,x+5,y+yy,45,2,"#654b38")
    palette = ("#b6c29e","#eab28e","#95aaa4","#f0d09f","#9aab9e")
    for i in range(16):
        bx=x+7+(i%8)*5
        by=y+7+(i//8)*11
        box(p,bx,by,3,7+(i%3),palette[i%len(palette)])


def kitchen_detail(p,x,y):
    # Small light-wood kitchen counter, tile backsplash and sink/cooktop.
    box(p,x,y,139,28,"#d8cbb0")
    for dx in range(0,139,12):
        box(p,x+dx,y+1,1,11,"#bfaa91")
    box(p,x+2,y+11,135,16,"#957a5d")
    box(p,x+5,y+13,129,11,"#dcc39e")
    box(p,x+15,y+14,28,9,"#a1b5b6")
    box(p,x+20,y+15,18,6,"#d9ede8")
    box(p,x+69,y+16,14,5,"#696760")
    box(p,x+92,y+16,14,5,"#696760")
    box(p,x+48,y+5,6,10,"#6f9f70")
    box(p,x+45,y+1,12,6,"#79ae7c")
    for cx in (57,110,121):
        box(p,x+cx,y+23,3,2,"#856846")


def pixel_cottage(p, layout, walls):
    """Paint richly layered home flooring, architectural details and tiny props."""
    t = TILE
    w,h = W*t,H*t
    # Continuous wood planks spanning rooms, staggered by half-width.
    box(p,0,0,w,h,"#af825b")
    shades = ("#bd9169","#c69b72","#d0a77d","#bf9670","#d0a681")
    for yy in range(18,h,18):
        base = shades[(yy//18)%len(shades)]
        box(p,0,yy,w,17,base)
        box(p,0,yy+16,w,2,"#a77c5a")
        shift = 62 if (yy//18)%2 else 0
        for xx in range(-120+shift,w,124):
            box(p,xx,yy,2,17,"#ae8662")
            box(p,xx+25,yy+5,34,1,"#b88e67")
            box(p,xx+81,yy+11,19,1,"#ddbb95")
    # Small quarter-round room area carpets and tile accents.
    rug(p,46,91,112,87,"#aaa47f","#e1cda9")           # bedroom
    rug(p,319,74,157,112,"#739782","#b9c8aa")         # living
    rug(p,51,258,111,74,"#b59a80","#e7dbc1")          # kitchen
    rug(p,326,257,139,77,"#b9a79a","#e9cdb7")         # nursery
    if layout=="open":
        rug(p,212,102,155,98,"#869d7e","#e6d4b4")
    if layout=="garden":
        box(p,304,225,219,124,"#d8b591")
        for row in range(229,344,22):
            box(p,304,row,219,2,"#c7a17e")
            for col in range(308+(row%3)*12,522,22):
                box(p,col,row,2,20,"#cba782")
        rug(p,353,265,100,69,"#769a80","#e0e2bc")
    # Each purchasable floor plan gets its own strongly recognizable ground:
    # the Open Plan has an expansive sage lounge, Garden an entire conservatory.
    if layout == "open":
        box(p,202,69,335,139,"#ccb08a")
        for yy in range(77,203,22):
            box(p,209,yy,319,3,"#efd5af")
            for xx in range(214+(yy % 3)*12,523,56):
                box(p,xx,yy+3,2,17,"#aa8665")
        rug(p,240,99,239,103,"#5c866f","#a9c5aa")
        box(p,272,106,174,6,"#e9d8b6")
    elif layout == "garden":
        # Premium plan uses a visually dramatic terracotta-and-sage
        # conservatory floor, extending through the open lower living zone.
        box(p,32,198,512,153,"#e3c8a0")
        for yy in range(200,350,24):
            for xx in range(35,542,24):
                box(p,xx,yy,22,22,
                    "#d6b28a" if (xx//24 + yy//24) % 2 else "#ecd8b9")
                box(p,xx+2,yy+3,4,4,"#e4c198")
        box(p,296,198,246,150,"#b6ccaa")
        for xx in range(298,540,32):
            box(p,xx,200,2,147,"#e2edce")
        for yy in range(200,347,32):
            box(p,296,yy,246,2,"#e4e9c6")
        rug(p,306,254,158,83,"#6f9377","#dde3c4")

    # Joined plaster partitions: draw beams only at genuine wall boundaries.
    # Keep the full old pathfinding footprint, remove Tetris-like tile seams.
    for x,y in walls:
        xx,yy=x*t,y*t
        box(p,xx,yy,t,t,"#c9bda1")
        if (x,y-1) not in walls:
            box(p,xx,yy,t,7,"#f5e8ca")
            box(p,xx,yy+7,t,3,"#9d8466")
        if (x,y+1) not in walls:
            box(p,xx,yy+t-7,t,4,"#8e7157")
            box(p,xx,yy+t-3,t,3,"#ddc7a5")
        if (x-1,y) not in walls:
            box(p,xx,yy,4,t,"#ead8b7")
            box(p,xx+4,yy,2,t,"#80654c")
        if (x+1,y) not in walls:
            box(p,xx+t-6,yy,3,t,"#92785e")
            box(p,xx+t-3,yy,3,t,"#f1dbb9")
    # Fix doorway gaps visually: warm timber thresholds make flow clear.
    for x,y in ((8,3),(8,4),(8,8),(3,6),(4,6),(12,6),(13,6),
                (8,2),(8,5),(8,9),(2,6),(11,6)):
        if (x,y) not in walls and 0<x<W-1 and 0<y<H-1:
            box(p,x*t,y*t+t-6,t,4,"#ad8664")
            box(p,x*t+3,y*t+t-6,t-6,2,"#e3c396")
    # Architectural wall decor. Windows extend across their wall tiles.
    window(p,75,0,58)
    window(p,382,0,58)
    window(p,0,245,30)
    window(p,539,245,30)
    # Wall shelves and flowers: restrained, cozy details.
    bookcase(p,347,34)
    box(p,32,33,72,15,"#806149")
    box(p,33,34,70,12,"#c89d71")
    for ix in range(6):
        box(p,38+ix*10,37,7,7,("#88a886","#e3c5ac","#a58e7c")[ix%3])
    kitchen_detail(p,41,227)
    # Windowsills, succulents and softly lit lamps.
    plant(p,471,39)
    plant(p,166,281)
    plant(p,487,295)
    box(p,477,78,9,21,"#685641")
    box(p,468,70,26,13,"#f4dfaa")
    box(p,474,66,14,4,"#ffedc9")
    # A few little toy props in the nursery corner.
    box(p,497,305,18,13,"#d49a65")
    box(p,500,298,11,10,"#ecd29e")
    box(p,499,295,5,5,"#be8966")
    box(p,509,295,5,5,"#be8966")
    draw_room_vignettes(p, layout)
    draw_upgrade_features(p, layout)
    # Small carved name plaques to replace large overlaid map captions.
    names = {
        "cottage": (("BEDROOM",48,59),("LIVING",320,54),("KITCHEN",40,207),("NURSERY",324,210)),
        "open": (("BEDROOM",48,59),("OPEN LOUNGE",312,54),("KITCHEN",40,207),("NURSERY",324,210)),
        "garden": (("BEDROOM",48,59),("SUNNY LOUNGE",309,54),("KITCHEN",40,207),("GARDEN",330,210)),
    }
    p.setFont(QFont("Sans",8,QFont.Weight.Bold))
    for label,x,y in names.get(layout,names["cottage"]):
        box(p,x-4,y-11,len(label)*7+10,17,"#e9d8b6")
        box(p,x-2,y-9,len(label)*7+6,13,"#c0a27a")
        p.setPen(QColor("#594a38"))
        p.drawText(x,y+1,label)


def cottage_item(p, px, py, item, tint):
    """Detailed 32x32 original furniture sprites, grounded with drop shadows."""
    if item not in ("bed","toy","rug","plant","sofa","ball","bowl","lamp"):
        return
    # Items retain exactly their existing click, cost, save and occupied-cell logic.
    box(p,px+6,py+25,24,4,"#876d59")
    if item=="bed":
        box(p,px+2,py+5,28,24,"#5d4b42")
        box(p,px+4,py+7,24,20,"#c99676")
        box(p,px+6,py+8,20,5,"#fff1d9")
        box(p,px+8,py+9,16,3,"#f7eee5")
        box(p,px+6,py+14,20,10,"#aab8a1")
        box(p,px+6,py+21,20,3,"#7c987f")
        box(p,px+7,py+15,3,6,"#c9d9b7")
        box(p,px+24,py+15,2,6,"#e6d9b6")
    elif item=="sofa":
        box(p,px+2,py+9,28,17,"#705f4f")
        box(p,px+5,py+7,22,14,"#769682")
        box(p,px+7,py+10,8,10,"#bad0b8")
        box(p,px+17,py+10,8,10,"#a7c1a5")
        box(p,px+4,py+20,24,5,"#526e60")
        box(p,px+3,py+16,4,10,"#5e826c")
        box(p,px+25,py+16,4,10,"#5e826c")
        box(p,px+5,py+25,4,4,"#5a4b40")
        box(p,px+24,py+25,4,4,"#5a4b40")
    elif item=="rug":
        rug(p,px+3,py+6,26,20,"#a9a080","#e6dbbb")
    elif item=="plant":
        plant(p,px+2,py+3)
    elif item=="toy":
        box(p,px+6,py+13,21,13,"#b07b50")
        box(p,px+5,py+6,8,9,"#c69b6e")
        box(p,px+20,py+6,8,9,"#c69b6e")
        box(p,px+8,py+9,17,14,"#d8ab7d")
        box(p,px+10,py+14,3,3,"#3d433f")
        box(p,px+20,py+14,3,3,"#3d433f")
        box(p,px+15,py+18,4,3,"#6b5347")
        box(p,px+11,py+25,5,3,"#8d7155")
        box(p,px+20,py+25,5,3,"#8d7155")
    elif item=="ball":
        box(p,px+7,py+8,18,18,"#7a6d60")
        box(p,px+9,py+7,14,18,"#ebc787")
        box(p,px+7,py+10,18,13,"#e7ac8d")
        box(p,px+14,py+8,5,17,"#f7dfaa")
    elif item=="bowl":
        box(p,px+5,py+16,22,10,"#786d66")
        box(p,px+7,py+17,18,6,"#e3e0d4")
        box(p,px+10,py+16,12,3,"#a28162")
        for x in (11,16,20):
            box(p,px+x,py+17,3,3,"#8a6946")
    elif item=="lamp":
        box(p,px+14,py+18,4,8,"#6a6253")
        box(p,px+10,py+24,13,3,"#74604e")
        box(p,px+7,py+7,19,12,"#f4dba1")
        box(p,px+9,py+9,15,8,"#fff0c5")
        box(p,px+13,py+4,7,3,"#9c8c6f")


def built_in_occupied(layout):
    """Reserved cells for built-in furnishings; kept away from every doorway."""
    tiles = {
        (4,2),(5,2),(4,3),(5,3),(4,4),(5,4),  # bedroom quilted bed
        (10,3),(11,3),(12,3),(10,4),(11,4),  # living room couch
        (1,8),(1,9),(1,10),                   # kitchen wall pantry
        (5,9),(6,9),                          # dining table
        (15,8),(16,8),(15,9),(16,9),          # nursery / garden structure
    }
    return tiles


def draw_room_vignettes(p, layout):
    """Recognizable, larger-than-one-tile furnishings for a lived-in cottage."""
    # Keep larger drawings within the actual 18×12 cottage boundaries.
    p.save()
    p.setClipRect(32, 32, 512, 320)

    # Room-specific scales keep furniture proportional to each little room.
    p.save()
    p.translate(145, 120)
    p.scale(0.82, 0.82)
    p.translate(-145, -120)
    # Distinct bedside furniture, a quilted double bed and a framed painting.
    box(p,136,66,80,92,"#74553e")
    box(p,132,61,80,92,"#b78d62")
    box(p,139,68,66,82,"#ecdcbd")
    box(p,142,71,60,22,"#fff4df")
    box(p,145,73,25,17,"#fffaf0")
    box(p,174,73,25,17,"#efe2d5")
    box(p,141,94,62,54,"#789b83")
    for yy in (97,114,131):
        for xx in (145,164,183):
            shade = "#c5d4b5" if (xx+yy)//17%2 else "#e5c7ac"
            box(p,xx,yy,17,14,shade)
            box(p,xx+6,yy+5,5,4,"#f5e2c3")
    box(p,141,147,63,4,"#526c57")
    box(p,139,151,9,5,"#614e40")
    box(p,199,151,9,5,"#614e40")
    box(p,217,106,26,24,"#7c5b46")    # nightstand
    box(p,219,104,22,19,"#be9169")
    box(p,227,97,7,11,"#987c63")
    box(p,224,90,15,9,"#f5d7a1")
    box(p,227,92,8,6,"#fff2cc")
    box(p,56,49,48,23,"#7b604a")      # landscape painting
    box(p,59,52,42,17,"#ddcbac")
    box(p,62,54,36,12,"#a1c0b7")
    box(p,67,60,29,6,"#71927c")
    box(p,83,54,6,5,"#f9e5b7")
    box(p,68,147,26,21,"#936f4d")     # woven basket
    for xx in (72,79,86):
        box(p,xx,151,2,14,"#e2bd89")
    for xx in (106,124):               # soft slippers
        box(p,xx,155,13,6,"#e4ceb2")

    p.restore()
    p.save()
    p.translate(419, 126)
    p.scale(0.82, 0.82)
    p.translate(-419, -126)
    # Proper upholstered 3-seat couch and round tea table.
    box(p,326,100,127,63,"#4f685b")
    box(p,335,91,110,63,"#709580")
    box(p,339,95,102,25,"#8daa95")
    for xx in (341,374,407):
        box(p,xx,104,31,32,"#b6cdb5")
        box(p,xx+4,107,24,24,"#d2dfca")
        box(p,xx+11,110,9,3,"#f4e7d3")
    box(p,336,136,105,17,"#5d7d6a")
    box(p,325,110,14,42,"#597663")
    box(p,441,110,14,42,"#597663")
    for xx in (329,441):
        box(p,xx,157,11,7,"#634a3b")
    p.setPen(QColor("#74563f"));p.setBrush(QColor("#846048"))
    p.drawEllipse(465,115,58,43)
    p.setPen(QColor("#d6ac80"));p.setBrush(QColor("#caa47a"))
    p.drawEllipse(462,110,58,43)
    p.setPen(QColor("#f1d9b5"));p.drawEllipse(468,115,46,32)
    box(p,481,126,13,8,"#f9efe2")
    box(p,486,125,4,3,"#9aab86")
    box(p,500,133,10,6,"#e6d4bd")
    box(p,502,132,6,2,"#a28c75")
    box(p,467,42,43,29,"#80634d")    # botanical wall art
    box(p,471,46,35,21,"#c9dabb")
    box(p,473,48,31,17,"#8aafaf")
    box(p,475,57,29,7,"#588572")
    box(p,484,48,7,6,"#fae6a9")

    p.restore()
    p.save()
    p.translate(144, 282)
    p.scale(0.82, 0.82)
    p.translate(-144, -282)
    # Kitchen: three-door pantry, copper cookware and dining nook.
    box(p,35,241,39,97,"#765640")
    box(p,38,244,32,90,"#b9946b")
    for yy in (248,278,307):
        box(p,41,yy,26,23,"#e2c6a1")
        box(p,61,yy+12,3,5,"#927257")
    box(p,73,287,15,34,"#f2e7cf")    # dishcloth
    for xx in (76,84):
        box(p,xx,290,3,27,"#a4b9a6")
    box(p,94,235,76,4,"#806045")    # hanging copper pots
    for xx in (98,123,148):
        box(p,xx+6,239,3,6,"#6e5442")
        box(p,xx,245,19,13,"#af7050")
        box(p,xx+2,247,15,8,"#dd9e69")
    p.setPen(QColor("#76563e"));p.setBrush(QColor("#97704f"))
    p.drawEllipse(163,265,62,25)        # chair above
    p.drawEllipse(163,322,62,19)        # chair below
    p.setPen(QColor("#b78e6a"));p.setBrush(QColor("#bb956d"))
    p.drawEllipse(172,273,55,46)        # dining table
    p.setPen(QColor("#e9ceaa"));p.setBrush(QColor("#e4bf95"))
    p.drawEllipse(176,276,47,39)
    box(p,184,289,12,8,"#f6ebd4")     # plates and tea
    box(p,203,290,11,7,"#f7e3cd")
    box(p,205,288,6,2,"#998066")
    box(p,188,287,4,2,"#83a783")

    p.restore()
    p.save()
    p.translate(416, 285)
    p.scale(0.82, 0.82)
    p.translate(-416, -285)
    if layout == "garden":
        # The premium layout replaces nursery furnishings with a conservatory.
        for xx in (328,374,420,466):
            box(p,xx,239,39,5,"#806b4d")
            box(p,xx+3,244,33,16,"#a6c09e")
            for leaf in (0,10,20):
                box(p,xx+5+leaf,231,8,11,"#5e8f65")
                box(p,xx+7+leaf,227,4,7,"#a1c88e")
        box(p,488,268,50,66,"#725a42")
        box(p,492,272,42,56,"#ad8660")
        for xx in (495,508,521):
            for yy in (276,295,314):
                box(p,xx,yy,8,11,"#5a9369")
                box(p,xx+3,yy-3,5,6,"#9bbb86")
        box(p,366,296,69,30,"#907455")
        box(p,370,290,61,29,"#c7b496")
        box(p,375,295,51,20,"#eee0bf")
        box(p,380,302,12,5,"#f6edcf")
    else:
        # Crib with wooden railings, teddy bear, toy shelves and pet cushion.
        box(p,475,246,63,77,"#806249")
        box(p,479,249,55,71,"#d9b28a")
        box(p,485,252,43,52,"#d8dbce")
        box(p,488,254,37,44,"#a8c0ac")
        box(p,490,255,33,12,"#fff0d7")
        for xx in range(483,532,7):
            box(p,xx,302,3,15,"#a9825f")
        box(p,480,317,53,4,"#715b49")
        box(p,316,249,62,33,"#947458")
        box(p,320,252,54,26,"#cba37e")
        for xx,c in ((323,"#adc7a6"),(341,"#eac99f"),(359,"#d4bfd3")):
            box(p,xx,261,12,12,c)
            box(p,xx+2,263,4,4,"#fff4db")
        p.setPen(QColor("#a68f81"));p.setBrush(QColor("#f0d3b4"))
        p.drawEllipse(378,296,62,31)
        p.setPen(QColor("#b68b67"));p.setBrush(QColor("#c39a70"))
        p.drawEllipse(390,267,26,25)
        box(p,385,266,8,9,"#c39a70")
        box(p,413,266,8,9,"#c39a70")
        box(p,396,280,3,3,"#453a34")
        box(p,409,280,3,3,"#453a34")
        box(p,403,285,3,3,"#715043")

    p.restore()
    # Cozy small touches: overhead lamps and a welcome runner.
    for xx,yy in ((218,41),(512,187),(165,204)):
        box(p,xx,yy,4,8,"#937458")
        box(p,xx-8,yy+8,21,11,"#f0d09a")
        box(p,xx-5,yy+9,15,9,"#fff0bc")
    for xx,yy in ((245,113),(95,195),(403,195)):
        box(p,xx,yy,29,12,"#9c8468")
        box(p,xx+3,yy+3,23,6,"#e2ceb2")
    p.restore()


def draw_upgrade_features(p, layout):
    """Large, layout-specific interior elements independent of saved furniture."""
    if layout == "open":
        # Breakfast island sits under the missing central partitions; a
        # warm lounge replaces the formerly divided kitchen/living corridor.
        box(p,244,153,90,36,"#756049")
        box(p,247,149,86,34,"#c09e72")
        box(p,250,151,80,26,"#e7cba2")
        box(p,260,157,23,13,"#e5ece0")
        box(p,263,160,17,7,"#94bcb5")
        box(p,298,157,21,15,"#8caf8a")
        box(p,302,154,13,6,"#cfe0a9")
        box(p,255,181,17,8,"#80664d")
        box(p,308,181,17,8,"#80664d")
        # Woven pouf and book basket give the great room recognizable purpose.
        box(p,217,80,31,25,"#9b825b")
        box(p,221,84,23,17,"#dfc79c")
        for xx in (223,229,235):
            box(p,xx,85,2,14,"#ac8f6f")
        box(p,493,171,29,13,"#7b624d")
        for xx,col in ((497,"#e6cb97"),(503,"#7fa08e"),(509,"#bc967e")):
            box(p,xx,165,5,16,col)
        # Strongly different arch treatment; no illusion of four closed rooms.
        for x in (187,353):
            box(p,x,186,8,23,"#d6bc91")
            box(p,x,186,8,5,"#f5deb1")
    elif layout == "garden":
        # Vertical greenhouse glazing and decorative espalier plant wall.
        for xx in (308,360,412,464,516):
            box(p,xx,201,39,8,"#a4c7b1")
            box(p,xx+4,203,31,4,"#f2efca")
            box(p,xx+17,208,4,25,"#4c866d")
            box(p,xx+5,219,12,11,"#6d9f72")
            box(p,xx+22,214,10,12,"#95ba79")
        # A water bowl and a lily pad make the garden feel different.
        p.setPen(QColor("#77999a"));p.setBrush(QColor("#8ebbb3"))
        p.drawEllipse(249,258,43,36)
        p.setPen(QColor("#d5e8c8"));p.drawEllipse(254,262,33,27)
        box(p,263,269,18,7,"#6fa285")
        box(p,278,265,5,4,"#f5d5bc")
        # Potted palms, seed tray, climbing vine and a garden bench.
        for xx in (300,337,475):
            plant(p,xx,302)
        box(p,160,232,91,25,"#705a43")
        box(p,164,229,83,24,"#a6b78b")
        for xx in range(169,244,15):
            box(p,xx,229,4,24,"#e1d9b4")
        box(p,173,254,9,17,"#80604a")
        box(p,227,254,9,17,"#80604a")
