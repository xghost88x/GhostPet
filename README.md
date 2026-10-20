# GhostPet v0.5.1 Preview — Founder Mouse & Woodland Cottage

A tiny original pixel creature that wanders around the desktop. Left-click it
to bring up a retro-styled care console; right-click for its menu; drag to move.
It works entirely offline and saves its progress locally.

## What's new in v0.5.1

- Founder companions now have their own compact mouse-style pixel sprite (no oversized side appendages).
- The Little House uses a warm, normal **Woodland Cottage** aesthetic with continuous pine floors, rugs, windows and trim instead of checkerboard floor tiles. Navigation and furniture saves are unchanged. Halloween remains a future optional seasonal theme.

## What's new in v0.5

Your original saved companion is marked with a 🌟 Founder star and is never overwritten by adopting another pet. Open the care console and select **Adoption Nursery**, buy an egg for 30 coins, then warm it five times to hatch a Ghost, Cat, Dog, Bunny, Fox, or Dragon. Name the hatchling, then open the Little House to see it explore. Up to six pets can live together. Housemate desktop roaming, breeding, and detailed artwork are not yet included.

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
- New players begin with a pixel egg: click it five times to hatch, then choose
  Ghost, Cat, Dog, Bunny, Fox, or Dragon. Existing saves remain hatched.
- Movable house entrance on the desktop. Right-click the pet and choose **Walk
  home**, or open its house and choose **Walk inside**. The pet physically walks
  toward the entrance, disappears from the desktop, then appears inside.
- From the house, choose **Visit desktop** to let the pet walk outside again.
- One live location per pet: it is not simultaneously rendered inside and out.
- Indoor position is remembered when you close the house window. Basic rest and
  happiness continue while your pet is indoors, even with the window closed;
  detailed room-by-room routines are still a future feature.
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
- **Drag** the small house entrance to reposition it on the desktop; click to
  open the interior. The entrance remains when your pet is indoors.
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
but furniture animations and interactions are still limited. Independent multi-pet desktop roaming,
species breeding, accessories, sounds,
and fully animated furniture interactions are planned for future versions.
No copyrighted Tamagotchi sprites are bundled.
