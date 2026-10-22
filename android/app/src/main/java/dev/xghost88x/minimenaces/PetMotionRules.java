package dev.xghost88x.minimenaces;

/** Pure, device-independent safeguards for the Android overlay pet animations. */
public final class PetMotionRules {
    private PetMotionRules() {}

    public static boolean areNear(int ax,int ay,int bx,int by,int maxDx,int maxDy) {
        return Math.abs((long)ax-bx)<=maxDx && Math.abs((long)ay-by)<=maxDy;
    }

    /** Which way the mouse should recoil when surprised by the cat. */
    public static int retreatDirection(int mouseX,int catX) {
        return mouseX <= catX ? -1 : 1;
    }

    public static int clamp(int n,int minimum,int maximum) {
        return Math.max(minimum,Math.min(n,maximum));
    }

    public static boolean zoomCooldownPassed(long now,long lastZoom,long minimumMs) {
        return now>=lastZoom && now-lastZoom>=minimumMs;
    }
}
