package com.screenlab.probe;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

/** adb-driven control: op=stop|dump|reset|a11ydump. */
public class ProbeCmdReceiver extends BroadcastReceiver {
    static final String TAG = "screenprobe";

    @Override
    public void onReceive(Context c, Intent i) {
        String op = i.getStringExtra("op");
        Log.i(TAG, "cmd " + op);
        if ("stop".equals(op)) {
            c.stopService(new Intent(c, ProbeService.class));
        } else if ("dump".equals(op)) {
            if (ProbeService.instance != null) ProbeService.instance.dump();
        } else if ("reset".equals(op)) {
            if (ProbeService.instance != null) ProbeService.instance.reset();
        } else if ("a11ydump".equals(op)) {
            if (ProbeA11yService.instance != null) ProbeA11yService.instance.dump();
        }
    }
}
