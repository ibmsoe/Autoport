package com.autoport.testcases;

import java.io.IOException;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.*;

import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.*;

public class BS_UseCase_2{
	
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
	 
	 @Test  (priority=0, dataProvider = "buildServers")
	  public void BS_List_Installed_Packages_002(String buildServer, String packagename) throws Exception{	 
		  		 
 	      buildServerTab.verifyPlaceHolderTextForSearchBox();
		  
		  buildServerTab.selectBuildServer(buildServer);
		  
		  buildServerTab.clickListBtn();		  
		  
		  String notificationMesssage = "Actions taken on the list below apply only to the chosen build server. The managed package list is not updated. In this way you may customize the runtime environment of a given build server to facilitate a specific porting effort. When you are done, use the install services provided below to restore the managed runtime environment.";
		  
		  buildServerTab.verifyNotificationMessage(notificationMesssage); 
		  
		  buildServerTab.verifyOnlyInstalledPackagesareDisplayed();
	  }
	
	 @Test(priority=1, dataProvider = "buildServers")
	  public void BS_List_Specific_Packages_003(String buildServer, String packagename) throws Exception{	  
		  
		  buildServerTab.enterPackageToSearch(packagename); 
		 
		  buildServerTab.selectBuildServer(buildServer);
		  
		  buildServerTab.clickListBtn();
		  	  
		  String notificationMesssage = "Actions taken on the list below apply only to the chosen build server. The managed package list is not updated. In this way you may customize the runtime environment of a given build server to facilitate a specific porting effort. When you are done, use the install services provided below to restore the managed runtime environment.";
		  
		  buildServerTab.verifyNotificationMessage(notificationMesssage);	
		  
		  buildServerTab.verifySearchResultsforPackage(packagename);
	  }
	  
	  @DataProvider(name = "buildServers")	  
	  public Object[][] listBuildServers() throws IOException { 
		  
		  return ReadTestData.readCSV(this.getClass().getSimpleName());
		  /*
		  return new Object[][] {
				  {"ppcle-ubuntu" ,"python-bson"},
				  {"x86-ubuntu" ,"python-bson"}, 
				  {"x86-64-rhel" ,"apache-ant"},
				  {"ppc64le-rhel" ,"apache-ant"}
				  };*/
	  }		
}
