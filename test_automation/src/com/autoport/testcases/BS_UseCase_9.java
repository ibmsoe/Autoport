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

public class BS_UseCase_9 {
	WebDriver driver;
	HomePage homePage;
	BuildServersTab buildServerTab;
	 
	 @BeforeTest
	  public void beforeTest() throws Exception {
		 
		 //CommonFunctions.launchBrowser(); 
		 driver = CommonFunctions.driver; 
		 homePage = CommonFunctions.homePage;
		 buildServerTab = CommonFunctions.buildServerTab;
		 CommonFunctions.goTo_UploadPackageToRepositorySection();	
	  }
	 
	 @Test(priority=0,  dataProvider = "packages")
	  public void BS_Upload_Packages_031(String packagename) throws Exception{ 
		 
		 buildServerTab.enterPackageToUpload(packagename);
		 
		 buildServerTab.selectPackageType("");
		 
		 buildServerTab.clickUploadBtn();
		 
		 buildServerTab.verifyUploadedSuccessfullyMessage();	
		 		 
	  }
	 
	 @DataProvider(name = "packages")	  
	 public Object[][] listBuildServers() throws IOException { 
		  
		  return ReadTestData.readCSV(this.getClass().getSimpleName());
	 
		  /*return new Object[][] {
				  
				  {"apache-ant-1.9.6-bin.zip"},
				  {"nmap-7.00-1.fc24.armv7hl.rpm"},
				  {"python-anyjson_0.3.3.orig.tar.gz"},
				  {"python-anyjson_0.3.3-1build1_all.deb"}				  
		  };	*/ 
	  }		 
}
