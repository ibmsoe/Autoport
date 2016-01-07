package com.autoport.testcases;

import java.io.IOException;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class BS_UseCase_4 {
	
	WebDriver driver;
	HomePage homePage;
	BuildServersTab buildServerTab;	
	 
	 @BeforeTest
	  public void beforeTest() throws Exception {
		 //CommonFunctions.launchBrowser(); 
		 driver = CommonFunctions.driver; 
		 homePage = CommonFunctions.homePage;
		 buildServerTab = CommonFunctions.buildServerTab;		 
		 CommonFunctions.goTo_ListInstallSingleSoftwarSection();		 
	  }
	 
	 @Test (priority=0, dataProvider = "buildServers")
	  public void BS_Update_Package_On_Servers_011_015(String buildServer) throws Exception{ 
		  		  
		  buildServerTab.selectBuildServer(buildServer);
		  
		  buildServerTab.clickListBtn();
		  
		  buildServerTab.selectMaximumRecordsToDisplay();
		  
		  buildServerTab.verifyInstallRemoveButtons("disabled");
		  
		  String packegeselected =  buildServerTab.selectPackageToUpdate();
		  
		  buildServerTab.verifyInstallRemoveButtons("enabled");
		  
		  buildServerTab.clickInstallUpdateBtn();
		  
		  buildServerTab.verifyUpdationSuccessPopUp(packegeselected);
		  
		  buildServerTab.enterPackageToSearch(packegeselected); 
			 
		  buildServerTab.selectBuildServer(buildServer);
		  
		  buildServerTab.clickListBtn();
		  
		  buildServerTab.VerifyPackageUpdateIsSuccessfull(packegeselected);
		  
		  buildServerTab.clearPackageName();
		  
	  }
	 
	 @DataProvider(name = "buildServers")	  
	 public Object[][] listBuildServers() throws IOException { 
		  
		  return ReadTestData.readCSV(this.getClass().getSimpleName());
	 
		 /* return new Object[][] {
				  {"ppcle-ubuntu"},
				  {"x86-ubuntu"},
				  {"x86-64-rhel"},
				  {"ppc64le-rhel"}
				  };*/	 
	  }	
}
