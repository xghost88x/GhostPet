package dev.xghost88x.minimenaces;

/** Runs on CI's plain Java toolchain: no emulator required. */
public final class PetMotionRulesTest {
    private static void ok(boolean result,String why) {
        if (!result) throw new AssertionError(why);
    }
    public static void main(String[] args) {
        ok(PetMotionRules.areNear(0,100,120,105,138,95),
           "Neighbors should greet");
        ok(!PetMotionRules.areNear(0,0,170,0,138,95),
           "Pets far apart should approach instead of emoting");
        ok(!PetMotionRules.areNear(0,0,10,100,138,95),
           "Vertical separation also matters");
        ok(!PetMotionRules.areNear(Integer.MIN_VALUE,0,
                                  Integer.MAX_VALUE,0,138,95),
           "Large coordinate values must not overflow proximity checks");
        ok(PetMotionRules.retreatDirection(200,400)==-1,
           "A left-side mouse must hop left away from the cat");
        ok(PetMotionRules.retreatDirection(400,200)==1,
           "A right-side mouse must hop right away from the cat");
        ok(PetMotionRules.clamp(-100,0,300)==0,"Stay on left edge");
        ok(PetMotionRules.clamp(2000,0,300)==300,"Stay on right edge");
        ok(PetMotionRules.clamp(180,0,300)==180,"No unnecessary movement");
        ok(!PetMotionRules.zoomCooldownPassed(20000,15000,47000),
           "Cat should not continuously zoom");
        ok(PetMotionRules.zoomCooldownPassed(62000,15000,47000),
           "Cat may zoom after cooldown");
        ok(!PetMotionRules.zoomCooldownPassed(1000,15000,47000),
           "Clock changes must not bypass cooldown");
        System.out.println("Mini Menaces Android motion tests passed.");
    }
}
