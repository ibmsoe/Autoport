package com.autoport.testcases;
import java.util.concurrent.TimeUnit;

import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.testng.annotations.*;

import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.*;


public class BS_UseCase_3{
	
	WebDriver driver;
	FluentWait<WebDriver> FluentWait;
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
	
	  @Test (priority=0, dataProvider = "buildServers")
	  public void BS_Install_Package_On_Servers(String buildServer, String packagename) throws Exception{
		  
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
	  
	  @Test (priority=1)
	  public void BS_Install_Already_Installed_Package_01() throws Exception{
		  
		  buildServerTab.selectBuildServer("ppcle-ubuntu");
		  
		  buildServerTab.enterPackageToSearch(""); 
		  
		  buildServerTab.clickListBtn();
		  
		  buildServerTab.selectAlreadyInstalledPackageToInstall();
		  
		  buildServerTab.clickInstallUpdateBtn();
		  
		  buildServerTab.verifyAlreadyInstalledMessage();
	  }	  
	  
	  @Test (priority=2)
	  public void BS_Install_package_with_different_versions_01() throws Exception{
		  
		  buildServerTab.enterPackageToSearch("apache-ant"); 
		  
		  buildServerTab.selectBuildServer("ppcle-ubuntu");
		  		  
		  buildServerTab.clickListBtn();
		  
		  String firstVersion = buildServerTab.selectTwoVersionsToInstall("apache-ant");
		  
		  buildServerTab.clickInstallUpdateBtn();
		  
		  buildServerTab.verifyTwoVersionMessage("apache-ant", firstVersion);
	  }
	  
	  @DataProvider(name = "buildServers")
	  
	  public static Object[][] listBuildServers() { 
	 
		  return new Object[][] {{"ppcle-ubuntu" ,"python-bson"},{"x86-ubuntu" ,"python-bson"}};	 
	  }	
	
	  @AfterTest
	  public void afterClass() {
		  
		  driver.quit();
	  }

}
