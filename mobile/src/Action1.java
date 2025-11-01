package org.laner.lan_ft;
import android.widget.Toast;
//The package name of your android app

import android.content.BroadcastReceiver;

public class Action1 extends BroadcastReceiver{



  @Override
  public void onReceive(Context context, Intent intent) {
    Toast.makeText(context, "Action1 triggered!", Toast.LENGTH_SHORT).show();
      // Code to execute once the button has been pressed
    }
}