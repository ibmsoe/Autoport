package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.utilities.CommonFunctions;

public class Reports_UseCase_2 {
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
	 public void Reports_View_Test_History_For_Local_Project_Result_004() throws Exception{		  
		 
		  reportsTab.enterProjectResultToSearch("bson"); 
		  
		  reportsTab.clickListLocalProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("bson");	
		  
		  reportsTab.selectCheckboxForPackage("bson");
		  
		  reportsTab.verifyButtonsAreEnabled();
		  
		  reportsTab.clickTestHistoryButton();
		  
		  reportsTab.clickBackToListButton();
		  
		  reportsTab.clearSearchedProjectResult();
	 }
	 
	 @Test(priority=1)
	 public void Reports_View_Test_Detail_For_Local_Project_Result_005() throws Exception{		  
		  
		  reportsTab.enterProjectResultToSearch("bson"); 
		  
		  reportsTab.clickListLocalProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("bson");	
		  
		  reportsTab.selectCheckboxForPackage("bson");
		  
		  reportsTab.verifyButtonsAreEnabled();
		  
		  reportsTab.clickTestDetailButton();
		  
		  reportsTab.clickBackToListButton();
		  
		  reportsTab.clearSearchedProjectResult();
	 }
	 
	 @Test(priority=2)
	 public void Reports_View_Test_History_For_Archived_Project_Result_006() throws Exception{		  
		 
		  reportsTab.enterProjectResultToSearch("bson"); 
		  
		  reportsTab.clickListArchivedProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("bson");	
		  
		  reportsTab.selectCheckboxForPackage("bson");
		  
		  reportsTab.verifyButtonsAreEnabled();
		  
		  reportsTab.clickTestHistoryButton();
		  
		  reportsTab.clickBackToListButton();
		  
		  reportsTab.clearSearchedProjectResult();
	 }
	 
	 @Test(priority=3)
	 public void Reports_View_Test_Detail_For_Archived_Project_Result_007() throws Exception{		  
		  
		  reportsTab.enterProjectResultToSearch("bson"); 
		  
		  reportsTab.clickListArchivedProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("bson");	
		  
		  reportsTab.selectCheckboxForPackage("bson");
		  
		  reportsTab.verifyButtonsAreEnabled();
		  
		  reportsTab.clickTestDetailButton();
		  
		  reportsTab.clickBackToListButton();
		  
		  reportsTab.clearSearchedProjectResult();
	 }
}
