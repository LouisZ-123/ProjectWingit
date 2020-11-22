package com.wingit.projectwingit.utils;

import com.wingit.projectwingit.debug.WingitErrors;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class WingitUtils {

    /**
     * Does a SHA256 hash of the given password string and returns a string in hex
     */
    public static String hashPassword(String password){
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            return bytesToHex(digest.digest(password.getBytes(StandardCharsets.UTF_8)));
        } catch (NoSuchAlgorithmException e) {}

        return null;
    }

    private static String bytesToHex(byte[] hash) {
        StringBuilder hexString = new StringBuilder(2 * hash.length);
        for (int i = 0; i < hash.length; i++) {
            String hex = Integer.toHexString(0xff & hash[i]);
            if(hex.length() == 1) {
                hexString.append('0');
            }
            hexString.append(hex);
        }
        return hexString.toString();
    }

    /**
     * Returns true if the user enters an acceptable password. As of now, we only check that the
     * password is at least 8 characters long.
     */
    public boolean checkAcceptablePassword(String password){
        return password.length() >= 8;
    }
}
