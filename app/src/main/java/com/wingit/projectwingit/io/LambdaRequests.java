package com.wingit.projectwingit.io;

import static com.wingit.projectwingit.utils.WingitLambdaConstants.*;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;

import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;

/**
 * Provides easy access to calling the Lambda API
 */
public class LambdaRequests {

    /**
     * Sends a create_account request to the API
     * @param username the username
     * @param email the email
     * @param passwordHash the password needs to be hashed first before giving to this method
     * @return A LambdaResponse of the response
     */
    public static LambdaResponse createAccount(String username, String email, String passwordHash){
        try{
            String[] params = {
                    USERNAME_STR, username,
                    EMAIL_STR, email,
                    PASSWORD_HASH_STR, passwordHash,
                    EVENT_TYPE_STR, EVENT_CREATE_ACCOUNT_STR,
            };

            return sendRequest("POST", params);
        }catch (IOException e){
            return new LambdaResponse(LambdaResponse.ErrorState.CLIENT_ERROR,
                    "Error sending createAccount request: " + e.getMessage());
        }
    }

    /**
     * Login to an account
     * @param userOrEmail either the username or the email
     * @param passwordHash the hash of the password
     * @return
     */
    public static LambdaResponse login(String userOrEmail, String passwordHash){
        try{
            if (userOrEmail.contains("@")){
                String[] params = {
                        EMAIL_STR, userOrEmail,
                        PASSWORD_HASH_STR, passwordHash,
                        EVENT_TYPE_STR, EVENT_LOGIN_STR,
                };
                return sendRequest("GET", params);
            }

            String[] params = {
                    USERNAME_STR, userOrEmail,
                    PASSWORD_HASH_STR, passwordHash,
                    EVENT_TYPE_STR, EVENT_LOGIN_STR,
            };
            return sendRequest("GET", params);

        }catch (IOException e){
            return new LambdaResponse(LambdaResponse.ErrorState.CLIENT_ERROR,
                    "Error sending login request: " + e.getMessage());
        }
    }

    /**
     * Send the prepared request and get back the response
     */
    private static LambdaResponse sendRequest(String httpMethod, String[] params) throws IOException{
        OkHttpClient client = new OkHttpClient();

        Request request;
        switch (httpMethod){
            case "POST":
                request = new Request.Builder().url(API_URL).post(buildParams(params)).build();
                break;
            case "DELETE":
                request = new Request.Builder().url(API_URL).delete(buildParams(params)).build();
                break;
            case "GET":
                request = new Request.Builder().url(buildGetUrl(params)).build();
                break;
            default:
                return new LambdaResponse(LambdaResponse.ErrorState.CLIENT_ERROR,
                        "Error unknown http method: " + httpMethod);
        }

        return new LambdaResponse(client.newCall(request));
    }

    /**
     * Gets the url encoded args string as a byte[]
     */
    private static String buildGetUrl(String[] params) throws UnsupportedEncodingException {
        StringBuilder ret = new StringBuilder();
        for(int i = 0; i < params.length; i+=2)
            ret.append(URLEncoder.encode(params[i], "UTF-8")).append("=").append(URLEncoder.encode(params[i+1], "UTF-8")).append("&");
        return ret.toString();
    }

    /**
     * Builds the request body
     */
    private static MultipartBody buildParams(String[] params){
        MultipartBody.Builder requestBody = new MultipartBody.Builder().setType(MultipartBody.FORM);
        for(int i = 0; i < params.length; i+=2){
            requestBody = requestBody.addFormDataPart(params[i], params[i+1]);
        }
        return requestBody.build();
    }
}
