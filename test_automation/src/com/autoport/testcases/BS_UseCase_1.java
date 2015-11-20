package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.testng.annotations.AfterTest;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.CommonFunctions;

public class BS_UseCase_1 {
	WebDriver driver;
	FluentWait<WebDriver> fluentWait;
	CommonFunctions functions;
	HomePage homePage;
	BuildServersTab buildServerTab;
	
	 @Parameters({"browser"})
	 @BeforeTest
	  public void beforeTest(String browser) throws Exception {
		 
		 functions = new CommonFunctions();
		 functions.launchBrowser(browser);
		 driver = functions.driver;		 
		 homePage = functions.homePage;
		 buildServerTab = functions.buildServerTab;
		 fluentWait = functions.fluentWait;
	  }
	 
	 @Test(priority=0)
	 public void openListInstallSingleSoftwarSection(){
		 
		 driver.get("http://10.233.188.49:5601/autoport/");
		  
		 homePage.clickBuildServerTab();  
	 }
	 
	 @AfterTest
	  public void afterClass() {
		  
		  driver.quit();
	  }

}
