package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class Reports_UseCase_7 {
    WebDriver driver;
    FluentWait<WebDriver> fluentWait;
    CommonFunctions functions;
    HomePage homePage;
    ReportsTab reportsTab;
    String localBatchJobResultToArchive;
    String localBatchJobResultToRemove;
    String archivedBatchJobResultToRemove;

     @BeforeTest
      public void beforeTest() throws Exception {

         //CommonFunctions.launchBrowser();
         driver = CommonFunctions.driver;
         homePage = CommonFunctions.homePage;

         homePage = CommonFunctions.homePage;
         reportsTab = CommonFunctions.reportsTab;

         localBatchJobResultToArchive = ReadTestData.readParameter("Reports_UseCase_7", "localBatchJobResultToArchive");
         localBatchJobResultToRemove = ReadTestData.readParameter("Reports_UseCase_7", "localBatchJobResultToRemove");
         archivedBatchJobResultToRemove = ReadTestData.readParameter("Reports_UseCase_7", "archivedBatchJobResultToRemove");


         homePage.openReportsTab();

         reportsTab.clickManageCompareBatchJobsResultsButton();
      }

     @Test(priority=0)
     public void Reports_Archive_Local_Batch_Job_Result_024() throws Exception{

          reportsTab.enterBatchJobResultToSearch(localBatchJobResultToArchive);

          reportsTab.clickListLocalBatchJobResultsButton();

          reportsTab.verifySearchResultsforBatchJob(localBatchJobResultToArchive);

          reportsTab.selectCheckboxForBatchJob(localBatchJobResultToArchive);

          reportsTab.verifyButtonsAreEnabledToManageBatchJobs();

          reportsTab.clickArchiveBatchJobsResultsBtn();

          reportsTab.verifyArchivedSuccessfullyMsg();

          reportsTab.clearSearchedBatchJobResult();
     }

     @Test(priority=1)
     public void Reports_Remove_Local_Batch_Job_Result_025() throws Exception{

          reportsTab.enterBatchJobResultToSearch(localBatchJobResultToRemove);

          reportsTab.clickListLocalBatchJobResultsButton();

          reportsTab.verifySearchResultsforBatchJob(localBatchJobResultToRemove);

          reportsTab.selectCheckboxForBatchJob(localBatchJobResultToRemove);

          reportsTab.verifyButtonsAreEnabledToManageBatchJobs();

          reportsTab.clickRemoveBatchJobsResultsBtn();

          reportsTab.verifyBatchJobDeletedSuccessfullyMsg();

          reportsTab.clearSearchedBatchJobResult();
     }

     @Test(priority=2)
     public void Reports_Remove_Archived_Batch_Job_Result_026() throws Exception{

         reportsTab.enterBatchJobResultToSearch(archivedBatchJobResultToRemove);

          reportsTab.clickListArchivedBatchJobsResultsButton();

          reportsTab.verifySearchResultsforBatchJob(archivedBatchJobResultToRemove);

          reportsTab.selectCheckboxForBatchJob(archivedBatchJobResultToRemove);

          reportsTab.verifyButtonsAreEnabledToManageBatchJobs();

          reportsTab.clickRemoveBatchJobsResultsBtn();

          reportsTab.verifyBatchJobDeletedSuccessfullyMsg();

          reportsTab.clearSearchedBatchJobResult();
     }
}
