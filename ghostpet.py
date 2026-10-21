#!/usr/bin/env python3
"""GhostPet: a tiny offline pixel pet for Linux desktops.

Requires PySide6. Designed for GNOME/X11 (or XWayland) on Zorin OS.
"""

from __future__ import annotations

import fcntl
import json
import math
import os
import random
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, fields
from pathlib import Path

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QCursor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from activities import GameDialog, pick_speech
from house import HouseDialog, house_feed_cycle
from nursery import NurseryDialog
# v0.5.4 updater did not know about additional Python modules. Each module
# has a fallback so an old one-click updater can still launch v0.6 safely.
try:
    from pet_presence import (FOUNDER, NONE, bring_to_desktop, current_pet,
                              find_adopted, repair_presence, send_desktop_pet_home,
                              active_desktop_ids, sync_locations, invite_companion,
                              send_companion_home, relationship_pairs,
                              relationship_score, strengthen_friendship,
                              advance_house_friendships, relationship_title,
                              pet_name)
except ModuleNotFoundError as exc:
    if exc.name != "pet_presence":
        raise
    FOUNDER = "founder"
    NONE = "none"


    def find_adopted(state, pet_id):
        return next(
            (pet for pet in (state.adopted_pets or [])
             if isinstance(pet, dict) and pet.get("id") == pet_id),
            None,
        )


    def repair_presence(state):
        """Migrate saved households without changing names, stats, positions or coins."""
        current = getattr(state, "desktop_pet_id", FOUNDER)
        if current not in (FOUNDER, NONE) and find_adopted(state, current) is None:
            current = FOUNDER if state.location == "desktop" else NONE
        if current == FOUNDER and state.location != "desktop":
            current = NONE  # Founder deliberately indoors on an old save.
        if current not in (FOUNDER, NONE):
            state.location = "house"
        for pet in state.adopted_pets or []:
            pet["location"] = ("desktop" if pet.get("id") == current else "house")
        state.desktop_pet_id = current
        return current


    def current_pet(state):
        """Return None for the founder, a housemate dict, or False for an empty desktop."""
        pet_id = state.desktop_pet_id
        if pet_id == FOUNDER:
            return None if state.location == "desktop" else False
        if pet_id == NONE:
            return False
        pet = find_adopted(state, pet_id)
        return pet if pet is not None and pet.get("location") == "desktop" else False


    def bring_to_desktop(state, pet_id):
        """Summon a pet, returning its associated record (None means Founder)."""
        if pet_id != FOUNDER and find_adopted(state, pet_id) is None:
            raise ValueError("That pet no longer exists in your nursery.")
        state.location = "desktop" if pet_id == FOUNDER else "house"
        for pet in state.adopted_pets or []:
            pet["location"] = "desktop" if pet.get("id") == pet_id else "house"
        state.desktop_pet_id = pet_id
        return None if pet_id == FOUNDER else find_adopted(state, pet_id)


    def send_desktop_pet_home(state):
        """Send only the displayed pet indoors; the founder save stays untouched."""
        pet_id = state.desktop_pet_id
        if pet_id == FOUNDER:
            state.location = "house"
        else:
            selected = find_adopted(state, pet_id)
            if selected is not None:
                selected["location"] = "house"
        state.desktop_pet_id = NONE
        return pet_id

    # Compatibility for upgrading straight from the old 0.5.x launchers.
    from itertools import combinations

    def active_desktop_ids(state):
        first = getattr(state, "desktop_pet_id", NONE)
        second = getattr(state, "desktop_companion_id", NONE)
        return [p for p in (first, second) if p != NONE and
                (p == FOUNDER or find_adopted(state,p) is not None)]

    def sync_locations(state):
        active = active_desktop_ids(state)
        state.location = "desktop" if FOUNDER in active else "house"
        for p in (state.adopted_pets or []):
            p["location"] = "desktop" if p.get("id") in active else "house"
        return active

    def invite_companion(state, pet_id):
        if pet_id != FOUNDER and not find_adopted(state,pet_id):
            raise ValueError("Unknown companion.")
        if state.desktop_pet_id == NONE:
            bring_to_desktop(state,pet_id)
            return False
        if pet_id == state.desktop_pet_id:
            return False
        state.desktop_companion_id = pet_id
        sync_locations(state)
        return True

    def send_companion_home(state):
        state.desktop_companion_id = NONE
        sync_locations(state)

    def repair_presence(state):
        first = getattr(state,"desktop_pet_id", FOUNDER)
        second = getattr(state,"desktop_companion_id", NONE)
        if first != NONE and first != FOUNDER and not find_adopted(state,first):
            first = FOUNDER if state.location == "desktop" else NONE
        if first == FOUNDER and state.location != "desktop" and second == NONE:
            first = NONE
        if second == first or (second != NONE and second != FOUNDER and
                              not find_adopted(state,second)):
            second = NONE
        state.desktop_pet_id = first
        state.desktop_companion_id = second
        if not isinstance(getattr(state,"relationships",None), dict):
            state.relationships = {}
        sync_locations(state)
        return first

    def bring_to_desktop(state, pet_id):
        if pet_id != FOUNDER and not find_adopted(state,pet_id):
            raise ValueError("Unknown companion.")
        if pet_id == state.desktop_companion_id:
            state.desktop_companion_id = state.desktop_pet_id
        state.desktop_pet_id = pet_id
        sync_locations(state)
        return None if pet_id == FOUNDER else find_adopted(state,pet_id)

    def send_desktop_pet_home(state):
        old = state.desktop_pet_id
        state.desktop_pet_id = state.desktop_companion_id
        state.desktop_companion_id = NONE
        sync_locations(state)
        return old

    def pet_name(state, pet_id):
        p = find_adopted(state,pet_id)
        return state.name if pet_id == FOUNDER else (p.get("name","Buddy") if p else "Buddy")

    def relationship_pairs(state):
        ids = [FOUNDER]+[p.get("id") for p in state.adopted_pets or []]
        return list(combinations(ids,2))

    def _pair_key(a,b):
        if a==b:
            raise ValueError("Two different pets required.")
        return "|".join(sorted((a,b)))

    def relationship_score(state,a,b):
        rel = state.relationships if isinstance(state.relationships,dict) else {}
        return max(0,min(100,float(rel.get(_pair_key(a,b),30))))

    def strengthen_friendship(state,a,b,points=1.0):
        if not isinstance(state.relationships,dict):
            state.relationships = {}
        score = round(min(100,relationship_score(state,a,b)+points),2)
        state.relationships[_pair_key(a,b)] = score
        return score

    def advance_house_friendships(state,hours):
        indoors = [p for p in [FOUNDER]+[x.get("id") for x in state.adopted_pets or []]
                   if p not in active_desktop_ids(state)]
        for a,b in combinations(indoors,2):
            strengthen_friendship(state,a,b,min(max(hours,0),24)*.24)

    def relationship_title(score):
        return ("Best buddies" if score>=85 else "Good friends" if score>=60 else
                "Getting closer" if score>=35 else "Acquaintances")

try:
    from adopted_sprites import draw_adopted_pet
except ModuleNotFoundError as exc:
    if exc.name != "adopted_sprites":
        raise
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

APP_NAME = "GhostPet"
DATA_DIR = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "ghostpet"
STATE_FILE = DATA_DIR / "state.json"

PALETTES = {
    "Mint": ("#9df0d4", "#49bea6", "#f7a6bc"),
    "Lilac": ("#d8b8ff", "#a986df", "#ff9fc4"),
    "Ember": ("#ffca8c", "#ef8c76", "#ff92a8"),
}
SPECIES = ("Ghost", "Cat", "Dog", "Bunny", "Fox", "Dragon")


def clamp(value: float, minimum: float = 0, maximum: float = 100) -> float:
    return max(minimum, min(maximum, value))


CURSOR_GAP = 30  # The pointer remains outside the pet window, not underneath it.
CURSOR_CHASE_SECONDS = 8.0
CURSOR_CHASE_COOLDOWN = 75.0


def cursor_chase_destination(window, cursor, screen, gap=CURSOR_GAP):
    """Return a safe window top-left that does not cover the mouse pointer.

    Prefer the pet's existing side of the pointer. If that side would move
    the pet off-screen, choose the opposite side. Stop if neither fits.
    This helper never moves the cursor or injects mouse events.
    """
    left = cursor.x() - window.width() - gap
    right = cursor.x() + gap
    x_min = screen.left()
    x_max = screen.right() - window.width() + 1
    if x_max < x_min:
        return None
    options = [x for x in (left, right) if x_min <= x <= x_max]
    if not options:
        return None
    x = min(options, key=lambda p: abs(p - window.x()))
    y = max(screen.top(), min(cursor.y() - window.height() // 2,
                              screen.bottom() - window.height() + 1))
    return QPoint(int(x), int(y))


@dataclass
class PetState:
    name: str = "Byte"
    hunger: float = 88
    happiness: float = 82
    cleanliness: float = 95
    energy: float = 87
    born: float = 0.0
    last_updated: float = 0.0
    games_played: int = 0
    times_fed: int = 0
    sleeping: bool = False
    roaming: bool = True
    color: str = "Mint"
    x: int = -1
    y: int = -1
    affection: float = 30
    playfulness: int = 0
    curiosity: int = 0
    gentleness: int = 0
    mischief: int = 0
    cuddles: int = 0
    words_learned: int = 0
    coins: int = 200
    furniture: list | None = None
    owned_furniture: list | None = None
    house_version: int = 1
    housewarming_granted: bool = False
    species: str = "Ghost"
    egg_hatched: bool = False
    hatch_taps: int = 0
    location: str = "desktop"
    portal_x: int = -1
    portal_y: int = -1
    house_pet_x: int = 2
    house_pet_y: int = 3
    founder: bool = False
    adopted_pets: list | None = None
    nursery_egg_taps: int = -1
    house_layout: str = "cottage"
    unlocked_house_layouts: list | None = None
    desktop_pet_id: str = "founder"
    desktop_companion_id: str = "none"
    relationships: dict | None = None
    preview_coins_claimed: bool = False
    last_bowl_meal: float = 0.0
    auto_social: bool = True
    auto_cursor_chase: bool = True

    @classmethod
    def load(cls) -> "PetState":
        now = time.time()
        allowed = {f.name for f in fields(cls)}
        try:
            values = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            state = cls(**{key: value for key, value in values.items() if key in allowed})
            if "egg_hatched" not in values:
                state.egg_hatched = True  # Existing companions stay hatched.
            if "founder" not in values:
                state.founder = True  # Migrated original pet: never replaced.
        except (OSError, ValueError, TypeError):
            state = cls()
        if state.born <= 0:
            state.born = now
        if state.last_updated <= 0:
            state.last_updated = now
        if state.color not in PALETTES:
            state.color = "Mint"
        if state.species not in SPECIES:
            state.species = "Ghost"
        if state.location not in ("desktop", "house"):
            state.location = "desktop"
        state.name = str(state.name)[:18] or "Byte"
        for stat in ("hunger", "happiness", "cleanliness", "energy"):
            setattr(state, stat, clamp(float(getattr(state, stat))))
        state.affection = clamp(float(state.affection))
        state.adopted_pets = state.adopted_pets if isinstance(state.adopted_pets, list) else []
        repair_presence(state)
        state.nursery_egg_taps = int(state.nursery_egg_taps) if isinstance(state.nursery_egg_taps, int) else -1
        # v0.5.2 layout progress is independent of the original pet and furniture.
        valid_layouts = ("cottage", "open", "garden")
        unlocked = state.unlocked_house_layouts if isinstance(state.unlocked_house_layouts, list) else []
        state.unlocked_house_layouts = ["cottage"] + [key for key in valid_layouts[1:] if key in unlocked]
        if state.house_layout not in state.unlocked_house_layouts:
            state.house_layout = "cottage"
        state.furniture = state.furniture if isinstance(state.furniture, list) else []
        state.owned_furniture = (state.owned_furniture if isinstance(state.owned_furniture, list)
                                 else ["bed"])
        state.advance(now)
        return state

    def advance(self, now: float | None = None) -> None:
        now = now or time.time()
        elapsed_hours = min(max(0.0, now - self.last_updated), 24 * 7) / 3600.0
        self.last_updated = now
        if self.sleeping:
            self.energy = clamp(self.energy + elapsed_hours * 20)
            self.hunger = clamp(self.hunger - elapsed_hours * 0.8)
        else:
            self.hunger = clamp(self.hunger - elapsed_hours * 5.0)
            self.happiness = clamp(self.happiness - elapsed_hours * 3.0)
            self.cleanliness = clamp(self.cleanliness - elapsed_hours * 3.5)
            self.energy = clamp(self.energy - elapsed_hours * 4.0)
        # Adopted housemates also get hungry over time, independently of
        # the Founder. A stocked bowl can then actually restore their hunger.
        for housemate in (self.adopted_pets or []):
            if not isinstance(housemate,dict):
                continue
            hunger = float(housemate.get("hunger",85))
            housemate["hunger"] = clamp(
                hunger-elapsed_hours*(.8 if housemate.get("sleeping") else 5.0))
        # Indoor pair bonds grow even when the cottage window is closed.
        advance_house_friendships(self, elapsed_hours)
        # Deliberately gentle: the pet never dies while you are away.

    @property
    def stage(self) -> str:
        age_hours = max(0, time.time() - self.born) / 3600
        return "Hatchling" if age_hours < 2 else "Youngling" if age_hours < 10 else "Companion"

    @property
    def mood(self) -> str:
        if self.sleeping:
            return "Dreaming"
        if self.hunger < 22:
            return "Hungry"
        if self.energy < 20:
            return "Sleepy"
        if self.cleanliness < 22:
            return "Needs a bath"
        if self.happiness < 22:
            return "Lonely"
        return "Very happy" if min(self.hunger, self.happiness, self.energy) > 65 else "Content"

    @property
    def age_days(self) -> int:
        return max(0, int((time.time() - self.born) // 86400))

    @property
    def personality(self) -> str:
        traits = {"Playful": self.playfulness, "Curious": self.curiosity,
                  "Cuddly": self.gentleness, "Mischievous": self.mischief}
        winner = max(traits, key=traits.get)
        return winner if traits[winner] >= 3 else "Discovering themselves"

    def save(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        temporary = STATE_FILE.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        os.replace(temporary, STATE_FILE)


def draw_pet(painter: QPainter, width: int, height: int, state: PetState,
             frame: int, scale: int = 4, facing: int = 1) -> None:
    """Draw an original chunky pixel critter with no external image assets."""
    main, shaded, pink = (QColor(c) for c in PALETTES[state.color])
    outline = QColor("#203146")
    eye = QColor("#152537")
    cream = QColor("#fff4dc")

    painter.save()
    base_x = (width - 20 * scale) // 2
    base_y = (height - 21 * scale) // 2 + (0 if state.sleeping else frame % 2)
    if facing < 0:
        painter.translate(width, 0)
        base_x = (width - 20 * scale) // 2
        painter.scale(-1, 1)

    def pix(x: int, y: int, w: int, h: int, color: QColor) -> None:
        painter.fillRect(base_x + x * scale, base_y + y * scale,
                         w * scale, h * scale, color)

    if not state.egg_hatched:
        pix(5, 7, 10, 11, outline)
        pix(6, 5, 8, 12, cream)
        pix(5, 10, 10, 6, QColor(PALETTES[state.color][0]))
        pix(9, 8, 2, 3, pink)
        pix(7, 13, 2, 2, pink)
        painter.restore()
        return

    if state.founder:
        # Exclusive founder mouse: compact ears, pear-shaped body, short paws.
        # Avoid the broad shared-species shoulders and side appendages entirely.
        pix(16, 13, 2, 2, outline)
        pix(18, 12, 2, 2, shaded)
        pix(18, 10, 1, 2, main)  # Thin curved tail.
        # Small rounded ears anchored above the head.
        pix(4, 3, 5, 5, outline)
        pix(11, 3, 5, 5, outline)
        pix(5, 4, 3, 3, main)
        pix(12, 4, 3, 3, main)
        pix(6, 5, 2, 2, pink)
        pix(12, 5, 2, 2, pink)
        # Soft rounded head instead of rectangular shoulder blocks.
        pix(5, 7, 10, 8, outline)
        pix(4, 9, 12, 5, outline)
        pix(6, 8, 8, 7, main)
        pix(5, 10, 10, 4, main)
        # Tapered lower body.
        pix(6, 14, 8, 4, outline)
        pix(7, 14, 6, 4, main)
        pix(8, 15, 4, 2, cream)
        # Tiny paws below the body (no visible arms).
        pix(6, 17, 3, 2, outline)
        pix(11, 17, 3, 2, outline)
        pix(7, 17, 2, 1, shaded)
        pix(11, 17, 2, 1, shaded)
        if state.sleeping or frame % 45 == 0:
            pix(7, 11, 2, 1, eye)
            pix(12, 11, 2, 1, eye)
        else:
            pix(7, 10, 2, 2, eye)
            pix(12, 10, 2, 2, eye)
            pix(7, 10, 1, 1, cream)
            pix(12, 10, 1, 1, cream)
        pix(6, 12, 2, 1, pink)
        pix(13, 12, 2, 1, pink)
        pix(10, 12, 1, 1, eye)
        pix(9, 14, 3, 1, eye)
        painter.restore()
        return

    # Tail, ears and their darker outlines.
    pix(17, 10, 2, 2, outline)
    pix(18, 8, 2, 3, main)
    pix(2, 2, 4, 7, outline)
    pix(14, 2, 4, 7, outline)
    pix(3, 3, 2, 5, main)
    pix(15, 3, 2, 5, main)
    pix(3, 3, 2, 2, pink)
    pix(15, 3, 2, 2, pink)

    # Square pixel-body, small toes, pale belly.
    pix(4, 5, 12, 13, outline)
    pix(3, 8, 14, 8, outline)
    pix(5, 6, 10, 11, main)
    pix(4, 9, 12, 7, main)
    pix(6, 14, 8, 3, shaded)
    pix(7, 13, 6, 3, cream)
    pix(5, 17, 4, 2, outline)
    pix(11, 17, 4, 2, outline)
    pix(6, 17, 2, 1, main)
    pix(12, 17, 2, 1, main)

    # Small tuft marks the last evolution stage.
    if state.stage == "Companion":
        pix(8, 4, 2, 2, outline)
        pix(9, 3, 2, 3, main)

    if state.sleeping or frame % 45 == 0:
        pix(6, 10, 3, 1, eye)
        pix(12, 10, 3, 1, eye)
    else:
        pix(7, 9, 2, 3, eye)
        pix(12, 9, 2, 3, eye)
        pix(7, 9, 1, 1, cream)
        pix(12, 9, 1, 1, cream)
    pix(5, 12, 2, 1, pink)
    pix(14, 12, 2, 1, pink)
    pix(9, 12, 2, 1, eye)
    if state.mood in ("Hungry", "Needs a bath", "Lonely"):
        pix(9, 15, 3, 1, eye)
    else:
        pix(9, 14, 3, 1, eye)
        pix(10, 15, 1, 1, eye)
    if state.species == "Bunny":
        pix(3, 0, 3, 8, outline)
        pix(14, 0, 3, 8, outline)
        pix(4, 1, 1, 5, pink)
        pix(15, 1, 1, 5, pink)
    elif state.species == "Dog":
        # Small floppy ears, not side limbs.
        pix(2, 5, 2, 4, shaded)
        pix(16, 5, 2, 4, shaded)
        pix(9, 12, 3, 2, outline)
    elif state.species == "Fox":
        pix(17, 13, 2, 3, shaded)
        pix(7, 14, 6, 2, cream)
    elif state.species == "Dragon":
        # Tiny folded wings contained within the sprite outline.
        pix(3, 9, 2, 4, shaded)
        pix(15, 9, 2, 4, shaded)
        pix(9, 1, 2, 4, cream)
    # Ghost intentionally uses the unchanged original v0.1 silhouette.
    painter.restore()


class PetSprite(QWidget):
    def __init__(self, state: PetState, parent=None, size: int = 120):
        super().__init__(parent)
        self.state = state
        self.frame = 0
        self.setFixedSize(size, size)

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        draw_pet(painter, self.width(), self.height(), self.state, self.frame,
                 scale=4 if self.width() <= 120 else 5)


class HomePortal(QWidget):
    """Movable little door shared by desktop and house simulation."""
    def __init__(self, pet):
        super().__init__()
        self.pet = pet
        self.drag_offset = None
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool |
                            Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(80, 95)
        screen = QApplication.primaryScreen().availableGeometry()
        x = pet.state.portal_x if pet.state.portal_x >= 0 else screen.right() - 110
        y = pet.state.portal_y if pet.state.portal_y >= 0 else screen.bottom() - 105
        self.move(x, y)
        self.setToolTip("Click to visit the house • Drag to move")

    def paintEvent(self, event):
        """Little woodland cottage entrance, matching the non-spooky interior."""
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        p.fillRect(10,42,62,49,QColor("#624f42"))    # cozy outline
        p.fillRect(14,45,54,43,QColor("#e6cfad"))    # cream plaster
        for yy in (52,64,76):
            p.fillRect(15,yy,52,2,QColor("#c9ae8c")) # clapboard detail
        p.fillRect(2,36,76,9,QColor("#586b59"))      # sage eaves
        p.fillRect(9,27,62,9,QColor("#789780"))
        p.fillRect(17,19,46,9,QColor("#91a987"))
        p.fillRect(25,12,30,8,QColor("#b5bba0"))
        p.fillRect(25,8,8,14,QColor("#b48b70"))      # chimney
        p.fillRect(25,8,8,3,QColor("#e5bdaa"))
        p.fillRect(28,59,24,31,QColor("#655445"))    # warm door
        p.fillRect(31,62,18,27,QColor("#927a5f"))
        p.fillRect(46,77,3,4,QColor("#ecd79f"))
        for xx in (18,57):
            p.fillRect(xx-2,53,13,14,QColor("#8f7259"))
            p.fillRect(xx,55,9,10,QColor("#accfca"))
            p.fillRect(xx+4,55,2,10,QColor("#f9f2cf"))
        p.fillRect(9,81,13,9,QColor("#9c765c"))
        p.fillRect(11,75,9,9,QColor("#729b6e"))
        p.fillRect(61,82,13,9,QColor("#9c765c"))
        p.fillRect(64,76,9,8,QColor("#83a977"))
        p.setPen(QColor("#3f5145"))
        p.setFont(QFont("Sans",8,QFont.Weight.Bold))
        p.drawText(24,9,"HOME")
        p.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
            self.was_dragged = False

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.was_dragged = True
            self.move(event.globalPosition().toPoint() - self.drag_offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drag_offset is not None:
            self.drag_offset = None
            self.pet.state.portal_x, self.pet.state.portal_y = self.x(), self.y()
            self.pet.persist()
            if not self.was_dragged:
                self.pet.open_house()


class DesktopBuddy(QWidget):
    """Independent second desktop sprite, attached to the same saved household."""
    def __init__(self, lead):
        super().__init__()
        self.lead = lead
        self.facing = -1
        self.frame = 0
        self.drag_start = None
        self.drag_offset = QPoint()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool |
                            Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setFixedSize(124, 116)
        self.setToolTip("Your second pet • click to care • drag to move")
        self.sync_presence()

    def pet_id(self):
        return getattr(self.lead.state, "desktop_companion_id", NONE)

    def sync_presence(self):
        pet_id = self.pet_id()
        if pet_id == NONE or pet_id not in active_desktop_ids(self.lead.state):
            self.hide()
            return
        record = find_adopted(self.lead.state, pet_id)
        x = record.get("desktop_x", -1) if record else self.lead.state.x
        y = record.get("desktop_y", -1) if record else self.lead.state.y
        geom = QApplication.primaryScreen().availableGeometry()
        if not isinstance(x, int) or x < geom.left() or x > geom.right():
            x = self.lead.x() + 140
        if not isinstance(y, int) or y < geom.top() or y > geom.bottom():
            y = self.lead.y()
        x = max(geom.left(), min(x, geom.right() - self.width() + 1))
        y = max(geom.top(), min(y, geom.bottom() - self.height() + 1))
        self.move(x,y)
        self.show()
        self.update()

    def persist(self):
        pet_id = self.pet_id()
        if pet_id == NONE:
            return
        if pet_id == FOUNDER:
            self.lead.state.x, self.lead.state.y = self.x(), self.y()
        else:
            record = find_adopted(self.lead.state, pet_id)
            if record:
                record["desktop_x"], record["desktop_y"] = self.x(), self.y()

    def paintEvent(self, _event):
        pet_id = self.pet_id()
        if pet_id == NONE or pet_id not in active_desktop_ids(self.lead.state):
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.save()
        if self.lead.cursor_chaser_id == self.pet_id():
            painter.translate(0,-[0,2,5,2][self.frame%4])
        if self.lead.pair_interaction in ("play","dance","highfive"):
            bounce = [1,4,6,3,0,3,6,4] if self.lead.pair_interaction=="play" else [0,4,1,6,0,5,2,7]
            painter.translate(0, -bounce[self.frame % 8])
            if self.lead.pair_interaction=="dance":
                painter.translate(3 if (self.frame//5)%2 else -3,0)
        if self.lead.pair_interaction=="peekaboo" and (
                time.monotonic()-self.lead.pair_started_at <
                (self.lead.pair_interaction_until-self.lead.pair_started_at)*.55):
            painter.setOpacity(.45)
        record = find_adopted(self.lead.state, pet_id)
        if record is None and pet_id == FOUNDER:
            draw_pet(painter, self.width(), self.height(), self.lead.state,
                     self.frame, scale=4, facing=self.facing)
        elif record is not None:
            scale = 2 if record.get("species") == "Cat" else 3
            draw_adopted_pet(painter, self.width(), self.height(), record,
                             self.frame, scale=scale, facing=self.facing)
        painter.restore()
        kind = self.lead.pair_interaction
        if self.lead.friend_heart_until > time.monotonic():
            painter.setPen(QColor("#ea829f"))
            painter.setFont(QFont("Sans",18,QFont.Weight.Bold))
            painter.drawText(57, 20,"♥")
        elif kind == "greet":
            painter.setPen(QColor("#74a68a"))
            painter.setFont(QFont("Sans",16,QFont.Weight.Bold))
            painter.drawText(52,17,"✦")
        elif kind == "chase":
            painter.setPen(QColor("#9f86b9"))
            painter.setFont(QFont("Sans",13,QFont.Weight.Bold))
            painter.drawText(57,18,"!!")
        elif self.lead.cursor_chaser_id == self.pet_id():
            painter.setPen(QColor("#be81a7"))
            painter.setFont(QFont("Sans",15,QFont.Weight.Bold))
            painter.drawText(53,17,"!")
        elif kind in ("dance","peekaboo","highfive","share_snack"):
            painter.setFont(QFont("Sans",14,QFont.Weight.Bold))
            painter.setPen(QColor("#a985bd"))
            symbol = {"dance":"♫","peekaboo":"?","highfive":"✦","share_snack":"♥"}[kind]
            painter.drawText(53,17,symbol)

    def advance(self):
        if not self.isVisible():
            return
        self.frame += 1
        if self.lead.cursor_chaser_id == self.pet_id():
            self.update()
            return
        kind = self.lead.pair_interaction
        if self.drag_start is None and self.frame % 3 == 0:
            geom = QApplication.primaryScreen().availableGeometry()
            if kind == "nuzzle":
                # Real approach: companions bring their sprites face to face.
                target_x = self.lead.x() + (58 if self.x() >= self.lead.x() else -58)
                target_y = self.lead.y()
                speed = 4
            elif kind == "chase":
                # Tag: follow more closely instead of just idle-walking.
                target_x = self.lead.x() + (-68 if self.lead.facing > 0 else 68)
                target_y = self.lead.y()
                speed = 5
            elif kind == "play":
                # Lighthearted back-and-forth hopping near the other pet.
                target_x = self.lead.x() + (78 if (self.frame//24)%2 == 0 else -78)
                target_y = self.lead.y()
                speed = 5
            elif kind in ("greet","highfive","share_snack"):
                gap = 58 if kind=="highfive" else 82
                target_x = self.lead.x() + (gap if self.x() >= self.lead.x() else -gap)
                target_y = self.lead.y()
                speed = 4 if kind == "highfive" else 3
            elif kind == "dance":
                target_x = self.lead.x() + (90 if (self.frame//15)%2==0 else 116)
                target_y = self.lead.y() + (6 if (self.frame//11)%2==0 else -6)
                speed = 4
            elif kind == "peekaboo":
                # Duck toward the little portal, then pop back into view.
                half = (self.lead.pair_interaction_until -
                        self.lead.pair_started_at)*.5
                if time.monotonic()-self.lead.pair_started_at < half:
                    target_x = self.lead.portal.x()
                    target_y = self.lead.portal.y()
                else:
                    target_x = self.lead.x()+90
                    target_y = self.lead.y()
                speed = 5
            else:
                target_x = self.lead.x() + (105 if self.facing < 0 else -105)
                target_y = self.lead.y()
                speed = 3
            dx, dy = target_x-self.x(), target_y-self.y()
            if abs(dx) > 10 or abs(dy) > 9:
                new_x = self.x()+max(-speed,min(speed,dx)) if abs(dx)>10 else self.x()
                new_y = self.y()+max(-2,min(2,dy)) if abs(dy)>9 else self.y()
                self.move(max(geom.left(),min(new_x,geom.right()-self.width()+1)),
                          max(geom.top(),min(new_y,geom.bottom()-self.height()+1)))
            if abs(dx) > 10:
                self.facing = 1 if dx >= 0 else -1
            elif kind in ("greet","nuzzle"):
                self.facing = -1 if self.x() >= self.lead.x() else 1
        self.update()

    def mousePressEvent(self, event):
        self.lead.stop_cursor_chase(celebrate=False)
        if event.button() == Qt.MouseButton.RightButton:
            menu = QMenu(self)
            menu.addAction("♥ Care for this pet", lambda: self.lead.open_console_for(self.pet_id()))
            menu.addAction("⌂ Send this pet home", self.lead.dismiss_buddy)
            menu.addAction("🐾 Chase pointer", lambda: self.lead.start_cursor_chase(self.pet_id(),manual=True))
            menu.addAction("🎾 Play together", lambda: self.lead.start_pair_interaction("play"))
            menu.addAction("♡ Nuzzle", lambda: self.lead.start_pair_interaction("nuzzle"))
            menu.exec(event.globalPosition().toPoint())
        elif event.button() == Qt.MouseButton.LeftButton:
            self.drag_start = event.globalPosition().toPoint()
            self.drag_offset = self.drag_start - self.pos()

    def mouseMoveEvent(self, event):
        if self.drag_start is not None and event.buttons() & Qt.MouseButton.LeftButton:
            if (event.globalPosition().toPoint()-self.drag_start).manhattanLength() > 6:
                self.move(event.globalPosition().toPoint()-self.drag_offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drag_start is not None:
            moved = (event.globalPosition().toPoint()-self.drag_start).manhattanLength() > 6
            self.drag_start = None
            self.persist()
            if not moved:
                self.lead.open_console_for(self.pet_id())


class CareConsole(QDialog):
    """Compact shared-household care panel; the original PetState remains canonical."""
    def __init__(self, pet: "RoamingPet"):
        super().__init__()
        self.pet = pet
        self.selected_id = "founder"
        self.setWindowTitle("GhostPet • Pocket Care")
        self.setFixedWidth(326)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet("""
            QDialog { background:#f5ebdb; color:#463f34; }
            QLabel { color:#463f34; }
            QPushButton { background:#759278; color:white; border:0;
                          border-radius:7px; padding:6px 7px; font-weight:600; }
            QPushButton:hover { background:#5d7e64; }
            QComboBox { background:#fff9ed; color:#463f34; border:1px solid #a3ab8b;
                        border-radius:6px; padding:5px; }
            QProgressBar { background:#dfd8c8; border:0; border-radius:4px;
                           height:10px; text-align:center; color:transparent; }
            QProgressBar::chunk { background:#83aa88; border-radius:4px; }
        """)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 10, 12, 10)
        outer.setSpacing(6)
        top = QHBoxLayout()
        top.addWidget(QLabel("♡  Pocket Care"))
        self.collapse = QPushButton("▾")
        self.collapse.setFixedWidth(32)
        self.collapse.clicked.connect(self.toggle_compact)
        top.addWidget(self.collapse)
        self.update_button = QPushButton("↻ Update")
        self.update_button.setToolTip("Check GitHub for a Ghost Pet update")
        self.update_button.clicked.connect(pet.open_updater)
        top.addWidget(self.update_button)
        outer.addLayout(top)
        self.selector = QComboBox()
        self.selector.currentIndexChanged.connect(self.select_pet)
        outer.addWidget(self.selector)
        self.summon_button = QPushButton("🐾 Bring selected pet to desktop")
        self.summon_button.setToolTip("Swap which companion is walking on your desktop")
        self.summon_button.clicked.connect(self.summon_selected)
        outer.addWidget(self.summon_button)
        self.buddy_button = QPushButton("♡ Invite selected pet as Buddy")
        self.buddy_button.clicked.connect(self.invite_selected)
        outer.addWidget(self.buddy_button)
        pair_actions = QHBoxLayout()
        self.pair_play_button = QPushButton("🎾 Play Together")
        self.pair_play_button.clicked.connect(lambda: self.start_pair_action("play"))
        pair_actions.addWidget(self.pair_play_button)
        self.pair_nuzzle_button = QPushButton("♡ Nuzzle")
        self.pair_nuzzle_button.clicked.connect(lambda: self.start_pair_action("nuzzle"))
        pair_actions.addWidget(self.pair_nuzzle_button)
        social_row = QHBoxLayout()
        self.auto_social_button = QPushButton("✨ Auto interactions: On")
        self.auto_social_button.clicked.connect(self.toggle_auto_social)
        self.auto_social_button.setToolTip(
            "Let your two roaming pets start playful encounters by themselves")
        social_row.addWidget(self.auto_social_button,1)
        self.surprise_button = QPushButton("🎲 Surprise!")
        self.surprise_button.clicked.connect(lambda: self.start_pair_action(None))
        social_row.addWidget(self.surprise_button,1)
        self.details = QWidget()
        details = QVBoxLayout(self.details)
        details.setContentsMargins(0, 0, 0, 0)
        details.setSpacing(5)
        details.addLayout(pair_actions)
        details.addLayout(social_row)
        overview = QHBoxLayout()
        self.avatar = QLabel("🐭")
        self.avatar.setFixedWidth(48)
        self.avatar.setStyleSheet("font-size:32px;")
        overview.addWidget(self.avatar)
        self.status = QLabel()
        self.status.setWordWrap(True)
        overview.addWidget(self.status, 1)
        details.addLayout(overview)
        self.stats = {}
        for label, key in (("Food","hunger"),("Happy","happiness"),
                           ("Clean","cleanliness"),("Energy","energy")):
            row = QHBoxLayout()
            title = QLabel(label)
            title.setFixedWidth(46)
            row.addWidget(title)
            bar = QProgressBar()
            bar.setRange(0,100)
            bar.setTextVisible(False)
            row.addWidget(bar,1)
            amount = QLabel()
            amount.setFixedWidth(35)
            row.addWidget(amount)
            details.addLayout(row)
            self.stats[key] = (bar, amount)
        actions = QGridLayout()
        for i,(label,action) in enumerate((("🍎 Feed","feed"),("🎾 Play","play"),
                                            ("🫧 Clean","clean"),("💤 Sleep","sleep"),
                                            ("♡ Cuddle","cuddle"))):
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked=False, a=action: self.care_selected(a))
            actions.addWidget(btn,i//2,i%2)
        details.addLayout(actions)
        nav = QHBoxLayout()
        for label,action in (("🏡 House",pet.open_house),("🥚 Nursery",pet.open_nursery)):
            btn = QPushButton(label)
            btn.clicked.connect(action)
            nav.addWidget(btn)
        details.addLayout(nav)
        self.personality_label = QLabel()
        self.personality_label.setWordWrap(True)
        details.addWidget(self.personality_label)
        friend_row = QHBoxLayout()
        friend_row.addWidget(QLabel("Friendship with:"))
        self.friend_partner = QComboBox()
        self.friend_partner.currentIndexChanged.connect(self.update_friend_meter)
        friend_row.addWidget(self.friend_partner,1)
        details.addLayout(friend_row)
        self.friend_meter = QProgressBar()
        self.friend_meter.setRange(0,100)
        self.friend_meter.setTextVisible(True)
        self.friend_meter.setFormat("%v / 100")
        details.addWidget(self.friend_meter)
        self.friendship_desc = QLabel()
        details.addWidget(self.friendship_desc)
        extras = QHBoxLayout()
        rename = QPushButton("✎ Rename")
        rename.clicked.connect(self.rename_pet)
        extras.addWidget(rename)
        self.roaming_button = QPushButton("Walk")
        self.roaming_button.clicked.connect(pet.toggle_roaming)
        extras.addWidget(self.roaming_button)
        details.addLayout(extras)
        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("Founder color:"))
        self.colors = QComboBox()
        self.colors.addItems(list(PALETTES))
        self.colors.setCurrentText(pet.state.color)
        self.colors.currentTextChanged.connect(pet.change_color)
        color_row.addWidget(self.colors)
        details.addLayout(color_row)
        outer.addWidget(self.details)
        self.tip = QLabel("Choose a pet to care for.")
        self.tip.setWordWrap(True)
        outer.addWidget(self.tip)
        self.refresh()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1000)

    def household_pet(self):
        if self.selected_id == "founder":
            return None
        return next((p for p in (self.pet.state.adopted_pets or [])
                     if p.get("id") == self.selected_id), None)

    def select_pet(self, _index):
        self.selected_id = self.selector.currentData() or "founder"
        self.refresh()

    def summon_selected(self):
        selected = self.selected_id
        if self.pet.bring_selected_pet_to_desktop(selected):
            self.tip.setText("That companion is now on your desktop! ♡")
        self.refresh()

    def invite_selected(self):
        if self.selected_id == self.pet.state.desktop_companion_id:
            self.pet.dismiss_buddy()
            self.tip.setText("Your buddy went home! ♡")
        elif self.pet.invite_selected_buddy(self.selected_id):
            self.tip.setText("Two little companions can wander together now! ♡")
        else:
            self.tip.setText("Hatch or adopt this pet before inviting them.")
        self.refresh()

    def toggle_auto_social(self):
        self.pet.state.auto_social = not self.pet.state.auto_social
        self.pet.persist()
        self.tip.setText("Pets will start their own antics!" if self.pet.state.auto_social
                         else "Automatic interactions paused.")
        self.refresh()

    def start_pair_action(self, kind):
        if not self.pet.start_pair_interaction(kind):
            if self.pet.pair_interaction:
                self.tip.setText("The pets are busy! Try again in a moment.")
            else:
                self.tip.setText("Both pets must be awake and outside to interact.")
        else:
            self.tip.setText("Watch the pets interact on your desktop! ♡")
        self.refresh()

    def update_friend_meter(self, _index=None):
        partner = self.friend_partner.currentData()
        if partner and partner != self.selected_id:
            score = relationship_score(self.pet.state, self.selected_id, partner)
            self.friend_meter.setValue(round(score))
            self.friendship_desc.setText(
                f"♡ {pet_name(self.pet.state, self.selected_id)} and "
                f"{pet_name(self.pet.state,partner)} — {relationship_title(score)}")
        else:
            self.friend_meter.setValue(0)
            self.friendship_desc.setText("Adopt another pet to build friendships.")

    def toggle_compact(self):
        self.details.setVisible(not self.details.isVisible())
        self.collapse.setText("▾" if self.details.isVisible() else "▸")
        self.adjustSize()

    def care_selected(self, action):
        if action == "cuddle":
            self.pet.open_cuddles(self.selected_id)
            return
        adopted = self.household_pet()
        if adopted is None:
            self.pet.care(action)
            return
        adopted.setdefault("hunger", 85)
        adopted.setdefault("happiness", 85)
        adopted.setdefault("cleanliness", 90)
        adopted.setdefault("energy", 85)
        adopted.setdefault("affection", 30)
        if action == "sleep":
            adopted["sleeping"] = not adopted.get("sleeping", False)
        elif adopted.get("sleeping", False):
            self.tip.setText("Wake this pet before feeding or playing.")
            return
        elif action == "feed":
            adopted["hunger"] = clamp(adopted["hunger"]+27)
            adopted["happiness"] = clamp(adopted["happiness"]+4)
            adopted["cleanliness"] = clamp(adopted["cleanliness"]-5)
        elif action == "play":
            adopted["happiness"] = clamp(adopted["happiness"]+18)
            adopted["energy"] = clamp(adopted["energy"]-12)
            adopted["affection"] = clamp(adopted["affection"]+3)
        elif action == "clean":
            adopted["cleanliness"] = clamp(adopted["cleanliness"]+42)
            adopted["happiness"] = clamp(adopted["happiness"]+5)
        self.pet.persist()
        self.tip.setText(f"{adopted.get('name','Buddy')} loved the attention! ♡")
        self.refresh()

    def rename_pet(self):
        adopted = self.household_pet()
        original = adopted.get("name","Buddy") if adopted is not None else self.pet.state.name
        name, accepted = QInputDialog.getText(self,"Name your pet","Pet name:",text=original)
        if accepted and name.strip():
            if adopted is not None:
                adopted["name"] = name.strip()[:18]
            else:
                self.pet.state.name = name.strip()[:18]
            self.pet.persist()
            self.refresh()

    def refresh(self):
        state = self.pet.state
        choices = [("🌟 " + state.name,"founder")]
        choices.extend((("🐾 " + p.get("name","Buddy")),p.get("id"))
                       for p in (state.adopted_pets or []))
        current = self.selected_id
        if current not in [id_ for _,id_ in choices]:
            current = "founder"
            self.selected_id = current
        self.selector.blockSignals(True)
        self.selector.clear()
        for label,id_ in choices:
            self.selector.addItem(label,id_)
        self.selector.setCurrentIndex([id_ for _,id_ in choices].index(current))
        self.selector.blockSignals(False)
        adopted = self.household_pet()
        species = adopted.get("species","Ghost") if adopted is not None else state.species
        emoji = {"Cat":"🐱","Dog":"🐶","Bunny":"🐰","Fox":"🦊",
                 "Dragon":"🐲","Ghost":"👻"}.get(species,"🐾")
        self.avatar.setText(emoji if adopted is not None else "🐭")
        label = adopted.get("name","Buddy") if adopted is not None else state.name
        mood = "Sleeping" if ((adopted.get("sleeping",False) if adopted is not None else state.sleeping)) else "Feeling loved"
        self.status.setText(f"{label}  {'🌟 Founder' if adopted is None else species}\n{mood}")
        for stat,(bar,amount) in self.stats.items():
            value = (adopted.get(stat,85) if adopted is not None else getattr(state,stat))
            value = round(clamp(float(value)))
            bar.setValue(value)
            amount.setText(f"{value}%")
        self.personality_label.setText(
            f"♡ Affection {round(adopted.get('affection',30))}% · {adopted.get('trait','Curious')}"
            if adopted is not None else
            f"♡ Affection {round(state.affection)}% · {state.personality} · 🪙 {state.coins}")
        active = state.desktop_pet_id == self.selected_id and current_pet(state) is not False
        self.summon_button.setText("✓ This pet is on your desktop" if active
                                   else "🐾 Bring selected pet to desktop")
        self.summon_button.setEnabled(not active)
        is_buddy = state.desktop_companion_id == self.selected_id
        is_lead = state.desktop_pet_id == self.selected_id
        self.buddy_button.setText("⌂ Send Buddy Home" if is_buddy
                                  else "♡ Invite as Second Pet")
        self.buddy_button.setEnabled(not is_lead and
                                      (len(state.adopted_pets or []) > 0 or
                                       self.selected_id != FOUNDER))
        for btn in (self.pair_play_button, self.pair_nuzzle_button,
                    self.surprise_button):
            btn.setEnabled(self.pet.pair_ready() and not self.pet.pair_interaction)
        self.auto_social_button.setText(
            "✨ Auto interactions: On" if state.auto_social
            else "⏸ Auto interactions: Off")
        other_ids = [id_ for _, id_ in choices if id_ != self.selected_id]
        previous = self.friend_partner.currentData()
        partner = previous if previous in other_ids else (other_ids[0] if other_ids else None)
        self.friend_partner.blockSignals(True)
        self.friend_partner.clear()
        for id_ in other_ids:
            self.friend_partner.addItem(pet_name(state,id_), id_)
        if partner in other_ids:
            self.friend_partner.setCurrentIndex(other_ids.index(partner))
        self.friend_partner.blockSignals(False)
        self.friend_partner.setEnabled(bool(other_ids))
        self.update_friend_meter()
        self.roaming_button.setVisible(active)
        roaming = adopted.get("roaming", True) if adopted is not None else state.roaming
        self.roaming_button.setText("⏸ Pause walk" if roaming else "▶ Resume walk")
        self.colors.setEnabled(adopted is None)
        self.tip.setStyleSheet("color:#706c5b;font-size:11px;")

class RoamingPet(QWidget):
    def __init__(self, state: PetState):
        super().__init__()
        self.state = state
        self.frame = 0
        self.facing = 1
        self.walk_offset = 0.0
        self.idle_ticks = 0
        self.drag_start: QPoint | None = None
        self.drag_offset = QPoint()
        self.dragging = False
        self.console: CareConsole | None = None
        self.game_dialog = None
        self.cuddle_taps = 0
        self.cuddle_mode = False
        self.house_dialog = None
        self.nursery_dialog = None
        self.going_home = False
        self.home_steps = 0
        self.bubble_text = ""
        self.bubble_until = 0.0
        self.friend_heart_until = 0.0
        self.last_friend_interaction = 0.0
        self.pair_interaction = None
        self.pair_interaction_until = 0.0
        self.pair_interaction_pair = ()
        self.pair_started_at = 0.0
        self.cursor_chaser_id = NONE
        self.cursor_chase_until = 0.0
        self.last_cursor_chase = time.monotonic()
        self.setWindowTitle("GhostPet")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool |
                            Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setFixedSize(124, 116)
        self.setToolTip("Left-click to care • Drag to move • Right-click for menu")

        screen = QApplication.primaryScreen().availableGeometry()
        active = current_pet(state)
        coords = active if isinstance(active, dict) else None
        saved_x = coords.get("desktop_x", state.x) if coords else state.x
        saved_y = coords.get("desktop_y", state.y) if coords else state.y
        start_x = saved_x if 0 <= saved_x <= screen.right() else screen.center().x()
        start_y = saved_y if 0 <= saved_y <= screen.bottom() else screen.bottom() - self.height()
        self.move(start_x, start_y)
        self.portal = HomePortal(self)
        self.portal.show()
        self.buddy = DesktopBuddy(self)
        if current_pet(state) is False:
            self.hide()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(80)
        self.needs_timer = QTimer(self)
        self.needs_timer.timeout.connect(self.update_needs)
        self.needs_timer.start(20_000)
        self.speech_timer = QTimer(self)
        self.speech_timer.timeout.connect(self.maybe_speak)
        self.speech_timer.start(28_000)

        self.tray = None
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray = QSystemTrayIcon(self._icon(), self)
            tray_menu = QMenu()
            tray_menu.addAction("Open care console", self.open_console)
            tray_menu.addAction("Pause / resume roaming", self.toggle_roaming)
            tray_menu.addSeparator()
            tray_menu.addAction("Quit GhostPet", QApplication.quit)
            self.tray.setContextMenu(tray_menu)
            self.tray.activated.connect(self._tray_activated)
            self.tray.show()

    def _icon(self) -> QIcon:
        image = QPixmap(48, 48)
        image.fill(QColor("#292d45"))
        painter = QPainter(image)
        painter.setBrush(QColor(PALETTES[self.state.color][0]))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(8, 8, 32, 32)
        painter.setBrush(QColor("#263047"))
        painter.drawEllipse(17, 22, 5, 6)
        painter.drawEllipse(27, 22, 5, 6)
        painter.end()
        return QIcon(image)

    def _tray_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.open_console()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        selected = current_pet(self.state)
        painter.save()
        if self.cursor_chaser_id == self.state.desktop_pet_id:
            painter.translate(0,-[0,2,5,2][self.frame%4])
        if self.pair_interaction in ("play","dance","highfive"):
            hops = [0,2,5,3,0,1,4,2] if self.pair_interaction=="play" else [0,5,2,7,0,6,2,5]
            painter.translate(0,-hops[self.frame%8])
            if self.pair_interaction=="dance":
                painter.translate(4 if (self.frame//7)%2 else -4,0)
        if isinstance(selected, dict):
            # Keep original Founder mouse pixel artwork untouched.
            scale = 2 if selected.get("species") == "Cat" else 3
            draw_adopted_pet(painter, self.width(), self.height(), selected,
                             self.frame, scale=scale, facing=self.facing)
        elif selected is None:
            draw_pet(painter, self.width(), self.height(), self.state,
                     self.frame, scale=4, facing=self.facing)
        painter.restore()
        if self.cursor_chaser_id == self.state.desktop_pet_id:
            painter.setFont(QFont("Sans",15,QFont.Weight.Bold))
            painter.setPen(QColor("#bf85a4"))
            painter.drawText(87,22,"!")
        if self.pair_interaction in ("highfive","dance","peekaboo","share_snack"):
            painter.setFont(QFont("Sans",13,QFont.Weight.Bold))
            painter.setPen(QColor("#cf89ab"))
            painter.drawText(88,26,{
                "highfive":"✦","dance":"♫","peekaboo":"?","share_snack":"♥",
            }[self.pair_interaction])
        if self.active_sleeping():
            painter.setPen(QColor("#bee8fa"))
            painter.setFont(QFont("monospace", 12, QFont.Weight.Bold))
            painter.drawText(91, 20 + (self.frame // 6) % 5, "Zz")
        if self.bubble_text and time.monotonic() < self.bubble_until:
            painter.setFont(QFont("Sans", 8, QFont.Weight.Bold))
            painter.setPen(QColor("#2b3348"))
            painter.setBrush(QColor("#f8f3ff"))
            painter.drawRoundedRect(2, 1, 120, 30, 9, 9)
            painter.drawText(5, 3, 114, 25, Qt.AlignmentFlag.AlignCenter |
                             Qt.TextFlag.TextWordWrap, self.bubble_text)
        if self.cuddle_mode:
            painter.setPen(QColor("#ff8fbd"))
            painter.setFont(QFont("Sans", 13, QFont.Weight.Bold))
            painter.drawText(82, 107, f"♥ {self.cuddle_taps}/5")

    def say(self, text: str) -> None:
        self.bubble_text = text[:80]
        self.bubble_until = time.monotonic() + 5
        self.update()

    def cursor_pet_ready(self, pet_id):
        """Cursor games can be enjoyed by either pet, including a solo mouse."""
        if pet_id not in active_desktop_ids(self.state):
            return False
        if self.going_home or self.pair_interaction or self.cuddle_mode:
            return False
        if self.dragging or self.buddy.drag_start is not None:
            return False
        pet = find_adopted(self.state, pet_id)
        sleeping = (self.state.sleeping if pet_id == FOUNDER
                    else pet.get("sleeping",False) if pet else True)
        if sleeping:
            return False
        if pet_id == self.state.desktop_pet_id:
            return self.isVisible()
        return self.buddy.isVisible()

    def start_cursor_chase(self, pet_id=None, manual=False):
        """An eight-second game; NEVER move or click the actual OS pointer."""
        pet_id = pet_id or self.state.desktop_pet_id
        if self.cursor_chaser_id != NONE or not self.cursor_pet_ready(pet_id):
            if manual and self.console:
                self.console.tip.setText(
                    "Choose an awake roaming pet that isn't busy playing.")
            return False
        self.cursor_chaser_id = pet_id
        self.cursor_chase_until = time.monotonic() + CURSOR_CHASE_SECONDS
        self.last_cursor_chase = time.monotonic()
        if self.console and manual:
            self.console.hide()
        self.say(random.choice([
            "OH! THE MOUSE IS MOVING! 🐭",
            "Wait! Come back, pointer!",
            "I'M GONNA GET IT! ♡",
        ]))
        self.update()
        self.buddy.update()
        return True

    def stop_cursor_chase(self, celebrate=True):
        if self.cursor_chaser_id == NONE:
            return
        pet_id = self.cursor_chaser_id
        self.cursor_chaser_id = NONE
        self.cursor_chase_until = 0.0
        self.last_cursor_chase = time.monotonic()
        if celebrate:
            pet = find_adopted(self.state,pet_id)
            if pet_id == FOUNDER:
                self.state.happiness = clamp(self.state.happiness+2)
            elif pet:
                pet["happiness"] = clamp(float(pet.get("happiness",80))+2)
            self.say("Aw, it got away! 😂")
            self.persist()
        self.update()
        self.buddy.update()

    def advance_cursor_chase(self, cursor=None):
        """Move only the pet window, staying a window-width from the pointer."""
        pet_id = self.cursor_chaser_id
        if pet_id == NONE:
            return
        if time.monotonic() >= self.cursor_chase_until:
            self.stop_cursor_chase()
            return
        if not self.cursor_pet_ready(pet_id):
            self.stop_cursor_chase(celebrate=False)
            return
        if self.console and self.console.isVisible():
            self.stop_cursor_chase(celebrate=False)
            return
        if self.house_dialog and self.house_dialog.isVisible():
            self.stop_cursor_chase(celebrate=False)
            return
        geom = QApplication.primaryScreen().availableGeometry()
        pointer = QCursor.pos() if cursor is None else cursor
        if not geom.contains(pointer):
            return
        window = self if pet_id == self.state.desktop_pet_id else self.buddy
        target = cursor_chase_destination(window,pointer,geom)
        if target is None:
            return
        delta_x = target.x()-window.x()
        delta_y = target.y()-window.y()
        step_x = max(-7,min(7,delta_x))
        step_y = max(-5,min(5,delta_y))
        if step_x or step_y:
            window.move(window.x()+step_x,window.y()+step_y)
            if step_x:
                window.facing = 1 if step_x > 0 else -1
            window.update()

    def maybe_start_cursor_chase(self):
        """Short, infrequent spontaneous curiosity, separate from duo play."""
        if not self.state.auto_cursor_chase or self.cursor_chaser_id != NONE:
            return False
        if self.console and self.console.isVisible():
            return False
        if self.house_dialog and self.house_dialog.isVisible():
            return False
        if time.monotonic()-self.last_cursor_chase < CURSOR_CHASE_COOLDOWN:
            return False
        geom = QApplication.primaryScreen().availableGeometry()
        if not geom.contains(QCursor.pos()):
            return False
        candidates = [p for p in active_desktop_ids(self.state)
                      if self.cursor_pet_ready(p)]
        if not candidates or random.random() >= .007:
            return False
        # Cats are especially tempted by the moving pointer.
        weights = [4 if (find_adopted(self.state,p) or {}).get("species")=="Cat"
                   else 1 for p in candidates]
        chosen = random.choices(candidates,weights=weights,k=1)[0]
        return self.start_cursor_chase(chosen)

    def pair_ready(self):
        """Both desktop pets must exist and be awake before playing."""
        ids = active_desktop_ids(self.state)
        if (len(ids) != 2 or not self.buddy.isVisible() or self.going_home
                or self.cursor_chaser_id != NONE):
            return False
        if self.dragging or self.buddy.drag_start is not None or self.cuddle_mode:
            return False
        for pet_id in ids:
            record = find_adopted(self.state, pet_id)
            sleeping = self.state.sleeping if pet_id == FOUNDER else (
                record.get("sleeping", False) if record else True)
            if sleeping:
                return False
        return True

    def start_pair_interaction(self, kind=None):
        """Begin a visually distinct duet, spontaneous or user-invoked."""
        actions = ("greet", "nuzzle", "play", "chase",
                   "highfive", "dance", "peekaboo", "share_snack")
        if kind is not None and kind not in actions:
            raise ValueError(f"Unknown pet interaction: {kind}")
        if not self.pair_ready():
            if self.console:
                self.console.tip.setText("Invite two awake pets outside to play together.")
            return False
        if self.pair_interaction:
            return False
        if kind is None:
            a,b = active_desktop_ids(self.state)
            friendship = relationship_score(self.state,a,b)
            weights = (3, 2 if friendship>=30 else 1, 3, 2,
                       2, 2, 2, 2 if friendship>=55 else 1)
            kind = random.choices(actions,weights=weights,k=1)[0]
        durations = {
            "greet":2.8,"nuzzle":3.8,"play":5.0,"chase":6.0,
            "highfive":3.2,"dance":5.3,"peekaboo":5.2,"share_snack":4.2,
        }
        now = time.monotonic()
        self.pair_interaction = kind
        self.pair_interaction_pair = tuple(active_desktop_ids(self.state))
        self.pair_started_at = now
        self.pair_interaction_until = now + durations[kind]
        self.last_friend_interaction = now
        self.friend_heart_until = now + durations[kind] if kind in (
            "nuzzle","play","highfive","share_snack") else 0
        self.idle_ticks = 0
        self.say({
            "greet":"Oh, hello! ♡",
            "nuzzle":"Cuddle buddies! ♥",
            "play":"Let's play! ✦",
            "chase":"Catch me! ♡",
            "highfive":"High five! ✨",
            "dance":"Dance party! ♫",
            "peekaboo":"Where'd you go?!",
            "share_snack":"Snack time! Yum!",
        }[kind])
        self.buddy.update()
        self.update()
        return True

    def maybe_start_auto_interaction(self):
        """Regular but unobtrusive ambient social actions, no manual button needed."""
        if not self.state.auto_social or self.pair_interaction or not self.pair_ready():
            return False
        if abs(self.x()-self.buddy.x()) >= 210 or abs(self.y()-self.buddy.y()) >= 120:
            return False
        if time.monotonic()-self.last_friend_interaction < 17:
            return False
        if random.random() >= .07:
            return False
        return self.start_pair_interaction()

    def advance_pair_interaction(self):
        """Finish each action once, or cancel cleanly when a pet goes away."""
        if not self.pair_interaction:
            return
        if (tuple(active_desktop_ids(self.state)) != self.pair_interaction_pair
                or not self.pair_ready()):
            self.pair_interaction = None
            self.pair_interaction_pair = ()
            self.friend_heart_until = 0
            self.buddy.update()
            return
        if time.monotonic() < self.pair_interaction_until:
            return
        kind = self.pair_interaction
        a,b = self.pair_interaction_pair
        rewards = {
            "greet":.7, "nuzzle":1.6, "play":2.6, "chase":2.1,
            "highfive":1.5, "dance":2.0, "peekaboo":1.4, "share_snack":2.2,
        }
        strengthen_friendship(self.state,a,b,rewards[kind])
        if kind in ("play","chase","dance","highfive","peekaboo","share_snack"):
            for pet_id in (a,b):
                record = find_adopted(self.state,pet_id)
                target = self.state if record is None else record
                if record is None:
                    self.state.happiness = clamp(self.state.happiness+4)
                    if kind in ("play","chase","dance"):
                        self.state.energy = clamp(self.state.energy-2)
                    if kind == "share_snack":
                        self.state.hunger = clamp(self.state.hunger+8)
                else:
                    record["happiness"] = clamp(float(record.get("happiness",80))+4)
                    if kind in ("play","chase","dance"):
                        record["energy"] = clamp(float(record.get("energy",85))-2)
                    if kind == "share_snack":
                        record["hunger"] = clamp(float(record.get("hunger",85))+8)
        self.pair_interaction = None
        self.pair_interaction_pair = ()
        self.friend_heart_until = time.monotonic()+1.1
        self.last_friend_interaction = time.monotonic()
        self.say("That was fun! ♡")
        self.persist()
        self.buddy.update()
        if self.house_dialog and self.house_dialog.isVisible():
            self.house_dialog.update_friendship()
        if self.console:
            self.console.refresh()

    def maybe_speak(self) -> None:
        selected = current_pet(self.state)
        if selected is False or self.active_sleeping():
            return
        if random.random() < .65:
            if isinstance(selected, dict):
                self.say(random.choice(["Hi hi! ♡", "Can we play?", "I love our cottage!", "♡"]))
            elif self.state.egg_hatched:
                self.say(pick_speech(self.state))

    def activity_reward(self, kind: str, score: int) -> None:
        state = self.state
        if kind == "cuddle":
            state.cuddles += 1
            state.affection = clamp(state.affection + 9 + score)
            state.gentleness += 2
            state.happiness = clamp(state.happiness + 10)
            self.say(pick_speech(state, "cuddle"))
        else:
            state.games_played += 1
            state.coins += max(2, score * 2)
            state.happiness = clamp(state.happiness + 8 + score)
            state.energy = clamp(state.energy - 6)
            state.hunger = clamp(state.hunger - 4)
            state.playfulness += 1 + score // 3
            if kind == "memory":
                state.curiosity += 2
            elif score <= 2:
                state.mischief += 1
            state.words_learned += 1 if state.games_played % 5 == 0 else 0
            self.say(pick_speech(state, "play"))
        self.persist()
        if self.console:
            self.console.refresh()

    def open_games(self) -> None:
        if self.state.sleeping or not self.state.egg_hatched:
            self.say("Zzz...")
            return
        self.game_dialog = GameDialog(self.activity_reward, self)
        self.game_dialog.show()

    def open_cuddles(self, pet_id=None) -> None:
        """Start or cancel the five-click cuddle ritual for either household pet."""
        selected_id = self.state.desktop_pet_id if pet_id is None else pet_id
        if selected_id == FOUNDER and not self.state.egg_hatched:
            self.say("Our Founder must hatch first! ♡")
            return
        active = current_pet(self.state)
        if selected_id != self.state.desktop_pet_id or active is False:
            if not self.bring_selected_pet_to_desktop(selected_id):
                return
            active = current_pet(self.state)
        sleeping = active.get("sleeping", False) if isinstance(active, dict) else self.state.sleeping
        if sleeping:
            self.say("Zzz... wake me for cuddles!")
            return
        if self.cuddle_mode:
            self.cuddle_mode = False
            self.cuddle_taps = 0
            self.say("Cuddles later! ♡")
        else:
            self.cuddle_mode = True
            self.cuddle_taps = 0
            self.say("Pat me five times! ♡")
        if self.console:
            self.console.tip.setText(
                "Click the roaming pet five times to cuddle; right-click to cancel.")
        self.update()

    def pat_directly(self) -> None:
        if not self.cuddle_mode:
            return
        self.cuddle_taps += 1
        if self.cuddle_taps >= 5:
            self.cuddle_mode = False
            self.cuddle_taps = 0
            selected = current_pet(self.state)
            if isinstance(selected, dict):
                selected["cuddles"] = int(selected.get("cuddles", 0)) + 1
                selected["affection"] = clamp(float(selected.get("affection", 30)) + 14)
                selected["happiness"] = clamp(float(selected.get("happiness", 80)) + 11)
                self.say(f"{selected.get('name', 'Buddy')} loved that! ♡")
                self.persist()
                if self.console:
                    self.console.refresh()
            else:
                self.activity_reward("cuddle", 5)
            if self.console:
                self.console.tip.setText("Cuddle complete! Your buddy feels loved. ♥")
        else:
            self.say(random.choice(["♥", "Eee! ♡", "More!", "hehe ♡"]))
        self.update()

    def open_updater(self) -> None:
        """Open the separate graphical updater, then exit cleanly for safe patching."""
        launcher = Path(__file__).resolve().with_name("update.sh")
        if not launcher.is_file():
            QMessageBox.warning(self, "Updater missing",
                                "Install the latest Ghost Pet from GitHub first.")
            return
        try:
            self.persist()
            subprocess.Popen(
                ["bash", str(launcher), "--wait-pid", str(os.getpid())],
                cwd=str(launcher.parent), start_new_session=True,
                env=os.environ.copy(),
            )
        except OSError as exc:
            QMessageBox.warning(self, "Could not open updater", str(exc))
            return
        QApplication.instance().quit()

    def open_nursery(self) -> None:
        if self.nursery_dialog and self.nursery_dialog.isVisible():
            self.nursery_dialog.raise_()
            return
        self.nursery_dialog = NurseryDialog(self.state, self.persist, self)
        self.nursery_dialog.show()

    def open_house(self) -> None:
        if self.house_dialog and self.house_dialog.isVisible():
            self.house_dialog.raise_()
            return
        self.house_dialog = HouseDialog(self.state, self.persist,
                                        self.return_from_house, self.send_home, self)
        self.house_dialog.show()

    def active_sleeping(self) -> bool:
        selected = current_pet(self.state)
        return bool(selected.get("sleeping", False)) if isinstance(selected, dict) else self.state.sleeping

    def active_roaming(self) -> bool:
        selected = current_pet(self.state)
        return bool(selected.get("roaming", True)) if isinstance(selected, dict) else self.state.roaming

    def bring_selected_pet_to_desktop(self, pet_id: str) -> bool:
        """Select a primary without deleting the optional second desktop pet."""
        self.stop_cursor_chase(celebrate=False)
        self.persist()
        self.buddy.persist()
        if pet_id == FOUNDER and not self.state.egg_hatched:
            if self.console:
                self.console.tip.setText("Hatch your Founder egg first.")
            return False
        try:
            chosen = bring_to_desktop(self.state, pet_id)
        except ValueError:
            if self.console:
                self.console.tip.setText("That pet has not hatched yet.")
            return False
        self.going_home = False
        self.home_steps = 0
        self.cuddle_mode = False
        self.cuddle_taps = 0
        self.bubble_text = ""
        geom = QApplication.primaryScreen().availableGeometry()
        px = chosen.get("desktop_x", -1) if isinstance(chosen, dict) else self.state.x
        py = chosen.get("desktop_y", -1) if isinstance(chosen, dict) else self.state.y
        if not isinstance(px, int) or px < 0:
            px = self.portal.x() - 55
        if not isinstance(py, int) or py < 0:
            py = self.portal.y()
        px = max(geom.left(), min(px, geom.right() - self.width() + 1))
        py = max(geom.top(), min(py, geom.bottom() - self.height() + 1))
        self.move(px, py)
        self.show()
        self.raise_()
        self.pair_interaction = None
        self.buddy.sync_presence()
        name = chosen.get("name", "Buddy") if isinstance(chosen, dict) else self.state.name
        self.say(f"{name} is here! ♡")
        self.persist()
        if self.house_dialog and self.house_dialog.isVisible():
            self.house_dialog.refresh()
        if self.console:
            self.console.refresh()
        return True

    def invite_selected_buddy(self, pet_id: str) -> bool:
        """Use the second desktop slot and preserve each pet's independent data."""
        self.persist()
        try:
            invited = invite_companion(self.state, pet_id)
        except ValueError:
            return False
        if not invited:
            if self.state.desktop_pet_id == pet_id:
                return True
            return self.bring_selected_pet_to_desktop(pet_id)
        self.buddy.sync_presence()
        self.state.save()
        if self.house_dialog and self.house_dialog.isVisible():
            self.house_dialog.refresh()
        if self.console:
            self.console.refresh()
        return True

    def dismiss_buddy(self):
        self.stop_cursor_chase(celebrate=False)
        self.pair_interaction = None
        self.persist()
        send_companion_home(self.state)
        self.buddy.sync_presence()
        self.state.save()
        if self.house_dialog and self.house_dialog.isVisible():
            self.house_dialog.refresh()
        if self.console:
            self.console.refresh()

    def open_console_for(self, pet_id):
        self.open_console()
        self.console.selected_id = pet_id
        self.console.refresh()

    def return_from_house(self) -> None:
        chosen = self.console.selected_id if self.console else FOUNDER
        self.bring_selected_pet_to_desktop(chosen)

    def send_home(self) -> None:
        self.stop_cursor_chase(celebrate=False)
        self.pair_interaction = None
        if current_pet(self.state) is not False and self.state.desktop_companion_id != NONE:
            # Promote the buddy when the primary returns indoors; do not
            # accidentally send both home or paint the same pet twice.
            self.persist()
            self.buddy.persist()
            old_position = self.buddy.pos()
            send_desktop_pet_home(self.state)
            self.buddy.sync_presence()
            self.move(old_position)
            self.show()
            self.state.save()
            if self.house_dialog and self.house_dialog.isVisible():
                self.house_dialog.refresh()
            if self.console:
                self.console.refresh()
            return
        if current_pet(self.state) is not False:
            self.going_home = True
            self.home_steps = 0
            self.say("Going home! ♡")

    def tap_egg(self) -> None:
        self.state.hatch_taps += 1
        if self.state.hatch_taps >= 5:
            species, accepted = QInputDialog.getItem(self, "Your egg is hatching!",
                         "Choose your starter species:", list(SPECIES), 0, False)
            if accepted and species:
                self.state.species = species
                self.state.egg_hatched = True
                self.state.born = time.time()
                self.say(f"{species} hatched! ♡")
                self.persist()
            else:
                self.say("Ready to hatch!")
        else:
            self.say(f"Crack! {self.state.hatch_taps}/5")
        self.update()

    def animate(self) -> None:
        self.frame += 1
        self.advance_pair_interaction()
        self.maybe_start_cursor_chase()
        self.advance_cursor_chase()
        self.buddy.advance()
        active = current_pet(self.state)
        self.maybe_start_auto_interaction()
        if self.going_home and active is not False:
            # The target must be reachable by the WHOLE pet window. Near the
            # taskbar/screen edge the window manager can clamp moves, so aiming
            # at the portal's top-left would leave the pet stuck outside.
            geom = QApplication.primaryScreen().availableGeometry()
            target_x = max(geom.left(), min(
                self.portal.x() + (self.portal.width() - self.width()) // 2,
                geom.right() - self.width() + 1))
            target_y = max(geom.top(), min(
                self.portal.y() + (self.portal.height() - self.height()) // 2,
                geom.bottom() - self.height() + 1))
            dx, dy = target_x - self.x(), target_y - self.y()
            self.home_steps += 1
            touching_door = self.geometry().intersects(self.portal.geometry())
            if (abs(dx) <= 5 and abs(dy) <= 5) or (touching_door and
                    abs(dx) <= 16 and abs(dy) <= 16) or self.home_steps > 500:
                self.going_home = False
                self.home_steps = 0
                self.persist()
                send_desktop_pet_home(self.state)
                self.buddy.sync_presence()
                self.hide()
                self.state.save()
                if self.house_dialog and self.house_dialog.isVisible():
                    self.house_dialog.refresh()
            else:
                self.facing = 1 if dx >= 0 else -1
                self.move(self.x() + max(-3, min(3, dx)), self.y() + max(-3, min(3, dy)))
            self.update()
            return
        if active is False:
            self.update()
            return
        if self.cursor_chaser_id == self.state.desktop_pet_id:
            self.update()
            return
        if self.active_roaming() and not self.active_sleeping() and not self.dragging:
            if self.pair_interaction == "chase" and self.frame % 42 == 0:
                self.facing *= -1
            if self.pair_interaction in ("nuzzle","greet","highfive","share_snack"):
                self.update()
                return
            if self.idle_ticks > 0:
                self.idle_ticks -= 1
            else:
                geom = QApplication.primaryScreen().availableGeometry()
                speed = 3 if self.pair_interaction in ("chase","dance") else 2
                next_x = self.x() + self.facing * speed
                if next_x < geom.left() or next_x > geom.right() - self.width():
                    self.facing *= -1
                    self.idle_ticks = 18
                else:
                    self.move(next_x, self.y())
                    if random.random() < 0.004:
                        self.idle_ticks = random.randint(18, 70)
                    if not self.pair_interaction and random.random() < .00018:
                        self.send_home()
        self.update()

    def update_needs(self) -> None:
        self.state.advance()
        if not (self.house_dialog and self.house_dialog.isVisible()):
            # Real household feeding continues while the cottage window is closed.
            # Only placed, stocked bowls can feed pets that are actually indoors.
            house_feed_cycle(self.state, require_near=False)
        if self.state.location == "house" and self.state.egg_hatched:
            self.state.energy = clamp(self.state.energy + .25)
            self.state.happiness = clamp(self.state.happiness + .1)
        self.persist()
        if self.console and self.console.isVisible():
            self.console.refresh()
        if self.house_dialog and self.house_dialog.isVisible():
            self.house_dialog.update_friendship()

    def persist(self) -> None:
        if hasattr(self, "buddy"):
            self.buddy.persist()
        selected = current_pet(self.state)
        if isinstance(selected, dict):
            selected["desktop_x"], selected["desktop_y"] = self.x(), self.y()
        elif selected is None:
            self.state.x, self.state.y = self.x(), self.y()
        self.state.save()

    def open_console(self) -> None:
        if self.console is None:
            self.console = CareConsole(self)
        if current_pet(self.state) is not False:
            self.console.selected_id = self.state.desktop_pet_id
        self.console.refresh()
        self.console.show()
        self.console.raise_()
        self.console.activateWindow()

    def care(self, action: str) -> None:
        state = self.state
        state.advance()
        if action == "sleep":
            state.sleeping = not state.sleeping
        elif state.sleeping:
            if self.console:
                self.console.tip.setText("Shh! Wake your little buddy before playing.")
            return
        elif action == "feed":
            state.hunger = clamp(state.hunger + 27)
            state.happiness = clamp(state.happiness + 4)
            state.cleanliness = clamp(state.cleanliness - 5)
            state.times_fed += 1
        elif action == "play":
            self.open_games()
            return
        elif action == "clean":
            state.cleanliness = clamp(state.cleanliness + 42)
            state.happiness = clamp(state.happiness + 5)
        self.persist()
        self.update()
        if self.console:
            self.console.tip.setText({
                "feed": "Nom nom! Your pet loved that snack.",
                "clean": "Squeaky clean! No suspicious smells remain.",
                "sleep": "Sweet dreams!" if state.sleeping else "Rise and shine!",
            }.get(action, ""))
            self.console.refresh()

    def toggle_roaming(self) -> None:
        selected = current_pet(self.state)
        if isinstance(selected, dict):
            selected["roaming"] = not selected.get("roaming", True)
        elif selected is None:
            self.state.roaming = not self.state.roaming
        self.persist()
        if self.console:
            self.console.refresh()

    def change_color(self, color: str) -> None:
        if color in PALETTES:
            self.state.color = color
            self.persist()
            if self.tray:
                self.tray.setIcon(self._icon())
            self.update()

    def mousePressEvent(self, event) -> None:
        self.stop_cursor_chase(celebrate=False)
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start = event.globalPosition().toPoint()
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
            self.dragging = False
        elif event.button() == Qt.MouseButton.RightButton:
            menu = QMenu(self)
            menu.addAction("♥ Care for pet", self.open_console)
            menu.addAction("⌂ Walk home", self.send_home)
            menu.addAction("🐾 Chase pointer", lambda: self.start_cursor_chase(manual=True))
            if self.buddy.isVisible():
                menu.addAction("🎾 Play together", lambda: self.start_pair_interaction("play"))
                menu.addAction("♡ Nuzzle", lambda: self.start_pair_interaction("nuzzle"))
            if self.cuddle_mode:
                menu.addAction("Cancel cuddle mode", self.open_cuddles)
            menu.addAction("Pause / resume walking", self.toggle_roaming)
            menu.addSeparator()
            menu.addAction("Quit GhostPet", QApplication.quit)
            menu.exec(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event) -> None:
        if self.drag_start is not None and event.buttons() & Qt.MouseButton.LeftButton:
            if (event.globalPosition().toPoint() - self.drag_start).manhattanLength() > 6:
                self.dragging = True
                self.move(event.globalPosition().toPoint() - self.drag_offset)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.drag_start is not None:
            self.drag_start = None
            if self.dragging:
                self.dragging = False
                self.persist()
            else:
                if not self.state.egg_hatched:
                    self.tap_egg()
                elif self.cuddle_mode:
                    self.pat_directly()
                else:
                    self.open_console()

    def closeEvent(self, event) -> None:
        self.persist()
        self.buddy.close()
        super().closeEvent(event)
        QApplication.quit()


def claim_single_instance_lock():
    """Prevent two desktop pets from loading and writing the same save at once."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    handle = (DATA_DIR / ".ghostpet-running.lock").open("a+")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        return None
    return handle


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)
    # Keep this open for the process lifetime. The OS releases the file lock
    # automatically when the app exits for updates or shutdown.
    instance_lock = claim_single_instance_lock()
    if instance_lock is None:
        QMessageBox.information(
            None, "Ghost Pet is already running",
            "Ghost Pet is already open. Click the existing desktop pet or "
            "its tray icon to open Pocket Care.")
        return
    state = PetState.load()
    pet = RoamingPet(state)
    if current_pet(state) is not False:
        pet.show()
    app.aboutToQuit.connect(pet.persist)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
