"""GhostPet's offline top-down pixel house, built entirely with Qt painting."""
from __future__ import annotations

import random
import time
from collections import deque

from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QColor, QFont, QPainter, QPen
try:
    from cottage_art import pixel_cottage, cottage_item
except ModuleNotFoundError as exc:
    if exc.name != "cottage_art":
        raise
    # Fallback for upgrading directly from the older v0.5.4 installer.
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

try:
    from pet_presence import current_pet
except ModuleNotFoundError as exc:
    if exc.name != "pet_presence":
        raise
    def current_pet(state):
        if state.desktop_pet_id == "founder" and state.location == "desktop":
            return None
        if state.desktop_pet_id != "none":
            return next((p for p in (state.adopted_pets or [])
                         if p.get("id")==state.desktop_pet_id and
                         p.get("location","house")=="desktop"), False)
        return False
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QHBoxLayout, QLabel,
                               QPushButton, QProgressBar, QVBoxLayout, QWidget)

# Optional imports keep older v0.5.4 updater installations working.
try:
    from cottage_art import built_in_occupied
except ImportError:
    def built_in_occupied(layout):
        return set()

try:
    from adopted_sprites import draw_adopted_pet as draw_housemate_sprite
except ImportError:
    draw_housemate_sprite = None

try:
    from pet_presence import (FOUNDER, active_desktop_ids, sync_locations,
                              relationship_pairs, relationship_score,
                              strengthen_friendship, relationship_title, pet_name)
except ModuleNotFoundError as exc:
    if exc.name != "pet_presence":
        raise

    from itertools import combinations

    FOUNDER = "founder"
    NONE = "none"


    def find_adopted(state, pet_id):
        return next((p for p in (state.adopted_pets or [])
                     if isinstance(p, dict) and p.get("id") == pet_id), None)


    def valid_id(state, pet_id):
        return pet_id == FOUNDER or find_adopted(state, pet_id) is not None


    def active_desktop_ids(state):
        primary = getattr(state, "desktop_pet_id", NONE)
        companion = getattr(state, "desktop_companion_id", NONE)
        result = [primary] if primary != NONE and valid_id(state, primary) else []
        if companion != NONE and companion not in result and valid_id(state, companion):
            result.append(companion)
        return result


    def sync_locations(state):
        """Derive locations exclusively from the two saved desktop slots."""
        active = active_desktop_ids(state)
        state.location = "desktop" if FOUNDER in active else "house"
        for pet in (state.adopted_pets or []):
            if isinstance(pet, dict):
                pet["location"] = "desktop" if pet.get("id") in active else "house"
        return active


    def repair_presence(state):
        primary = getattr(state, "desktop_pet_id", FOUNDER)
        second = getattr(state, "desktop_companion_id", NONE)
        if primary != NONE and not valid_id(state, primary):
            primary = FOUNDER if state.location == "desktop" else NONE
        # Migrated pre-duo users who sent Founder indoors stay indoors.
        if primary == FOUNDER and state.location != "desktop" and second == NONE:
            primary = NONE
        if second == primary or second == NONE or not valid_id(state, second):
            second = NONE
        if primary == NONE and second != NONE:
            primary, second = second, NONE
        state.desktop_pet_id = primary
        state.desktop_companion_id = second
        sync_locations(state)
        if not isinstance(getattr(state, "relationships", None), dict):
            state.relationships = {}
        return primary


    def current_pet(state):
        """None means active Founder, False means no primary desktop pet."""
        primary = state.desktop_pet_id
        if primary == FOUNDER:
            return None
        return find_adopted(state, primary) if primary != NONE else False


    def bring_to_desktop(state, pet_id):
        """Make this pet primary; preserve the second pet when possible."""
        if not valid_id(state, pet_id):
            raise ValueError("That pet does not exist.")
        secondary = getattr(state, "desktop_companion_id", NONE)
        if pet_id == secondary:
            old = state.desktop_pet_id
            state.desktop_companion_id = old if old != pet_id else NONE
        elif pet_id == state.desktop_pet_id:
            pass
        else:
            # Keep an existing duo when switching lead to a newly chosen pet.
            state.desktop_companion_id = secondary if secondary != pet_id else NONE
        state.desktop_pet_id = pet_id
        sync_locations(state)
        return None if pet_id == FOUNDER else find_adopted(state, pet_id)


    def invite_companion(state, pet_id):
        """Invite one additional pet; never permit more than two active pets."""
        if not valid_id(state, pet_id):
            raise ValueError("That pet does not exist.")
        if state.desktop_pet_id == NONE:
            bring_to_desktop(state, pet_id)
            return False
        if pet_id == state.desktop_pet_id:
            return False
        state.desktop_companion_id = pet_id
        sync_locations(state)
        return True


    def send_companion_home(state):
        state.desktop_companion_id = NONE
        sync_locations(state)


    def send_desktop_pet_home(state):
        """Send the primary home and promote its buddy, if present."""
        old = state.desktop_pet_id
        state.desktop_pet_id = getattr(state, "desktop_companion_id", NONE)
        state.desktop_companion_id = NONE
        sync_locations(state)
        return old


    def all_pet_ids(state):
        return [FOUNDER] + [p["id"] for p in (state.adopted_pets or [])
                            if isinstance(p,dict) and isinstance(p.get("id"),str)]


    def pet_name(state, pet_id):
        if pet_id == FOUNDER:
            return state.name
        pet = find_adopted(state, pet_id)
        return pet.get("name", "Buddy") if pet else "Buddy"


    def friendship_key(a, b):
        if a == b or a == NONE or b == NONE:
            raise ValueError("Relationship needs two different pets.")
        return "|".join(sorted((a, b)))


    def relationship_pairs(state):
        return [(a,b) for a,b in combinations(all_pet_ids(state), 2)]


    def relationship_score(state, a, b):
        rel = getattr(state, "relationships", None)
        if not isinstance(rel, dict):
            state.relationships = {}
            rel = state.relationships
        return max(0, min(100, float(rel.get(friendship_key(a,b), 30))))


    def strengthen_friendship(state, a, b, points=1.0):
        key = friendship_key(a, b)
        state.relationships[key] = round(
            min(100.0, max(0.0, relationship_score(state,a,b) + points)), 2)
        return state.relationships[key]


    def advance_house_friendships(state, hours):
        """Friendship grows quietly while pets share a home, even if house is closed."""
        if hours <= 0:
            return
        indoors = [pid for pid in all_pet_ids(state)
                   if pid not in active_desktop_ids(state)]
        for a, b in combinations(indoors, 2):
            strengthen_friendship(state, a, b, min(hours, 24)*.24)


    def relationship_title(score):
        if score >= 85:
            return "Best buddies"
        if score >= 60:
            return "Good friends"
        if score >= 35:
            return "Getting closer"
        return "Acquaintances"


TILE = 32
W, H = 18, 12
ROOMS = ("Bedroom", "Living room", "Kitchen", "Playroom")
ITEMS = {
    "bed": ("Bed", 0, "#f2b9d8"),
    "toy": ("Teddy", 10, "#d8a66e"),
    "rug": ("Rug", 8, "#b6a5ea"),
    "plant": ("Plant", 12, "#7ac7a1"),
    "sofa": ("Sofa", 20, "#91b9e5"),
    "ball": ("Ball", 6, "#f6d280"),
    "bowl": ("Food bowl", 8, "#e6b07a"),
    "lamp": ("Lamp", 14, "#fff0b0"),
}


def walls():
    result = {(x, 0) for x in range(W)} | {(x, H - 1) for x in range(W)}
    result |= {(0, y) for y in range(H)} | {(W - 1, y) for y in range(H)}
    result |= {(8, y) for y in range(1, H - 1) if y not in (3, 4, 8)}
    result |= {(x, 6) for x in range(1, W - 1) if x not in (3, 4, 12, 13)}
    return result


WALLS = walls()
LAYOUTS = {
    "cottage": ("Woodland Cottage", 0),
    "open": ("Open Plan Cottage", 120),
    "garden": ("Sunny Garden Cottage", 260),
}


def walls_for_layout(layout):
    """Truly different plans within the same exterior footprint.

    Woodland has four fully partitioned rooms. Open Plan has one secluded
    bedroom nook and a connected kitchen/lounge. Sunny Garden is a mostly
    uninterrupted conservatory with only a few structural glasshouse posts.
    Existing pets and placed furniture are reflowed on a layout switch.
    """
    exterior = {(x,0) for x in range(W)} | {(x,H-1) for x in range(W)}
    exterior |= {(0,y) for y in range(H)} | {(W-1,y) for y in range(H)}
    if layout == "open":
        # Small private sleeping nook upper-left. Everything else is open.
        partition = {(6,y) for y in (1,2,4,5)}
        partition |= {(x,5) for x in (1,2,3,5,6)}
        return exterior | partition
    if layout == "garden":
        # Atrium posts, not the old cottage's interior walls.
        return exterior | {(12,1),(12,2),(12,9),(12,10)}
    return set(WALLS)


def path_between(start, goal, blocked=frozenset(), wall_tiles=None):
    """Four-directional shortest walk; returns [] if the target cannot be reached."""
    wall_tiles = WALLS if wall_tiles is None else wall_tiles
    if goal in wall_tiles or goal in blocked or not (0 <= goal[0] < W and 0 <= goal[1] < H):
        return []
    frontier = deque([start])
    previous = {start: None}
    while frontier:
        current = frontier.popleft()
        if current == goal:
            result = []
            while current != start:
                result.append(current)
                current = previous[current]
            return list(reversed(result))
        for delta in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            next_tile = (current[0] + delta[0], current[1] + delta[1])
            if (0 <= next_tile[0] < W and 0 <= next_tile[1] < H
                    and next_tile not in wall_tiles and next_tile not in blocked
                    and next_tile not in previous):
                previous[next_tile] = current
                frontier.append(next_tile)
    return []


class HouseCanvas(QWidget):
    def __init__(self, dialog):
        super().__init__(dialog)
        self.dialog = dialog
        # Fit the actual available Zorin screen, including taskbar and fractional
        # desktop scaling. Rendering and mouse hit testing share one zoom factor.
        geometry = QApplication.primaryScreen().availableGeometry()
        max_width = max(220, geometry.width() - 110)
        max_height = max(170, geometry.height() - 280)
        self.zoom = min(1.0, max_width / (W * TILE), max_height / (H * TILE))
        self.setFixedSize(round(W * TILE * self.zoom), round(H * TILE * self.zoom))
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        x = int(event.position().x() / (TILE * self.zoom))
        y = int(event.position().y() / (TILE * self.zoom))
        if event.button() == Qt.MouseButton.RightButton:
            self.dialog.remove_item((x, y))
        elif event.button() == Qt.MouseButton.LeftButton:
            self.dialog.tile_clicked((x, y))

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        p.scale(self.zoom, self.zoom)
        self.draw_floor(p)
        for entry in self.dialog.state.furniture:
            pos = self.dialog.entry_tile(entry)
            if pos and pos not in self.dialog.wall_tiles():
                self.draw_furniture(p, pos[0] * TILE, pos[1] * TILE, entry.get("item"))
        # desktop_pet_id is authoritative. Saved household dictionaries can
        # retain an old "house" field; never draw the active desktop pet twice.
        active_ids = set(active_desktop_ids(self.dialog.state))
        if (FOUNDER not in active_ids and self.dialog.state.egg_hatched):
            self.draw_pet(p)
        for housemate in self.dialog.state.adopted_pets or []:
            if housemate.get("id") not in active_ids:
                self.draw_housemate(p, housemate)
        if self.dialog.friend_heart_until > time.monotonic():
            p.setPen(QColor("#e77896"))
            p.setFont(QFont("Sans",16,QFont.Weight.Bold))
            p.drawText(270,195,"♥")
        if self.dialog.mode == "Decorate":
            p.setPen(QPen(QColor("#bdb1e0"), 1, Qt.PenStyle.DotLine))
            for x in range(1, W - 1):
                for y in range(1, H - 1):
                    if (x, y) not in self.dialog.wall_tiles():
                        p.drawRect(x * TILE, y * TILE, TILE, TILE)
        p.end()

    def draw_floor(self, p):
        # Beautiful original painter-based cottage art, independent from navigation.
        pixel_cottage(p, self.dialog.state.house_layout, self.dialog.wall_tiles())

    def draw_furniture(self, p, px, py, item):
        if item in ITEMS:
            cottage_item(p, px, py, item, ITEMS[item][2])

    def draw_housemate(self, p, pet):
        """Small, species-specific pixel silhouettes for nursery pets."""
        x = max(1, min(W-2, int(pet.get("x", 12))))
        y = max(1, min(H-2, int(pet.get("y", 8))))
        px, py = x*TILE+4, y*TILE+4
        species = pet.get("species","Ghost")
        if species == "Cat" and draw_housemate_sprite is not None:
            p.save()
            p.translate(x*TILE, y*TILE)
            draw_housemate_sprite(p, TILE, TILE, pet, 1, scale=1)
            p.restore()
            return
        tint = QColor({"Ghost":"#dfd5ff","Cat":"#f0bd81","Dog":"#bb9a77",
                       "Bunny":"#f4e9e0","Fox":"#ea945b","Dragon":"#81cc9b"}.get(species,"#dfd5ff"))
        dark = QColor("#303047")
        p.fillRect(px+4,py+7,18,16,dark)
        p.fillRect(px+6,py+8,14,14,tint)
        p.fillRect(px+4,py+13,18,8,tint)
        if species == "Ghost":
            p.fillRect(px+3,py+20,6,4,tint)
            p.fillRect(px+17,py+20,6,4,tint)
        elif species == "Bunny":
            p.fillRect(px+6,py-4,5,14,tint)
            p.fillRect(px+17,py-4,5,14,tint)
        elif species in ("Cat","Fox"):
            p.fillRect(px+5,py+3,6,7,tint)
            p.fillRect(px+17,py+3,6,7,tint)
            if species == "Fox":
                p.fillRect(px+22,py+17,6,4,tint)
        elif species == "Dog":
            p.fillRect(px+3,py+8,4,8,dark)
            p.fillRect(px+21,py+8,4,8,dark)
        elif species == "Dragon":
            p.fillRect(px+1,py+12,6,9,QColor("#548c72"))
            p.fillRect(px+21,py+12,6,9,QColor("#548c72"))
            p.fillRect(px+11,py+2,5,7,tint)
        p.fillRect(px+9,py+12,3,4,dark)
        p.fillRect(px+17,py+12,3,4,dark)

    def draw_pet(self, p):
        """Miniature indoor version of the approved small Founder mouse."""
        x,y = self.dialog.position
        px,py = x*TILE+2,y*TILE+2
        tint = QColor("#b8e7ce") if self.dialog.state.color=="Mint" else (
            QColor("#d5bbef") if self.dialog.state.color=="Lilac" else QColor("#eac29d"))
        outline = QColor("#485449")
        blush = QColor("#e8afbc")
        cream = QColor("#fff3db")
        # Small thin tail and round ears; no large side limbs.
        p.fillRect(px+23,py+16,5,3,outline)
        p.fillRect(px+26,py+12,3,5,tint)
        p.fillRect(px+5,py+3,8,8,outline)
        p.fillRect(px+18,py+3,8,8,outline)
        p.fillRect(px+7,py+5,4,4,blush)
        p.fillRect(px+20,py+5,4,4,blush)
        p.fillRect(px+6,py+11,20,15,outline)
        p.fillRect(px+8,py+10,16,15,tint)
        p.fillRect(px+10,py+22,12,4,cream)
        p.fillRect(px+8,py+25,5,3,outline)
        p.fillRect(px+19,py+25,5,3,outline)
        p.fillRect(px+10,py+14,3,4,outline)
        p.fillRect(px+19,py+14,3,4,outline)
        p.fillRect(px+9,py+20,3,2,blush)
        p.fillRect(px+21,py+20,3,2,blush)
        p.fillRect(px+16,py+20,2,2,outline)
        if self.dialog.activity:
            p.setPen(QColor("#e77b98"))
            p.setFont(QFont("Sans",10,QFont.Weight.Bold))
            p.drawText(px+7,py-2,"♥")


class HouseDialog(QDialog):
    def __init__(self, state, save, return_home, send_home, parent=None):
        super().__init__(parent)
        self.state = state
        self.save = save
        self.return_home = return_home
        self.send_home = send_home
        self.mode = "Explore"
        self.position = (state.house_pet_x, state.house_pet_y)
        if self.position in self.wall_tiles() or not (0 <= self.position[0] < W and 0 <= self.position[1] < H):
            self.position = (2, 3)
        self.path = []
        self.activity = ""
        self.idle_ticks = 0
        self.friend_heart_until = 0.0
        self.last_house_bond = 0.0
        if not self.state.housewarming_granted:
            self.state.coins = max(200, self.state.coins)
            self.state.housewarming_granted = True
            self.save()
        self._migrate_old_room()
        # Relocate housemates away from newly furnished cells without losing them.
        old_position = self.position
        self.position = self.safe_position(self.position, self.wall_tiles())
        if self.state.location == "house":
            self.state.house_pet_x, self.state.house_pet_y = self.position
        changed = self.position != old_position
        for housemate in self.state.adopted_pets or []:
            if housemate.get("location", "house") != "house":
                continue
            old = (int(housemate.get("x",12)), int(housemate.get("y",8)))
            adjusted = self.safe_position(old, self.wall_tiles())
            if adjusted != old:
                housemate["x"], housemate["y"] = adjusted
                changed = True
        if changed:
            self.save()
        self.setWindowTitle(f"GhostPet • {LAYOUTS[self.state.house_layout][0]} • v0.7.0")
        self.setStyleSheet("""QDialog{background:#f1e4d2;color:#443e31}
QLabel{color:#443e31;font-size:13px}
QPushButton,QComboBox{background:#759278;color:white;border:1px solid #55735b;
border-radius:6px;padding:8px} QPushButton:hover{background:#5f8268}""")
        body = QVBoxLayout(self)
        bar = QHBoxLayout()
        self.mode_button = QPushButton("✦ Explore mode")
        self.mode_button.clicked.connect(self.toggle_mode)
        bar.addWidget(self.mode_button)
        self.selector = QComboBox()
        self.selector.addItems([f"{label} • {cost} coins" for label, cost, _ in ITEMS.values()])
        self.selector.setEnabled(False)
        bar.addWidget(self.selector)
        self.balance = QLabel()
        bar.addWidget(self.balance)
        self.door_button = QPushButton()
        self.door_button.clicked.connect(self.travel)
        bar.addWidget(self.door_button)
        body.addLayout(bar)
        layout_row = QHBoxLayout()
        layout_row.addWidget(QLabel("Cottage floor plan:"))
        self.layout_selector = QComboBox()
        for key, (label, price) in LAYOUTS.items():
            suffix = " • owned" if key in self.state.unlocked_house_layouts else f" • {price} coins"
            self.layout_selector.addItem(label + suffix, key)
        self.layout_selector.setCurrentIndex(list(LAYOUTS).index(self.state.house_layout))
        self.layout_selector.currentIndexChanged.connect(self.update_layout_button)
        layout_row.addWidget(self.layout_selector)
        self.layout_button = QPushButton("Use layout")
        self.layout_button.clicked.connect(self.choose_layout)
        layout_row.addWidget(self.layout_button)
        body.addLayout(layout_row)
        # Keep warnings and unlock confirmations above the drawing. On laptops,
        # an inaccessible bottom label made a working unlock look unresponsive.
        self.status = QLabel("Select a cottage layout and click Unlock to upgrade.")
        self.status.setWordWrap(True)
        self.status.setMinimumHeight(24)
        body.addWidget(self.status)
        friend_row = QHBoxLayout()
        friend_row.addWidget(QLabel("♡ Pet friendships:"))
        self.friend_selector = QComboBox()
        self.friend_selector.currentIndexChanged.connect(self.update_friendship)
        friend_row.addWidget(self.friend_selector,1)
        self.friend_bar = QProgressBar()
        self.friend_bar.setRange(0,100)
        self.friend_bar.setMaximumWidth(132)
        friend_row.addWidget(self.friend_bar)
        body.addLayout(friend_row)
        self.friend_status = QLabel("Friendships grow while pets share the house.")
        body.addWidget(self.friend_status)
        self.preview_button = QPushButton("🎁 Claim 600 preview coins")
        self.preview_button.setToolTip("One-time test reward to try both house upgrades and furniture")
        self.preview_button.clicked.connect(self.claim_preview_coins)
        body.addWidget(self.preview_button)
        self.canvas = HouseCanvas(self)
        body.addWidget(self.canvas)
        self.tick_timer = QTimer(self)
        self.tick_timer.timeout.connect(self.tick)
        self.tick_timer.start(260)
        self.refresh()

    def claim_preview_coins(self):
        """One-time preview gift; no save-file editing or repeat farming."""
        if self.state.preview_coins_claimed:
            return
        self.state.coins += 600
        self.state.preview_coins_claimed = True
        self.save()
        self.status.setText("🎁 600 coins added for preview testing. Enjoy your cottage upgrades!")
        self.refresh()

    def wall_tiles(self):
        return walls_for_layout(self.state.house_layout)

    def update_layout_button(self, _index=None):
        key = self.layout_selector.currentData()
        if key == self.state.house_layout:
            text = "✓ Current layout"
            enabled = False
        elif key in self.state.unlocked_house_layouts:
            text = "Switch layout"
            enabled = True
        else:
            text = f"Unlock • {LAYOUTS[key][1]} coins"
            enabled = True
        self.layout_button.setText(text)
        self.layout_button.setEnabled(enabled)

    def choose_layout(self):
        """Unlock and switch plans without altering the pet or furniture inventory."""
        key = self.layout_selector.currentData()
        if key not in LAYOUTS or key == self.state.house_layout:
            return
        new_walls = walls_for_layout(key)
        # Floor plans really rearrange partitions now. Preserve every purchased
        # furnishing and move only pieces that collide with new built-ins/walls.
        reserved = set(new_walls) | set(built_in_occupied(key))
        furniture_cells = set()
        moves = []
        for entry in self.state.furniture:
            old_tile = self.entry_tile(entry)
            if old_tile is None:
                continue  # Keep any legacy/unknown furniture entry intact.
            ok = (1 <= old_tile[0] < W-1 and 1 <= old_tile[1] < H-1
                  and old_tile not in reserved and old_tile not in furniture_cells)
            if ok:
                target = old_tile
            else:
                candidates = [(x,y) for y in range(1,H-1)
                              for x in range(1,W-1)
                              if (x,y) not in reserved
                              and (x,y) not in furniture_cells]
                if not candidates:
                    self.status.setText("No free tile for all your furniture in this plan.")
                    return
                target = min(candidates, key=lambda cell:
                             abs(cell[0]-old_tile[0])+abs(cell[1]-old_tile[1]))
            furniture_cells.add(target)
            moves.append((entry,target))
        if key not in self.state.unlocked_house_layouts:
            if key == "garden" and "open" not in self.state.unlocked_house_layouts:
                self.status.setText("Unlock the Open Plan Cottage first.")
                return
            cost = LAYOUTS[key][1]
            if self.state.coins < cost:
                self.status.setText(f"Need {cost} coins to unlock this floor plan!")
                return
            self.state.coins -= cost
            self.state.unlocked_house_layouts.append(key)
        self.state.house_layout = key
        relocated = 0
        for entry, target in moves:
            if self.entry_tile(entry) != target:
                relocated += 1
                entry["cell"] = target[1]*W + target[0]
        self.setWindowTitle(f"GhostPet • {LAYOUTS[key][0]} • v0.7.0")
        self.position = self.safe_position(self.position, new_walls)
        self.state.house_pet_x, self.state.house_pet_y = self.position
        for pet in self.state.adopted_pets or []:
            target = self.safe_position((int(pet.get("x",12)), int(pet.get("y",8))), new_walls)
            pet["x"], pet["y"] = target
        self.path = []
        self.idle_ticks = 10
        self.save()
        self.layout_selector.blockSignals(True)
        self.layout_selector.clear()
        for item_key, (label, price) in LAYOUTS.items():
            suffix = " • owned" if item_key in self.state.unlocked_house_layouts else f" • {price} coins"
            self.layout_selector.addItem(label + suffix, item_key)
        self.layout_selector.setCurrentIndex(list(LAYOUTS).index(key))
        self.layout_selector.blockSignals(False)
        self.status.setText(
            f"Welcome to your {LAYOUTS[key][0]}! "
            + (f"Safely rearranged {relocated} furniture piece(s)." if relocated else
               "Your furniture and pets are safe."))
        self.refresh()

    def safe_position(self, tile, new_walls):
        occupied = self.blocked()
        if (0 < tile[0] < W-1 and 0 < tile[1] < H-1
                and tile not in new_walls and tile not in occupied):
            return tile
        possible = [(x, y) for y in range(1, H-1) for x in range(1, W-1)
                    if (x,y) not in new_walls and (x,y) not in occupied]
        return min(possible, key=lambda cell: abs(cell[0]-tile[0])+abs(cell[1]-tile[1])) if possible else (2,3)

    def travel(self):
        # Only one household member can walk on the desktop at a time.
        if current_pet(self.state) is False:
            self.return_home()
        else:
            self.send_home()
        self.refresh()

    def entry_tile(self, entry):
        cell = entry.get("cell") if isinstance(entry, dict) else None
        if not isinstance(cell, int):
            return None
        return (cell % W, cell // W)

    def _migrate_old_room(self):
        # Old editor had 6 columns and 5 rows; relocate them into Bedroom.
        if getattr(self.state, "house_version", 1) >= 2:
            return
        migrated = []
        for entry in self.state.furniture:
            if isinstance(entry, dict) and isinstance(entry.get("cell"), int):
                old_cell = entry["cell"]
                x, y = 1 + old_cell % 6, 1 + old_cell // 6
                if (x, y) in WALLS or (x, y) == (2, 3):
                    continue
                migrated.append({"cell": y * W + x, "item": entry.get("item")})
        self.state.furniture = migrated
        self.state.house_version = 2
        self.save()

    def blocked(self):
        # Furniture and built-in large furnishings block the hidden movement grid.
        owned = {tile for entry in self.state.furniture
                 if entry.get("item") != "rug"
                 for tile in [self.entry_tile(entry)] if tile is not None}
        return owned | built_in_occupied(self.state.house_layout)

    def update_friendship(self, _index=None):
        ids = self.friend_selector.currentData()
        if ids and len(ids)==2:
            score = relationship_score(self.state, *ids)
            self.friend_bar.setValue(round(score))
            self.friend_status.setText(
                f"♡ {relationship_title(score)} • {round(score)}/100"
                " — also grows when they're indoors together")
        else:
            self.friend_bar.setValue(0)
            self.friend_status.setText("Adopt a second pet to see their friendship.")

    def refresh(self):
        # One authoritative two-slot roster, regardless of stale saved flags.
        sync_locations(self.state)
        self.balance.setText(f"🪙 {self.state.coins}")
        previous = self.friend_selector.currentData()
        pairs = relationship_pairs(self.state)
        self.friend_selector.blockSignals(True)
        self.friend_selector.clear()
        for a,b in pairs:
            self.friend_selector.addItem(
                f"{pet_name(self.state,a)} + {pet_name(self.state,b)}", (a,b))
        if previous in pairs:
            self.friend_selector.setCurrentIndex(pairs.index(previous))
        self.friend_selector.blockSignals(False)
        self.friend_selector.setEnabled(bool(pairs))
        self.update_friendship()
        self.preview_button.setVisible(not self.state.preview_coins_claimed)
        self.door_button.setText("↗ Bring selected pet outside" if current_pet(self.state) is False
                                else "⌂ Send desktop pet home")
        self.update_layout_button()
        self.canvas.update()

    def toggle_mode(self):
        self.mode = "Decorate" if self.mode == "Explore" else "Explore"
        self.mode_button.setText("⌂ Decorate mode" if self.mode == "Decorate" else "✦ Explore mode")
        self.selector.setEnabled(self.mode == "Decorate")
        self.status.setText("Choose an item, then click a floor tile. Right-click to store."
                            if self.mode == "Decorate" else
                            "Click any reachable floor tile; your pet will walk there!")
        self.canvas.update()

    def tile_clicked(self, tile):
        if tile in self.wall_tiles() or not (0 <= tile[0] < W and 0 <= tile[1] < H):
            self.status.setText("That's a wall. Try the floor or a doorway.")
            return
        if self.mode == "Decorate":
            self.place_item(tile)
            return
        route = path_between(self.position, tile, self.blocked(), self.wall_tiles())
        if route or tile == self.position:
            self.path = route
            self.idle_ticks = 25
            self.status.setText("On my way! 👻")
        else:
            self.status.setText("That tile is blocked; try another destination.")

    def place_item(self, tile):
        if tile in built_in_occupied(self.state.house_layout):
            self.status.setText("That spot has built-in cottage furniture. Pick an open tile!")
            return
        if tile == self.position:
            self.status.setText("Let your pet move aside first!")
            return
        key = list(ITEMS)[self.selector.currentIndex()]
        current = next((e for e in self.state.furniture if self.entry_tile(e) == tile), None)
        if current:
            self.state.furniture.remove(current)
        if key not in self.state.owned_furniture:
            cost = ITEMS[key][1]
            if self.state.coins < cost:
                if current:
                    self.state.furniture.append(current)
                self.status.setText("Not enough coins. Play a minigame to earn more!")
                return
            self.state.coins -= cost
            self.state.owned_furniture.append(key)
        self.state.furniture.append({"cell": tile[1] * W + tile[0], "item": key})
        self.path = []
        self.save()
        self.status.setText(f"Placed {ITEMS[key][0]}! Unlocked items are free to rearrange.")
        self.refresh()

    def remove_item(self, tile):
        if self.mode != "Decorate":
            return
        before = len(self.state.furniture)
        self.state.furniture = [e for e in self.state.furniture if self.entry_tile(e) != tile]
        if len(self.state.furniture) < before:
            self.save()
            self.status.setText("Furniture stored! Its unlock stays yours.")
            self.refresh()

    def tick(self):
        if self.mode != "Explore":
            return
        # Housemates keep exploring even when the founder is outside.
        occupied = self.blocked()
        indoors = [pid for pid in [FOUNDER]+
                   [p.get("id") for p in (self.state.adopted_pets or [])]
                   if pid not in active_desktop_ids(self.state)]
        if len(indoors) >= 2 and time.monotonic() - self.last_house_bond > 14:
            positions = {FOUNDER:self.position}
            positions.update({p.get("id"):(int(p.get("x",12)),int(p.get("y",8)))
                              for p in (self.state.adopted_pets or [])
                              if isinstance(p,dict)})
            close = [(a,b) for i,a in enumerate(indoors)
                     for b in indoors[i+1:]
                     if a in positions and b in positions and
                     abs(positions[a][0]-positions[b][0])+
                     abs(positions[a][1]-positions[b][1])<=3]
            if close and random.random() < .12:
                a,b = random.choice(close)
                strengthen_friendship(self.state, a, b, .8)
                self.last_house_bond = time.monotonic()
                self.friend_heart_until = time.monotonic() + 2.5
                self.save()
                self.update_friendship()
        for pet in self.state.adopted_pets or []:
            if pet.get("location", "house") == "house" and random.random() < .18:
                x, y = int(pet.get("x",12)), int(pet.get("y",8))
                options = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
                options = [(a,b) for a,b in options if 0<a<W-1 and 0<b<H-1
                           and (a,b) not in self.wall_tiles() and (a,b) not in occupied]
                if options:
                    pet["x"], pet["y"] = random.choice(options)
        if self.state.location != "house":
            self.canvas.update()
            return
        if self.path:
            self.position = self.path.pop(0)
            self.state.house_pet_x, self.state.house_pet_y = self.position
            self.activity = "walking"
        elif self.idle_ticks > 0:
            self.idle_ticks -= 1
            self.activity = ""
        elif random.random() < .12:
            possible = [(x, y) for x in range(1, W-1) for y in range(1, H-1)
                        if (x, y) not in self.wall_tiles() and (x, y) not in self.blocked()]
            target = random.choice(possible)
            self.path = path_between(self.position, target, self.blocked(), self.wall_tiles())
            self.idle_ticks = 7
            self.activity = "exploring"
        else:
            self.activity = ""
        if random.random() < .007:
            if self.position[1] > 6:
                self.state.happiness = min(100, self.state.happiness + .4)
            else:
                self.state.energy = min(100, self.state.energy + .25)
            self.save()
        self.canvas.update()

    def closeEvent(self, event):
        self.state.house_pet_x, self.state.house_pet_y = self.position
        self.save()
        super().closeEvent(event)
