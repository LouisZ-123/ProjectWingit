package com.wingit.projectwingit.debug;

import java.io.PrintWriter;
import java.io.StringWriter;

import static com.wingit.projectwingit.debug.WingitLogging.LogType;

/**
 * Class to handle showing exceptions, and any ramifications of certain types of exceptions
 */
public class WingitErrors {

    /**
     * Different error types increasing in severity
     */
    public enum ErrorSeverity{
        NOTICE, WARNING, SEVERE
    }

    /**
     * Method for raising errors from exceptions and logging them
     * @param tag the tag for logging
     * @param message the error message
     * @param severity the severity of the error:
     *      NOTICE - just show the notice, probably nothing wrong
     *      WARNING - just show the warning, but continue the app. Something is probably
     *                  wrong but the app will continue working
     *      SEVERE - terminal error, kill the app
     * @param ex the exception that was raised, will print stack trace
     */
    public static void error(String tag, String message, ErrorSeverity severity, Exception ex){
        StringWriter sw = new StringWriter();
        PrintWriter pw = new PrintWriter(sw);
        ex.printStackTrace(pw);
        error(tag, message + "\n\nStack Trace:\n" + sw.toString(), severity);
    }

    /**
     * Method for raising errors (not from exceptions) and logging them
     * @param tag the tag for logging
     * @param message the error message
     * @param severity the severity of the error:
     *      NOTICE - just show the notice, probably nothing wrong
     *      WARNING - just show the warning, but continue the app. Something is probably
     *                  wrong but the app will continue working
     *      SEVERE - terminal error, kill the app
     */
    public static void error(String tag, String message, ErrorSeverity severity){
        WingitLogging.log(tag, message, getLogType(severity));

        // Exit iff E_SEVERE
        if (severity == ErrorSeverity.SEVERE) System.exit(-1);
    }

    /**
     * Helper function to get the LogType from the severity
     * @param severity the severity
     */
    private static LogType getLogType(ErrorSeverity severity){
        switch(severity){
            case SEVERE:
                return LogType.ERROR;
            default:
                return LogType.WARN;
        }
    }

}



