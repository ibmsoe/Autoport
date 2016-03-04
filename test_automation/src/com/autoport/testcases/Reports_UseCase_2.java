package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class Reports_UseCase_2 {
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

         localProjectResult = ReadTestData.readParameter("Reports_UseCase_2", "localProjectResultForWhichBuildIsSuccess");
         archivedProjectResult = ReadTestData.readParameter("Reports_UseCase_2", "archivedProjectResultForWhichBuildIsSuccess");


         homePage.openReportsTab();

         reportsTab.clickManageCompareProjectResultsButton();
      }

     //This is a system test case
     @Test(priority=0)
     public void Reports_View_Test_History_For_Local_Project_Result_004() throws Exception{

          reportsTab.enterProjectResultToSearch(localProjectResult);

          reportsTab.clickListLocalProjectResultsButton();

          reportsTab.verifySearchResultsforProject(localProjectResult);

          reportsTab.selectCheckboxForPackage(localProjectResult);

          reportsTab.verifyButtonsAreEnabled();

          reportsTab.clickTestHistoryButton();

          reportsTab.clickBackToListButton();

          reportsTab.clearSearchedProjectResult();
     }

     //This is a system test case
     @Test(priority=1)
     public void Reports_View_Test_Detail_For_Local_Project_Result_005() throws Exception{

          reportsTab.enterProjectResultToSearch(localProjectResult);

          reportsTab.clickListLocalProjectResultsButton();

          reportsTab.verifySearchResultsforProject(localProjectResult);

          reportsTab.selectCheckboxForPackage(localProjectResult);

          reportsTab.verifyButtonsAreEnabled();

          reportsTab.clickTestDetailButton();

          reportsTab.clickBackToListButton();

          reportsTab.clearSearchedProjectResult();
     }

    //This is a system test case
     @Test(priority=2)
     public void Reports_View_Test_History_For_Archived_Project_Result_006() throws Exception{

          reportsTab.enterProjectResultToSearch(archivedProjectResult);

          reportsTab.clickListArchivedProjectResultsButton();

          reportsTab.verifySearchResultsforProject(archivedProjectResult);

          reportsTab.selectCheckboxForPackage(archivedProjectResult);

          reportsTab.verifyButtonsAreEnabled();

          reportsTab.clickTestHistoryButton();

          reportsTab.clickBackToListButton();

          reportsTab.clearSearchedProjectResult();
     }

    //This is a system test case
     @Test(priority=3)
     public void Reports_View_Test_Detail_For_Archived_Project_Result_007() throws Exception{

          reportsTab.enterProjectResultToSearch(archivedProjectResult);

          reportsTab.clickListArchivedProjectResultsButton();

          reportsTab.verifySearchResultsforProject(archivedProjectResult);

          reportsTab.selectCheckboxForPackage(archivedProjectResult);

          reportsTab.verifyButtonsAreEnabled();

          reportsTab.clickTestDetailButton();

          reportsTab.clickBackToListButton();

          reportsTab.clearSearchedProjectResult();
     }
}
