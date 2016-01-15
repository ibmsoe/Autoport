package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.CommonFunctions;

public class BS_UseCase_6 {
	
	WebDriver driver;
	HomePage homePage;
	BuildServersTab buildServerTab;
	
	 @BeforeTest
	  public void beforeTest() throws Exception {
		//CommonFunctions.launchBrowser(); 
		 driver = CommonFunctions.driver; 
		 homePage = CommonFunctions.homePage;
		 buildServerTab = CommonFunctions.buildServerTab;		
		 CommonFunctions.goTo_ListInstallUsingManagedServicesSection();	
	  }
	 @Test (priority=0)
	  public void BS_List_Managed_Packages_RHEL_022() throws Exception{	
		 
		 buildServerTab.clickListRhelBtn(); 
		 
		 String notificationMesssage = "This tool defines a minimum set of packages and package versions that cannot be removed. You can search for new packages and Add them to the Managed List. You can Remove any package that you added, but you cannot remove packages from the minimum set as they are required for proper function. These packages cannot be selected --- gray selection box. Once the Managed List is correct, select a Build server and press Sync and install procedures will commence.";
		  
		  buildServerTab.verifyNotificationMessageForManagedServices(notificationMesssage); 
		  
		  buildServerTab.verifyPopulatedBuildServers("RHEL");
		  
		  buildServerTab.verifySearchResultsForManagedServicesList("RHEL");		 
		 
	  }
	
	 @Test (priority=1)
	  public void BS_List_Managed_Packages_Ubuntu_023() throws Exception{	
		 
		  buildServerTab.clickListUbuntuBtn(); 
		 
		  String notificationMesssage = "This tool defines a minimum set of packages and package versions that cannot be removed. You can search for new packages and Add them to the Managed List. You can Remove any package that you added, but you cannot remove packages from the minimum set as they are required for proper function. These packages cannot be selected --- gray selection box. Once the Managed List is correct, select a Build server and press Sync and install procedures will commence.";
		  
		  buildServerTab.verifyNotificationMessageForManagedServices(notificationMesssage); 
		  
		  buildServerTab.verifyPopulatedBuildServers("Ubuntu");
		  
		  buildServerTab.verifySearchResultsForManagedServicesList("Ubuntu");
	  }
	 
	 @Test (priority=2)
	  public void BS_List_Managed_Packages_All_024() throws Exception{	
		 
		  buildServerTab.clickListAllBtn();
		  
		  String notificationMesssage = "This tool defines a minimum set of packages and package versions that cannot be removed. You can search for new packages and Add them to the Managed List. You can Remove any package that you added, but you cannot remove packages from the minimum set as they are required for proper function. These packages cannot be selected --- gray selection box. Once the Managed List is correct, select a Build server and press Sync and install procedures will commence.";
		  
		  buildServerTab.verifyNotificationMessageForManagedServices(notificationMesssage); 
		  
		  buildServerTab.verifyPopulatedBuildServers("All");
		  
		  buildServerTab.verifySearchResultsForManagedServicesList("All");
	  }
}
