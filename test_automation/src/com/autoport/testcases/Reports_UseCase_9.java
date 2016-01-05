package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.utilities.CommonFunctions;

public class Reports_UseCase_9 {
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
	 public void Reports_Test_History_View_Build_Logs_033() throws Exception{		  
		 
		  reportsTab.enterProjectResultToSearch("bson"); 
		  
		  reportsTab.clickListLocalProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("bson");	
		  
		  reportsTab.selectCheckboxForPackage("bson");
		  
		  reportsTab.verifyButtonsAreEnabled();
		  
		  reportsTab.clickTestHistoryButton();
		  
		  reportsTab.clickViewBuildLogBtn();
		  
		  reportsTab.closeLogTableForProject();
		  
		  reportsTab.clearSearchedProjectResult();
	 }
	 
	 @Test(priority=1)
	 public void Reports_Test_History_View_Test_Logs_034() throws Exception{		  
		 
		  reportsTab.enterProjectResultToSearch("bson"); 
		  
		  reportsTab.clickListLocalProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("bson");	
		  
		  reportsTab.selectCheckboxForPackage("bson");
		  
		  reportsTab.verifyButtonsAreEnabled();
		  
		  reportsTab.clickTestHistoryButton();
		  
		  reportsTab.clickViewTestLogBtn();
		  
		  reportsTab.closeLogTableForProject();
		  
		  reportsTab.clearSearchedProjectResult();
	 }
	 
	 @Test(priority=2)
	 public void Reports_Test_Detail_View_Build_Logs_035() throws Exception{		  
		 
		  reportsTab.enterProjectResultToSearch("bson"); 
		  
		  reportsTab.clickListLocalProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("bson");	
		  
		  reportsTab.selectCheckboxForPackage("bson");
		  
		  reportsTab.verifyButtonsAreEnabled();
		  
		  reportsTab.clickTestDetailButton();
		  
		  reportsTab.clickViewBuildLogBtn();
		  
		  reportsTab.closeLogTableForProject();
		  
		  reportsTab.clearSearchedProjectResult();
	 }
	 
	 @Test(priority=3)
	 public void Reports_Test_Detail_View_Test_Logs_036() throws Exception{		  
		 
		  reportsTab.enterProjectResultToSearch("bson"); 
		  
		  reportsTab.clickListLocalProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("bson");	
		  
		  reportsTab.selectCheckboxForPackage("bson");
		  
		  reportsTab.verifyButtonsAreEnabled();
		  
		  reportsTab.clickTestDetailButton();
		  
		  reportsTab.clickViewTestLogBtn();
		  
		  reportsTab.closeLogTableForProject();
		  
		  reportsTab.clearSearchedProjectResult();
	 }
	 
	 @Test(priority=4)
	 public void Reports_Test_Compare_View_Build_Logs_037() throws Exception{		  
		 
		  reportsTab.enterProjectResultToSearch("bson"); 
		  
		  reportsTab.clickListLocalProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("bson");	
		  
		  reportsTab.sortResultsByDateCompletedDescending();
		  
		  reportsTab.selectProjectResultsToCompare("bson");
		  
		  reportsTab.verifyCompareButtonsAreEnabledForProjectResults();		  
		  
		  reportsTab.clickTestCompareForProjectresults();
		  
		  reportsTab.clickViewBuildLogBtn();
		  
		  reportsTab.closeLogTableForProject();
		  
		  reportsTab.clearSearchedProjectResult();
	 }	 
	 
	 @Test(priority=5)
	 public void Reports_Test_Compare_View_Test_Logs_038() throws Exception{		  
		 
		  reportsTab.enterProjectResultToSearch("bson"); 
		  
		  reportsTab.clickListLocalProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("bson");	
		  
		  reportsTab.sortResultsByDateCompletedDescending();
		  
		  reportsTab.selectProjectResultsToCompare("bson");
		  
		  reportsTab.verifyCompareButtonsAreEnabledForProjectResults();		  
		  
		  reportsTab.clickTestCompareForProjectresults();
		  
		  reportsTab.clickViewTestLogBtn();
		  
		  reportsTab.closeLogTableForProject();		  
		  
		  reportsTab.clearSearchedProjectResult();
	 }	 
}
