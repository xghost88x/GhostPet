# Mini Menaces Android overlay experiment (v0.3)

This is a **separate experimental Android prototype**, not a port of the completed Windows/Linux game. It lives under `android/` to avoid touching those installations.

## What works in the Android MVP

- User-initiated **Display over other apps** permission from Android system settings.
- Two independent, tiny, transparent floating pets (demo mouse and cat).
- Pet-only touch targets with tap hearts, draggable positions, automatic roaming, and saved positions.
- Hearts and emotes render inside a reserved 13px headroom, fixing Android overlay clipping.
- Cats and mice have distinct walking paws, blinks, flicking tails, excited hops, and dancing.
- New mischievous two-pet stories: the cat **swats gently**, the mouse **hops back** and then plays; the duo **rub cheeks** and sometimes **curl up for a nap** with floating z's.
- The orange cat occasionally gets **zoomies**, sprinting and zig-zagging briefly without accessing other apps' touch input.
- For hands-on testing the home screen now has **Surprise me** (choose swat, nuzzle or sleepy cuddle) and **Orange-cat zoomies!** buttons. You can also double-tap the cat when she's away from her buddy to trigger zoomies.
- New tested overlay motion rules guard proximity, the mouse's retreat direction, screen bounds and zoomie frequency.
- Dragging or touching a pet interrupts choreographed motion; **Send pets home** still clears both overlays, preserving saved positions.

- Tap either pet for happy hearts, double-tap to play; bring both nearby to get automatic greeting, nuzzling, playing, and dancing. Double-tap while nearby for a shared dance.
- The pets sometimes approach one another autonomously; both still roam independently and can be dragged between ordinary Android apps.
- Stop via the app **Send pets home** button or persistent foreground-service notification.
- Runs as a native Java Android app with no Python environment, accounts, Internet permission, or tracking.
- No automatic start on reboot.

## What is NOT built yet

- The exact founder and adopted sprites from desktop GhostPet (the MVP uses simplified test sprites).
- The full cottage, food stats, coin inventory, adoption, relationship persistence, and community content.
- In-app auto-updates / stable production signing / Play Store distribution.
- Chasing finger touches inside *other* apps. Android overlays cannot simply read other apps' touch streams.
- Displaying pets on secure system screens or reliably over keyboards/full-screen apps.

## Build from a computer

GitHub Actions workflow **Android floating-pets APK** builds the debug APK on Ubuntu with Android SDK 35 and Gradle 8.10.2.
Go to the Actions run → Artifacts → `MiniMenaces-Android-Prototype-APK`. Extract the artifact and install `app-debug.apk` on an Android device (allow that source to install apps if prompted).

Alternatively with Android Studio open `android/` as a project and run the `app` module.

**Updating from earlier Android previews:** The public test APKs are signed with temporary GitHub runner debug keys. If the new build fails to install over v0.1, uninstall the old preview in Android Settings, then install this v0.3 APK. This clears only the experimental Android pet positions (the desktop game and saves are separate).

**Debug-signing caution:** CI test APKs may have different debug signing keys between runs. Installing a newer CI build over an earlier one may fail until you uninstall the old test app (which also clears prototype settings). A persistent release signing key will be added before public beta testers are invited.

## Try it

1. Open Mini Menaces Preview.
2. Tap **Grant overlay permission**, select the app in Android settings, and enable "Display over other apps".
3. Return to Mini Menaces Preview and tap **Let pets roam**.
4. Leave the app: a little mouse and cat should float over your launcher or other ordinary apps.
5. Drag them by touching their bodies, tap for a petting reaction, or double-tap for play; watch them wander.
6. Place the pets near each other and see them greet, nuzzle, play and dance. Double-tap near the buddy to make them dance together.
7. Tap **Surprise me** in the main Mini Menaces app for an immediate pair activity. If the pets are apart, they will approach each other first. Tap **Orange-cat zoomies!** to unleash a short sprint.
8. Tap **Send pets home** or use **Send pets home** on its ongoing notification to stop. There is no background auto-respawn.

Foreground service behavior differs between devices. Android 15+ restricts launching services from background; this app starts the service only after the user presses the button while the activity is visible. Floating layers may be hidden by some system surfaces for privacy and security.

## Privacy

No Internet permission, no Accessibility Service, no screen capture, and no access to other app data are required for this demo. The persistent notification is visible while the pets are active. Positions are only stored locally in this app's SharedPreferences.
