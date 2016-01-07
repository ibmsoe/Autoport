package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.CommonFunctions;

public class BS_UseCase_7 {
	
	WebDriver driver;
	HomePage homePage;
	BuildServersTab buildServerTab;	
	 
	 @BeforeTest
	  public void beforeTest() throws Exception {
		//CommonFunctions.launchBrowser(); 
		 driver = CommonFunctions.driver; 
		 homePage = CommonFunctions.homePage;
		 buildServerTab = CommonFunctions.buildServerTab;		
		 CommonFunctions.goTo_ListInstallUsingManagedServicesSection();	
	  }
	 
	 @Test(priority=0)
	  public void BS_Add_Package_To_Managed_List_RHEL_Server_025() throws Exception{ 
		 
		 buildServerTab.enterPackageToSearchUsingManagedServices("apache-ant");
		 
		 buildServerTab.clickListRhelBtn();
		 
		 String version =  buildServerTab.selectPackageToAddRemove("apache-ant");
		 
		 buildServerTab.clickAddToManagedListBtn();
		 
		 buildServerTab.verifyAndAcceptAddPopup("apache-ant", version);
		 
		 buildServerTab.verifyPkgAddSuccessMessage();
	  }
	 
	 @Test(priority=1)
	  public void BS_Add_Package_To_Managed_List_Ubuntu_Server_026() throws Exception{ 
		 
		 buildServerTab.enterPackageToSearchUsingManagedServices("apache-ant");
		 
		 buildServerTab.clickListUbuntuBtn();
		 
		 String version =  buildServerTab.selectPackageToAddRemove("apache-ant");
		 
		 buildServerTab.clickAddToManagedListBtn();
		 
		 buildServerTab.verifyAndAcceptAddPopup("apache-ant", version);
		 
		 buildServerTab.verifyPkgAddSuccessMessage();
		  
	  }
	 
	  @Test(priority=2)
	  public void BS_Remove_Package_from_Managed_List_RHEL_Server_027() throws Exception{ 
		  
		  buildServerTab.enterPackageToSearchUsingManagedServices("apache-ant");
			 
			 buildServerTab.clickListRhelBtn();
			 
			 String version =  buildServerTab.selectPackageToAddRemove("apache-ant");
			 
			 buildServerTab.clickremoveFromManagedListBtn();
			 
			 buildServerTab.verifyAndAcceptAddPopup("apache-ant", version);
			 
			 buildServerTab.verifyPkgRemoveSuccessMessage();
	  }
	 
	 @Test(priority=3)
	  public void BS_Remove_Package_from_Managed_List_Ubuntu_Server_028() throws Exception{ 
		  
		 buildServerTab.enterPackageToSearchUsingManagedServices("");
		 
		 buildServerTab.clickListUbuntuBtn();
		 
		 String version =  buildServerTab.selectPackageToAddRemove("apache-ant");
		 
		 buildServerTab.clickremoveFromManagedListBtn();
		 
		 buildServerTab.verifyAndAcceptAddPopup("apache-ant", version);
		 
		 buildServerTab.verifyPkgRemoveSuccessMessage();
	  }	 
	 
}
