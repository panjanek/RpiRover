package org.panjanek.rpirover;

import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.Display;
import android.view.MotionEvent;
import android.view.View;
import android.view.Menu;
import android.view.MenuItem;
import android.view.Window;
import android.view.WindowManager;
import android.view.inputmethod.InputMethodManager;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.ToggleButton;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;

import java.net.URI;
import java.net.URISyntaxException;

public class MainRpi extends AppCompatActivity {

    private WebSocketClient mWebSocketClient = null;

    private Button buttonForward = null;
    private Button buttonLeft = null;
    private Button buttonStop = null;
    private Button buttonRight = null;
    private Button buttonBackward = null;
    private Button buttonLights = null;
    private Button buttonReboot = null;
    private Button buttonShutdown = null;

    private ToggleButton connectButton = null;

    private String url = null;

    boolean lights = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main_rpi);

        buttonForward = (Button) findViewById(R.id.forward);
        attachTouchEvents(buttonForward, "forward");
        buttonLeft = (Button) findViewById(R.id.left);
        attachTouchEvents(buttonLeft, "left");
        buttonStop = (Button) findViewById(R.id.stop);
        attachTouchEvents(buttonStop, "stop");
        buttonRight = (Button) findViewById(R.id.right);
        attachTouchEvents(buttonRight, "right");
        buttonBackward = (Button) findViewById(R.id.backward);
        attachTouchEvents(buttonBackward, "backward");

        buttonLights = (Button) findViewById(R.id.lights);
        buttonReboot = (Button) findViewById(R.id.reboot);
        buttonShutdown = (Button) findViewById(R.id.shutdown);
        connectButton = (ToggleButton) findViewById(R.id.connect);

        ToggleButton toggle = (ToggleButton) findViewById(R.id.connect);
        toggle.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if (isChecked) {
                    connect(buttonView);
                } else {
                    disconnect();
                }
            }
        });
    }

    private void attachTouchEvents(Button button, final String cmd)
    {
        button.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                switch (event.getAction()) {
                    case MotionEvent.ACTION_DOWN:
                        sendCommand(cmd);
                        return true;
                    case MotionEvent.ACTION_UP:
                        sendCommand("stop");
                        return true;
                }
                return false;
            }
        });
    }

    public void connect(View view) {
        //hide keyboard
        InputMethodManager inputManager = (InputMethodManager)
                getSystemService(Context.INPUT_METHOD_SERVICE);
        inputManager.hideSoftInputFromWindow(getCurrentFocus().getWindowToken(),
                InputMethodManager.HIDE_NOT_ALWAYS);
        ((Button) findViewById(R.id.connect)).requestFocus();

        EditText edit = (EditText) findViewById(R.id.ip);
        this.url = edit.getText().toString();
        Log.i("Main", "Connecting to "+this.url);

        // load camera view
        WebView wv = (WebView) findViewById(R.id.web);
        wv.setWebChromeClient(new WebChromeClient());
        wv.loadUrl("http://"+this.url+":8081");
        wv.setInitialScale(getScale(view.getContext(), 960));

        //connect socket
        connectWebSocket("ws://"+this.url+"/ws");
    }


    private void disconnect() {
        try {
            mWebSocketClient.close();
        } catch (Exception e) {
            e.printStackTrace();
        }

        enableButtons(false);
        connectButton.setChecked(false);
        WebView wv = (WebView) findViewById(R.id.web);
        wv.loadData("<html><body><h1>Disconnected</h1></body></html>", "text/html", "UTF8");

    }

    public void lightsClicked(View view) {
        lights = ! lights;
        String cmd = lights ? "lightson" : "lightsoff";
        this.sendCommand(cmd);
    }

    public void rebootClicked(View view) {
        if (this.mWebSocketClient == null) {
            showError("Not connected to rover!");
            return;
        }

        new AlertDialog.Builder(view.getContext())
                .setTitle("Reboot?")
                .setMessage("Are you sure you want to reboot the rover?")
                .setPositiveButton(android.R.string.yes, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        Log.i("Popup", "Rebooting");
                        sendCommand("reboot");
                        disconnect();
                    }
                })
                .setNegativeButton(android.R.string.cancel, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        Log.i("Popup", "Cancel");
                    }
                })
                .setIcon(android.R.drawable.ic_menu_revert)
                .show();
    }

    public void shutdownClicked(View view) {
        if (this.mWebSocketClient == null) {
            showError("Not connected to rover!");
            return;
        }

        new AlertDialog.Builder(view.getContext())
                .setTitle("Shutdown?")
                .setMessage("Are you sure you want to shutdown the rover?")
                .setPositiveButton(android.R.string.yes, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        Log.i("Popup", "Shuting down");
                        sendCommand("shutdown");
                        disconnect();
                    }
                })
                .setNegativeButton(android.R.string.cancel, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        Log.i("Popup", "Cancel");
                    }
                })
                .setIcon(android.R.drawable.ic_lock_power_off)
                .show();
    }

    private void connectWebSocket(String url)
    {
        URI uri;
        try {
            uri = new URI(url);
        } catch (URISyntaxException e) {
            e.printStackTrace();
            return;
        }

        mWebSocketClient = new WebSocketClient(uri) {
            @Override
            public void onOpen(ServerHandshake serverHandshake) {
                Log.i("Websocket", "Opened");
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                       enableButtons(true);
                }});
            }

            @Override
            public void onMessage(String s) {
                final String message = s;
                Log.i("Websocket", "Data: "+s);
            }

            @Override
            public void onClose(int i, String s, boolean b) {
                Log.i("Websocket", "Closed " + s);
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        disconnect();
                    }});
            }

            @Override
            public void onError(Exception e) {
                Log.i("Websocket", "Error " + e.getMessage());
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        disconnect();
                    }
                });
            }
        };
        mWebSocketClient.connect();
    }

    private void showError(String message)
    {
        new AlertDialog.Builder(getCurrentFocus().getContext())
                .setTitle("Error")
                .setMessage(message)
                .setPositiveButton(android.R.string.ok, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) { }
                })
                .setIcon(android.R.drawable.stat_notify_error)
                .show();
    }

    private int getScale(Context ctx, int picWidth){
        Display display = ((WindowManager) getSystemService(Context.WINDOW_SERVICE)).getDefaultDisplay();
        int width = display.getWidth();
        Double val = new Double(width)/new Double(picWidth);
        val = val * 100d;
        return val.intValue();
    }

    private void sendCommand(String cmd)
    {
        if (this.mWebSocketClient != null) {
            try {
                mWebSocketClient.send(cmd);
            } catch (Exception e) {
                e.printStackTrace();
                showError("Error sending command!");
            }
            Log.i("Websocket", "Command '" + cmd + "' sent.");
        } else {
            showError("Not connected to rover!");
        }
    }

    private void enableButtons(boolean state)
    {
        buttonForward.setEnabled(state);
        buttonLeft.setEnabled(state);
        buttonStop.setEnabled(state);
        buttonRight.setEnabled(state);
        buttonBackward.setEnabled(state);
        buttonLights.setEnabled(state);
        buttonReboot.setEnabled(state);
        buttonShutdown.setEnabled(state);
    }
}
