"""GhostPet v0.5 nursery: adopt a new species without replacing the founder."""
from __future__ import annotations
import random
import time
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QInputDialog, QMessageBox

SPECIES = ("Ghost", "Cat", "Dog", "Bunny", "Fox", "Dragon")
MAX_PETS = 6

class NurseryDialog(QDialog):
    def __init__(self, state, save, parent=None):
        super().__init__(parent)
        self.state, self.save = state, save
        self.setWindowTitle("GhostPet • Adoption Nursery")
        self.setMinimumWidth(370)
        self.setStyleSheet("""
            QDialog { background:#292d46; color:#f8eafa; }
            QLabel { color:#f8eafa; font-size:14px; }
            QPushButton { background:#59668d; color:white; border:2px solid #8597c4;
                border-radius:9px; padding:10px; font-weight:bold; }
            QPushButton:hover { background:#8176af; }
        """)
        self.layout = QVBoxLayout(self)
        self.header = QLabel("🥚 Adoption Nursery")
        self.layout.addWidget(self.header)
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        self.layout.addWidget(self.summary)
        self.pet_list = QLabel()
        self.pet_list.setWordWrap(True)
        self.layout.addWidget(self.pet_list)
        self.adopt_button = QPushButton("🥚 Adopt an egg (30 coins)")
        self.adopt_button.clicked.connect(self.adopt)
        self.layout.addWidget(self.adopt_button)
        self.hatch_button = QPushButton("💕 Warm the egg")
        self.hatch_button.clicked.connect(self.warm_egg)
        self.layout.addWidget(self.hatch_button)
        self.message = QLabel("Your original pet is always protected.")
        self.message.setWordWrap(True)
        self.layout.addWidget(self.message)
        self.refresh()

    def refresh(self):
        pets = self.state.adopted_pets
        self.summary.setText(f"🪙 {self.state.coins} coins  •  Household {len(pets)+1}/{MAX_PETS} pets")
        founder = "🌟 Founder" if self.state.founder else "Original companion"
        lines = [f"🐾 {self.state.name} — {founder} ({self.state.species})"]
        lines += [f"💕 {p.get('name','Buddy')} — {p.get('species','Ghost')}" for p in pets]
        self.pet_list.setText("\n".join(lines))
        self.hatch_button.setVisible(self.state.nursery_egg_taps >= 0)
        self.hatch_button.setText(f"💕 Warm the egg ({self.state.nursery_egg_taps}/5)")
        self.adopt_button.setEnabled(self.state.nursery_egg_taps < 0 and len(pets) + 1 < MAX_PETS)

    def adopt(self):
        if self.state.nursery_egg_taps >= 0:
            self.message.setText("One egg at a time! Warm the egg first.")
            return
        if len(self.state.adopted_pets)+1 >= MAX_PETS:
            self.message.setText("Your house is full (6 pets maximum).")
            return
        if self.state.coins < 30:
            self.message.setText("Play minigames to earn 30 coins!")
            return
        self.state.coins -= 30
        self.state.nursery_egg_taps = 0
        self.save()
        self.message.setText("A tiny egg! Give it five gentle taps. ♡")
        self.refresh()

    def warm_egg(self):
        if self.state.nursery_egg_taps < 0:
            return
        if self.state.nursery_egg_taps < 4:
            self.state.nursery_egg_taps += 1
            self.save()
            self.message.setText(random.choice(["The egg wiggles! ♡","Tap tap...","A tiny crack appears!"]))
            self.refresh()
            return
        species, ok = QInputDialog.getItem(self, "Hatching!", "Choose a species:", SPECIES, 0, False)
        if not ok:
            return
        name, named = QInputDialog.getText(self, "Name your new pet", "Pet name:", text=species)
        if not named:
            return
        self.state.adopted_pets.append({
            "id": f"pet-{time.time_ns()}",
            "name": (name.strip() or species)[:18],
            "species": species,
            "born": time.time(),
            "x": random.randint(9,15),
            "y": random.randint(7,10),
            "trait": random.choice(["Playful", "Curious", "Cuddly", "Mischievous"]),
            "hunger": 88,
            "happiness": 82,
            "cleanliness": 95,
            "energy": 87,
            "affection": 30,
            "sleeping": False,
        })
        self.state.nursery_egg_taps = -1
        self.save()
        self.message.setText("Welcome home, little one! Visit the house to meet them. ♡")
        self.refresh()
