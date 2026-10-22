package dev.xghost88x.minimenaces;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.os.SystemClock;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewConfiguration;

/** No image assets or network calls: small self-drawn pixel-pet placeholders. */
public final class PetView extends View {
    public interface OnMove {
        void move(int dx,int dy,boolean save);
    }
    private final Paint paint=new Paint();
    private final boolean cat;
    private OnMove movement;
    private float touchX,touchY;
    private float totalMove=0;
    private boolean dragging=false;
    private long heartsUntil=0;
    private int frame=0;
    private final int slop;

    public PetView(Context context,boolean isCat) {
        super(context);
        cat=isCat;
        slop=ViewConfiguration.get(context).getScaledTouchSlop();
        paint.setAntiAlias(false);
        paint.setFilterBitmap(false);
        setLayerType(View.LAYER_TYPE_SOFTWARE,null);
    }
    public void setOnMove(OnMove m){movement=m;}
    public boolean isBeingDragged(){return dragging;}
    public void animate(int n) {
        frame=n;
        invalidate();
    }

    @Override public boolean onTouchEvent(MotionEvent event) {
        switch(event.getActionMasked()) {
            case MotionEvent.ACTION_DOWN:
                touchX=event.getRawX(); touchY=event.getRawY();
                totalMove=0;
                dragging=false;
                return true;
            case MotionEvent.ACTION_MOVE:
                float dx=event.getRawX()-touchX;
                float dy=event.getRawY()-touchY;
                totalMove+=Math.abs(dx)+Math.abs(dy);
                if(totalMove>=slop) dragging=true;
                if(dragging && movement!=null)
                    movement.move(Math.round(dx),Math.round(dy),false);
                touchX=event.getRawX();
                touchY=event.getRawY();
                return true;
            case MotionEvent.ACTION_UP:
                if(dragging) {
                    if(movement!=null) movement.move(0,0,true);
                } else {
                    heartsUntil=SystemClock.uptimeMillis()+1400;
                    invalidate();
                }
                dragging=false;
                performClick();
                return true;
            case MotionEvent.ACTION_CANCEL:
                dragging=false;
                return true;
            default: return super.onTouchEvent(event);
        }
    }
    @Override public boolean performClick() {
        super.performClick();
        return true;
    }

    private void pix(Canvas c,int color,float x,float y,float w,float h) {
        paint.setColor(color);
        paint.setStyle(Paint.Style.FILL);
        c.drawRect(x,y,x+w,y+h,paint);
    }

    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        canvas.save();
        float scale=Math.min(getWidth()/34f,getHeight()/38f);
        canvas.translate((getWidth()-29*scale)/2f,
                         (getHeight()-34*scale)/2f);
        canvas.scale(scale,scale);
        // Do not draw any bounding panel or window background.
        float bob=dragging?0f:((frame/4)%2==0?-1.0f:0.0f);
        canvas.translate(0,bob);
        if(cat) drawCat(canvas); else drawMouse(canvas);
        if(heartsUntil>SystemClock.uptimeMillis()) {
            paint.setColor(Color.rgb(249,125,168));
            paint.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);
            paint.setTextSize(13);
            canvas.drawText("♥",20,5,paint);
            canvas.drawText("♡",2,11,paint);
        }
        canvas.restore();
    }

    private void drawCat(Canvas c) {
        int ink=Color.rgb(66,57,57),fur=Color.rgb(235,170,106);
        int stripe=Color.rgb(167,105,69),cream=Color.rgb(254,237,203);
        int blush=Color.rgb(249,170,174);
        // Upturned striped tail; ears + cheeks are visibly distinct.
        pix(c,ink,23,19,3,11);pix(c,fur,24,16,3,9);
        pix(c,ink,22,15,6,4);pix(c,stripe,25,18,3,2);
        pix(c,ink,7,17,17,12);pix(c,fur,8,18,15,9);
        pix(c,cream,11,21,8,6);
        pix(c,ink,8,27,5,3);pix(c,ink,18,27,5,3);
        pix(c,fur,9,27,3,2);pix(c,fur,19,27,3,2);
        // Big ears with narrow inner shading.
        pix(c,ink,3,5,7,12);pix(c,ink,19,5,7,12);
        pix(c,fur,5,7,5,9);pix(c,fur,19,7,5,9);
        pix(c,blush,6,9,3,6);pix(c,blush,20,9,3,6);
        // Eyes and little triangular cheeks.
        pix(c,ink,3,12,23,13);pix(c,fur,4,13,21,11);
        pix(c,cream,9,20,12,3);
        pix(c,stripe,11,13,2,3);pix(c,stripe,16,13,2,3);
        pix(c,ink,9,18,3,3);pix(c,ink,19,18,3,3);
        pix(c,cream,10,18,1,1);pix(c,cream,20,18,1,1);
        pix(c,blush,6,21,3,2);pix(c,blush,22,21,3,2);
        pix(c,blush,14,21,2,2);
        pix(c,ink,1,20,5,1);pix(c,ink,23,20,5,1);
        pix(c,ink,1,23,5,1);pix(c,ink,23,23,5,1);
    }

    private void drawMouse(Canvas c) {
        int ink=Color.rgb(57,65,65),fur=Color.rgb(220,208,235);
        int shadow=Color.rgb(158,148,188),pink=Color.rgb(246,163,181);
        int cream=Color.rgb(255,246,234);
        // Twisty tail, separate from the body.
        pix(c,ink,23,23,5,2);pix(c,pink,25,22,2,3);pix(c,pink,27,19,2,4);
        pix(c,ink,8,19,17,11);pix(c,shadow,9,20,15,9);
        pix(c,fur,11,20,12,8);
        pix(c,ink,8,29,5,2);pix(c,ink,19,29,5,2);
        pix(c,pink,10,29,2,2);pix(c,pink,20,29,2,2);
        // Mouse ears *and* face are drawn distinctly from the cat.
        pix(c,ink,3,7,10,12);pix(c,ink,18,7,10,12);
        pix(c,pink,5,9,6,8);pix(c,pink,20,9,6,8);
        pix(c,fur,4,9,8,7);pix(c,fur,19,9,8,7);
        pix(c,pink,6,11,4,5);pix(c,pink,21,11,4,5);
        pix(c,ink,7,15,19,12);pix(c,fur,8,16,17,10);
        pix(c,cream,10,21,13,4);
        pix(c,ink,11,19,2,3);pix(c,ink,19,19,2,3);
        pix(c,pink,16,23,2,2);
        pix(c,shadow,10,24,3,1);pix(c,shadow,20,24,3,1);
    }
}
