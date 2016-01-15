package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class BS_UseCase_8 {
	
	WebDriver driver;
	HomePage homePage;
	BuildServersTab buildServerTab;
	String rhelBuildServerToSync;
	String ubuntuBuildServerToSync;
	
	 @BeforeTest
	  public void beforeTest() throws Exception {
		//CommonFunctions.launchBrowser(); 
		 driver = CommonFunctions.driver; 
		 homePage = CommonFunctions.homePage;
		 buildServerTab = CommonFunctions.buildServerTab;
		 rhelBuildServerToSync = ReadTestData.readParameter("BS_UseCase_8", "rhelBuildServerToSync");
		 ubuntuBuildServerToSync = ReadTestData.readParameter("BS_UseCase_8", "ubuntuBuildServerToSync");
		 
		 CommonFunctions.goTo_ListInstallUsingManagedServicesSection();	
	  }
	 
	 @Test(priority=0)
	  public void BS_Synch_Packages_On_RHEL_Servers_029() throws Exception{ 
		  buildServerTab.clickListRhelBtn();
		  
		  buildServerTab.verifyPopulatedBuildServers("RHEL");
		  
		  buildServerTab.clickSynchBtn();
		  
		  buildServerTab.verifySelectBuildServerMsg();
		  
		  buildServerTab.selectBuildServerToSynch(rhelBuildServerToSync);
		  
		  buildServerTab.clickSynchBtn();
		  
		  buildServerTab.verifyBackgroundInstallationPopup(rhelBuildServerToSync);
		  
		  buildServerTab.verifySychSuccessPopUp();
	  }
	
	 @Test(priority=1)
	  public void BS_Synch_Packages_On_Ubuntu_Servers_030() throws Exception{ 
		 buildServerTab.clickListUbuntuBtn(); 
		  
		  buildServerTab.verifyPopulatedBuildServers("Ubuntu");		  
		  
		  buildServerTab.clickSynchBtn();
		  
		  buildServerTab.verifySelectBuildServerMsg();
		  
		  buildServerTab.selectBuildServerToSynch(ubuntuBuildServerToSync);
		  
		  buildServerTab.clickSynchBtn();
		  
		  buildServerTab.verifyBackgroundInstallationPopup(ubuntuBuildServerToSync);
		  
		  buildServerTab.verifySychSuccessPopUp();
	  }	 
}
