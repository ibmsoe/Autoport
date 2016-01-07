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

public class BS_UseCase_5 {
	
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
	  public void BS_Uninstall_Package_On_Servers_016_020(String buildServer, String packagename) throws Exception{
		  
		  buildServerTab.enterPackageToSearch(packagename); 
		  
		  buildServerTab.selectBuildServer(buildServer);
		  
		  buildServerTab.clickListBtn();
		  
		  buildServerTab.verifyInstallRemoveButtons("disabled");
		  
		  buildServerTab.selectPackageToUninstall();
		  
		  buildServerTab.verifyInstallRemoveButtons("enabled");
		  
		  buildServerTab.clickRemoveButtonToUninstall();
		  
		  buildServerTab.verifyUninstallationSuccessPopUp(packagename);		  
		  
		  buildServerTab.enterPackageToSearch(packagename); 
			 
		  buildServerTab.selectBuildServer(buildServer);
		  
		  buildServerTab.clickListBtn();
		  
		  buildServerTab.verifyInstalledVersionIsNA(packagename);	  
		  
	  }
	 
	 @Test
	  public void BS_Uninstall_Not_Installed_Package_021() throws Exception{
		  
		  buildServerTab.enterPackageToSearch("python-bson"); 
		  
		  buildServerTab.selectFirstBuildServer();
		  
		  buildServerTab.clickListBtn();
		  
		  buildServerTab.verifyInstallRemoveButtons("disabled");
		  
		  buildServerTab.selectPackageToUninstall();
		  
		  buildServerTab.verifyInstallRemoveButtons("enabled");
		  
		  buildServerTab.clickRemoveButtonToUninstall();
		  
		  buildServerTab.verifyPkgNotInstalledMessage();
		  
	  }
	 
	 @DataProvider(name = "buildServers")
	 public Object[][] listBuildServers() throws IOException { 
		  
		  return ReadTestData.readCSV(this.getClass().getSimpleName());
	 
		 /* return new Object[][] {
				  {"ppcle-ubuntu" ,"python-bson"},
				  {"x86-ubuntu" ,"python-bson"}, 
				  {"x86-64-rhel" ,"apache-ant"},
				  {"ppc64le-rhel" ,"apache-ant"}
				  };	 */
	  }	 
}
