package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class BS_UseCase_7 {
	
	WebDriver driver;
	HomePage homePage;
	BuildServersTab buildServerTab;
	String packageToAddToManagedList;
	String packageToRemoveFromManagedList;
	String BSUbuntu;
	String BSCentOS;
	
	 
	 @BeforeTest
	  public void beforeTest() throws Exception {
		//CommonFunctions.launchBrowser(); 
		 driver = CommonFunctions.driver; 
		 homePage = CommonFunctions.homePage;
		 buildServerTab = CommonFunctions.buildServerTab;
		 packageToAddToManagedList = ReadTestData.readParameter("BS_UseCase_7", "packageToAddToManagedList");
		 packageToRemoveFromManagedList = ReadTestData.readParameter("BS_UseCase_7", "packageToRemoveFromManagedList");
		 BSUbuntu = ReadTestData.readParameter("BS_UseCase_6", "BSUbuntu");
		 BSCentOS = ReadTestData.readParameter("BS_UseCase_6", "BSCentOS");
		
	
		 CommonFunctions.goTo_ListInstallUsingManagedServicesSection();	
	  }
	 
	 //This is a system test case
	 @Test(priority=0)
	  public void BS_Add_Package_To_Managed_List_CentOS_Server_025() throws Exception{ 
		 
		 buildServerTab.enterPackageToSearchUsingManagedServices(packageToAddToManagedList);
		 
		 buildServerTab.SelectBuiltServer(BSCentOS);
		 
		 String version =  buildServerTab.selectPackageToAdd(packageToAddToManagedList);
		 
		 buildServerTab.clickAddToManagedListBtn();
		 
		 buildServerTab.verifyAndAcceptAddPopup(packageToAddToManagedList, version);
		 
		 buildServerTab.verifyPkgAddSuccessMessage();
	  }
	 
	//This is a system test case
	 @Test(priority=1)
	  public void BS_Add_Package_To_Managed_List_Ubuntu_Server_026() throws Exception{ 
		 
		 buildServerTab.enterPackageToSearchUsingManagedServices(packageToAddToManagedList);
		 
		 buildServerTab.SelectBuiltServer(BSUbuntu);
		 
		 String version =  buildServerTab.selectPackageToAdd(packageToAddToManagedList);
		 
		 buildServerTab.clickAddToManagedListBtn();
		 
		 buildServerTab.verifyAndAcceptAddPopup(packageToAddToManagedList, version);
		 
		 buildServerTab.verifyPkgAddSuccessMessage();
		  
	  }
	 
	//This is a system test case
	  @Test(priority=2)
	  public void BS_Remove_Package_from_Managed_List_CentOS_Server_027() throws Exception{ 
		  
		  buildServerTab.enterPackageToSearchUsingManagedServices(packageToRemoveFromManagedList);
			 
		  buildServerTab.SelectBuiltServer(BSCentOS);
			 
			 String version =  buildServerTab.selectPackageToRemove(packageToRemoveFromManagedList);
			 
			 buildServerTab.clickremoveFromManagedListBtn();
			 
			 buildServerTab.verifyAndAcceptAddPopup(packageToRemoveFromManagedList, version);
			 
			 buildServerTab.verifyPkgRemoveSuccessMessage();
	  }
	 
	//This is a system test case
	 @Test(priority=3)
	  public void BS_Remove_Package_from_Managed_List_Ubuntu_Server_028() throws Exception{ 
		  
		 buildServerTab.enterPackageToSearchUsingManagedServices(packageToRemoveFromManagedList);
		 
		 buildServerTab.SelectBuiltServer(BSUbuntu);
		 
		 String version =  buildServerTab.selectPackageToRemove(packageToRemoveFromManagedList);
		 
		 buildServerTab.clickremoveFromManagedListBtn();
		 
		 buildServerTab.verifyAndAcceptAddPopup(packageToRemoveFromManagedList, version);
		 
		 buildServerTab.verifyPkgRemoveSuccessMessage();
	  }
	 }
