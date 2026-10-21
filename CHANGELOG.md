# Changelog

## v0.6.0-preview — Cozy Cottage & Desktop Pet Selection

- Rework the house's visual rendering with original wood planks, rugs, cozy decor, shelves, windows, plants, warm walls and redesigned little furniture.
- Make the desktop house portal a non-spooky woodland cottage.
- Keep the approved Founder mouse's outdoor sprite untouched and give her a matching small indoor sprite.
- Add Pocket Care's **Bring selected pet to desktop** button with independent saved location and roaming state for adopted pets.
- Keep only one companion outside at a time; the other household pets remain visible inside the cottage.
- Preserve pets, coins, care stats, nursery, house layouts, furniture, and original save structure.
- Add fallback rendering and pet-presence code so the older one-click updater can safely install v0.6.
- Add offscreen Qt GUI smoke tests in addition to pathfinding, updater, save and installer tests.


## v0.5.4-preview — Zorin Launcher & Updates

- Add a friendly original Ghost Pet mouse icon (SVG) and a one-time no-root installer.
- Add app-menu launchers for Ghost Pet and Update Ghost Pet, plus a desktop shortcut where supported.
- Add a compact ↻ Update button in Pocket Care and a separate graphical update center.
- Verify GitHub source revision, validate ZIP paths, and back up pet saves and previous program files before installing updates.
- Preserve the existing Founder mouse, pet stats, house layouts, coins, furniture and local Python environment.
- Add automated launcher installation and update safety tests.


## v0.5.3-preview — Upgradeable Woodland Cottages

- Keep the approved v0.5.1 Founder mouse exactly as it is.
- Add two permanent coin-unlockable floor plans: Open Plan (120 coins) and Sunny Garden (260 coins, requires Open Plan).
- Add floor-plan selector and free switching between unlocked plans directly inside the house.
- Each upgrade opens extra interior wall passages; the garden plan has a sunny conservatory accent.
- Preserve all pet data, coins, nursery state, and furniture inventory, and prevent switches that would conceal placed furniture.
- Test reachability and walking routes through all three layouts.


## v0.5.2-preview — Compact Household Care

- Compact woodland-colored pocket-care console (326 pixels wide) with collapse control.
- Pet dropdown includes adopted pets from existing saved households.
- Feed, play, clean, sleep, and rename the selected adopted pet independently.
- Newly adopted pets now initialize separate care statistics; older adopted pets read safe defaults.
- Founder retains existing minigames, roaming and shell-color controls.


## v0.5.1-preview — Founder Mouse & Woodland Cottage

- Original Founder pets now use an independent small rounded mouse silhouette with no shared-species side arms.
- Redesigned default home as a non-spooky woodland cottage with continuous wood plank floors, cozy rugs, curtains, and warm trim.
- Preserved existing pet states, furniture placements, navigation tiles, and nursery.
- Halloween is reserved as an optional future theme, not the default.


## v0.5.0-preview — Founders & Adoption Nursery

- Existing companions receive a persistent Founder star during save migration.
- Added adoption nursery, egg warming and six starter species (30 coins per egg).
- Up to six pets share the household; existing pet statistics and furniture remain.
- New housemates wander inside the pixel house with distinct starter silhouettes.
- Multi-pet desktop roaming and breeding remain future work.


## v0.4.2-preview — Original Sprite Silhouette

- Restored the original Ghost desktop sprite outline.
- Reduced oversized dog/fox/dragon side shapes that looked like arms.

## v0.4.1-preview — Doorway Fix

- Fixed pets getting stuck in front of the desktop house near screen edges.
- Door entry now uses a reachable position and accepts doorway overlap.

## v0.4.0-preview — Eggs, Species and Connected House

- New games start with a hatchable egg; existing companions are unaffected.
- Choice of six starting species with distinct early sprite markings.
- Movable desktop house entrance and physically animated walk-home transition.
- One shared location for desktop and house views, with return-home controls.
- Early background house routines affect energy and happiness.

## v0.3.0 — Little Haunted House (preview)

- Added a code-drawn 18×12 top-down pixel house with four rooms and doorways.
- Added pet walking, autonomous wandering, and click-to-move routes.
- Added Decorate mode and saved unlockable furniture.
- Starting coins increased to 200 with a one-time top-up for older saves.
- Prepared project metadata and syntax checking for eventual GitHub publication.

## v0.2.2

- Cuddles moved from a modal window to directly clicking the desktop pet.

## v0.2.0

- Interactive minigames, affection, personality growth, speech bubbles and
  early furniture prototype.
