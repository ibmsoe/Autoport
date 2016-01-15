package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class Reports_UseCase_6 {
	WebDriver driver;
	FluentWait<WebDriver> fluentWait;
	CommonFunctions functions;
	HomePage homePage;
	ReportsTab reportsTab;	
	String localBatchJobResult;
	String archivedBatchJobResult;
	 
	 @BeforeTest
	  public void beforeTest() throws Exception {
		 
		 //CommonFunctions.launchBrowser(); 
		 driver = CommonFunctions.driver; 
		 homePage = CommonFunctions.homePage;
		 
		 homePage = CommonFunctions.homePage;
		 reportsTab = CommonFunctions.reportsTab;	
		 
		 localBatchJobResult = ReadTestData.readParameter("Reports_UseCase_6", "localBatchJobResultForWhichBuildIsSuccess");
		 archivedBatchJobResult = ReadTestData.readParameter("Reports_UseCase_6", "archivedBatchJobResultForWhichBuildIsSuccess");
		 		 
		 homePage.openReportsTab();
		 
		 reportsTab.clickManageCompareBatchJobsResultsButton();
	  }
	 
	 @Test(priority=0)
	 public void Reports_View_Test_History_For_Local_Batch_Jobs_Result_020() throws Exception{	
		 
		 reportsTab.enterBatchJobResultToSearch(localBatchJobResult);
		  
		  reportsTab.clickListLocalBatchJobResultsButton();
		  
		  reportsTab.verifySearchResultsforBatchJob(localBatchJobResult);
		  
		  reportsTab.selectCheckboxForBatchJob(localBatchJobResult);
		  
		  reportsTab.verifyButtonsAreEnabledToManageBatchJobs();
		  
		  reportsTab.clickTestHistoryButtonForBatchJobs();
		  
		  reportsTab.clickBackToListButtonForBatchJobs();
		  
		  reportsTab.clearSearchedBatchJobResult();
	 }
	 
	 @Test(priority=1)
	 public void Reports_View_Test_Detail_For_Local_Batch_Job_Result_021() throws Exception{	
		 
		 reportsTab.enterBatchJobResultToSearch(localBatchJobResult);
		  
		  reportsTab.clickListLocalBatchJobResultsButton();
		  
		  reportsTab.verifySearchResultsforBatchJob(localBatchJobResult);
		  
		  reportsTab.selectCheckboxForBatchJob(localBatchJobResult);
		  
		  reportsTab.verifyButtonsAreEnabledToManageBatchJobs();
		  
		  reportsTab.clickTestDetailButtonForBatchJobs();
		  
		  reportsTab.clickBackToListButtonForBatchJobs();
		  
		  reportsTab.clearSearchedBatchJobResult();
	 }
	 
	 @Test(priority=2)
	 public void Reports_View_Test_History_For_Archived_Batch_Jobs_Result_022() throws Exception{	
		 
		 reportsTab.enterBatchJobResultToSearch(archivedBatchJobResult);
		  
		  reportsTab.clickListArchivedBatchJobsResultsButton();
		  
		  reportsTab.verifySearchResultsforBatchJob(archivedBatchJobResult);
		  
		  reportsTab.selectCheckboxForBatchJob(archivedBatchJobResult);
		  
		  reportsTab.verifyButtonsAreEnabledToManageBatchJobs();
		  
		  reportsTab.clickTestHistoryButtonForBatchJobs();
		  
		  reportsTab.clickBackToListButtonForBatchJobs();
		  
		  reportsTab.clearSearchedBatchJobResult();
	 }
	 
	 @Test(priority=3)
	 public void Reports_View_Test_Detail_For_Archived_Batch_Jobs_Result_023() throws Exception{	
		 
		 reportsTab.enterBatchJobResultToSearch(archivedBatchJobResult);
		  
		  reportsTab.clickListArchivedBatchJobsResultsButton();
		  
		  reportsTab.verifySearchResultsforBatchJob(archivedBatchJobResult);
		  
		  reportsTab.selectCheckboxForBatchJob(archivedBatchJobResult);
		  
		  reportsTab.verifyButtonsAreEnabledToManageBatchJobs();
		  
		  reportsTab.clickTestDetailButtonForBatchJobs();
		  
		  reportsTab.clickBackToListButtonForBatchJobs();
		  
		  reportsTab.clearSearchedBatchJobResult();
	 }

}
