# Changelog

## v0.7.0-preview — Three Distinctly Designed Homes

- Recompose Open Plan from scratch: cozy private nook, long kitchen wall, large breakfast island, open great room, L-shaped sofa and large pet corner. Do not reuse the Woodland living/kitchen/nursery vignette.
- Recompose Sunny Garden from scratch: huge glazed conservatory, cedar deck, raised potting shelves, trellises, broad garden seating and a lily pond. Do not reuse the Woodland layout's room positions.
- Give all three home upgrades truly different interior wall topology, with walkable doorways and accessible pet paths.
- Preserve furniture inventories when switching layouts by gently moving any items colliding with newly installed partitions or fixed fittings, instead of blocking the upgrade.
- Add regression tests that demand at least 43% changed sampled pixels between floor plans and confirm purchased furniture survives a renovation.
- Retain two roaming desktop pets, the house/desktop friendship meters, original Founder mouse sprite, nursery, coins and save compatibility.


## v0.6.5-preview — Two Pets & Persistent Friendship

- Add a second desktop pet window, with the same clickable care access, drag behavior, and independent saved desktop coordinates as the lead pet.
- Add **Invite as Second Pet** and **Send Buddy Home** controls inside Pocket Care, with no more than two active desktop pets.
- Let desktop pets wander together, greet, and produce heart reactions as their shared relationship improves.
- Add per-pair relationship values, capped at 100, separate from each pet's own individual affection score.
- Add selectable friendship meters in Pocket Care and directly above the house canvas, even when a pair is indoors.
- Allow relationships to increase when indoor pets meet and passively over real elapsed time while both are inside, including when the house window is closed.
- Make the two-slot desktop roster authoritative, preserve single-pet saves and all Founder/nursery/furniture progress, and avoid duplicate indoor/outdoor renderings.
- Expand GUI and persistence regression tests for duo invitations, dismissal, promotion, and indoor relationship growth.


## v0.6.4-preview — Distinct Home Upgrades & No Duplicate Cats

- Scale desktop Cat art to 2× and other adopted sprites to 3×, retaining the Founder mouse at its approved size.
- Use authoritative desktop_pet_id for rendering: the roaming companion cannot simultaneously appear indoors, even with outdated saved location flags.
- Add a single-instance save lock to avoid competing pet windows and conflicting household saves.
- Give Open Plan larger missing wall partitions, a continuous sage great-room floor, furniture and a breakfast island.
- Give Sunny Garden a dramatically different open conservatory with glazed tile floor, foliage, benches and water accents.
- Show the active purchased cottage by name in the house title bar.
- Add tests for significant image differences between three layouts, desktop cat sizing, duplicate pet prevention and game instance locking.


## v0.6.3-preview — Cottage Fit, Layout Unlock UI & Cuddles

- Scale the cottage automatically to fit the available Zorin display and coordinate-match mouse clicks to the zoom factor.
- Scale the four large furnished room compositions to 82% and clip furnishings to the house interior.
- Relocate layout unlock status messages above the canvas so purchase failures are immediately visible.
- GUI-test the actual Open Plan and Sunny Garden unlock buttons, coin deductions and free switching back to owned layouts.
- Restore the missing **♡ Cuddle** Pocket Care button and five-pat cuddle mode for Founder and adopted companions.
- Keep adopted pet affection and cuddle totals separate from the Founder, preserving all save data.
- Validate cuddle mode, layout purchase, and offscreen scene rendering in automated tests.


## v0.6.2-preview — Furnished Woodland Cottage & Cat Sprite

- Replace block-looking wall seams with joined plaster trim and wood-edged doors.
- Furnish every room with much more recognizable, larger pixel-art props: patchwork bed, pillows, bedside lamp, large couch, tea table, botanical paintings, kitchen cabinets and dining nook, toy shelf and crib.
- Give Sunny Garden its own visible conservatory furnishing scene rather than a recolored nursery.
- Keep heavy built-in furniture out of pet movement routes and ensure pets are relocated safely from newly occupied positions.
- Replace generic Cat desktop rendering with a dedicated tabby cat with triangular ears, whiskers, paws and curled tail; use the same design indoors.
- Add a one-time, explicitly opt-in +600 preview testing coin gift inside the house. Existing coins and purchased layouts are preserved.
- Keep the Founder mouse's approved sprite exactly as it was in v0.5.1.
- Add offscreen GUI, artwork and save-state regression tests.


## v0.6.1-preview — Responsive Update Center

- Replace the unresponsive updater worker thread with a separately monitored process.
- Show the specific stage and elapsed time during update checks.
- Add a safe cancellation button while downloading and a 95-second timeout before applying files.
- Present actual network errors and a Retry option instead of hanging on “Getting the latest version”.
- Preserve existing save backups, pet stats, desktop selection and v0.6 cottage artwork.
- Add offscreen GUI tests for successful updates and GitHub connection failures.


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
