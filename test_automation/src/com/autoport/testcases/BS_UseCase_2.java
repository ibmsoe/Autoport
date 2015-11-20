package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.testng.annotations.*;

import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.*;

public class BS_UseCase_2{
	
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
	 
	 @Test  (priority=0, dataProvider = "buildServers")
	  public void BS_List_Installed_Packages(String buildServer, String packagename) throws Exception{	 
		  
	 	  buildServerTab.verifyPlaceHolderTextForSearchBox();
		  
		  buildServerTab.selectBuildServer(buildServer);
		  
		  buildServerTab.clickListBtn();		  
		  
		  String notificationMesssage = "Actions taken on the list below apply only to the chosen build server. The managed package list is not updated. In this way you may customize the runtime environment of a given build server to facilitate a specific porting effort. When you are done, use the install services provided below to restore the managed runtime environment.";
		  
		  buildServerTab.verifyNotificationMessage(notificationMesssage); 
		  
		  buildServerTab.verifyOnlyInstalledPackagesareDisplayed();
	  }
	
	 @Test(priority=1, dataProvider = "buildServers")
	  public void BS_List_Specific_Packages(String buildServer, String packagename) throws Exception{	  
		  
		  buildServerTab.enterPackageToSearch(packagename); 
		 
		  buildServerTab.selectBuildServer(buildServer);
		  
		  buildServerTab.clickListBtn();
		  	  
		  String notificationMesssage = "Actions taken on the list below apply only to the chosen build server. The managed package list is not updated. In this way you may customize the runtime environment of a given build server to facilitate a specific porting effort. When you are done, use the install services provided below to restore the managed runtime environment.";
		  
		  buildServerTab.verifyNotificationMessage(notificationMesssage);	
		  
		  buildServerTab.verifySearchResultsforPackage(packagename);
	  }
	  
	  @DataProvider(name = "buildServers")	  
	  public static Object[][] listBuildServers() { 
	 
		  return new Object[][] {{"ppcle-ubuntu" ,"python-bson"}, {"x86-ubuntu" ,"python-bson"}};
	  }	
	
	  @AfterTest
	  public void afterClass() {
		  
		  driver.quit();
	  }

}
