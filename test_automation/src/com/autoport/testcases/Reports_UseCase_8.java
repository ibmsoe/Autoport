package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class Reports_UseCase_8 {

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

             localBatchJobResult = ReadTestData.readParameter("Reports_UseCase_8", "localBatchJobResultForWhichBuildIsSuccess");
             archivedBatchJobResult = ReadTestData.readParameter("Reports_UseCase_8", "archivedBatchJobResultForWhichBuildIsSuccess");


             homePage.openReportsTab();

             reportsTab.clickManageCompareBatchJobsResultsButton();
      }


     //This is a system test case
     @Test(priority=0)
     public void Reports_Test_Compare_Local_BatchJobs_Results_027() throws Exception{

          reportsTab.enterBatchJobResultToSearch(localBatchJobResult);

          reportsTab.clickListLocalBatchJobResultsButton();

          reportsTab.verifySearchResultsforBatchJob(localBatchJobResult);

          reportsTab.sortBatchJobsResultsByDateCompletedDescending();

          reportsTab.selectBatchJobResultsToCompare(localBatchJobResult);

          reportsTab.verifyCompareButtonsAreEnabledForBatchJobsResults();

          reportsTab.clickTestCompareForBatchJobresults();

          reportsTab.clickBackToListButtonForBatchJobs();

          reportsTab.clearSearchedBatchJobResult();
     }

    //This is a system test case
     @Test(priority=1)
     public void Reports_Build_Log_Compare_Local_BatchJobs_Results_028() throws Exception{

         reportsTab.enterBatchJobResultToSearch(localBatchJobResult);

          reportsTab.clickListLocalBatchJobResultsButton();

          reportsTab.verifySearchResultsforBatchJob(localBatchJobResult);

          reportsTab.sortBatchJobsResultsByDateCompletedDescending();

          reportsTab.selectBatchJobResultsToCompare(localBatchJobResult);

          reportsTab.verifyCompareButtonsAreEnabledForBatchJobsResults();

          reportsTab.clickBuildLogCompareForBatchJobsresults();

          reportsTab.clickBackToComparisionBtnForBatchJobs();

          reportsTab.clearSearchedBatchJobResult();
     }

    //This is a system test case
     @Test(priority=2)
     public void Reports_Test_Log_compare_Local_BatchJobs_Results_029() throws Exception{

         reportsTab.enterBatchJobResultToSearch(localBatchJobResult);

          reportsTab.clickListLocalBatchJobResultsButton();

          reportsTab.verifySearchResultsforBatchJob(localBatchJobResult);

          reportsTab.sortBatchJobsResultsByDateCompletedDescending();

          reportsTab.selectBatchJobResultsToCompare(localBatchJobResult);

          reportsTab.verifyCompareButtonsAreEnabledForBatchJobsResults();

          reportsTab.clickTestLogCompareForBatchJobsresults();

          reportsTab.clickBackToComparisionBtnForBatchJobs();

          reportsTab.clearSearchedBatchJobResult();
     }

    //This is a system test case
     @Test(priority=3)
     public void Reports_Test_Compare_Archived_BatchJobs_Results_030() throws Exception{

         reportsTab.enterBatchJobResultToSearch(archivedBatchJobResult);

          reportsTab.clickListArchivedBatchJobsResultsButton();

          reportsTab.verifySearchResultsforBatchJob(archivedBatchJobResult);

          reportsTab.sortBatchJobsResultsByDateCompletedDescending();

          reportsTab.selectBatchJobResultsToCompare(archivedBatchJobResult);

          reportsTab.verifyCompareButtonsAreEnabledForBatchJobsResults();

          reportsTab.clickTestCompareForBatchJobresults();

          reportsTab.clickBackToListButtonForBatchJobs();

          reportsTab.clearSearchedBatchJobResult();
     }

    //This is a system test case
     @Test(priority=4)
     public void Reports_Build_Log_Compare_Archived_BatchJobs_Results_031() throws Exception{

         reportsTab.enterBatchJobResultToSearch(archivedBatchJobResult);

          reportsTab.clickListArchivedBatchJobsResultsButton();

          reportsTab.verifySearchResultsforBatchJob(archivedBatchJobResult);

          reportsTab.sortBatchJobsResultsByDateCompletedDescending();

          reportsTab.selectBatchJobResultsToCompare(archivedBatchJobResult);

          reportsTab.verifyCompareButtonsAreEnabledForBatchJobsResults();

          reportsTab.clickBuildLogCompareForBatchJobsresults();

          reportsTab.clickBackToComparisionBtnForBatchJobs();

          reportsTab.clearSearchedBatchJobResult();
     }

    //This is a system test case
     @Test(priority=5)
     public void Reports_Test_Log_compare_Archived_BatchJobs_Results_032() throws Exception{

         reportsTab.enterBatchJobResultToSearch(archivedBatchJobResult);

          reportsTab.clickListArchivedBatchJobsResultsButton();

          reportsTab.verifySearchResultsforBatchJob(archivedBatchJobResult);

          reportsTab.sortBatchJobsResultsByDateCompletedDescending();

          reportsTab.selectBatchJobResultsToCompare(archivedBatchJobResult);

          reportsTab.verifyCompareButtonsAreEnabledForBatchJobsResults();

          reportsTab.clickTestLogCompareForBatchJobsresults();

          reportsTab.clickBackToComparisionBtnForBatchJobs();

          reportsTab.clearSearchedBatchJobResult();
     }
}
