package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.CommonFunctions;

public class BS_UseCase_8 {
	
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
	 
	 @Test(priority=0)
	  public void BS_Synch_Packages_On_RHEL_Servers_029() throws Exception{ 
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
	  public void BS_Synch_Packages_On_Ubuntu_Servers_030() throws Exception{ 
		 buildServerTab.clickListUbuntuBtn(); 
		  
		  buildServerTab.verifyPopulatedBuildServers("Ubuntu");		  
		  
		  buildServerTab.clickSynchBtn();
		  
		  buildServerTab.verifySelectBuildServerMsg();
		  
		  buildServerTab.selectBuildServerToSynch("ppcle-ubuntu");
		  
		  buildServerTab.clickSynchBtn();
		  
		  buildServerTab.verifyBackgroundInstallationPopup("ppcle-ubuntu");
		  
		  buildServerTab.verifySychSuccessPopUp();
	  }	 
}
