package com.example.projectwingit;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.MenuItem;

import com.google.android.material.navigation.NavigationView;

public class UserAccount extends AppCompatActivity implements NavigationView.OnNavigationItemSelectedListener {

    private NavigationView accountView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_user_account);

        NavigationView accountView = findViewById(R.id.userAccountView);
        accountView.setNavigationItemSelectedListener(this);
    }

    @Override
    public boolean onNavigationItemSelected(@NonNull MenuItem item) {

//        switch (item.getItemId()) {
//
//        }

        return false;
    }
}