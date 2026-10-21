GHOSTPET WINDOWS TESTER BETA
============================

This is an early Windows build of a desktop pet game, shared for testing.
No Python installation or administrator permission is required.

INSTALL
1. Download the official GhostPet-Windows-Testers.zip from this project's
   GitHub Releases page.
2. Right-click the ZIP -> Extract All. Do NOT run from inside the ZIP.
3. Double-click Install-Windows.cmd in the extracted folder.
4. The installer copies GhostPet.exe, GhostPetUpdater.exe and VERSION
   to your local user folder and makes Desktop and Start Menu shortcuts.
5. GhostPet opens. Hatch and name your first pet!

If Windows SmartScreen warns about an unknown publisher, this tester executable
is not code-signed. Verify that you downloaded it from the official
xghost88x/GhostPet GitHub Releases page. Never disable antivirus globally.

CLEAN START
- Your first new Windows save gets 600 coins.
- No developer pets, previous playthroughs, preview bonus or custom inventory.
- A different Windows user gets a different pet household.
- Saves: %LOCALAPPDATA%\GhostPet\state.json
- Uninstalling the app files does not automatically delete your pet saves.

UPDATE
- Use Pocket Care -> Update. GhostPet exits and a separate small updater
  checks the published Windows tester beta on GitHub.
- The updater verifies the downloaded release SHA256 digest and upgrades the
  app without overwriting state.json, pet friendships, coins or room purchases.
- Click Launch GhostPet after a successful update.
- Alternatively download and extract a newer tester ZIP, close GhostPet,
  and run Install-Windows.cmd again. Your existing saved pets remain.

GAME TIPS
- Invite a second pet from Pocket Care so they can roam together.
- Toggle automatic social antics and cursor chasing in Pocket Care.
- Your pet's cottage has distinct room layouts, furniture, and refillable bowls.
- Right-click either pet for extra actions, including pointer chase.
- Quit via pet menu or system tray; closing Pocket Care does NOT quit the pet.

KNOWN BETA LIMITATIONS
- Windows 10/11 64-bit only.
- Unsigned executables may produce Windows SmartScreen warnings.
- Floating topmost windows and cursor interactions can vary by Windows
  version, multi-monitor position, taskbar alignment and display scaling.
- No automatic background download/update; updates are requested by the user.
- A published GitHub Windows beta release is required for the Update button.
- Please report bugs and reproduction details on the GitHub Issues page.

PROJECT
https://github.com/xghost88x/GhostPet
