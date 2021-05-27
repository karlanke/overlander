package com.example.backupcameraclient;

import androidx.appcompat.app.AppCompatActivity;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import com.google.android.material.floatingactionbutton.FloatingActionButton;
import com.neovisionaries.ws.client.WebSocket;
import com.neovisionaries.ws.client.WebSocketAdapter;
import com.neovisionaries.ws.client.WebSocketFactory;

import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends AppCompatActivity {

    WebSocket ws;
    String server = "backup.trailer.local";
    Boolean lights = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if(Build.PRODUCT.contains("sdk")){
            server = "10.0.2.2";
        }

        setContentView(R.layout.activity_main);

        FloatingActionButton clickButton = (FloatingActionButton) findViewById(R.id.lights);
        clickButton.setOnClickListener( new View.OnClickListener() {

            @Override
            public void onClick(View v) {
                lights = !lights;

                if (ws != null && ws.isOpen()){
                    ExecutorService executor = Executors.newSingleThreadExecutor();

                    executor.execute(new Runnable() {
                        @Override
                        public void run() {
                            ws.sendText("light|" + (lights ? "on" : "off"));
                        }
                    });
                }
            }
        });

    }

    @Override
    protected void onPause() {
        super.onPause();
        stopStreaming();
    }

    @Override
    protected void onPostResume() {
        super.onPostResume();
        startStreaming();
    }

    private void startStreaming() {
        ExecutorService executor = Executors.newSingleThreadExecutor();
        Handler handler = new Handler(Looper.getMainLooper());
        TextView tv1 = (TextView) findViewById(R.id.errorBox);

        executor.execute(new Runnable() {
            @Override
            public void run() {

                try {
                    ws = new WebSocketFactory().createSocket("ws://" + server + ":8000/stream");
                    // Register a listener to receive WebSocket events.
                    ws.addListener(new WebSocketAdapter() {
                        @Override
                        public void onBinaryMessage(WebSocket websocket, byte[] binary) throws Exception {
                            super.onBinaryMessage(websocket, binary);
                            Bitmap bmp = BitmapFactory.decodeByteArray(binary, 0, binary.length);

                            handler.post(new Runnable() {
                                @Override
                                public void run() {
                                    //UI Thread work here
                                    tv1.setText("");
                                    ImageView image = (ImageView) findViewById(R.id.imageView);
                                    image.setImageBitmap(bmp);

                                }
                            });

                        }
                    });
                    // Connect to the server and perform an opening handshake.
                    // This method blocks until the opening handshake is finished.
                    ws.connect();
                } catch (Exception e) {
                    e.printStackTrace();

                    StringWriter sw = new StringWriter();
                    e.printStackTrace(new PrintWriter(sw));
                    String exceptionAsString = sw.toString();
                    handler.post(new Runnable() {
                        @Override
                        public void run() {
                            //UI Thread work here
                            tv1.setText(exceptionAsString);
                        }
                    });

                }
            }
        });
    }

    private void stopStreaming(){
        if (ws.isOpen()){
            ws.disconnect();
        }
    }
}
