package com.wingit.projectwingit.debug;

import android.util.Log;

/**
 * Class to handle showing logging info
 */
public class WingitLogging {

    /**
     * Different error types increasing in severity
     */
    public enum LogType{
        DEBUG, INFO, WARN, ERROR
    }

    // Some default tags for logging
    public static final String TAG_GENERAL = "general_info";
    public static final String TAG_DEFAULT = TAG_GENERAL;  // Default tag if one isn't specified
    public static final String TAG_ERROR_BASIC = "NOTICE";
    public static final String TAG_ERROR = "ERROR";
    public static final String TAG_ERROR_SEVERE = "SEVERE";
    public static final String TAG_SQL_ERROR = "SQL_ERROR";

    /**
     * Print a debug message to the console under tag "default"
     * @param message the message to print
     */
    public static void log(String message){
        log(TAG_DEFAULT, message, LogType.DEBUG);
    }

    /**
     * Print a debug message to the console with the given tag
     * @param tag the tag for the message
     * @param message the message to print
     */
    public static void log(String tag, String message){
        log(tag, message, LogType.DEBUG);
    }

    /**
     * Print a message to the console with the given log type and tag
     * @param tag the tag for the message
     * @param message the message to print
     * @param logType the type of log to log (DEBUG, INFO, WARN, ERROR)
     */
    public static void log(String tag, String message, LogType logType){
        switch(logType){
            case INFO:
                Log.i(tag, message);
                break;
            case WARN:
                Log.w(tag, message);
                break;
            case ERROR:
                Log.e(tag, message);
                break;

            // Debug and default
            default:
                Log.d(tag, message);
        }
    }


}