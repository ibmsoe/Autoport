package com.autoport.testcases;

import java.util.concurrent.TimeUnit;

import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.CommonFunctions;

public class BS_UseCase_7 {
	
	WebDriver driver;
	FluentWait<WebDriver> wait;
	CommonFunctions functions;
	HomePage homePage;
	BuildServersTab buildServerTab;
	
	 @Parameters({"browser"})
	 @BeforeTest
	  public void beforeTest(String browser) throws Exception {
		 //String browser = "firefox";
		 functions = new CommonFunctions();
		 functions.launchBrowser(browser);	
		 
		 driver = functions.driver;
		 homePage = functions.homePage;
		 buildServerTab = functions.buildServerTab;
		 
		 functions.openAutoport();
		 functions.goTo_ListInstallSingleSoftwarSection();	
	  }
	 
	 @Test(priority=0)
	  public void BS_Add_Package_To_Managed_List_RHEL_Server_01() throws Exception{ 
		  
	  }
	 
	 @Test(priority=0)
	  public void BS_Add_Package_To_Managed_List_Ubuntu_Server_01() throws Exception{ 
		  
	  }
	 
	  @Test(priority=0)
	  public void BS_Remove_Package_from_Managed_List_RHEL_Server_01() throws Exception{ 
		  
	  }
	 
	 @Test(priority=0)
	  public void BS_Remove_Package_from_Managed_List_Ubuntu_Server_01() throws Exception{ 
		  
	  }
}
