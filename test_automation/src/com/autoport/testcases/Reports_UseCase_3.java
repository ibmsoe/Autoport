package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.utilities.CommonFunctions;

public class Reports_UseCase_3 {
	WebDriver driver;
	FluentWait<WebDriver> fluentWait;
	CommonFunctions functions;
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
	 public void Reports_Archive_Local_Project_Result_008() throws Exception{			 
		 
		  reportsTab.enterProjectResultToSearch("bson"); 
		  
		  reportsTab.clickListLocalProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("bson");	
		  
		  reportsTab.selectCheckboxForPackage("bson");
		  
		  reportsTab.verifyButtonsAreEnabled();
		  
		  reportsTab.clickArchiveProjectResultsBtn();
		  
		  reportsTab.clearSearchedProjectResult();
	 }	 
	 @Test(priority=1)
	 public void Reports_Remove_Local_Project_Resul_009() throws Exception{		  
		 
		  reportsTab.enterProjectResultToSearch("bson"); 
		  
		  reportsTab.clickListLocalProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("bson");	
		  
		  reportsTab.selectCheckboxForPackage("bson");
		  
		  reportsTab.verifyButtonsAreEnabled();
		  
		  reportsTab.clickRemoveProjectResultsBtn();
		  
		  reportsTab.verifyDeletedSuccessfullyMsg();
		  
		  reportsTab.clearSearchedProjectResult();
	 }	 
	 @Test(priority=2)
	 public void Reports_Remove_Archived_Project_Result_010() throws Exception{		  
		 
		  reportsTab.enterProjectResultToSearch("bson"); 
		  
		  reportsTab.clickListArchivedProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("bson");	
		  
		  reportsTab.selectCheckboxForPackage("bson");
		  
		  reportsTab.verifyButtonsAreEnabled();
		  
		  reportsTab.clickRemoveProjectResultsBtn();
		  
		  reportsTab.verifyDeletedSuccessfullyMsg();
		  
		  reportsTab.clearSearchedProjectResult();
	 }	 
}
