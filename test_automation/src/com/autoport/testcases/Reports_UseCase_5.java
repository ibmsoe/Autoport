package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.utilities.CommonFunctions;

public class Reports_UseCase_5 {
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
		 
		 reportsTab.clickManageCompareBatchJobsResultsButton();
	  }
	 
	 @Test(priority=0)
	 public void Reports_List_Local_Batch_Jobs_Results_017() throws Exception{		  
		  
		  reportsTab.clickListLocalBatchJobResultsButton();
		  
		  reportsTab.verifyOnlyLocalBatchJobResultsDisplayed();
		  
		  reportsTab.enterBatchJobResultToSearch("sunilBatchJobs");
		  
		  reportsTab.clickListLocalBatchJobResultsButton();
		  
		  reportsTab.verifySearchResultsforBatchJob("sunilBatchJobs");		  
		  
		  reportsTab.verifyOnlyLocalBatchJobResultsDisplayed();	
		  
		  reportsTab.clearSearchedBatchJobResult();
		  
	 }
	 
	 @Test(priority=1)
	 public void Reports_List_Archived_Batch_Jobs_Results_018() throws Exception{		  
		  
		  reportsTab.clickListArchivedBatchJobsResultsButton();
		  
		  reportsTab.verifyOnlyArchivedBatchJobResultsDisplayed();
		  
		  reportsTab.enterBatchJobResultToSearch("bootstrap-05");
		  
		  reportsTab.clickListArchivedBatchJobsResultsButton();
		  
		  reportsTab.verifySearchResultsforBatchJob("bootstrap-05");		  
		  
		  reportsTab.verifyOnlyArchivedBatchJobResultsDisplayed();	
		  
		  reportsTab.clearSearchedBatchJobResult();
		  
	 }
	 @Test(priority=2)
	 public void Reports_List_All_Batch_Jobs_Results_019() throws Exception{		  
		  
		  reportsTab.clickListAllBatchJobsResultsButton();
		  
		  reportsTab.verifyAllBatchJObResultsDisplayed();
		  
		  reportsTab.enterBatchJobResultToSearch("bootstrap-05");
		  
		  reportsTab.clickListAllBatchJobsResultsButton();
		  
		  reportsTab.verifySearchResultsforBatchJob("bootstrap-05");		  
		  
		  reportsTab.verifyAllBatchJObResultsDisplayed();	
		  
		  reportsTab.clearSearchedBatchJobResult();
		  
	 }
}
