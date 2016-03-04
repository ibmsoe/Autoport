package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.testng.annotations.AfterTest;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class Reports_UseCase_1 {
    WebDriver driver;
    HomePage homePage;
    ReportsTab reportsTab;
    String localProjectResult;
    String archivedProjectResult;

     @BeforeTest
      public void beforeTest() throws Exception {

//         CommonFunctions.launchBrowser();
         driver = CommonFunctions.driver;
         homePage = CommonFunctions.homePage;

         homePage = CommonFunctions.homePage;
         reportsTab = CommonFunctions.reportsTab;
         localProjectResult = ReadTestData.readParameter("Reports_UseCase_1", "localProjectResultForWhichBuildIsSuccess");
         archivedProjectResult = ReadTestData.readParameter("Reports_UseCase_1", "archivedProjectResultForWhichBuildIsSuccess");

         homePage.openReportsTab();

         reportsTab.clickManageCompareProjectResultsButton();
      }

     @Test(priority=0)
     public void Reports_List_Local_Projects_Results_001() throws Exception{

          reportsTab.clickListLocalProjectResultsButton();

          reportsTab.verifyOnlyLocalProjectResultsDisplayed();

          reportsTab.enterProjectResultToSearch(localProjectResult);

          reportsTab.clickListLocalProjectResultsButton();

          reportsTab.verifySearchResultsforProject(localProjectResult);

          reportsTab.verifyOnlyLocalProjectResultsDisplayed();

          reportsTab.clearSearchedProjectResult();

     }

     @Test(priority=1)
     public void Reports_List_Archived_Projects_Results_002() throws Exception{

          reportsTab.clickListArchivedProjectResultsButton();

          reportsTab.verifyOnlyArchivedProjectResultsDisplayed();

          reportsTab.enterProjectResultToSearch(archivedProjectResult);

          reportsTab.clickListArchivedProjectResultsButton();

          reportsTab.verifySearchResultsforProject(archivedProjectResult);

          reportsTab.verifyOnlyArchivedProjectResultsDisplayed();

          reportsTab.clearSearchedProjectResult();
     }

     @Test(priority=2)
     public void Reports_List_All_Project_Results_003() throws Exception{

          reportsTab.clickListAllProjectResultsButton();

          reportsTab.verifyAllProjectResultsDisplayed();

          reportsTab.enterProjectResultToSearch(localProjectResult);

          reportsTab.clickListAllProjectResultsButton();

          reportsTab.verifySearchResultsforProject(localProjectResult);

          reportsTab.verifyAllProjectResultsDisplayed();

          reportsTab.clearSearchedProjectResult();
     }
}
