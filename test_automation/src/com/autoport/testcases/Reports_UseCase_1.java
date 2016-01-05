package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.testng.annotations.AfterTest;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.utilities.CommonFunctions;

public class Reports_UseCase_1 {
	WebDriver driver;
	HomePage homePage;
	ReportsTab reportsTab;	
	 
	 @BeforeTest
	  public void beforeTest() throws Exception {
		 
		 //CommonFunctions.launchBrowser(); 
		 driver = CommonFunctions.driver; 
		 homePage = CommonFunctions.homePage;
		 
		 homePage = CommonFunctions.homePage;
		 reportsTab = CommonFunctions.reportsTab;		 
		 
		 homePage.openReportsTab();
		 
		 reportsTab.clickManageCompareProjectResultsButton();
	  }
	 
	 @Test(priority=0)
	 public void Reports_List_Local_Projects_Results_001() throws Exception{		  
		  
		  reportsTab.clickListLocalProjectResultsButton();
		  
		  reportsTab.verifyOnlyLocalProjectResultsDisplayed();
		  
		  reportsTab.enterProjectResultToSearch("bson");
		  
		  reportsTab.clickListLocalProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("bson");		  
		  
		  reportsTab.verifyOnlyLocalProjectResultsDisplayed();	
		  
		  reportsTab.clearSearchedProjectResult();
		  
	 }
	 
	 @Test(priority=1)
	 public void Reports_List_Archived_Projects_Results_002() throws Exception{		  
		  
		  reportsTab.clickListArchivedProjectResultsButton();
		  
		  reportsTab.verifyOnlyArchivedProjectResultsDisplayed();
		  
		  reportsTab.enterProjectResultToSearch("bson");
		  
		  reportsTab.clickListArchivedProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("bson");		  
		  
		  reportsTab.verifyOnlyArchivedProjectResultsDisplayed();		  
		  
		  reportsTab.clearSearchedProjectResult();
	 }
	 
	 @Test(priority=2)
	 public void Reports_List_All_Project_Results_003() throws Exception{		  
		  
		  reportsTab.clickListAllProjectResultsButton();
		  
		  reportsTab.verifyAllProjectResultsDisplayed();
		  
		  reportsTab.enterProjectResultToSearch("bson");
		  
		  reportsTab.clickListAllProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("bson");		  
		  
		  reportsTab.verifyAllProjectResultsDisplayed();  
		  
		  reportsTab.clearSearchedProjectResult();
	 } 	
}
