package com.wingit.projectwingit.io;
import android.os.Build;

import androidx.annotation.RequiresApi;

import com.wingit.projectwingit.io.LambdaResponse;
import static com.wingit.projectwingit.utils.WingitLambdaConstants.*;
import static com.wingit.projectwingit.debug.WingitErrors.ErrorSeverity.*;
import com.wingit.projectwingit.debug.WingitErrors;

import java.io.IOException;
import java.io.OutputStream;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

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
    @RequiresApi(api = Build.VERSION_CODES.N)
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
            WingitErrors.error("lambda-request", "Error sending request", WARNING, e);
        }

        return LambdaResponse.CLIENT_ERROR;
    }

    /**
     * Send the prepared request and get back the response
     */
    @RequiresApi(api = Build.VERSION_CODES.N)
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
                throw new IOException("Unknown httpMethod: " + httpMethod);
        }


        Response response = client.newCall(request).execute();
        return new LambdaResponse(response.body().string());
    }

    /**
     * Gets the url encoded args string as a byte[]
     */
    @RequiresApi(api = Build.VERSION_CODES.N)
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
