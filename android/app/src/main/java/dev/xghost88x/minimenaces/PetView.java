package dev.xghost88x.minimenaces;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Typeface;
import android.os.SystemClock;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewConfiguration;

/**
 * Transparent, pixel-perfect floating character. Effects have dedicated
 * headroom INSIDE this overlay: no text or hearts are drawn past its bounds.
 * v0.2 replaces the single idle bob with animated paws, tail, blink and
 * expression changes for social, petting and dancing actions.
 */
public final class PetView extends View {
    public static final int IDLE = 0;
    public static final int WALK = 1;
    public static final int PETTED = 2;
    public static final int GREET = 3;
    public static final int NUZZLE = 4;
    public static final int PLAY = 5;
    public static final int DANCE = 6;
    public static final int SLEEPY = 7;
    public static final int SWAT = 8;
    public static final int STARTLED = 9;
    public static final int CURL_UP = 10;
    public static final int ZOOMIES = 11;

    public interface OnMove {
        void move(int dx, int dy, boolean save);
    }
    public interface OnPetTap {
        void tapped(boolean doubleTap);
    }

    private final Paint paint = new Paint();
    private final boolean cat;
    private OnMove movement;
    private OnPetTap tap;
    private float touchX, touchY, totalMove;
    private boolean touching, dragging;
    private int frame, direction = 1, action = IDLE;
    private boolean walking;
    private long actionUntil, lastTap;
    private final int slop;

    public PetView(Context context, boolean isCat) {
        super(context);
        cat = isCat;
        slop = ViewConfiguration.get(context).getScaledTouchSlop();
        paint.setAntiAlias(false);
        paint.setFilterBitmap(false);
        setLayerType(View.LAYER_TYPE_SOFTWARE, null);
    }

    public void setOnMove(OnMove move) { movement = move; }
    public void setOnPetTap(OnPetTap listener) { tap = listener; }
    public boolean isBeingDragged() { return dragging; }
    public boolean isBeingTouched() { return touching; }

    public void setDirection(int value) {
        direction = value < 0 ? -1 : 1;
    }

    public void setWalking(boolean value) {
        walking = value;
    }

    public void react(int pose, long durationMs) {
        action = pose;
        actionUntil = SystemClock.uptimeMillis() + durationMs;
        invalidate();
    }

    private int pose(long now) {
        if (now < actionUntil) return action;
        return walking ? WALK : IDLE;
    }

    public void animate(int tick) {
        frame = tick;
        invalidate();
    }

    @Override public boolean onTouchEvent(MotionEvent event) {
        switch (event.getActionMasked()) {
            case MotionEvent.ACTION_DOWN:
                touchX = event.getRawX();
                touchY = event.getRawY();
                totalMove = 0;
                touching = true;
                dragging = false;
                return true;
            case MotionEvent.ACTION_MOVE: {
                float dx = event.getRawX() - touchX;
                float dy = event.getRawY() - touchY;
                totalMove += Math.abs(dx) + Math.abs(dy);
                if (totalMove >= slop) dragging = true;
                if (dragging && movement != null) {
                    movement.move(Math.round(dx), Math.round(dy), false);
                }
                touchX = event.getRawX();
                touchY = event.getRawY();
                return true;
            }
            case MotionEvent.ACTION_UP:
                touching = false;
                if (dragging) {
                    if (movement != null) movement.move(0, 0, true);
                } else {
                    long now = SystemClock.uptimeMillis();
                    boolean doubleTap = now - lastTap < 350;
                    lastTap = now;
                    react(doubleTap ? DANCE : PETTED, doubleTap ? 1850 : 1450);
                    if (tap != null) tap.tapped(doubleTap);
                }
                dragging = false;
                performClick();
                return true;
            case MotionEvent.ACTION_CANCEL:
                touching = false;
                dragging = false;
                return true;
            default:
                return super.onTouchEvent(event);
        }
    }

    @Override public boolean performClick() {
        super.performClick();
        return true;
    }

    private void pix(Canvas c, int color, float x, float y, float w, float h) {
        paint.setColor(color);
        paint.setStyle(Paint.Style.FILL);
        c.drawRect(x, y, x + w, y + h, paint);
    }

    @Override protected void onDraw(Canvas screen) {
        super.onDraw(screen);
        final long now = SystemClock.uptimeMillis();
        final int mood = pose(now);

        // 32 x 49 logical pixels. Sprite occupies y=13..46, while y=0..12
        // is exclusively for hearts/emotes. All artwork stays inside bounds.
        final float scale = Math.min(getWidth() / 34f, getHeight() / 51f);
        screen.save();
        screen.translate((getWidth() - 32f * scale) * .5f,
                         (getHeight() - 49f * scale) * .5f);
        screen.scale(scale, scale);

        float hop = 0;
        if (!touching) {
            if (mood == WALK) hop = (frame % 4 == 0 || frame % 4 == 1) ? -1 : 0;
            else if (mood == PETTED || mood == GREET || mood == PLAY)
                hop = -new int[]{0, 2, 4, 2, 0, 1, 3, 1}[frame % 8];
            else if (mood == DANCE) hop = -new int[]{1, 3, 0, 4, 1, 4, 0, 3}[frame % 8];
            else if (mood == SWAT) hop = -new int[]{0, 1, 3, 1}[frame % 4];
            else if (mood == STARTLED) hop = -new int[]{1, 5, 3, 0, 3, 1}[frame % 6];
            else if (mood == ZOOMIES) hop = -new int[]{0, 2, 1, 3}[frame % 4];
            else if (mood == IDLE) hop = (frame / 11) % 2 == 0 ? 0 : -1;
        }

        screen.save();
        if (mood == CURL_UP || mood == SLEEPY) {
            // A low sleeping silhouette, kept clear of the emote space.
            screen.translate(1.2f, 20);
            screen.scale(.92f, .76f);
        } else {
            screen.translate(mood == STARTLED && frame % 2 == 0 ? 1 : 0, 13 + hop);
        }
        if (direction < 0) {
            screen.translate(30, 0);
            screen.scale(-1, 1);
        }
        if (cat) drawCat(screen, mood); else drawMouse(screen, mood);
        screen.restore();

        // Draw hearts with safe baselines, not at y=5 (which clipped glyph
        // ascenders outside the old overlay). Never depend on system emoji
        // extents at the top of an Android TYPE_APPLICATION_OVERLAY window.
        if (now < actionUntil) {
            String effect = mood == DANCE ? "♪" :
                            mood == PLAY || mood == SWAT ? "✦" :
                            mood == GREET ? "!" :
                            mood == STARTLED ? "!!" :
                            mood == SLEEPY || mood == CURL_UP ? "z" :
                            mood == ZOOMIES ? "✧" :
                            (mood == PETTED || mood == NUZZLE) ? "♥" : "";
            if (!effect.isEmpty()) {
                paint.setTypeface(Typeface.DEFAULT_BOLD);
                paint.setTextSize(10);
                paint.setAntiAlias(true);
                paint.setColor(mood == GREET ? Color.rgb(239, 181, 103)
                                           : Color.rgb(246, 122, 163));
                // All glyph baselines >=10px from top and inside the 32px width.
                screen.drawText(effect, 17, 11, paint);
                if (mood == PETTED || mood == NUZZLE || mood == DANCE ||
                        mood == CURL_UP || mood == ZOOMIES) {
                    paint.setTextSize(7);
                    String extra = mood == DANCE ? "♫" :
                                   mood == CURL_UP ? "z" :
                                   mood == ZOOMIES ? "✧" : "♡";
                    screen.drawText(extra, 5, 13, paint);
                }
                paint.setAntiAlias(false);
            }
        }

        screen.restore();
    }

    private void drawCat(Canvas c, int mood) {
        int ink = Color.rgb(66, 57, 57), fur = Color.rgb(235, 170, 106);
        int stripe = Color.rgb(167, 105, 69), cream = Color.rgb(254, 237, 203);
        int blush = Color.rgb(249, 170, 174);
        boolean stepping = (mood == WALK || mood == ZOOMIES) && (frame / 2) % 2 == 0;
        boolean dancing = mood == DANCE;
        boolean swatting = mood == SWAT;
        boolean napping = mood == CURL_UP || mood == SLEEPY;
        boolean pawUp = mood == PETTED || mood == GREET || mood == PLAY
                        || dancing || mood == NUZZLE || swatting;
        boolean blink = frame % 103 < 4 || mood == NUZZLE || napping;
        int tailLift = (frame / (mood == ZOOMIES ? 1 : 3)) % 2;

        // Tail flicks, then head/ears remain distinct from the body.
        pix(c, ink, 23, 20 - tailLift, 3, 9);
        pix(c, fur, 24, 16 - tailLift, 3, 9);
        pix(c, ink, 22, 14 - tailLift, 6, 4);
        pix(c, stripe, 25, 17 - tailLift, 3, 2);
        pix(c, ink, 7, 17, 17, 12);
        pix(c, fur, 8, 18, 15, 9);
        pix(c, cream, 11, 21, 8, 6);
        pix(c, ink, 8, 27 + (stepping ? 1 : 0), 5, 3);
        pix(c, ink, 18, 27 + (stepping ? 0 : 1), 5, 3);
        pix(c, fur, 9, 27 + (stepping ? 1 : 0), 3, 2);
        pix(c, fur, 19, 27 + (stepping ? 0 : 1), 3, 2);

        pix(c, ink, 3, 5, 7, 12); pix(c, ink, 19, 5, 7, 12);
        pix(c, fur, 5, 7, 5, 9); pix(c, fur, 19, 7, 5, 9);
        pix(c, blush, 6, 9, 3, 6); pix(c, blush, 20, 9, 3, 6);
        pix(c, ink, 3, 12, 23, 13); pix(c, fur, 4, 13, 21, 11);
        pix(c, cream, 9, 20, 12, 3);
        pix(c, stripe, 11, 13, 2, 3); pix(c, stripe, 16, 13, 2, 3);
        if (blink) {
            pix(c, ink, 9, 20, 3, 1); pix(c, ink, 19, 20, 3, 1);
        } else {
            pix(c, ink, 9, 18, 3, 3); pix(c, ink, 19, 18, 3, 3);
            pix(c, cream, 10, 18, 1, 1); pix(c, cream, 20, 18, 1, 1);
        }
        pix(c, blush, 6, 21, 3, 2); pix(c, blush, 22, 21, 3, 2);
        pix(c, blush, 14, 21, 2, 2);
        pix(c, ink, 1, 20, 5, 1); pix(c, ink, 23, 20, 5, 1);
        pix(c, ink, 1, 23, 5, 1); pix(c, ink, 23, 23, 5, 1);
        if (pawUp) {
            // Raised waving paw vs running legs.
            pix(c, ink, 3, dancing ? 14 : 17, 5, 5);
            pix(c, fur, 4, dancing ? 14 : 17, 3, 4);
            if (dancing) pix(c, cream, 20, 13, 4, 3);
        }
        if (swatting) {
            // A little outstretched, alternating paw-swipe.
            int swipe = (frame / 2) % 2 == 0 ? 0 : 2;
            pix(c, ink, 0, 17 + swipe, 7, 4);
            pix(c, fur, 0, 18 + swipe, 6, 2);
            pix(c, cream, 1, 18 + swipe, 2, 1);
        }
        if (napping) {
            // Tucked paws accentuate the sleep pose (the canvas is squashed).
            pix(c, cream, 9, 27, 13, 2);
        }
    }

    private void drawMouse(Canvas c, int mood) {
        int ink = Color.rgb(57, 65, 65), fur = Color.rgb(220, 208, 235);
        int shadow = Color.rgb(158, 148, 188), pink = Color.rgb(246, 163, 181);
        int cream = Color.rgb(255, 246, 234);
        boolean stepping = (mood == WALK || mood == STARTLED) && (frame / 2) % 2 == 0;
        boolean waving = mood == PETTED || mood == GREET ||
                         mood == DANCE || mood == PLAY || mood == STARTLED;
        boolean napping = mood == CURL_UP || mood == SLEEPY;
        boolean blink = frame % 109 < 4 || mood == NUZZLE || napping;
        int flick = (frame / 4) % 2;

        pix(c, ink, 23, 23, 5, 2);
        pix(c, pink, 25, 22 - flick, 2, 3);
        pix(c, pink, 27, 19 - flick, 2, 4);
        pix(c, ink, 8, 19, 17, 11); pix(c, shadow, 9, 20, 15, 9);
        pix(c, fur, 11, 20, 12, 8);
        pix(c, ink, 8, 29 + (stepping ? 1 : 0), 5, 2);
        pix(c, ink, 19, 29 + (stepping ? 0 : 1), 5, 2);
        pix(c, pink, 10, 29 + (stepping ? 1 : 0), 2, 2);
        pix(c, pink, 20, 29 + (stepping ? 0 : 1), 2, 2);
        pix(c, ink, 3, 7, 10, 12); pix(c, ink, 18, 7, 10, 12);
        pix(c, pink, 5, 9, 6, 8); pix(c, pink, 20, 9, 6, 8);
        pix(c, fur, 4, 9, 8, 7); pix(c, fur, 19, 9, 8, 7);
        pix(c, pink, 6, 11, 4, 5); pix(c, pink, 21, 11, 4, 5);
        pix(c, ink, 7, 15, 19, 12); pix(c, fur, 8, 16, 17, 10);
        pix(c, cream, 10, 21, 13, 4);
        if (blink) {
            pix(c, ink, 11, 21, 3, 1); pix(c, ink, 19, 21, 3, 1);
        } else {
            pix(c, ink, 11, 19, 2, 3); pix(c, ink, 19, 19, 2, 3);
        }
        pix(c, pink, 16, 23, 2, 2);
        pix(c, shadow, 10, 24, 3, 1); pix(c, shadow, 20, 24, 3, 1);
        if (mood == STARTLED) {
            // Wide surprised eyes with tiny highlights, then jump backwards.
            pix(c, ink, 10, 18, 4, 4);
            pix(c, ink, 19, 18, 4, 4);
            pix(c, cream, 11, 18, 1, 1);
            pix(c, cream, 20, 18, 1, 1);
        }
        if (napping) pix(c, cream, 9, 28, 14, 2);
        if (waving) {
            pix(c, ink, 5, mood == DANCE ? 13 : 18, 4, 5);
            pix(c, pink, 6, mood == DANCE ? 14 : 18, 2, 3);
        }
    }
}
