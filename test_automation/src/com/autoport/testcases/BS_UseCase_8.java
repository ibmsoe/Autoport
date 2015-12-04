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

public class BS_UseCase_8 {
	
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
	 
	 @Test(priority=0)
	  public void BS_Synch_Packages_On_RHEL_Servers() throws Exception{ 
		  buildServerTab.clickListRhelBtn();
		  
		  buildServerTab.verifyPopulatedBuildServers("RHEL");
		  
		  buildServerTab.clickSynchBtn();
		  
		  buildServerTab.verifySelectBuildServerMsg();
		  
		  buildServerTab.selectBuildServerToSynch("ppc64le-rhel");
		  
		  buildServerTab.clickSynchBtn();
		  
		  buildServerTab.verifyBackgroundInstallationPopup("ppc64le-rhel");
		  
		  buildServerTab.verifySychSuccessPopUp();
	  }
	
	 @Test(priority=1)
	  public void BS_Synch_Packages_On_Ubuntu_Servers() throws Exception{ 
		 buildServerTab.clickListUbuntuBtn(); 
		  
		  buildServerTab.verifyPopulatedBuildServers("Ubuntu");		  
		  
		  buildServerTab.clickSynchBtn();
		  
		  buildServerTab.verifySelectBuildServerMsg();
		  
		  buildServerTab.selectBuildServerToSynch("ppc64le-64-ubuntu");
		  
		  buildServerTab.clickSynchBtn();
		  
		  buildServerTab.verifyBackgroundInstallationPopup("ppc64le-64-ubuntu");
		  
		  buildServerTab.verifySychSuccessPopUp();
	  }
	 
	 @AfterTest
	  public void afterClass() {
		  
		  driver.quit();
	  }
	 
}
