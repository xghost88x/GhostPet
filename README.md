# GhostPet v0.3 — Little Haunted House for Zorin OS

A tiny original pixel creature that wanders around the desktop. Left-click it
to bring up a retro-styled care console; right-click for its menu; drag to move.
It works entirely offline and saves its progress locally.

## Features

- Cute animated desktop companion with three selectable colors.
- Retro handheld-style care console: feed, clean, sleep/wake, cuddle and play.
- Two actual minigames: tap moving stars against a timer, or repeat light sequences.
- Cuddle directly on the roaming pet! Select **Pet Directly** in the care console,
  then click the pet five times. Hearts and little speech bubbles show progress.
  The fifth pat gives affection rewards and automatically exits cuddle mode.
  Right-click the pet to cancel early, or press the console cuddle button again.
- Age-based speech bubbles from baby noises to sentences (age is measured in real days).
- Playable top-down pixel-art house with four connected rooms, doors, furniture,
  click-to-walk pathfinding, autonomous roaming and a separate Decorate mode.
- Start with 200 coins; existing saves receive a one-time housewarming top-up
  to at least 200 coins when first opening the v0.3 house.
- Saves affection, personality, coins, furniture and game progress alongside v0.1 state.
- Needs slowly change in real time, including while the app is closed.
- Hatchling → Youngling → Companion stages.
- Rename pet, pause/resume walking, drag anywhere; close the console to keep it roaming.
- Optional tray menu where a tray is available. It never installs a GNOME extension.
- Your pet *never dies from neglect* in this first cozy release.

## Install on Zorin

1. Unzip this folder somewhere permanent (for example `~/Applications/GhostPet`).
2. In a terminal, navigate into that folder.
3. Run:

   ```bash
   sudo apt install python3-venv libxcb-cursor0
   chmod +x start.sh
   ./start.sh
   ```

The first launch creates a private Python environment and installs PySide6
from PyPI, which needs internet access. Later launches reuse it.

## Using it

- **Click** the pet: care console.
- **Drag** the pet: move to another location.
- **Right-click** the pet: care, pause, quit.
- **Close** the console: pet keeps walking.
- **Quit** from the pet's menu to exit completely.

The pet state lives at `~/.local/share/ghostpet/state.json`. The folder containing
this file is safe to back up. Moving or deleting the app folder does not erase
your saved pet state. **Back it up before upgrading.** GhostPet v0.2 reads the
v0.1 save and fills in new fields automatically; v0.1 does not understand all
the new features. The house has four small connected rooms. Switch between
**Explore** and **Decorate** at the top: in Explore mode, click any walkable
floor tile to send your pet there; in Decorate mode, choose an item and click
a floor tile to place it. Right-click a furnished tile to store its item.
Furniture is unlocked once using coins, then can be placed again freely.
Old six-column v0.2 house arrangements are migrated to the new floor plan.

## Desktop shortcut (optional, after first launch works)

Create a launcher through Zorin's menu editor, targeting the absolute path to
`start.sh`. Set its working directory to the folder containing the script.
The startup-at-login option can be added in Zorin's **Startup Applications**.

## Platform note

Designed for X11 or GNOME with XWayland. Floating windows cannot freely position
themselves on a pure Wayland compositor; the launcher requests Qt's X11 backend
to support roaming. Test it under your Zorin session before enabling autostart.

## Limitations and next ideas

This is an early playable build, not yet a full Giga Pet remake. The house
now includes an original code-drawn pixel environment with a walking pet,
but furniture animations and interactions are still limited. Multiple pets,
eggs, species breeding, accessories, sounds,
and fully animated furniture interactions are planned for future versions.
No copyrighted Tamagotchi sprites are bundled.
