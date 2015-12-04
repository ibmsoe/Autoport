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

public class BS_UseCase_6 {
	
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
		 functions.goTo_ListInstallUsingManagedServicesSection();	
	  }
	 @Test (priority=0)
	  public void BS_List_Managed_Packages_RHEL() throws Exception{	
		 
		 buildServerTab.clickListRhelBtn(); 
		 
		 String notificationMesssage = "This tool defines a minimum set of packages and package versions that cannot be removed. You can search for new packages and Add them to the Managed List. You can Remove any package that you added, but you cannot remove packages from the minimum set as they are required for proper function. These packages cannot be selected --- gray selection box. Once the Managed List is correct, select a Build server and press Sync and install procedures will commence.";
		  
		  buildServerTab.verifyNotificationMessageForManagedServices(notificationMesssage); 
		  
		  buildServerTab.verifyPopulatedBuildServers("RHEL");
		  
		  buildServerTab.verifySearchResultsForManagedServicesList("RHEL");		 
		 
	  }
	
	 @Test (priority=1)
	  public void BS_List_Managed_Packages_Ubuntu() throws Exception{	
		 
		  buildServerTab.clickListUbuntuBtn(); 
		 
		  String notificationMesssage = "This tool defines a minimum set of packages and package versions that cannot be removed. You can search for new packages and Add them to the Managed List. You can Remove any package that you added, but you cannot remove packages from the minimum set as they are required for proper function. These packages cannot be selected --- gray selection box. Once the Managed List is correct, select a Build server and press Sync and install procedures will commence.";
		  
		  buildServerTab.verifyNotificationMessageForManagedServices(notificationMesssage); 
		  
		  buildServerTab.verifyPopulatedBuildServers("Ubuntu");
		  
		  buildServerTab.verifySearchResultsForManagedServicesList("Ubuntu");
	  }
	 
	 @Test (priority=2)
	  public void BS_List_Managed_Packages_All() throws Exception{	
		 
		  buildServerTab.clickListAllBtn();
		  
		  String notificationMesssage = "This tool defines a minimum set of packages and package versions that cannot be removed. You can search for new packages and Add them to the Managed List. You can Remove any package that you added, but you cannot remove packages from the minimum set as they are required for proper function. These packages cannot be selected --- gray selection box. Once the Managed List is correct, select a Build server and press Sync and install procedures will commence.";
		  
		  buildServerTab.verifyNotificationMessageForManagedServices(notificationMesssage); 
		  
		  buildServerTab.verifyPopulatedBuildServers("All");
		  
		  buildServerTab.verifySearchResultsForManagedServicesList("All");
	  }
	 
	 @AfterTest
	  public void afterClass() {
		  
		  driver.quit();
	  }
	 
}
