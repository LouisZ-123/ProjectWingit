package com.wingit.projectwingit.io;

/**
 * The returned response from a LambdaRequest
 */
public class LambdaResponse {
    public static final LambdaResponse CLIENT_ERROR = new LambdaResponse("CLIENT_ERROR");

    private final int errorState;
    private final String response;
    private static final int NO_ERROR = 0;
    private static final int NORMAL_ERROR = 1;
    private static final int C_ERROR = 2;
    private static final int NULL_ERROR = 3;

    public LambdaResponse(String response){
        if (response == null) {
            errorState = NULL_ERROR;
            this.response = "null error";
        }else if (response.equals("CLIENT_ERROR")) {
            errorState = C_ERROR;
            this.response = "client error";
        }else {
            errorState = NO_ERROR;
            this.response = response;
        }
    }

    /**
     * Returns true if the error was on the client side and not the server side
     */
    public boolean isClientError() {
        return errorState == C_ERROR;
    }

    /**
     * Returns true if there was an error
     */
    public boolean isError() {
        return errorState != NO_ERROR;
    }

    /**
     * Gets the response string
     */
    public String getResponse(){
        if (isError()){
            return "Error state: " + errorState + " response: " + response;
        }
        return response;
    }

}
