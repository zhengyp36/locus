package com.screenlab.probe;

import android.accessibilityservice.AccessibilityService;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.accessibility.AccessibilityEvent;

import java.io.File;
import java.io.FileOutputStream;
import java.util.Locale;

/**
 * Research probe: counts accessibility change events by type. Used only as a
 * "something changed" trigger; window content is never read.
 */
public class ProbeA11yService extends AccessibilityService {
    static final String TAG = "screenprobe.a11y";
    static volatile ProbeA11yService instance;

    private final long[] counts = new long[32];
    private long total;
    private long lastTotal;
    private final Handler ui = new Handler(Looper.getMainLooper());
    private File outFile;
    private final String[] NAMES = {
            "VIEW_CLICKED", "VIEW_LONG_CLICKED", "VIEW_SELECTED", "VIEW_FOCUSED",
            "VIEW_TEXT_CHANGED", "WINDOW_STATE_CHANGED", "NOTIFICATION_STATE_CHANGED",
            "VIEW_HOVER_ENTER", "VIEW_HOVER_EXIT", "TOUCH_EXPLORATION_GESTURE_START",
            "TOUCH_EXPLORATION_GESTURE_END", "WINDOW_CONTENT_CHANGED", "VIEW_SCROLLED",
            "VIEW_TEXT_SELECTION_CHANGED", "ANNOUNCEMENT", "VIEW_ACCESSIBILITY_FOCUSED",
            "VIEW_ACCESSIBILITY_FOCUS_CLEARED", "VIEW_TEXT_TRAVERSED_AT_MOVEMENT_GRANULARITY",
            "GESTURE_DETECTION_START", "GESTURE_DETECTION_END",
            "TOUCH_INTERACTION_START", "TOUCH_INTERACTION_END", "WINDOWS_CHANGED"};

    @Override
    protected void onServiceConnected() {
        instance = this;
        outFile = new File(getExternalFilesDir(null), "a11y-stats.txt");
        Log.i(TAG, "connected");
        ui.removeCallbacksAndMessages(null);
        ui.postDelayed(new Runnable() {
            @Override
            public void run() {
                if (instance != ProbeA11yService.this) return;
                sample();
                ui.postDelayed(this, 1000);
            }
        }, 1000);
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent e) {
        if (e == null) return;
        int type = e.getEventType();
        int idx = type > 0 ? Integer.numberOfTrailingZeros(type) : -1;
        synchronized (counts) {
            total++;
            if (idx >= 0 && idx < counts.length) counts[idx]++;
        }
    }

    private void sample() {
        long t;
        long[] snap = new long[counts.length];
        synchronized (counts) {
            t = total;
            System.arraycopy(counts, 0, snap, 0, counts.length);
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < snap.length; i++) {
            if (snap[i] > 0) {
                String n = i < NAMES.length ? NAMES[i] : ("bit" + i);
                sb.append(n).append('=').append(snap[i]).append(' ');
            }
        }
        String line = String.format(Locale.US, "t event_rate=%.1f/s total=%d | %s",
                (double) (t - lastTotal), t, sb.toString().trim());
        lastTotal = t;
        Log.i(TAG, line);
        try (FileOutputStream fos = new FileOutputStream(outFile, true)) {
            fos.write((line + "\n").getBytes());
        } catch (Throwable ignored) {
        }
    }

    void dump() {
        long t;
        StringBuilder sb = new StringBuilder();
        synchronized (counts) {
            t = total;
            for (int i = 0; i < counts.length; i++) {
                if (counts[i] > 0) {
                    String n = i < NAMES.length ? NAMES[i] : ("bit" + i);
                    sb.append(n).append('=').append(counts[i]).append(' ');
                }
            }
        }
        String line = "DUMP total=" + t + " | " + sb.toString().trim();
        Log.i(TAG, line);
        try (FileOutputStream fos = new FileOutputStream(outFile, true)) {
            fos.write((line + "\n").getBytes());
        } catch (Throwable ignored) {
        }
    }

    @Override
    public void onInterrupt() {
    }
}
