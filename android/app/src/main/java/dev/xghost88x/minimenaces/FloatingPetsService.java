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
import android.os.SystemClock;
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
    private final int[] travelTicks = {32,44};
    private final int[] idleTicks = {0,14};
    private final int[] verticalSign = {1,-1};
    private long socialUntil = 0L;
    private long lastSocialAt = 0L;
    private long approachUntil = 0L;
    private long lastApproachAt = 0L;
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
                pets[i].setDirection(facing[i]);
                pets[i].setOnMove((dx,dy,save) -> movePet(idx,dx,dy,save));
                pets[i].setOnPetTap(doubleTap -> reactToTap(idx,doubleTap));
                windowManager.addView(pets[i],lp);
            }
        } catch (RuntimeException error) {
            removeOverlays();
            throw error;
        }
        running=true;
        lastSocialAt=SystemClock.uptimeMillis()-3500L;
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

    private boolean nearEachOther() {
        if (params[0] == null || params[1] == null) return false;
        int dx=Math.abs(params[0].x-params[1].x);
        int dy=Math.abs(params[0].y-params[1].y);
        return dx <= dp(138) && dy <= dp(95);
    }

    private void faceBuddy() {
        if (params[0] == null || params[1] == null) return;
        facing[0] = params[1].x >= params[0].x ? 1 : -1;
        facing[1] = -facing[0];
        for(int i=0;i<2;i++) if (pets[i]!=null)
            pets[i].setDirection(facing[i]);
    }

    private void startSocial(int pose, long duration, long now) {
        if (pets[0] == null || pets[1] == null ||
            pets[0].isBeingTouched() || pets[1].isBeingTouched()) return;
        faceBuddy();
        socialUntil = now+duration;
        lastSocialAt = now;
        approachUntil = 0L;
        pets[0].setWalking(false);
        pets[1].setWalking(false);
        pets[0].react(pose,duration);
        pets[1].react(pose,duration);
    }

    private void reactToTap(int petId,boolean doubleTap) {
        if (pets[petId] == null) return;
        final int friendId=1-petId;
        final long now=SystemClock.uptimeMillis();
        // Tap the cat: the mouse can wave back! Double-tap near the buddy
        // to trigger an entire two-pet dance, all inside the existing overlays.
        if (nearEachOther() && pets[friendId] != null &&
            !pets[friendId].isBeingTouched()) {
            if (doubleTap) {
                faceBuddy();
                pets[petId].react(PetView.DANCE,1900);
                pets[friendId].react(PetView.DANCE,1900);
                socialUntil=now+1900;
                lastSocialAt=now;
            } else {
                pets[friendId].react(PetView.GREET,1300);
            }
        } else if (doubleTap) {
            pets[petId].react(PetView.PLAY,1550);
        }
    }

    private void explore(int index,long now) {
        if (pets[index] == null || pets[index].isBeingTouched() ||
            params[index] == null) return;
        PetView pet=pets[index];
        if (now<socialUntil) {
            pet.setWalking(false);
            return;
        }
        // Every few seconds the pair deliberately seeks one another, then
        // switches to social choreography at close range.
        if (now<approachUntil && !nearEachOther() &&
            params[1-index]!=null) {
            int deltaX=params[1-index].x-params[index].x;
            int deltaY=params[1-index].y-params[index].y;
            if(Math.abs(deltaX)>dp(111) || Math.abs(deltaY)>dp(62)) {
                int x=Math.abs(deltaX)>dp(111) ? (deltaX>0?dp(3):-dp(3)):0;
                int y=Math.abs(deltaY)>dp(62) ? (deltaY>0?dp(2):-dp(2)):0;
                if(x!=0) {
                    facing[index]=x>0?1:-1;
                    pet.setDirection(facing[index]);
                }
                pet.setWalking(x!=0 || y!=0);
                movePet(index,x,y,false);
                return;
            }
        }
        if (idleTicks[index]>0) {
            idleTicks[index]--;
            pet.setWalking(false);
            return;
        }
        if (--travelTicks[index]<=0) {
            if (random.nextInt(3)!=0) facing[index]*=-1;
            pet.setDirection(facing[index]);
            idleTicks[index]=4+random.nextInt(14);
            travelTicks[index]=18+random.nextInt(43);
            verticalSign[index]=random.nextBoolean()?1:-1;
            pet.setWalking(false);
            return;
        }
        pet.setWalking(true);
        int y=(ticks%12==0)?verticalSign[index]*dp(2):0;
        movePet(index,facing[index]*dp(2),y,false);
        // Reverse at the physical edge instead of sticking to it.
        if (params[index].x==0 ||
            params[index].x>=Math.max(0,screenWidth-params[index].width)) {
            facing[index]*=-1;
            pet.setDirection(facing[index]);
        }
    }

    private void maybeSocialize(long now) {
        if (now<socialUntil || pets[0]==null || pets[1]==null ||
            pets[0].isBeingTouched() || pets[1].isBeingTouched()) return;
        if (nearEachOther() && now-lastSocialAt>8500L) {
            int[] activities={PetView.GREET, PetView.NUZZLE,
                              PetView.PLAY, PetView.DANCE};
            startSocial(activities[random.nextInt(activities.length)],
                        2100+random.nextInt(900),now);
        } else if (!nearEachOther() && now-lastApproachAt>15000L) {
            // Short approach bursts; never move or inspect other apps' input.
            approachUntil=now+7000L;
            lastApproachAt=now;
        }
    }

    private final Runnable ticker = new Runnable() {
        @Override public void run() {
            if (!running) return;
            if (!Settings.canDrawOverlays(FloatingPetsService.this)) {
                stopSelf(); // Permission can be revoked while the pets roam.
                return;
            }
            ticks++;
            final long now=SystemClock.uptimeMillis();
            if (ticks % 4 == 0) maybeSocialize(now);
            for (int i=0;i<2;i++) {
                PetView pet=pets[i];
                if(pet==null) continue;
                if(ticks%2==0) explore(i,now);
                pet.animate(ticks);
            }
            if(ticks%80==0) {
                SharedPreferences.Editor editor=prefs.edit();
                for (int i=0;i<2;i++) if(params[i]!=null) {
                    editor.putInt("x"+i,params[i].x);
                    editor.putInt("y"+i,params[i].y);
                }
                editor.apply();
            }
            handler.postDelayed(this,110);
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
