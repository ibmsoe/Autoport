package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class Reports_UseCase_9 {
    WebDriver driver;
    FluentWait<WebDriver> fluentWait;
    CommonFunctions functions;
    HomePage homePage;
    ReportsTab reportsTab;
    String localProjectResult;
    String archivedProjectResult;

     @BeforeTest
      public void beforeTest() throws Exception {

         //CommonFunctions.launchBrowser();
         driver = CommonFunctions.driver;
         homePage = CommonFunctions.homePage;

         homePage = CommonFunctions.homePage;
         reportsTab = CommonFunctions.reportsTab;

         localProjectResult = ReadTestData.readParameter("Reports_UseCase_9", "localProjectResultForWhichBuildIsSuccess");
         archivedProjectResult = ReadTestData.readParameter("Reports_UseCase_9", "archivedProjectResultForWhichBuildIsSuccess");


         homePage.openReportsTab();

         reportsTab.clickManageCompareProjectResultsButton();
      }

    //This is a system test case
     @Test(priority=0)
     public void Reports_Test_History_View_Build_Logs_033() throws Exception{

          reportsTab.enterProjectResultToSearch(localProjectResult);

          reportsTab.clickListLocalProjectResultsButton();

          reportsTab.verifySearchResultsforProject(localProjectResult);

          reportsTab.selectCheckboxForPackage(localProjectResult);

          reportsTab.verifyButtonsAreEnabled();

          reportsTab.clickTestHistoryButton();

          reportsTab.clickViewBuildLogBtn();

          reportsTab.closeLogTableForProject();

          reportsTab.clearSearchedProjectResult();
     }

    //This is a system test case
     @Test(priority=1)
     public void Reports_Test_History_View_Test_Logs_034() throws Exception{

          reportsTab.enterProjectResultToSearch(localProjectResult);

          reportsTab.clickListLocalProjectResultsButton();

          reportsTab.verifySearchResultsforProject(localProjectResult);

          reportsTab.selectCheckboxForPackage(localProjectResult);

          reportsTab.verifyButtonsAreEnabled();

          reportsTab.clickTestHistoryButton();

          reportsTab.clickViewTestLogBtn();

          reportsTab.closeLogTableForProject();

          reportsTab.clearSearchedProjectResult();
     }

    //This is a system test case
     @Test(priority=2)
     public void Reports_Test_Detail_View_Build_Logs_035() throws Exception{

          reportsTab.enterProjectResultToSearch(localProjectResult);

          reportsTab.clickListLocalProjectResultsButton();

          reportsTab.verifySearchResultsforProject(localProjectResult);

          reportsTab.selectCheckboxForPackage(localProjectResult);

          reportsTab.verifyButtonsAreEnabled();

          reportsTab.clickTestDetailButton();

          reportsTab.clickViewBuildLogBtn();

          reportsTab.closeLogTableForProject();

          reportsTab.clearSearchedProjectResult();
     }

    //This is a system test case
     @Test(priority=3)
     public void Reports_Test_Detail_View_Test_Logs_036() throws Exception{

          reportsTab.enterProjectResultToSearch(localProjectResult);

          reportsTab.clickListLocalProjectResultsButton();

          reportsTab.verifySearchResultsforProject(localProjectResult);

          reportsTab.selectCheckboxForPackage(localProjectResult);

          reportsTab.verifyButtonsAreEnabled();

          reportsTab.clickTestDetailButton();

          reportsTab.clickViewTestLogBtn();

          reportsTab.closeLogTableForProject();

          reportsTab.clearSearchedProjectResult();
     }

    //This is a system test case
     @Test(priority=4)
     public void Reports_Test_Compare_View_Build_Logs_037() throws Exception{

          reportsTab.enterProjectResultToSearch(localProjectResult);

          reportsTab.clickListLocalProjectResultsButton();

          reportsTab.verifySearchResultsforProject(localProjectResult);

          reportsTab.sortResultsByDateCompletedDescending();

          reportsTab.selectProjectResultsToCompare(localProjectResult);

          reportsTab.verifyCompareButtonsAreEnabledForProjectResults();

          reportsTab.clickTestCompareForProjectresults();

          reportsTab.clickViewBuildLogBtn();

          reportsTab.closeLogTableForProject();

          reportsTab.clearSearchedProjectResult();
     }

    //This is a system test case
     @Test(priority=5)
     public void Reports_Test_Compare_View_Test_Logs_038() throws Exception{

          reportsTab.enterProjectResultToSearch(localProjectResult);

          reportsTab.clickListLocalProjectResultsButton();

          reportsTab.verifySearchResultsforProject(localProjectResult);

          reportsTab.sortResultsByDateCompletedDescending();

          reportsTab.selectProjectResultsToCompare(localProjectResult);

          reportsTab.verifyCompareButtonsAreEnabledForProjectResults();

          reportsTab.clickTestCompareForProjectresults();

          reportsTab.clickViewTestLogBtn();

          reportsTab.closeLogTableForProject();

          reportsTab.clearSearchedProjectResult();
     }
}
