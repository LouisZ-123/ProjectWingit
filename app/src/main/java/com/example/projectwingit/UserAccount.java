package com.example.projectwingit;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.view.GravityCompat;
import androidx.drawerlayout.widget.DrawerLayout;

import android.app.FragmentTransaction;
import android.content.Intent;
import android.os.Bundle;
import android.view.Gravity;
import android.view.MenuItem;

import com.google.android.material.navigation.NavigationView;

public class UserAccount extends AppCompatActivity implements NavigationView.OnNavigationItemSelectedListener {

    private NavigationView accountView;
    private DrawerLayout account_Drawer;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_user_account);

        account_Drawer = findViewById(R.id.drawer_Acc);
        account_Drawer.openDrawer(GravityCompat.START);
        NavigationView accountView = findViewById(R.id.userAccountView);
        accountView.setNavigationItemSelectedListener(this);
//        getSupportFragmentManager().beginTransaction().replace(R.id.container_user_account, new LoginFragment()).commit();

    }

    @Override
    public boolean onNavigationItemSelected(@NonNull MenuItem item) {

        switch (item.getItemId()) {
            case R.id.user_account_login:
                getSupportFragmentManager().beginTransaction().replace(R.id.container_user_account, new LoginFragment()).commit();
                break;
            case R.id.user_account_create:
                getSupportFragmentManager().beginTransaction().replace(R.id.container_user_account, new RegisterFragment()).commit();
                break;
        }
        account_Drawer.closeDrawer(GravityCompat.START);

        return true;
    }
}