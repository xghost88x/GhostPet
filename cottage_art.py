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
    # Architectural walls with a lifted 3D effect and continuous trim.
    for x,y in walls:
        xx,yy=x*t,y*t
        box(p,xx+2,yy+5,t,t-3,"#6c5240")  # shadow
        box(p,xx,yy,t,t-5,"#dcd1b3")
        box(p,xx,yy,t,7,"#f2e7cd")
        box(p,xx,yy+7,t,3,"#a28d70")
        box(p,xx,yy+10,t,t-16,"#b7aa89")
        box(p,xx,yy+t-7,t,3,"#8f795b")
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
