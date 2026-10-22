package dev.xghost88x.minimenaces;

import android.app.Service;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.ServiceInfo;
import android.graphics.PixelFormat;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.provider.Settings;
import android.util.DisplayMetrics;
import android.view.Gravity;
import android.view.WindowManager;
import java.util.Random;

/** Foreground overlay exists only when the user has explicitly started it. */
public final class FloatingPetsService extends Service {
    public static final String ACTION_START = "dev.xghost88x.minimenaces.START";
    public static final String ACTION_STOP = "dev.xghost88x.minimenaces.STOP";
    private static final String CHANNEL = "mini_menaces_roaming";

    private final Handler handler=new Handler(Looper.getMainLooper());
    private final Random random=new Random();
    private final PetView[] pets=new PetView[2];
    private final WindowManager.LayoutParams[] params=new WindowManager.LayoutParams[2];
    private final int[] facing = {1,-1};
    private final int[] ticksUntilTurn = {24,36};
    private WindowManager windowManager;
    private SharedPreferences prefs;
    private boolean running=false;
    private int ticks=0;
    private int screenWidth,screenHeight;

    private int dp(int x) {
        return Math.round(x*getResources().getDisplayMetrics().density);
    }

    @Override public IBinder onBind(Intent intent) {return null;}

    @Override public int onStartCommand(Intent intent,int flags,int startId) {
        if (intent != null && ACTION_STOP.equals(intent.getAction())) {
            stopSelf();
            return START_NOT_STICKY;
        }
        if (!Settings.canDrawOverlays(this)) {
            stopSelf();
            return START_NOT_STICKY;
        }
        if (running) return START_NOT_STICKY;
        try {
            startRoaming();
        } catch (Exception error) {
            android.util.Log.e("MiniMenaces","Could not create overlays",error);
            stopSelf();
        }
        return START_NOT_STICKY; // Never recreate floating windows without request.
    }

    private Notification notification() {
        NotificationManager manager =
            (NotificationManager)getSystemService(Context.NOTIFICATION_SERVICE);
        if (Build.VERSION.SDK_INT>=26) {
            manager.createNotificationChannel(new NotificationChannel(
                CHANNEL,"Mini Menaces roaming",
                NotificationManager.IMPORTANCE_LOW));
        }
        int pendingFlags=PendingIntent.FLAG_UPDATE_CURRENT
                         |PendingIntent.FLAG_IMMUTABLE;
        Intent controls=new Intent(this,MainActivity.class);
        controls.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK
                         |Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent open=PendingIntent.getActivity(this,10,controls,pendingFlags);

        Intent stop=new Intent(this,FloatingPetsService.class);
        stop.setAction(ACTION_STOP);
        PendingIntent end=PendingIntent.getService(this,11,stop,pendingFlags);
        return new Notification.Builder(this,CHANNEL)
            .setSmallIcon(android.R.drawable.ic_menu_myplaces)
            .setContentTitle("Mini Menaces are roaming! 🐱")
            .setContentText("Tap to open controls or send your pets home")
            .setContentIntent(open)
            .addAction(new Notification.Action.Builder(
                android.R.drawable.ic_menu_close_clear_cancel,
                "Send pets home",end).build())
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .build();
    }

    private void startRoaming() {
        Notification note=notification();
        if (Build.VERSION.SDK_INT>=34) {
            startForeground(42711,note,ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE);
        } else {
            startForeground(42711,note);
        }
        windowManager=(WindowManager)getSystemService(Context.WINDOW_SERVICE);
        prefs=getSharedPreferences("pet_positions_v1",MODE_PRIVATE);
        DisplayMetrics metrics=new DisplayMetrics();
        windowManager.getDefaultDisplay().getRealMetrics(metrics);
        // Work conservatively within ordinary bounds, not navigation/system bars.
        screenWidth=Math.min(metrics.widthPixels,
                            getResources().getDisplayMetrics().widthPixels);
        screenHeight=Math.min(metrics.heightPixels,
                             getResources().getDisplayMetrics().heightPixels);
        int width=dp(106), height=dp(114);

        try {
            for(int i=0;i<2;i++) {
                final int idx=i;
                pets[i]=new PetView(this,i==1);
                pets[i].setContentDescription(i==0?"Mini Menace mouse":"Mini Menace cat");
                WindowManager.LayoutParams lp = new WindowManager.LayoutParams(
                    width,height,
                    WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
                    WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                        |WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL,
                    PixelFormat.TRANSLUCENT);
                lp.gravity=Gravity.TOP|Gravity.START;
                int fallbackX = (i==0)?dp(30):Math.max(dp(30),screenWidth-width-dp(25));
                lp.x=prefs.getInt("x"+i,fallbackX);
                lp.y=prefs.getInt("y"+i,screenHeight-height-dp(135));
                constrain(lp);
                params[i]=lp;
                pets[i].setOnMove((dx,dy,save) -> movePet(idx,dx,dy,save));
                windowManager.addView(pets[i],lp);
            }
        } catch (RuntimeException error) {
            removeOverlays();
            throw error;
        }
        running=true;
        handler.post(ticker);
    }

    private void constrain(WindowManager.LayoutParams lp) {
        lp.x=Math.max(0,Math.min(lp.x,Math.max(0,screenWidth-lp.width)));
        lp.y=Math.max(dp(24),Math.min(lp.y,Math.max(dp(24),screenHeight-lp.height-dp(35))));
    }

    private void movePet(int i,int dx,int dy,boolean save) {
        WindowManager.LayoutParams lp=params[i];
        if(lp==null || pets[i]==null || windowManager==null) return;
        lp.x+=dx; lp.y+=dy;
        constrain(lp);
        try {
            windowManager.updateViewLayout(pets[i],lp);
            if(save) prefs.edit().putInt("x"+i,lp.x)
                           .putInt("y"+i,lp.y).apply();
        } catch (IllegalArgumentException ignored) {
            // Android can remove overlays during permission changes.
        }
    }

    private final Runnable ticker = new Runnable() {
        @Override public void run() {
            if (!running) return;
            ticks++;
            for(int i=0;i<2;i++) {
                PetView pet=pets[i];
                if(pet==null) continue;
                pet.animate(ticks);
                // Roam gently to avoid battery drain and not interfere with taps.
                if (ticks%5==0 && !pet.isBeingDragged()) {
                    ticksUntilTurn[i]--;
                    if(ticksUntilTurn[i]<=0) {
                        facing[i]*=-1;
                        ticksUntilTurn[i]=20+random.nextInt(50);
                    }
                    movePet(i,facing[i]*dp(2),0,false);
                }
            }
            if(ticks%80==0) {
                for(int i=0;i<2;i++) if(params[i]!=null && prefs!=null) {
                    prefs.edit().putInt("x"+i,params[i].x)
                               .putInt("y"+i,params[i].y).apply();
                }
            }
            handler.postDelayed(this,120);
        }
    };

    private void removeOverlays() {
        if(windowManager==null) return;
        for(int i=0;i<2;i++) {
            if(pets[i]!=null) {
                try {windowManager.removeViewImmediate(pets[i]);}
                catch(IllegalArgumentException ignored){}
                pets[i]=null;
            }
        }
    }
    @Override public void onDestroy() {
        running=false;
        handler.removeCallbacks(ticker);
        if(prefs!=null) {
            SharedPreferences.Editor editor=prefs.edit();
            for(int i=0;i<2;i++) if(params[i]!=null) {
                editor.putInt("x"+i,params[i].x);
                editor.putInt("y"+i,params[i].y);
            }
            editor.apply();
        }
        removeOverlays();
        stopForeground(STOP_FOREGROUND_REMOVE);
        super.onDestroy();
    }
}
