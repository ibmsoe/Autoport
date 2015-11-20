package com.autoport.utilities;

import org.testng.Reporter;

public class LogResult {
	
public static void pass(String message){
		
		Reporter.log("PASS : <font color=\"green\"><b> "+ message +"</b></font><br/>");		
	}
	
	public static void fail(String message){
		
		Reporter.log("FAIL : <font color=\"red\"><b> "+ message +"</b></font><br/>");		
	}
}
