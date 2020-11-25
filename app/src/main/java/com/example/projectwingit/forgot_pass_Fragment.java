package com.example.projectwingit;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;

import androidx.fragment.app.Fragment;



import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.view.View.OnClickListener;
import android.widget.Toast;


public class forgot_pass_Fragment extends Fragment implements OnClickListener {

    private EditText fp_Email;
    private Button link_Password;
    private EditText back_Login;
    public forgot_pass_Fragment() {
        // Required empty public constructor
    }

//
//    public static forgot_pass_Fragment newInstance(String param1, String param2) {
//        forgot_pass_Fragment fragment = new forgot_pass_Fragment();
//        Bundle args = new Bundle();
//        args.putString(ARG_PARAM1, param1);
//        args.putString(ARG_PARAM2, param2);
//        fragment.setArguments(args);
//        return fragment;
//    }

//    @Override
//    public void onCreate(Bundle savedInstanceState) {
//        super.onCreate(savedInstanceState);
//
//        fp_Email = getView().findViewById(R.id.rec_pass_email);
//        link_Password = getView().findViewById(R.id.link_fp);
//        back_Login = getView().findViewById(R.id.fp_Back);
//
//        link_Password.setOnClickListener(new View.OnClickListener() {
//            @Override
//            public void onClick(View v) {
//                String user_Email = fp_Email.getText().toString().trim();
//
//                if (user_Email.isEmpty() || user_Email == null) {
//                    Toast.makeText(getActivity(), "Please enter valid email", Toast.LENGTH_LONG).show();
//                }
//                else {
//                    //Send password to email
//                }
//            }
//        });
//    }

    @Override
    public void onClick(View view) {
        Intent intent = new Intent(getActivity(), MainActivity.class);
        startActivity(intent);
    }

    @Override
    public void onViewCreated(View view, Bundle savedInstanceState) {
        TextView back_Login = getActivity().findViewById(R.id.back_fp);
        back_Login.setOnClickListener((View.OnClickListener) this);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_forgot_pass_, container, false);
    }
}