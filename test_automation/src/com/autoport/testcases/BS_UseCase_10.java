package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class BS_UseCase_10 {
	
	
	WebDriver driver;
	HomePage homePage;
	BuildServersTab buildServerTab;
	String jenkinsUrl;
	 
	 @BeforeTest
	  public void beforeTest() throws Exception {
		 //CommonFunctions.launchBrowser(); 
		 driver = CommonFunctions.driver; 
		 homePage = CommonFunctions.homePage;
		 buildServerTab = CommonFunctions.buildServerTab;
		 jenkinsUrl = ReadTestData.readParameter("BS_UseCase_1", "JenkinsUrl");
		 
		 CommonFunctions.goTo_ShowCleanSlavesUsingManagedServicesSection();
		 	
	  }
	 
	 
	 @Test (priority=0 ) 
	  public void BS_reboot_sync_UI_32() { 
		  
		 buildServerTab.verifyRebootSyncUI();
		 
		 String helpMesssage="If you see inconsistent build or test results, you may want to restore the managed runtime environment of the build server.    Before attempting to re-sync the server, you should ensure that the server is not busy.    The Jenkins Slave link may be used for this purpose.";
		 
		 buildServerTab
			.verifyHelpTextForRebootSyncBuildSlaves(helpMesssage);
		 
		 buildServerTab.verifyRebootSyncBtn("enabled");
		 
		 buildServerTab.verifySelectBuildSlavePopupMsg();
		 
 
	  }
	 
	 
	 @Test(priority=1)
	 public void BS_reboot_sync_build_slave_33() throws InterruptedException{
		 
		 buildServerTab.selectBuildServerForSync();
		 
	 }
	
	 
	 @Test (priority=2)
	 public void BS_click_jenkins_link_34() throws InterruptedException{
	 
		 buildServerTab.checkJenkinslinkForBuildServers(jenkinsUrl);
		 
	 }
	 
}
