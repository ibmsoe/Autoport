package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.utilities.CommonFunctions;

public class Reports_UseCase_7 {
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
		 
		 reportsTab.clickManageCompareBatchJobsResultsButton();
	  }
	 
	 @Test(priority=0)
	 public void Reports_Archive_Local_Batch_Job_Result_024() throws Exception{			 
		 
		  reportsTab.enterBatchJobResultToSearch("bootstrap-25");
		  
		  reportsTab.clickListLocalBatchJobResultsButton();
		  
		  reportsTab.verifySearchResultsforBatchJob("bootstrap-25");
		  
		  reportsTab.selectCheckboxForBatchJob("bootstrap-25");
		  
		  reportsTab.verifyButtonsAreEnabledToManageBatchJobs();
		  
		  reportsTab.clickArchiveBatchJobsResultsBtn();
		  
		  reportsTab.verifyBatchJobArchivedSuccessfullyMsg();
		  
		  reportsTab.clearSearchedBatchJobResult();
	 }	 
	 
	 @Test(priority=1)
	 public void Reports_Remove_Local_Batch_Job_Result_025() throws Exception{		  
		 
		  reportsTab.enterBatchJobResultToSearch("bootstrap-25");
		  
		  reportsTab.clickListLocalBatchJobResultsButton();
		  
		  reportsTab.verifySearchResultsforBatchJob("bootstrap-25");
		  
		  reportsTab.selectCheckboxForBatchJob("bootstrap-25");
		  
		  reportsTab.verifyButtonsAreEnabledToManageBatchJobs();
		  
		  reportsTab.clickRemoveBatchJobsResultsBtn();
		  
		  reportsTab.verifyBatchJobDeletedSuccessfullyMsg();
		  
		  reportsTab.clearSearchedBatchJobResult();
	 }	 
	 
	 @Test(priority=2)
	 public void Reports_Remove_Archived_Batch_Job_Result_026() throws Exception{		  
		 
		 reportsTab.enterBatchJobResultToSearch("bootstrap-25");
		  
		  reportsTab.clickListArchivedBatchJobsResultsButton();
		  
		  reportsTab.verifySearchResultsforBatchJob("bootstrap-25");
		  
		  reportsTab.selectCheckboxForBatchJob("bootstrap-25");
		  
		  reportsTab.verifyButtonsAreEnabledToManageBatchJobs();
		  
		  reportsTab.clickRemoveBatchJobsResultsBtn();
		  
		  reportsTab.verifyBatchJobDeletedSuccessfullyMsg();
		  
		  reportsTab.clearSearchedBatchJobResult();
	 }	 
}
