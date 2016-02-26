package com.autoport.testcases;

import java.io.IOException;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.*;

import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.*;


public class BS_UseCase_3{
	
	WebDriver driver;		
	HomePage homePage;
	BuildServersTab buildServerTab;
	String packageHavingTwoVersions;
	 
	 @BeforeTest
	  public void beforeTest() throws Exception {
		 //CommonFunctions.launchBrowser(); 
		 driver = CommonFunctions.driver; 
		 homePage = CommonFunctions.homePage;
		 buildServerTab = CommonFunctions.buildServerTab; 		
		 packageHavingTwoVersions = ReadTestData.readParameter("BS_UseCase_3", "packageNameHavingTwoVersionsAvailable");
		 
		 CommonFunctions.goTo_ListInstallSingleSoftwarSection();
	  }	 	
	
	 
	 //This is a system test case
	  @Test (priority=0, dataProvider = "buildServers")
	  public void BS_Install_Package_On_Servers_005_008(String buildServer, String packagename) throws Exception{
		  		 
		  buildServerTab.enterPackageToSearch(packagename); 
		  
		  buildServerTab.selectBuildServer(buildServer);
		  
		  buildServerTab.clickListBtn();
		  
		  buildServerTab.verifyInstallRemoveButtons("disabled");
		  
		  String packegeselected =  buildServerTab.selectRandomPackageToInstall();
		  
		  buildServerTab.verifyInstallRemoveButtons("enabled");
		  
		  buildServerTab.clickInstallUpdateBtn();
		  
		  buildServerTab.verifyInstallationSuccessPopUp(packegeselected);		  
		  
		  buildServerTab.enterPackageToSearch(packegeselected); 
			 
		  buildServerTab.selectBuildServer(buildServer);
		  
		  buildServerTab.clickListBtn();
		  
		  buildServerTab.verifyInstalledVersionIsNotNA(packegeselected);
	  }
	 
	  //This is a system test case
	  @Test (priority=1)
	  public void BS_Install_Already_Installed_Package_009() throws Exception{
		  
		  buildServerTab.selectFirstBuildServer();
		  
		  buildServerTab.enterPackageToSearch(""); 
		  
		  buildServerTab.clickListBtn();
		  
		  buildServerTab.selectAlreadyInstalledPackageToInstall();
		  
		  buildServerTab.clickInstallUpdateBtn();
		  
		  buildServerTab.verifyAlreadyInstalledMessage();
	  }	  
	  
	  ////This is a system test case
	   @Test (priority=2)
	  public void BS_Install_package_with_different_versions_010() throws Exception{
		  
		  buildServerTab.enterPackageToSearch(packageHavingTwoVersions); 
		  
		  buildServerTab.selectFirstBuildServer();
		  		  
		  buildServerTab.clickListBtn();
		  
		  String firstVersion = buildServerTab.selectTwoVersionsToInstall(packageHavingTwoVersions);
		  
		  buildServerTab.clickInstallUpdateBtn();
		  
		  buildServerTab.verifyTwoVersionMessage(packageHavingTwoVersions, firstVersion);
		  
		  buildServerTab.verifyInstallationSuccessPopUp(packageHavingTwoVersions);		  
		  
		  buildServerTab.enterPackageToSearch(packageHavingTwoVersions); 
			 
		  buildServerTab.selectFirstBuildServer();
		  
		  buildServerTab.clickListBtn();
		  
		  buildServerTab.verifyInstalledVersionIsNotNA(packageHavingTwoVersions);
		  
	  }
	  
	  @DataProvider(name = "buildServers")	  
	  public Object[][] listBuildServers() throws IOException { 
		  
		  return ReadTestData.readCSV(this.getClass().getSimpleName());
	 
		  /*return new Object[][] {
				  {"ppcle-ubuntu" ,"python-bson"},
				  {"x86-ubuntu" ,"python-bson"}, 
				  {"x86-64-rhel" ,"apache-ant"},
				  {"ppc64le-rhel" ,"apache-ant"}
				  };	*/ 
	  }	
	  
}
