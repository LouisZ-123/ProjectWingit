package com.wingit.projectwingit;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Build;
import android.os.Bundle;
import android.widget.TextView;

import com.wingit.projectwingit.debug.WingitLogging;
import com.wingit.projectwingit.io.LambdaRequests;
import com.wingit.projectwingit.io.LambdaResponse;
import com.wingit.projectwingit.utils.WingitLambdaConstants;

import static com.wingit.projectwingit.io.LambdaRequests.createAccount;
import static com.wingit.projectwingit.utils.WingitUtils.hashPassword;

/**
 * The main application class
 */
public class WingitApp extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        final TextView textView = (TextView) findViewById(R.id.testText);
        String passwordHash = hashPassword("testPassword");

        LambdaResponse response = LambdaRequests.createAccount("applefdgf", "adsagsa@b.com", passwordHash);

        textView.post(new Runnable() {
            public void run() {
                textView.setText(response.getResponseInfo());
            }
        });
    }

}