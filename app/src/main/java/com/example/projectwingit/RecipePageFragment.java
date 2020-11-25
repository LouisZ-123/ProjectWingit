package com.example.projectwingit;

import android.os.Bundle;

import androidx.fragment.app.Fragment;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.app.Dialog;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link Settings#newInstance} factory method to
 * create an instance of this fragment.
 */
public class RecipePageFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "param1";
    private static final String ARG_PARAM2 = "param2";

    // TODO: Rename and change types of parameters
    private String mParam1;
    private String mParam2;

    private Button rateButton;
    Dialog rateDialog;

    public RecipePageFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param param1 Parameter 1.
     * @param param2 Parameter 2.
     * @return A new instance of fragment Settings.
     */
    // TODO: Rename and change types and number of parameters
    public static RecipePageFragment newInstance(String param1, String param2) {
        RecipePageFragment fragment = new RecipePageFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, param1);
        args.putString(ARG_PARAM2, param2);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            mParam1 = getArguments().getString(ARG_PARAM1);
            mParam2 = getArguments().getString(ARG_PARAM2);
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View v = inflater.inflate(R.layout.fragment_recipe_page, container, false);

        // rating dialog characteristics TODO maybe make the rating dialog its own method
        rateDialog = new Dialog(getActivity());
        rateDialog.setContentView(R.layout.rating_dialog);
        rateDialog.setCancelable(false);

        Button cancel = rateDialog.findViewById(R.id.cancel_dialog_button);
        Button okay = rateDialog.findViewById(R.id.ok_dialog_button);

        cancel.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v){
                rateDialog.dismiss();
            }
        });

        okay.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v){
                rateDialog.dismiss();
            }
        });

        // rating button characteristics
        rateButton = (Button) v.findViewById(R.id.ratebutton);
        rateButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                rateDialog.show();
            }
        });


        // Inflate the layout for this fragment
        return v;
    }
}