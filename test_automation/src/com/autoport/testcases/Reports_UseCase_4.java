package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.utilities.CommonFunctions;

public class Reports_UseCase_4 {
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
	 public void Reports_Test_Compare_Local_Project_Results_011() throws Exception{		  
		 
		  reportsTab.enterProjectResultToSearch("ant"); 
		  
		  reportsTab.clickListLocalProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("ant");	
		  
		  reportsTab.sortResultsByDateCompletedDescending();
		  
		  reportsTab.selectProjectResultsToCompare("ant");
		  
		  reportsTab.verifyCompareButtonsAreEnabledForProjectResults();		  
		  
		  reportsTab.clickTestCompareForProjectresults();
		  
		  reportsTab.clickBackToListButton();
		  
		  reportsTab.clearSearchedProjectResult();
	 }	 
	 
	 @Test(priority=1)
	 public void Reports_Build_Log_Compare_Local_Project_Results_012() throws Exception{		  
		 
		  reportsTab.enterProjectResultToSearch("ant"); 
		  
		  reportsTab.clickListLocalProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("ant");	
		  
		  reportsTab.sortResultsByDateCompletedDescending();
		  
		  reportsTab.selectProjectResultsToCompare("ant");
		  
		  reportsTab.verifyCompareButtonsAreEnabledForProjectResults();	
		  
		  reportsTab.clickBuildLogCompareForProjectresults();
		  
		  reportsTab.verifyAndCloseLogCompareForProjectresults();
		  
		  reportsTab.clearSearchedProjectResult();
	 }
	 
	 @Test(priority=2)
	 public void Reports_Test_Log_compare_Local_Project_Results_013() throws Exception{		  
		 
		  reportsTab.enterProjectResultToSearch("ant"); 
		  
		  reportsTab.clickListLocalProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("ant");	
		  
		  reportsTab.sortResultsByDateCompletedDescending();
		  
		  reportsTab.selectProjectResultsToCompare("ant");
		  
		  reportsTab.verifyCompareButtonsAreEnabledForProjectResults();	
		  
		  reportsTab.clickTestLogCompareForProjectresults();
		  
		  reportsTab.verifyAndCloseLogCompareForProjectresults();
		  
		  reportsTab.clearSearchedProjectResult();
	 }
	 
	 @Test(priority=3)
	 public void Reports_Test_Compare_Archived_Project_Results_014() throws Exception{		  
		 
		 reportsTab.enterProjectResultToSearch("ant"); 
		  
		  reportsTab.clickListArchivedProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("ant");	
		  
		  reportsTab.sortResultsByDateCompletedDescending();
		  
		  reportsTab.selectProjectResultsToCompare("ant");
		  
		  reportsTab.verifyCompareButtonsAreEnabledForProjectResults();		  
		  
		  reportsTab.clickTestCompareForProjectresults();
		  
		  reportsTab.clickBackToListButton();
		  
		  reportsTab.clearSearchedProjectResult();
	 }
	
	 @Test(priority=4)
	 public void Reports_Build_Log_Compare_Archived_Project_Results_015() throws Exception{		  
		 
		 reportsTab.enterProjectResultToSearch("ant"); 
		  
		  reportsTab.clickListArchivedProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("ant");	
		  
		  reportsTab.sortResultsByDateCompletedDescending();
		  
		  reportsTab.selectProjectResultsToCompare("ant");
		  
		  reportsTab.verifyCompareButtonsAreEnabledForProjectResults();	
		  
		  reportsTab.clickBuildLogCompareForProjectresults();
		  
		  reportsTab.verifyAndCloseLogCompareForProjectresults();
		  
		  reportsTab.clearSearchedProjectResult();
	 }
	 
	 @Test(priority=5)
	 public void Reports_Test_Log_compare_Archived_Project_Results_016() throws Exception{		  
		 
		 reportsTab.enterProjectResultToSearch("ant"); 
		  
		  reportsTab.clickListArchivedProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject("ant");	
		  
		  reportsTab.sortResultsByDateCompletedDescending();
		  
		  reportsTab.selectProjectResultsToCompare("ant");
		  
		  reportsTab.verifyCompareButtonsAreEnabledForProjectResults();	
		  
		  reportsTab.clickTestLogCompareForProjectresults();
		  
		  reportsTab.verifyAndCloseLogCompareForProjectresults();
		  
		  reportsTab.clearSearchedProjectResult();
	 }

}
