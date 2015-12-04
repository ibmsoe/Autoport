package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.testng.annotations.AfterTest;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.CommonFunctions;

public class BS_UseCase_9 {
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
		 functions.goTo_UploadPackageToRepositorySection();	
	  }
	 
	 @Test(priority=0,  dataProvider = "packages")
	  public void BS_Upload_Packages(String packagename) throws Exception{ 
		 
		 buildServerTab.enterPackageToUpload(packagename);
		 
		 buildServerTab.selectPackageType("");
		 
		 buildServerTab.clickUploadBtn();
		 
		 buildServerTab.verifyUploadedSuccessfullyMessage();	 
		 		 
	  }
	 
	 @DataProvider(name = "packages")	  
	  public static Object[][] listBuildServers() { 
	 
		  return new Object[][] {
				  
				  {"apache-ant-1.9.6-bin.zip"},
				  {"nmap-7.00-1.fc24.armv7hl.rpm"},
				  {"python-anyjson_0.3.3.orig.tar.gz"},
				  {"python-anyjson_0.3.3-1build1_all.deb"}				  
		  };	 
	  }	
	 
	 @AfterTest
	  public void afterClass() {
		  
		  driver.quit();
	  }
}
