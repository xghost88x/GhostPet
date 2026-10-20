"""Offline interactive activities and the first little-house prototype."""
import random

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QDialog, QGridLayout, QHBoxLayout, QLabel,
                               QPushButton, QVBoxLayout, QWidget)


STYLE = """QDialog { background:#292d46; color:#f8eafa; }
QLabel { color:#f8eafa; font-size:14px; }
QPushButton { background:#59668d; color:white; border:2px solid #8597c4;
border-radius:9px; padding:12px; font-size:14px; font-weight:bold; }
QPushButton:hover { background:#8176af; }
QPushButton:disabled { background:#393e55; color:#8b91a4; }"""


def pick_speech(state, context="idle"):
    """Age gates plus disposition; entirely local, no generated network text."""
    age = state.age_days
    if age < 4:
        return random.choice(["bloop!", "mrrp?", "eep!", "♡", "boop boop"])
    if age < 10:
        return random.choice(["ba-ba?", "mama?", "bwoo!", "he-he!", "nom nom!"])
    if age < 20:
        return random.choice(["play?", "hugs!", "you!", "hi hi!", "more?", "luv you!"])
    if age < 40:
        phrases = ["Play with me?", "You're my friend!", "More hugs?", "I found a thing!"]
    else:
        phrases = ["I missed you!", "This is our little world.",
                   "I definitely didn't eat the moon.", "Can we have a snack?"]
    if context == "cuddle":
        phrases += ["Best hugs ever!", "Stay a little longer?", "♡♡♡"]
    elif context == "play":
        phrases += ["Again! Again!", "That was FUN!", "I almost won!"]
    if state.personality == "Mischievous":
        phrases += ["I did a thing...", "You saw NOTHING."]
    elif state.personality == "Cuddly":
        phrases += ["You're my favorite human.", "Cuddle time?"]
    elif state.personality == "Curious":
        phrases += ["What's that?", "Why is the cursor moving?"]
    elif state.personality == "Playful":
        phrases += ["Catch me!", "Let's play again!"]
    return random.choice(phrases)


class GameDialog(QDialog):
    def __init__(self, reward, parent=None):
        super().__init__(parent)
        self.reward = reward
        self.setWindowTitle("GhostPet • Arcade")
        self.setStyleSheet(STYLE)
        self.setMinimumWidth(390)
        self.layout = QVBoxLayout(self)
        self.heading = QLabel("🎮 Pick a little game!")
        self.layout.addWidget(self.heading)
        self.area = QWidget()
        self.grid = QGridLayout(self.area)
        self.layout.addWidget(self.area)
        self.message = QLabel("Win coins and grow your pet's personality.")
        self.message.setWordWrap(True)
        self.layout.addWidget(self.message)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.mode = None
        self.turns = 0
        self.score = 0
        self.sequence = []
        self.index = 0
        self.buttons = []
        self._menu()

    def _clear(self):
        self.timer.stop()
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.buttons = []

    def _menu(self):
        self._clear()
        self.mode = None
        self.heading.setText("🎮 GhostPet Arcade")
        for i, (text, fn) in enumerate((("🎯 Catch the Star", self._catch),
                                         ("🧠 Memory Lights", self._memory))):
            button = QPushButton(text)
            button.clicked.connect(fn)
            self.grid.addWidget(button, i, 0)
        self.message.setText("Both games need your clicks; prizes depend on your score.")

    def _finish(self):
        self.timer.stop()
        mode = self.mode
        score = self.score
        self._clear()
        self.heading.setText("✨ Round complete!")
        self.message.setText(f"Score: {score} • Earned {max(2, score * 2)} coins!")
        self.reward(mode, score)
        back = QPushButton("Play another game")
        back.clicked.connect(self._menu)
        self.grid.addWidget(back, 0, 0)

    def _catch(self):
        self._clear()
        self.mode = "catch"
        self.score = 0
        self.turns = 0
        self.heading.setText("🎯 Catch the star! 10 seconds")
        for i in range(12):
            button = QPushButton("·")
            button.setMinimumHeight(53)
            button.clicked.connect(lambda checked=False, slot=i: self._hit(slot))
            self.grid.addWidget(button, i // 4, i % 4)
            self.buttons.append(button)
        self.target = -1
        self._move_target()
        self.timer.start(1000)

    def _move_target(self):
        self.target = random.randrange(12)
        for i, button in enumerate(self.buttons):
            button.setText("⭐" if i == self.target else "·")

    def _hit(self, slot):
        if slot == self.target:
            self.score += 1
            self.message.setText(f"Caught {self.score} stars! Keep going!")
            self._move_target()

    def _tick(self):
        self.turns += 1
        if self.turns >= 10:
            self._finish()
        else:
            self.heading.setText(f"🎯 Catch the star! {10-self.turns} seconds")
            self._move_target()

    def _memory(self):
        self._clear()
        self.mode = "memory"
        self.score = 0
        self.sequence = []
        self.index = 0
        self.heading.setText("🧠 Repeat the lights")
        for i, symbol in enumerate(("🌸", "⭐", "🍀", "💜")):
            button = QPushButton(symbol)
            button.setMinimumHeight(75)
            button.clicked.connect(lambda checked=False, slot=i: self._guess(slot))
            self.grid.addWidget(button, i // 2, i % 2)
            self.buttons.append(button)
        self._next_pattern()

    def _next_pattern(self):
        if self.score >= 5:
            self._finish()
            return
        self.sequence.append(random.randrange(4))
        self.index = 0
        for button in self.buttons:
            button.setEnabled(False)
        self.message.setText("Watch the sequence...")
        QTimer.singleShot(250, lambda: self._show_step(0))

    def _show_step(self, step):
        if self.mode != "memory" or not self.isVisible():
            return
        if step >= len(self.sequence):
            self.message.setText("Your turn! Repeat what you saw.")
            for button in self.buttons:
                button.setEnabled(True)
            return
        slot = self.sequence[step]
        self.buttons[slot].setText("✨✨")
        QTimer.singleShot(550, lambda: self._hide_step(step, slot))

    def _hide_step(self, step, slot):
        if self.mode != "memory" or not self.buttons:
            return
        self.buttons[slot].setText(("🌸", "⭐", "🍀", "💜")[slot])
        QTimer.singleShot(260, lambda: self._show_step(step + 1))

    def _guess(self, slot):
        if slot != self.sequence[self.index]:
            self.message.setText("Oops! Let's see how you did.")
            self._finish()
            return
        self.index += 1
        if self.index == len(self.sequence):
            self.score += 1
            for button in self.buttons:
                button.setEnabled(False)
            QTimer.singleShot(700, self._next_pattern)


class CuddleDialog(QDialog):
    def __init__(self, reward, parent=None):
        super().__init__(parent)
        self.reward = reward
        self.taps = 0
        self.done = False
        self.setWindowTitle("GhostPet • Cuddle Time")
        self.setStyleSheet(STYLE)
        box = QVBoxLayout(self)
        self.label = QLabel("💕 Give your little buddy five gentle pets!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box.addWidget(self.label)
        self.button = QPushButton("👻\n♥ PAT ♥")
        self.button.setMinimumSize(260, 140)
        self.button.clicked.connect(self.pat)
        box.addWidget(self.button)
        self.close_button = QPushButton("✕ Close cuddle time")
        self.close_button.clicked.connect(self.accept)
        box.addWidget(self.close_button)

    def pat(self):
        if self.done:
            return
        self.taps += 1
        self.button.setText(random.choice(["🥹 ♡", "👻 💕", "✨ ♥ ✨", "(づ｡◕‿‿◕｡)づ"]))
        self.label.setText(f"Cuddles: {self.taps}/5")
        if self.taps == 5:
            self.done = True
            self.reward("cuddle", 5)
            self.label.setText("💕 Your pet feels so loved!")
            self.button.setText("♡ HUG COMPLETE ♡")
            self.button.setEnabled(False)
            self.close_button.setText("♡ Done — return to pet")


class HouseDialog(QDialog):
    """Small saved grid; furniture stock will expand in later releases."""
    ITEMS = {"bed": ("🛏️", 0), "toy": ("🧸", 10), "rug": ("🟪", 8),
             "plant": ("🪴", 12), "sofa": ("🛋️", 20), "ball": ("⚽", 6)}

    def __init__(self, state, save, parent=None):
        super().__init__(parent)
        self.state = state
        self.save = save
        self.selected = "bed"
        self.setWindowTitle("GhostPet • Little House")
        self.setStyleSheet(STYLE)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("🏠 Your pet's little house • furniture stays saved"))
        self.coins = QLabel()
        layout.addWidget(self.coins)
        self.grid = QGridLayout()
        layout.addLayout(self.grid)
        self.tiles = []
        for i in range(30):
            button = QPushButton()
            button.setMinimumSize(50, 47)
            button.clicked.connect(lambda checked=False, cell=i: self.place(cell))
            self.grid.addWidget(button, i // 6, i % 6)
            self.tiles.append(button)
        choices = QGridLayout()
        layout.addLayout(choices)
        for index, (item, (emoji, cost)) in enumerate(self.ITEMS.items()):
            button = QPushButton(f"{emoji} {item.title()} ({cost}🪙)")
            button.clicked.connect(lambda checked=False, name=item: self.choose(name))
            choices.addWidget(button, index // 3, index % 3)
        self.note = QLabel("Choose furniture, then tap a tile to place it.")
        layout.addWidget(self.note)
        self.refresh()

    def choose(self, item):
        if item not in self.state.owned_furniture:
            cost = self.ITEMS[item][1]
            if self.state.coins < cost:
                self.note.setText("Not enough coins — play a minigame!")
                return
            self.state.coins -= cost
            self.state.owned_furniture.append(item)
            self.save()
        self.selected = item
        self.note.setText(f"Unlocked/selected {item}. Tap a tile to place it.")
        self.refresh()

    def place(self, cell):
        if not 0 <= cell < 30:
            return
        item = self.selected
        old = next((entry for entry in self.state.furniture if entry.get("cell") == cell), None)
        if old and old.get("item") == item:
            self.state.furniture.remove(old)
            self.note.setText("Furniture moved into storage (no refund).")
        else:
            self.state.furniture = [entry for entry in self.state.furniture if entry.get("cell") != cell]
            self.state.furniture.append({"cell": cell, "item": item})
            self.note.setText(f"Placed {item}!")
        self.save()
        self.refresh()

    def refresh(self):
        self.coins.setText(f"🪙 {self.state.coins} coins  •  Owned: {', '.join(self.state.owned_furniture)}")
        for i, tile in enumerate(self.tiles):
            entry = next((e for e in self.state.furniture if e.get("cell") == i), None)
            item = entry.get("item") if entry else None
            tile.setText(self.ITEMS[item][0] if item in self.ITEMS else "·")
