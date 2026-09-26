package com.screenlab.probe;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.hardware.display.DisplayManager;
import android.hardware.display.VirtualDisplay;
import android.media.Image;
import android.media.ImageReader;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.IBinder;
import android.os.Looper;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.WindowManager;

import java.io.File;
import java.io.FileOutputStream;
import java.nio.ByteBuffer;
import java.util.Locale;

/**
 * Research probe: holds a MediaProjection at a *low* resolution, computes a
 * per-cell raw-pixel fingerprint on every incoming frame, and reports frame
 * cadence / change signal / CPU cost. No PNG encode anywhere.
 */
public class ProbeService extends Service {
    static final String TAG = "screenprobe";
    static final String ACTION_START = "com.screenlab.probe.START";
    static final String EXTRA_CODE = "code";
    static final String EXTRA_DATA = "data";

    static volatile ProbeService instance;
    static int pendingW, pendingH, pendingCell, pendingThresh;

    private MediaProjection projection;
    private VirtualDisplay display;
    private ImageReader reader;
    private HandlerThread thread;
    private Handler proc;
    private Handler ui;
    private Thread statsThread;

    private int fullW, fullH, density;
    private int probeW, probeH, cellPx, thresh;
    private int cols, rows;
    private int[] prev, cur;
    private boolean first = true;
    private int rowStride, pixelStride;
    private int lastBboxX0, lastBboxY0, lastBboxX1, lastBboxY1;
    private int lastChangeCells;

    private volatile boolean running;
    private long t0Ns;
    private long frames, changedFrames;
    private long sumProcNs, sumIntervalNs;
    private long lastFrameNs;
    private long cpuTicks0;
    private long cpuWallNs0;
    private double cpuPct;

    private File outFile;

    @Override
    public IBinder onBind(Intent i) {
        return null;
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        startForeground(1, buildNotification());
        instance = this;
        if (intent != null && ACTION_START.equals(intent.getAction())) {
            int code = intent.getIntExtra(EXTRA_CODE, 0);
            Intent data = intent.getParcelableExtra(EXTRA_DATA);
            startProjection(code, data);
        }
        return START_NOT_STICKY;
    }

    private void startProjection(int code, Intent data) {
        DisplayMetrics dm = new DisplayMetrics();
        WindowManager wm = (WindowManager) getSystemService(Context.WINDOW_SERVICE);
        wm.getDefaultDisplay().getRealMetrics(dm);
        fullW = dm.widthPixels;
        fullH = dm.heightPixels;
        density = dm.densityDpi;
        probeW = pendingW > 0 ? pendingW : Math.max(1, fullW / 4);
        probeH = pendingH > 0 ? pendingH : Math.max(1, fullH / 4);
        cellPx = pendingCell > 0 ? pendingCell : 24;
        thresh = pendingThresh > 0 ? pendingThresh : 24;
        cols = (probeW + cellPx - 1) / cellPx;
        rows = (probeH + cellPx - 1) / cellPx;
        prev = new int[cols * rows];
        cur = new int[cols * rows];
        first = true;
        outFile = new File(getExternalFilesDir(null), "probe-stats.txt");

        MediaProjectionManager mpm =
                (MediaProjectionManager) getSystemService(Context.MEDIA_PROJECTION_SERVICE);
        projection = mpm.getMediaProjection(code, data);
        projection.registerCallback(new MediaProjection.Callback() {
            @Override
            public void onStop() {
                Log.i(TAG, "projection stopped");
                running = false;
            }
        }, new Handler(Looper.getMainLooper()));

        thread = new HandlerThread("probe-proc");
        thread.start();
        proc = new Handler(thread.getLooper());
        ui = new Handler(Looper.getMainLooper());

        reader = ImageReader.newInstance(probeW, probeH, android.graphics.PixelFormat.RGBA_8888, 2);
        reader.setOnImageAvailableListener(new ImageReader.OnImageAvailableListener() {
            @Override
            public void onImageAvailable(ImageReader r) {
                process(r);
            }
        }, proc);
        display = projection.createVirtualDisplay("screenprobe", probeW, probeH, density,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR, reader.getSurface(), null, proc);

        t0Ns = System.nanoTime();
        cpuTicks0 = cpuTicks();
        cpuWallNs0 = t0Ns;
        running = true;
        Log.i(TAG, String.format(Locale.US,
                "started probe=%dx%d (full=%dx%d) cols=%d rows=%d cell=%d thresh=%d",
                probeW, probeH, fullW, fullH, cols, rows, cellPx, thresh));
        statsThread = new Thread(new Runnable() {
            @Override
            public void run() {
                statsLoop();
            }
        }, "probe-stats");
        statsThread.start();
    }

    private void process(ImageReader r) {
        if (!running) return;
        long ts = System.nanoTime();
        Image img = null;
        try {
            img = r.acquireLatestImage();
        } catch (Throwable t) {
            return;
        }
        if (img == null) return;
        try {
            Image.Plane p = img.getPlanes()[0];
            ByteBuffer buf = p.getBuffer();
            pixelStride = p.getPixelStride();
            rowStride = p.getRowStride();
            int changed = diff(buf);
            long dt = System.nanoTime() - ts;
            frames++;
            if (changed > 0) {
                changedFrames++;
                lastChangeCells = changed;
            }
            sumProcNs += dt;
            if (lastFrameNs != 0) sumIntervalNs += (ts - lastFrameNs);
            lastFrameNs = ts;
        } catch (Throwable t) {
            Log.e(TAG, "process failed", t);
        } finally {
            img.close();
        }
    }

    private int diff(ByteBuffer buf) {
        int changed = 0;
        int minx = Integer.MAX_VALUE, miny = Integer.MAX_VALUE, maxx = -1, maxy = -1;
        for (int cy = 0; cy < rows; cy++) {
            int y0 = cy * probeH / rows, y1 = (cy + 1) * probeH / rows;
            for (int cx = 0; cx < cols; cx++) {
                int x0 = cx * probeW / cols, x1 = (cx + 1) * probeW / cols;
                int sx = Math.max(1, (x1 - x0) / 4), sy = Math.max(1, (y1 - y0) / 4);
                int sr = 0, sg = 0, sb = 0, n = 0;
                for (int y = y0; y < y1; y += sy) {
                    int rowoff = y * rowStride;
                    for (int x = x0; x < x1; x += sx) {
                        int off = rowoff + x * pixelStride;
                        sr += buf.get(off) & 0xff;
                        sg += buf.get(off + 1) & 0xff;
                        sb += buf.get(off + 2) & 0xff;
                        n++;
                    }
                }
                if (n == 0) continue;
                int packed = ((sr / n) << 16) | ((sg / n) << 8) | (sb / n);
                int idx = cy * cols + cx;
                if (!first) {
                    int pv = prev[idx];
                    int d = Math.abs(((packed >> 16) & 0xff) - ((pv >> 16) & 0xff))
                            + Math.abs(((packed >> 8) & 0xff) - ((pv >> 8) & 0xff))
                            + Math.abs((packed & 0xff) - (pv & 0xff));
                    if (d > thresh) {
                        changed++;
                        if (x0 < minx) minx = x0;
                        if (y0 < miny) miny = y0;
                        if (x1 > maxx) maxx = x1;
                        if (y1 > maxy) maxy = y1;
                    }
                }
                cur[idx] = packed;
            }
        }
        int[] t = prev;
        prev = cur;
        cur = t;
        first = false;
        if (changed > 0) {
            lastBboxX0 = minx;
            lastBboxY0 = miny;
            lastBboxX1 = maxx;
            lastBboxY1 = maxy;
        }
        return changed;
    }

    private void statsLoop() {
        long lastFrames = 0, lastChanged = 0;
        long lastCpuTicks = cpuTicks0;
        long lastCpuWall = cpuWallNs0;
        while (running) {
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                return;
            }
            long now = System.nanoTime();
            long f = frames, c = changedFrames;
            long ticks = cpuTicks();
            double dtWall = (now - lastCpuWall) / 1e9;
            double cpu = dtWall > 0 ? ((ticks - lastCpuTicks) / 100.0) / dtWall * 100.0 : 0;
            cpuPct = cpu;
            double total = (now - t0Ns) / 1e9;
            double fps = (f - lastFrames) / dtWall;
            double avgInterval = f > 1 ? (sumIntervalNs / (double) (f - 1)) / 1e6 : 0;
            double avgProc = f > 0 ? (sumProcNs / (double) f) / 1e6 : 0;
            String bbox = lastBboxX1 >= 0
                    ? lastBboxX0 + "," + lastBboxY0 + "," + lastBboxX1 + "," + lastBboxY1 : "-";
            String line = String.format(Locale.US,
                    "t=%.1f fps=%.1f avg_interval_ms=%.2f avg_proc_ms=%.3f frames=%d chg_frames=%d chg_cells=%d bbox=%s cpu=%.1f%%",
                    total, fps, avgInterval, avgProc, f, c, lastChangeCells, bbox, cpu);
            Log.i(TAG, line);
            append(line);
            lastFrames = f;
            lastChanged = c;
            lastCpuTicks = ticks;
            lastCpuWall = now;
        }
    }

    private long cpuTicks() {
        try {
            java.io.BufferedReader br = new java.io.BufferedReader(
                    new java.io.FileReader("/proc/self/stat"));
            String s = br.readLine();
            br.close();
            int i = s.lastIndexOf(')');
            String[] f = s.substring(i + 2).split(" ");
            // after ')' fields start at state(3); utime=14, stime=15 -> idx 11,12
            return Long.parseLong(f[11]) + Long.parseLong(f[12]);
        } catch (Throwable t) {
            return 0;
        }
    }

    private void append(String line) {
        if (outFile == null) return;
        try (FileOutputStream fos = new FileOutputStream(outFile, true)) {
            fos.write((line + "\n").getBytes());
        } catch (Throwable ignored) {
        }
    }

    void dump() {
        String s = String.format(Locale.US,
                "frames=%d chg_frames=%d last_chg_cells=%d cpu=%.1f%% probe=%dx%d",
                frames, changedFrames, lastChangeCells, cpuPct, probeW, probeH);
        Log.i(TAG, "dump " + s);
        append("DUMP " + s);
    }

    void reset() {
        frames = 0;
        changedFrames = 0;
        sumProcNs = 0;
        sumIntervalNs = 0;
        t0Ns = System.nanoTime();
        Log.i(TAG, "counters reset");
    }

    private Notification buildNotification() {
        NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        String id = "probe";
        if (nm.getNotificationChannel(id) == null) {
            nm.createNotificationChannel(new NotificationChannel(
                    id, getString(R.string.chan_name), NotificationManager.IMPORTANCE_LOW));
        }
        return new Notification.Builder(this, id)
                .setContentTitle(getString(R.string.app_name))
                .setContentText(getString(R.string.notif_text))
                .setSmallIcon(android.R.drawable.ic_menu_info_details)
                .setOngoing(true)
                .build();
    }

    @Override
    public void onDestroy() {
        running = false;
        if (display != null) {
            display.release();
            display = null;
        }
        if (reader != null) {
            reader.close();
            reader = null;
        }
        if (projection != null) {
            projection.stop();
            projection = null;
        }
        if (thread != null) {
            thread.quitSafely();
            thread = null;
        }
        Log.i(TAG, "stopped");
        instance = null;
        super.onDestroy();
    }
}
