# GhostPet v0.7.4 Preview — Mouse-Pointer Catch

A tiny original pixel creature that wanders around the desktop. Left-click it
to bring up a retro-styled care console; right-click for its menu; drag to move.
It works entirely offline and saves its progress locally.

## What's new in v0.7.4

**Now the cat can actually catch it!** The pointer chase previously stayed 30 pixels away from the mouse pointer for click safety but never tested whether the pet had arrived. A successful virtual paw-pounce now happens **when a chasing pet reaches the safe target beside the pointer and the pointer stays mostly still for about 0.4 seconds**. The pointer is never moved or clicked and remains outside the pet's window. Successful catches show **✦ GOTCHA! ✦** above the catching pet, display a victory speech bubble, grant **+6 happiness** and **2 coins**, and end the chase so rewards happen only once. If you keep moving the cursor and the pet cannot catch it within eight seconds, the usual playful escape still happens with the existing +2 happiness reward. You can tease the cat, stop the pointer to let her win, or disable cursor antics in Pocket Care.

Catching works for the cat as either the lead or second desktop buddy, and for the Founder mouse. Sleeping/dragging, opening care, sending a pet home or changing the pet roster still cancel ongoing chases safely. A new offscreen regression test verifies the correct reward, no double payments, a moving pointer evading the catch, and the safety gap remaining intact. Your existing pets, coins, cottage layouts, friendship and stocked food bowls are preserved.

## What's new in v0.7.3

**🐭 The pets chase your other mouse pointer!** Both desktop pets, including the Founder mouse, can occasionally notice and scamper after the real mouse pointer. The cat is weighted four times as likely as the other species to start a chase. It lasts a maximum of **8 seconds**, and spontaneous chases wait at least **75 seconds** since the previous one before randomly starting again. When chasing, their drawn bodies bounce in excitement. The computer's actual mouse pointer is **never moved, clicked, intercepted intentionally, or otherwise controlled**.

**Keep your cursor accessible:** Chase navigation leaves at least a 30px horizontal gap outside the full pet window when selecting a destination and clamps pet movement to the available monitor area. Pet movement never deliberately targets the position *under* the cursor. If you start caring for the pet, drag it, open the house or put it to sleep, the chase ends safely. Like other always-on-top desktop pets, a pet can still momentarily overlap the pointer if you move the pointer directly over it; this is an experimental Qt behavior and screen/window manager support varies.

**Your choice of mischief level:** Pocket Care's collapsible details include **🐾 Chase Pointer** for the selected desktop pet and **🐭 Cursor antics: On/Off** for spontaneous chases. Automatic antics are enabled by default, separately from the two-pet Auto interactions option. Clicking the manual button temporarily hides Pocket Care to leave the desktop clear. Both the lead pet and the second buddy also have a right-click **Chase pointer** action. A successful completed chase adds +2 happiness to the chaser, never consumes coins, and never changes the other pet's stats. The preference is saved across relaunches.

**Existing features stay intact:** Both companions, cuddle mode, 8 duo social actions, friendship meters, the refillable house food bowl and all three distinct cottages remain unchanged. Original petite Founder mouse pixel art is preserved. Added headless GUI tests for desktop edges, chase completion, sleeping and returning-home cancellation, companion-only chases, toggle persistence and not interfering with duo interactions.

## What's new in v0.7.2

**More than manual nuzzling:** Two pets now independently start one of **eight timed social activities**: greeting, nuzzling, bouncing play, chasing/tag, high-fives, synchronized dancing, peekaboo, and sharing snacks. The second pet visibly moves toward their partner, hops/dances, or hides and reappears during peekaboo. The pet's speech bubble and little hearts/symbols respond to the activity. When an interaction finishes, its pair's friendship meter improves once; energetic activities also influence their happiness/energy. The approved original Founder sprite remains untouched.

Spontaneous social encounters are **enabled by default** and can start roughly every 17+ seconds when two awake, free-roaming pets are near each other. The exact timing varies. Pocket Care now includes **✨ Auto interactions: On/Off**, **🎲 Surprise!**, **🎾 Play Together** and **♡ Nuzzle** inside the collapsible section. Disabling automatic encounters does not disable manual play. Dragging, sleeping or going home interrupts unfinished interactions safely.

**Actual house food bowls:** Buy/place the **Food bowl (8 coins)** in House → Decorate if you don't already own one. Each placed bowl holds **six meals**; the number of portions is visible on the furniture and in a new **🥣 Food bowls** counter above the canvas. Press **🥣 Refill bowls** to refill all placed bowls, or in Explore mode click one bowl to top up that bowl. Refilling is free in this preview. Hungry pets who stay indoors walk toward bowls, eat, use up one portion, and gain **26 hunger (fullness) points**, capped at 100, with a 60-second cooldown per pet. Pets indoors can also eat while the house window is closed *if Ghost Pet is running*; outdoor pets can't consume house food. Empty bowls can't feed until refilled. Each old bowl starts full when upgrading. Existing bowl placements, furniture, pets, coins and unlocked cottages are preserved.

Added offscreen Qt tests for all eight duo actions, rewards, automatic-play toggle, bowl migration, refills, portions, indoor-only feeding, cooldowns and preserving food across layout upgrades.

## What's new in v0.7.1

**Room labels removed:** No more floating `BEDROOM`, `OPEN LIVING + DINING`, `KITCHEN` or `SUNLIT GLASS GARDEN` text covering the floor art. All three cottage layouts, upgrades and floor-plan dropdown remain. The room purpose comes from the actual furniture. The older fallback renderer also hides labels.

**Two desktop pets interact:** After inviting a second pet in Pocket Care, you can press **🎾 Play Together** or **♡ Nuzzle** (or right-click either roaming pet for the same actions). The two companions now visibly approach for nuzzling, bounce during a play session, follow more closely during tag/chase, and greet each other. They sometimes start a random interaction themselves while close and awake. The shared friendship meter rises **only after an interaction successfully completes**, not once per animation frame; playful actions also lightly adjust both pets' happiness and energy. The pets can't interact while sleeping, dragged, cuddling, or going home. Leaving the desktop cancels unfinished interactions without granting rewards.

**Founder sprite remains untouched:** The original petite mouse sprite is unchanged; playful bouncing moves the drawn sprite temporarily without repainting its design.

Existing household saves, pets, coins, previously unlocked layouts, second-pet roaming and indoor relationships remain. Open Pocket Care → **↻ Update**, then relaunch to try the controls.

## What's new in v0.7.0

**Three genuinely different home arrangements (not just recolors):**
- **Woodland Cottage** keeps its original cozy four-room layout, patterned rugs, small bedroom, kitchen, sofa and nursery.
- **Open Plan Cottage** now renders an entirely different scene: a compact private sleeping nook, long wall-to-wall kitchen, freestanding breakfast island, oversized L-shaped sofa, central coffee table, a single generous shared great room and open pet corner. Its structural walls were redesigned to match.
- **Sunny Garden Cottage** now renders an entirely different retreat: a cedar deck and nap area to the left, and a huge glass-roofed greenhouse to the right with climbing plants, potting stands, a lily pond, and bright tiled conservatory flooring. Only a few structural glasshouse posts interrupt the open floor.

Unlike the prior releases, Open Plan and Sunny Garden no longer reuse the same four-room furniture composition. The new artwork still fits the existing 18×12 map and keeps the desktop house size and pet sizes unchanged.

**Renovations respect saved belongings:** Switching between floor plans preserves every purchased furniture item, coin balance, unlocked layout, and pet. If furniture occupies a newly built wall, the game moves it to the nearest free floor tile and shows a message; nothing is deleted. The one-time preview coins, dual roaming pets, friendships, cuddling, and Founder mouse remain as they were.

We added headless Qt pixel-rendering tests demanding that each new home changes **more than 43% of sampled pixels** compared with the prior plan, plus tests for distinct walkable wall arrangements and automatic furniture relocation. These guard against slipping back to superficial recoloring. Update with Pocket Care → **↻ Update**, then reopen the house and switch between your owned plans.

## What's new in v0.6.5

**Two pets on the desktop:** Open Pocket Care, select another hatched pet and click **♡ Invite as Second Pet**. It appears as a separate clickable, draggable pixel sprite beside your current pet. The two roam near each other and occasionally greet one another with floating hearts. Click the second pet for its care controls or right-click it to **Send this pet home**. Only two pets can roam at once. Replacing the second pet sends the previous buddy home. Bringing a new pet out as the lead does not delete anybody or change the Founder's sprite.

**Persistent pair relationship meters:** Pocket Care now has a **Friendship with** selector and meter, plus a little status such as *Getting closer*, *Good friends* and *Best buddies*. The house includes its own **♡ Pet friendships** dropdown and relationship meter covering all pairs, whether they're inside or outside. Relationships start at 30/100, are saved for each unique pair, rise when desktop buddies greet and when housemates meet, and continue rising slowly while pets share the house even if the cottage window is closed. This is separate from the individual pet's affection stat.

**One household save:** Locations derive from the two current desktop slots, avoiding duplicate cats appearing inside and outside. When the lead goes indoors, the other pet becomes the only outdoor pet; no progress is lost. Older single-pet saves migrate automatically. Existing coins, furniture, house upgrades, nursery, Founder mouse and update controls remain.

## What's new in v0.6.4

**Cat now fits beside the little house:** The adopted desktop cat renders at 2× scale (56 pixels across), smaller than the 80-pixel cottage icon, while the beloved Founder mouse remains unchanged. Other adopted species use 3×.

**No pet clones:** The House canvas uses the selected desktop pet ID as the authoritative location. A pet chosen for the desktop is never drawn in the house, even if its old `location` save field was stale. The house refresh also repairs those flags. Ghost Pet now takes an exclusive single-instance lock to prevent two game copies from updating the same save simultaneously.

**Upgrades look different:** Woodland Cottage retains its four cozy rooms. Open Plan removes much more of the partitions, gains an expansive sage great-room floor and a breakfast island. Sunny Garden opens the remaining inner walls and adds a large glazed conservatory floor, hanging plants, garden benches and a water bowl. Window title shows the selected floor plan. Each version retains purchased items, pets and coins.

The offscreen GUI test checks the actual pixels differ substantially between each layout, verifies the cat is smaller than the 80-pixel portal, and prevents rendering the active adopted cat indoors. Existing unlock prices and the 600 preview-coin reward remain.

## What's new in v0.6.3

**House fits the screen:** The cottage canvas now automatically scales down to fit the available Zorin desktop area, including space for the controls and taskbar. Pointer coordinates scale with the art, so tile movement and decorating still work. The larger room furnishings are now drawn at 82% of their former size and clipped within the cottage.

**Layout unlock feedback fixed:** Layout purchase/denial messages now appear **above** the canvas instead of below it, where short displays could hide them. Select Open Plan or Sunny Garden from the layout dropdown, then click the **Unlock** button next to it. Open Plan costs 120 coins; Garden costs 260 coins and requires Open Plan first. Insufficient-coins and furniture-collision messages appear in that visible status strip. The 600-coin preview gift remains in the house until claimed. Automated GUI tests click both unlock buttons and check the saved coin balances.

**Cuddle is now accessible:** In Pocket Care, choose your pet and press **♡ Cuddle**. That pet will come to the desktop if it is indoors. Then click the pet **five times** to complete the cuddle. Cuddles work with the Founder mouse and adopted pets, increasing the selected pet's affection and happiness; sleeping pets must be awakened first. Click the Cuddle button again or right-click the desktop pet to cancel.

The approved Founder mouse appearance is unchanged. Use Pocket Care's **↻ Update** button to install this revision, then relaunch Ghost Pet.

## What's new in v0.6.2

**A visibly furnished cottage:** We replaced the plain block-wall appearance with seamless plaster partitions and painted original multi-tile bedroom, living-room, kitchen and nursery furniture. There is a large patchwork quilt and pillows, a three-seat sage couch, a round tea table, cabinetry, dining nook, plush nursery and little decorations. The Sunny Garden layout replaces the nursery decorations with a conservatory bench and planters. Built-in large furnishings block pets' walking paths and avoid doorway cells; your existing purchased furniture and layout saves are retained.

**The cat is actually a cat:** The adopted Cat desktop sprite is now independent of the generic species body. It has distinctly triangular pink-lined ears, orange tabby stripes, rounded cheeks, symmetrical whiskers, little paws, and a curled upright tail. The miniature house cat also uses that drawing. The beloved Founder mouse sprite is untouched.

**600 free testing coins (once):** Open the House and click **🎁 Claim 600 preview coins** above the canvas. The button appears only until used. Both existing floor-plan unlocks cost 120 + 260 = 380 coins, leaving 220 coins for experimenting with furniture. Your regular coin income from minigames is unchanged; the one-time claim persists in your save.

This is still a code-drawn 2D cottage preview. We aren't claiming it already matches a professionally hand-painted pixel-art reference, but rooms now have distinctive larger furniture rather than color-only scenery. Update through the fixed v0.6.1 **↻ Update** button.

## What's new in v0.6.1

**Updater reliability fix:** The Update Center now runs downloads in an isolated child process, shows progress stages and elapsed time, supports cancelling the download before installation, and times out stalled requests rather than leaving “Getting the latest version” forever. On failure it shows the error and allows Retry. During actual file installation, cancel is disabled to avoid corrupting the app.

**If you're stuck on an older updater:** Close/force-close only the old Update Center, download the latest main-branch ZIP, unzip to Downloads, and run `bash install.sh` in the extracted `GhostPet-main` folder. This overwrites installed application files but does *not* touch `~/.local/share/ghostpet/state.json`. Afterwards, in-app updates use the fixed Update Center.

## What's new in v0.6

**Cozy Cottage artwork overhaul:** The interior uses original detailed, code-rendered pixel art—continuous wood floors, patterned rugs, windows, curtain details, shelves, plants, kitchen counter details, textured partition trim, and recognizable little furniture sprites. The porch/desktop house icon is now a welcoming woodland cottage rather than a purple haunted-house marker. The existing Woodland/Open Plan/Garden upgrades, navigation, coins and furnishings remain. This is a substantial first art pass, not yet a complete hand-illustrated game environment.

**Bring your chosen pet to the desktop:** Click the roaming companion, choose your Founder or an adopted pet from the **Pocket Care pet selector**, then click **🐾 Bring selected pet to desktop**. The displayed pet swaps to the selected species; the previous pet returns to the house. Your Founder retains the approved v0.5.1 mouse sprite and her own stats. The active pet's desktop coordinates and roaming state persist between launches. **Only one pet roams the desktop at a time** for now. Selecting a pet for care alone does not switch the roaming companion until you press the button.

From the desktop pet, right-click and choose **Walk home** to return it to the house. Open Pocket Care and summon it again whenever you like. Adopted pets disappear from the indoor view while roaming the desktop; the Founder is shown indoors when an adopted pet is outside.

This version is compatible with the v0.5.4 built-in updater, including older installations whose updater does not yet copy the new standalone artwork modules. For a normal update, select **↻ Update** in Pocket Care. You do not need to reset the save.

## What's new in v0.5.4

**No terminal needed after one-time installation.** Run `bash install.sh` from the downloaded project folder to install Ghost Pet to `~/Applications/GhostPet`. The installer adds **Ghost Pet** and **Update Ghost Pet** to Zorin's application menu, and creates a clickable desktop icon if the desktop directory is present. The compact Pocket Care panel now has a **↻ Update** button.

Updates fetch the latest GitHub main revision in a separate graphical window. They make backups of the previous program files and your pet's `~/.local/share/ghostpet/state.json` before replacing application files. They leave the Python virtual environment, pet saves, furnishings, coins, and Founder sprite intact. Reopen the app using the updater's **Launch Ghost Pet** button when finished.

## What's new in v0.5.3

The house has three switchable floor plans. Open the **Little House**, use the **Cottage floor plan** dropdown, and click **Unlock** or **Switch layout**. Each unlock is permanent and the Founder mouse sprite is unchanged.

- **Woodland Cottage** — starter floor plan, free.
- **Open Plan Cottage** — 120 coins; wider archways and an open lounge.
- **Sunny Garden Cottage** — 260 coins after unlocking Open Plan; spacious indoor garden, terracotta accents and fewer partitions.

Your coins pay only once per upgrade. Switching among owned floor plans is free. Furniture and pets stay saved. If furniture occupies a wall that would reappear when switching backwards, the game asks you to move it before changing layouts rather than deleting it. All three plans use the same outer house footprint for now.

## What's new in v0.5.2

The compact 326-pixel **Pocket Care** panel lets you choose any adopted housemate from a dropdown, care for them individually, and collapse the details. Your existing save and Founder companion remain intact. Adopted pets receive independent basic stats and simple play interactions; Founder-only minigames and desktop roaming remain separate. Existing adopted pets get sensible default stats until first interaction.

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

## Install on Zorin (once)

1. Download the ZIP using GitHub's **Code → Download ZIP** and extract it to Downloads.
2. If an older Ghost Pet is running, quit that copy.
3. Open a terminal *only for this one-time setup* and run:

   ```bash
   sudo apt install python3-venv libxcb-cursor0
   cd ~/Downloads/GhostPet-main
   bash install.sh
   ```

4. Open Zorin's application menu and search for **Ghost Pet**, or double-click the new **Ghost Pet** desktop shortcut. On some Zorin desktops, first right-click the icon and choose **Allow Launching**.
5. The first launch creates a private Python environment and downloads PySide6. Later launches reuse it. You can pin the app to your dock or favorites.

**Future updates:** In **Pocket Care**, click **↻ Update**. Ghost Pet saves and quits while the separate updater window checks GitHub. Click **Launch Ghost Pet** after a successful update. Alternatively, find **Update Ghost Pet** in the app menu (quit the main app first). No additional ZIP downloads are needed.

The installer stores application files in `~/Applications/GhostPet` and never removes your save data at `~/.local/share/ghostpet/state.json`. The updater creates a timestamped save backup in `~/.local/share/ghostpet/backups/` and keeps the previous program files in `~/Applications/GhostPet/.previous-version/` for recovery.

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

## Desktop launcher

The installer automatically creates a Zorin application-menu launcher, a dedicated
**Update Ghost Pet** launcher, and a desktop shortcut if the desktop directory
exists. You may pin **Ghost Pet** to the dash/dock after opening it.
Automatic startup can be configured using Zorin's **Startup Applications**.

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
