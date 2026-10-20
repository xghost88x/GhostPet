#!/usr/bin/env python3
"""GhostPet: a tiny offline pixel pet for Linux desktops.

Requires PySide6. Designed for GNOME/X11 (or XWayland) on Zorin OS.
"""

from __future__ import annotations

import json
import math
import os
import random
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
from house import HouseDialog


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

    @classmethod
    def load(cls) -> "PetState":
        now = time.time()
        allowed = {f.name for f in fields(cls)}
        try:
            values = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            state = cls(**{key: value for key, value in values.items() if key in allowed})
            if "egg_hatched" not in values:
                state.egg_hatched = True  # Existing companions stay hatched.
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
        pix(0, 6, 5, 5, shaded)
        pix(16, 6, 4, 5, shaded)
        pix(9, 12, 3, 2, outline)
    elif state.species == "Fox":
        pix(0, 13, 4, 3, shaded)
        pix(16, 13, 4, 3, shaded)
        pix(7, 14, 6, 2, cream)
    elif state.species == "Dragon":
        pix(0, 8, 4, 7, shaded)
        pix(16, 8, 4, 7, shaded)
        pix(9, 1, 2, 4, cream)
    elif state.species == "Ghost":
        pix(2, 16, 3, 3, main)
        pix(15, 16, 3, 3, main)
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
        p = QPainter(self)
        p.fillRect(9, 37, 63, 54, QColor("#35314e"))
        p.fillRect(16, 43, 50, 41, QColor("#c9b1e8"))
        p.fillRect(3, 32, 75, 12, QColor("#74588f"))
        p.fillRect(15, 19, 55, 14, QColor("#8f6dad"))
        p.fillRect(27, 58, 25, 32, QColor("#49405e"))
        p.fillRect(33, 63, 12, 21, QColor("#ab90d0"))
        p.fillRect(58, 54, 7, 9, QColor("#f5e6ab"))
        p.setPen(QColor("#fff3fc"))
        p.setFont(QFont("Sans", 9, QFont.Weight.Bold))
        p.drawText(15, 14, "HOME")
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


class CareConsole(QDialog):
    def __init__(self, pet: "RoamingPet"):
        super().__init__()
        self.pet = pet
        self.setWindowTitle("GhostPet • Pocket Care Console")
        self.setMinimumWidth(380)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setObjectName("console")
        self.setStyleSheet("""
            QDialog#console { background: #282b43; color: #ecf5f3; }
            QLabel { color: #ecf5f3; }
            QLabel#heading { color: #f8bed8; font-size: 19px; font-weight: 900; }
            QLabel#subheading { color: #9cead5; font-size: 12px; letter-spacing: 1px; }
            QLabel#status { color: #263f3b; font-size: 15px; font-weight: 800; }
            QLabel#metric { color: #dbe7ef; font-weight: bold; }
            QWidget#lcd { background: #b7d8ad; border: 7px solid #45566e; border-radius: 9px; }
            QPushButton { background: #5b6389; border: 2px solid #8994bd; border-radius: 11px;
                          color: white; padding: 11px; font-weight: bold; }
            QPushButton:hover { background: #737da8; }
            QPushButton:pressed { background: #394363; }
            QProgressBar { color: #edf9ff; background: #454b67; border-radius: 6px;
                           height: 15px; text-align: center; }
            QProgressBar::chunk { background: #53cdb5; border-radius: 6px; }
            QComboBox { background: #4a526e; color: white; border-radius: 5px; padding: 5px; }
        """)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 17, 20, 18)
        outer.setSpacing(11)

        header = QLabel("✦  GHOSTPET  //  POCKET CARE")
        header.setObjectName("heading")
        outer.addWidget(header)
        subtitle = QLabel("CLASSIC VIRTUAL COMPANION  •  V0.2")
        subtitle.setObjectName("subheading")
        outer.addWidget(subtitle)

        lcd = QWidget()
        lcd.setObjectName("lcd")
        lcd_layout = QVBoxLayout(lcd)
        lcd_layout.setContentsMargins(4, 2, 4, 5)
        self.display_sprite = PetSprite(pet.state, size=142)
        lcd_layout.addWidget(self.display_sprite, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.status = QLabel()
        self.status.setObjectName("status")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lcd_layout.addWidget(self.status)
        outer.addWidget(lcd)

        self.stats: dict[str, QProgressBar] = {}
        for label, attribute in (("🍓  Fullness", "hunger"),
                                 ("♥  Happiness", "happiness"),
                                 ("✧  Cleanliness", "cleanliness"),
                                 ("☾  Energy", "energy")):
            row = QHBoxLayout()
            name = QLabel(label)
            name.setObjectName("metric")
            name.setFixedWidth(113)
            bar = QProgressBar()
            bar.setRange(0, 100)
            row.addWidget(name)
            row.addWidget(bar)
            outer.addLayout(row)
            self.stats[attribute] = bar

        buttons = QGridLayout()
        for index, (label, action) in enumerate((
            ("🍓  FEED", "feed"), ("🎮  PLAY", "play"),
            ("🧼  CLEAN", "clean"), ("💤  SLEEP / WAKE", "sleep"),
        )):
            button = QPushButton(label)
            button.clicked.connect(lambda _checked=False, a=action: self.pet.care(a))
            buttons.addWidget(button, index // 2, index % 2)
        outer.addLayout(buttons)

        activity_row = QHBoxLayout()
        for label, callback in (("♥ PET DIRECTLY", self.pet.open_cuddles),
                                ("⌂ LITTLE HOUSE", self.pet.open_house)):
            button = QPushButton(label)
            button.clicked.connect(callback)
            activity_row.addWidget(button)
        outer.addLayout(activity_row)
        self.personality_label = QLabel()
        self.personality_label.setWordWrap(True)
        outer.addWidget(self.personality_label)

        footer = QHBoxLayout()
        rename = QPushButton("✎ Rename")
        rename.clicked.connect(self.rename_pet)
        footer.addWidget(rename)
        self.roaming_button = QPushButton()
        self.roaming_button.clicked.connect(self.pet.toggle_roaming)
        footer.addWidget(self.roaming_button)
        outer.addLayout(footer)

        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("Shell color:"))
        self.colors = QComboBox()
        self.colors.addItems(list(PALETTES))
        self.colors.setCurrentText(self.pet.state.color)
        self.colors.currentTextChanged.connect(self.pet.change_color)
        color_row.addWidget(self.colors)
        outer.addLayout(color_row)

        self.tip = QLabel("Click the little pet to open this console anytime.")
        self.tip.setWordWrap(True)
        self.tip.setStyleSheet("color: #b5bed4; font-size: 11px;")
        outer.addWidget(self.tip)
        self.refresh()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1000)

    def rename_pet(self) -> None:
        name, accepted = QInputDialog.getText(self, "Name your pet", "Pet name:", text=self.pet.state.name)
        if accepted and name.strip():
            self.pet.state.name = name.strip()[:18]
            self.pet.persist()
            self.refresh()

    def refresh(self) -> None:
        state = self.pet.state
        self.status.setText(f"{state.name}  •  {'Egg' if not state.egg_hatched else state.species}  •  {state.mood}")
        self.personality_label.setText(
            f"♥ Affection {round(state.affection)}%  •  Personality: {state.personality}\n"
            f"Age {state.age_days} days  •  {state.coins} coins  •  Cuddles {state.cuddles}")
        for stat, bar in self.stats.items():
            bar.setValue(round(getattr(state, stat)))
        self.roaming_button.setText("⏸ Pause walking" if state.roaming else "▶ Resume walking")
        self.display_sprite.frame = self.pet.frame
        self.display_sprite.update()


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
        self.going_home = False
        self.bubble_text = ""
        self.bubble_until = 0.0
        self.setWindowTitle("GhostPet")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool |
                            Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setFixedSize(124, 116)
        self.setToolTip("Left-click to care • Drag to move • Right-click for menu")

        screen = QApplication.primaryScreen().availableGeometry()
        start_x = state.x if 0 <= state.x <= screen.right() else screen.center().x()
        start_y = state.y if 0 <= state.y <= screen.bottom() else screen.bottom() - self.height()
        self.move(start_x, start_y)
        self.portal = HomePortal(self)
        self.portal.show()
        if state.location == "house":
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
        draw_pet(painter, self.width(), self.height(), self.state,
                 self.frame, scale=4, facing=self.facing)
        if self.state.sleeping:
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

    def maybe_speak(self) -> None:
        if self.state.egg_hatched and self.state.location == "desktop" and not self.state.sleeping and random.random() < .65:
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

    def open_cuddles(self) -> None:
        if self.state.sleeping or not self.state.egg_hatched:
            self.say("Zzz...")
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
            self.console.tip.setText("Click the roaming pet five times to cuddle; right-click to cancel.")
        self.update()

    def pat_directly(self) -> None:
        if not self.cuddle_mode:
            return
        self.cuddle_taps += 1
        if self.cuddle_taps >= 5:
            self.cuddle_mode = False
            self.cuddle_taps = 0
            self.activity_reward("cuddle", 5)
            if self.console:
                self.console.tip.setText("Cuddle complete! Your buddy feels loved. ♥")
        else:
            self.say(random.choice(["♥", "Eee! ♡", "More!", "hehe ♡"]))
        self.update()

    def open_house(self) -> None:
        if self.house_dialog and self.house_dialog.isVisible():
            self.house_dialog.raise_()
            return
        self.house_dialog = HouseDialog(self.state, self.persist,
                                        self.return_from_house, self.send_home, self)
        self.house_dialog.show()

    def return_from_house(self) -> None:
        self.state.location = "desktop"
        self.going_home = False
        self.move(self.portal.x() - 55, self.portal.y())
        self.show()
        self.say("I'm baaaack! ♡")
        self.persist()

    def send_home(self) -> None:
        if self.state.egg_hatched and self.state.location == "desktop":
            self.going_home = True
            self.state.roaming = True
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
        if self.going_home and self.state.location == "desktop":
            target_x = self.portal.x() + 12
            target_y = self.portal.y() + 18
            dx, dy = target_x - self.x(), target_y - self.y()
            if abs(dx) <= 3 and abs(dy) <= 3:
                self.going_home = False
                self.state.location = "house"
                self.hide()
                self.persist()
                if self.house_dialog and self.house_dialog.isVisible():
                    self.house_dialog.refresh()
            else:
                self.facing = 1 if dx >= 0 else -1
                self.move(self.x() + max(-3, min(3, dx)), self.y() + max(-3, min(3, dy)))
            self.update()
            return
        if self.state.roaming and not self.state.sleeping and not self.dragging:
            if self.idle_ticks > 0:
                self.idle_ticks -= 1
            else:
                geom = QApplication.primaryScreen().availableGeometry()
                next_x = self.x() + self.facing * 2
                if next_x < geom.left() or next_x > geom.right() - self.width():
                    self.facing *= -1
                    self.idle_ticks = 18
                else:
                    self.move(next_x, self.y())
                    if random.random() < 0.004:
                        self.idle_ticks = random.randint(18, 70)
                    if self.state.egg_hatched and random.random() < .00018:
                        self.send_home()
        self.update()

    def update_needs(self) -> None:
        self.state.advance()
        if self.state.location == "house" and self.state.egg_hatched:
            self.state.energy = clamp(self.state.energy + .25)
            self.state.happiness = clamp(self.state.happiness + .1)
        self.persist()
        if self.console and self.console.isVisible():
            self.console.refresh()

    def persist(self) -> None:
        self.state.x, self.state.y = self.x(), self.y()
        self.state.save()

    def open_console(self) -> None:
        if self.console is None:
            self.console = CareConsole(self)
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
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start = event.globalPosition().toPoint()
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
            self.dragging = False
        elif event.button() == Qt.MouseButton.RightButton:
            menu = QMenu(self)
            menu.addAction("♥ Care for pet", self.open_console)
            menu.addAction("⌂ Walk home", self.send_home)
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
        super().closeEvent(event)
        QApplication.quit()


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)
    state = PetState.load()
    pet = RoamingPet(state)
    if state.location == "desktop":
        pet.show()
    app.aboutToQuit.connect(pet.persist)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
