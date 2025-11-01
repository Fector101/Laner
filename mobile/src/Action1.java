package org.laner.lan_ft;
// import android.util.Log;
import android.widget.Toast;

import android.content.BroadcastReceiver;

public class Action1 extends BroadcastReceiver{



  @Override
  public void onReceive(Context context, Intent intent) {
      // Code to execute once the button has been pressed
       Toast.makeText(context, "Action1 triggered!", Toast.LENGTH_SHORT).show();
    //  Log.d(TAG, "BroadcastReceiver received an intent!");
    }
}
