package dev.xghost88x.minimenaces;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.content.pm.PackageManager;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

/** Entry screen: permission is voluntary and overlays start only after a tap. */
public final class MainActivity extends Activity {
    private TextView status;
    private Button permissionButton;
    private Button startButton;

    private int dp(int n) {
        return Math.round(n * getResources().getDisplayMetrics().density);
    }

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        GradientDrawable bg = new GradientDrawable(
            GradientDrawable.Orientation.TOP_BOTTOM,
            new int[]{Color.rgb(29,33,52),Color.rgb(39,49,69)});
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        root.setBackground(bg);
        root.setPadding(dp(23),dp(45),dp(23),dp(25));

        TextView heading = text("🐭 Mini Menaces 🐱",25,Color.rgb(248,216,238));
        heading.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        root.addView(heading);
        TextView sub = text("Floating Android Preview · v0.2",15,Color.rgb(196,213,224));
        root.addView(sub);

        TextView explanation = text(
            "Your tiny troublemakers can wander above other apps.\n\n"
          + "The overlay is optional. Tap the button below to enable it "
          + "in Android Settings, then return here to start roaming.",
            16, Color.WHITE);
        explanation.setPadding(0,dp(30),0,dp(14));
        root.addView(explanation);

        status = text("",15,Color.rgb(170,230,186));
        status.setPadding(0,dp(8),0,dp(20));
        root.addView(status);
        permissionButton = button("1. Grant overlay permission");
        permissionButton.setOnClickListener(v -> {
            if (!Settings.canDrawOverlays(this)) {
                Intent intent = new Intent(
                    Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                    Uri.parse("package:" + getPackageName()));
                startActivity(intent);
            } else {
                refreshStatus();
            }
        });
        root.addView(permissionButton);

        startButton = button("2. Let pets roam 🐾");
        startButton.setOnClickListener(v -> {
            if (!Settings.canDrawOverlays(this)) {
                refreshStatus();
                return;
            }
            try {
                Intent pet = new Intent(this,FloatingPetsService.class);
                pet.setAction(FloatingPetsService.ACTION_START);
                startForegroundService(pet);
                status.setText("🐱 Pet windows starting. Press Home to see them!");
                if (Build.VERSION.SDK_INT >= 33 &&
                    checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                        != PackageManager.PERMISSION_GRANTED) {
                    requestPermissions(new String[]{
                        Manifest.permission.POST_NOTIFICATIONS},101);
                }
            } catch (RuntimeException ex) {
                status.setText("Could not start overlays: " + ex.getMessage());
            }
        });
        root.addView(startButton);

        Button stopButton = button("⌂ Send pets home");
        stopButton.setOnClickListener(v -> {
            Intent pet = new Intent(this,FloatingPetsService.class);
            pet.setAction(FloatingPetsService.ACTION_STOP);
            // The service was explicitly launched by the user if running.
            startService(pet);
            status.setText("The pets are going home. 🏡");
        });
        root.addView(stopButton);
        TextView info = text(
            "Tap a pet for hearts, drag to move it, or let it explore.\n\n"
          + "This is an overlay-only prototype. The full desktop cottage, "
          + "coins and adoption systems aren't ported yet.\n\n"
          + "No screen recording, accessibility access or other app data needed.",
            13,Color.rgb(190,201,211));
        info.setPadding(0,dp(22),0,0);
        root.addView(info);

        ScrollView scroller = new ScrollView(this);
        scroller.addView(root);
        setContentView(scroller);
        refreshStatus();
    }

    private TextView text(String value, int sp, int color) {
        TextView t = new TextView(this);
        t.setText(value);
        t.setTextSize(sp);
        t.setTextColor(color);
        t.setGravity(Gravity.CENTER);
        return t;
    }

    private Button button(String title) {
        Button b=new Button(this);
        b.setAllCaps(false);
        b.setText(title);
        b.setTextSize(16);
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,dp(54));
        lp.topMargin=dp(10);
        b.setLayoutParams(lp);
        return b;
    }

    @Override protected void onResume() {
        super.onResume();
        if (status!=null) refreshStatus();
    }
    private void refreshStatus() {
        boolean allowed=Settings.canDrawOverlays(this);
        status.setText(allowed
            ? "✓ Android overlay permission granted"
            : "Overlay permission is OFF. Enable it to release the pets.");
        permissionButton.setText(allowed
            ? "✓ Overlay permission granted" : "1. Grant overlay permission");
        startButton.setEnabled(allowed);
    }
}
