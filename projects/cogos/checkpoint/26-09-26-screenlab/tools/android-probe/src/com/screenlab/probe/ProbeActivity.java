package com.screenlab.probe;

import android.app.Activity;
import android.content.Intent;
import android.media.projection.MediaProjectionManager;
import android.os.Bundle;
import android.util.Log;

/**
 * Launches the MediaProjection consent dialog and hands the grant to
 * {@link ProbeService}. Config (probe size / cell px) is passed via intent
 * extras and stashed on ProbeService statics.
 */
public class ProbeActivity extends Activity {
    static final String TAG = "screenprobe";
    static final int REQ = 7001;

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        Intent src = getIntent();
        ProbeService.pendingW = src.getIntExtra("w", 0);
        ProbeService.pendingH = src.getIntExtra("h", 0);
        ProbeService.pendingCell = src.getIntExtra("cell", 24);
        ProbeService.pendingThresh = src.getIntExtra("thresh", 24);
        MediaProjectionManager mpm =
                (MediaProjectionManager) getSystemService(MEDIA_PROJECTION_SERVICE);
        startActivityForResult(mpm.createScreenCaptureIntent(), REQ);
    }

    @Override
    protected void onActivityResult(int req, int res, Intent data) {
        super.onActivityResult(req, res, data);
        Log.i(TAG, "consent result=" + res + " data=" + (data != null));
        if (res == RESULT_OK && data != null) {
            Intent i = new Intent(this, ProbeService.class)
                    .setAction(ProbeService.ACTION_START)
                    .putExtra(ProbeService.EXTRA_CODE, res)
                    .putExtra(ProbeService.EXTRA_DATA, data);
            startForegroundService(i);
        }
        finish();
    }
}
