//package com.wingit.projectwingit;
//
//import androidx.annotation.RequiresApi;
//import androidx.appcompat.app.AppCompatActivity;
//
//import android.os.Build;
//import android.os.Bundle;
//import android.widget.TextView;
//
//import com.wingit.projectwingit.debug.WingitLogging;
//
//import static com.wingit.projectwingit.io.LambdaRequests.createAccount;
//import static com.wingit.projectwingit.utils.WingitUtils.hashPassword;
//
///**
// * The main application class
// */
//public class WingitApp extends AppCompatActivity {
//
//    @RequiresApi(api = Build.VERSION_CODES.N)
//    @Override
//    protected void onCreate(Bundle savedInstanceState) {
//        super.onCreate(savedInstanceState);
//        setContentView(R.layout.activity_main);
//
//        final TextView edit =  (TextView) findViewById(R.id.testText);
//        String passwordHash = hashPassword("testPassword");
//
//        Runnable runnable = () -> {
//            edit.setText();
//        };
//
//        Thread thread = new Thread(runnable);
//        thread.start();
//    }
//
//}