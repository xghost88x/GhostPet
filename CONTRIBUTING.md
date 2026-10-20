# Contributing to GhostPet

GhostPet is a small offline PySide6 desktop pet, developed primarily for Zorin OS.

## Local development

1. Install Python 3.10+ and create a virtual environment.
2. Install `pip install -r requirements.txt`.
3. Run `python ghostpet.py` from an X11/XWayland desktop session.
4. Run `python -m compileall -q ghostpet.py activities.py house.py` before submitting a change.

Please keep saved-state migration backward-compatible, protect user save files,
and keep gameplay offline unless an optional online feature is explicitly added.

This project is licensed under MIT; contributions are made under that license.
