"""GhostPet's offline top-down pixel house, built entirely with Qt painting."""
from __future__ import annotations

import random
from collections import deque

from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QLabel,
                               QPushButton, QVBoxLayout, QWidget)

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


def path_between(start, goal, blocked=frozenset()):
    """Four-directional shortest walk; returns [] if the target cannot be reached."""
    if goal in WALLS or goal in blocked or not (0 <= goal[0] < W and 0 <= goal[1] < H):
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
                    and next_tile not in WALLS and next_tile not in blocked
                    and next_tile not in previous):
                previous[next_tile] = current
                frontier.append(next_tile)
    return []


class HouseCanvas(QWidget):
    def __init__(self, dialog):
        super().__init__(dialog)
        self.dialog = dialog
        self.setFixedSize(W * TILE, H * TILE)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        x = int(event.position().x()) // TILE
        y = int(event.position().y()) // TILE
        if event.button() == Qt.MouseButton.RightButton:
            self.dialog.remove_item((x, y))
        elif event.button() == Qt.MouseButton.LeftButton:
            self.dialog.tile_clicked((x, y))

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        self.draw_floor(p)
        for entry in self.dialog.state.furniture:
            pos = self.dialog.entry_tile(entry)
            if pos and pos not in WALLS:
                self.draw_furniture(p, pos[0] * TILE, pos[1] * TILE, entry.get("item"))
        if self.dialog.state.location == "house" and self.dialog.state.egg_hatched:
            self.draw_pet(p)
        for housemate in self.dialog.state.adopted_pets or []:
            self.draw_housemate(p, housemate)
        if self.dialog.mode == "Decorate":
            p.setPen(QPen(QColor("#bdb1e0"), 1, Qt.PenStyle.DotLine))
            for x in range(1, W - 1):
                for y in range(1, H - 1):
                    if (x, y) not in WALLS:
                        p.drawRect(x * TILE, y * TILE, TILE, TILE)
        p.end()

    def draw_floor(self, p):
        colors = (("#70587a", "#786282"), ("#76688c", "#7f7194"),
                  ("#8c716d", "#957976"), ("#597b7d", "#628587"))
        for y in range(H):
            for x in range(W):
                room = (2 if y > 6 else 0) + (1 if x > 8 else 0)
                base = colors[room][(x + y) % 2]
                p.fillRect(x * TILE, y * TILE, TILE, TILE, QColor(base))
                if (x, y) in WALLS:
                    p.fillRect(x * TILE, y * TILE, TILE, TILE, QColor("#292b46"))
                    p.fillRect(x * TILE + 2, y * TILE + 2, TILE - 4, 7, QColor("#777397"))
                    p.fillRect(x * TILE + 2, y * TILE + 11, TILE - 4, 17, QColor("#4c496c"))
                elif (x + 3*y) % 7 == 0:
                    p.fillRect(x*TILE + 6, y*TILE + 7, 3, 3, QColor("#ffffff22"))
        p.setFont(QFont("monospace", 9, QFont.Weight.Bold))
        p.setPen(QColor("#f5e1ff"))
        for title, x, y in (("BEDROOM", 2, 1), ("LIVING", 11, 1),
                            ("KITCHEN", 2, 7), ("PLAYROOM", 11, 7)):
            p.drawText(x*TILE, y*TILE+13, title)
        # Four windows with cyan glass, positioned on outer walls.
        for x, y in ((3, 0), (13, 0), (0, 8), (17, 8)):
            p.fillRect(x*TILE + 6, y*TILE + 7, 20, 17, QColor("#8bd4dc"))
            p.fillRect(x*TILE + 15, y*TILE + 7, 3, 17, QColor("#edf9ee"))

    def draw_furniture(self, p, px, py, item):
        if item not in ITEMS:
            return
        color = QColor(ITEMS[item][2])
        outline = QColor("#33334d")
        p.fillRect(px + 4, py + 7, 24, 20, outline)
        p.fillRect(px + 6, py + 9, 20, 16, color)
        if item == "bed":
            p.fillRect(px + 8, py + 10, 16, 7, QColor("#fff4df"))
            p.fillRect(px + 8, py + 19, 16, 4, QColor("#e995b9"))
        elif item == "sofa":
            p.fillRect(px + 8, py + 13, 16, 3, QColor("#d5e8ff"))
            p.fillRect(px + 5, py + 18, 22, 5, QColor("#597ca2"))
        elif item == "rug":
            p.fillRect(px + 8, py + 11, 16, 12, QColor("#e4d3f9"))
        elif item == "plant":
            p.fillRect(px + 11, py + 19, 10, 6, QColor("#bd7d6c"))
            p.fillRect(px + 8, py + 11, 16, 11, QColor("#5caa76"))
        elif item == "toy":
            p.fillRect(px + 10, py + 11, 12, 13, QColor("#b78257"))
            p.fillRect(px + 8, py + 9, 5, 6, QColor("#d8a66e"))
            p.fillRect(px + 20, py + 9, 5, 6, QColor("#d8a66e"))
        elif item == "ball":
            p.fillRect(px + 10, py + 10, 12, 13, QColor("#f6d280"))
            p.fillRect(px + 15, py + 10, 3, 13, QColor("#e69fbd"))
        elif item == "bowl":
            p.fillRect(px + 7, py + 15, 18, 8, QColor("#e7c3ab"))
            p.fillRect(px + 10, py + 15, 12, 3, QColor("#8c5c45"))
        elif item == "lamp":
            p.fillRect(px + 14, py + 15, 4, 9, QColor("#c7c4df"))
            p.fillRect(px + 9, py + 9, 14, 9, QColor("#fff0b0"))

    def draw_housemate(self, p, pet):
        """Small, species-specific pixel silhouettes for nursery pets."""
        x = max(1, min(W-2, int(pet.get("x", 12))))
        y = max(1, min(H-2, int(pet.get("y", 8))))
        px, py = x*TILE+4, y*TILE+4
        species = pet.get("species","Ghost")
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
        x, y = self.dialog.position
        px, py = x*TILE + 3, y*TILE + 2
        species = self.dialog.state.species
        tint = QColor({"Ghost":"#e2ccff", "Cat":"#f3d6a5", "Dog":"#c8a781",
                       "Bunny":"#f4e8de", "Fox":"#f2a773", "Dragon":"#91dcab"}.get(species,"#e2ccff"))
        p.fillRect(px + 4, py + 3, 18, 20, QColor("#262a49"))
        p.fillRect(px + 6, py + 2, 14, 19, tint)
        p.fillRect(px + 4, py + 9, 18, 11, tint)
        p.fillRect(px + 4, py + 20, 6, 4, tint)
        p.fillRect(px + 16, py + 20, 6, 4, tint)
        if species == "Bunny":
            p.fillRect(px + 6, py - 5, 5, 10, tint)
            p.fillRect(px + 18, py - 5, 5, 10, tint)
        elif species in ("Cat", "Fox"):
            p.fillRect(px + 5, py, 5, 6, tint)
            p.fillRect(px + 18, py, 5, 6, tint)
        elif species == "Dragon":
            p.fillRect(px, py + 11, 7, 10, QColor("#5dae83"))
            p.fillRect(px + 22, py + 11, 7, 10, QColor("#5dae83"))
        p.fillRect(px + 9, py + 10, 3, 5, QColor("#28334d"))
        p.fillRect(px + 17, py + 10, 3, 5, QColor("#28334d"))
        p.fillRect(px + 6, py + 15, 3, 2, QColor("#f9a4c5"))
        p.fillRect(px + 20, py + 15, 3, 2, QColor("#f9a4c5"))
        if self.dialog.activity:
            p.setPen(QColor("#fff3cc"))
            p.setFont(QFont("monospace", 10, QFont.Weight.Bold))
            p.drawText(px - 3, py - 1, "♥")


class HouseDialog(QDialog):
    def __init__(self, state, save, return_home, send_home, parent=None):
        super().__init__(parent)
        self.state = state
        self.save = save
        self.return_home = return_home
        self.send_home = send_home
        self.mode = "Explore"
        self.position = (state.house_pet_x, state.house_pet_y)
        if self.position in WALLS or not (0 <= self.position[0] < W and 0 <= self.position[1] < H):
            self.position = (2, 3)
        self.path = []
        self.activity = ""
        self.idle_ticks = 0
        if not self.state.housewarming_granted:
            self.state.coins = max(200, self.state.coins)
            self.state.housewarming_granted = True
            self.save()
        self._migrate_old_room()
        self.setWindowTitle("GhostPet • Little Haunted House v0.3")
        self.setStyleSheet("""QDialog{background:#272a42;color:#f9edf9}
QLabel{color:#f8e9fa;font-size:13px}
QPushButton,QComboBox{background:#59648b;color:white;border:1px solid #9b91c0;
border-radius:6px;padding:8px} QPushButton:hover{background:#8175aa}""")
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
        self.canvas = HouseCanvas(self)
        body.addWidget(self.canvas)
        self.status = QLabel("Click a floor tile to guide your pet between rooms!")
        body.addWidget(self.status)
        self.tick_timer = QTimer(self)
        self.tick_timer.timeout.connect(self.tick)
        self.tick_timer.start(260)
        self.refresh()

    def travel(self):
        if self.state.location == "house":
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
        # Rugs are walkable; large objects occupy their tile.
        return {tile for entry in self.state.furniture
                if entry.get("item") != "rug"
                for tile in [self.entry_tile(entry)] if tile is not None}

    def refresh(self):
        self.balance.setText(f"🪙 {self.state.coins}")
        self.door_button.setText("↗ Visit desktop" if self.state.location == "house" else "⌂ Walk inside")
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
        if tile in WALLS or not (0 <= tile[0] < W and 0 <= tile[1] < H):
            self.status.setText("That's a wall. Try the floor or a doorway.")
            return
        if self.mode == "Decorate":
            self.place_item(tile)
            return
        route = path_between(self.position, tile, self.blocked())
        if route or tile == self.position:
            self.path = route
            self.idle_ticks = 25
            self.status.setText("On my way! 👻")
        else:
            self.status.setText("That tile is blocked; try another destination.")

    def place_item(self, tile):
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
        for pet in self.state.adopted_pets or []:
            if random.random() < .18:
                x, y = int(pet.get("x",12)), int(pet.get("y",8))
                options = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
                options = [(a,b) for a,b in options if 0<a<W-1 and 0<b<H-1
                           and (a,b) not in WALLS and (a,b) not in occupied]
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
                        if (x, y) not in WALLS and (x, y) not in self.blocked()]
            target = random.choice(possible)
            self.path = path_between(self.position, target, self.blocked())
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
