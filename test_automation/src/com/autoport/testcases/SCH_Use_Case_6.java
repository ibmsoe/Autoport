package com.autoport.testcases;

import java.text.ParseException;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.pageobjects.SearchTab;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class SCH_Use_Case_6 {

    WebDriver driver;

    HomePage homePage;
    SearchTab searchTab;
    ReportsTab reportsTab;

    String buildAndTestRepositoryName;

    @BeforeTest
    public void beforeTest() throws Exception {

        // CommonFunctions.launchBrowser();
        driver = CommonFunctions.driver;

        homePage = CommonFunctions.homePage;
        searchTab = CommonFunctions.searchTab;
        reportsTab = CommonFunctions.reportsTab;

        buildAndTestRepositoryName = ReadTestData.readParameter(
                "searchTabData", "buildAndTestRepositoryName");

        searchTab.clickOnSingleProjectBtn();

    }

    @Test(priority = 0)
    public void SCH_Use_current_version_repository_details_single_project_024() {

        searchTab.searchForRepository(buildAndTestRepositoryName);

        searchTab.pressEnterKey();

        searchTab.waitingForResultPanel();

        searchTab.clickOnFirstRepositoryDetailsBtn();

        searchTab.verifyUseCurrentVersion();
    }

    @Test(priority = 1)
    public void SCH_Select_build_servers_repository_details_single_project_025()
            throws InterruptedException {

        searchTab.verifySelectBuildServer();
    }

    //This is a system test case
    @Test(priority = 2)
    public void SCH_Build_Test_repository_single_project_026()
            throws InterruptedException, ParseException {

        searchTab.clickOnBuildAndTestBtn();

        searchTab.clickOnAlertCloseBtn();

        homePage.openReportsTab();

        reportsTab.clickOnManageCompareProjectResultsBtn();

        reportsTab.enterProjectNameForSearch(searchTab.getRepositoryName());

        reportsTab.clickOnListLocalBtn();

        reportsTab.clickOnDateCompletedHeader();

        reportsTab.verifyJenkinsJobCompletion(searchTab.getBuildClickTime(),
                searchTab.getBuildServersCount());

        homePage.clickSearchTab();

    }

    @Test(priority = 3)
    public void SCH_Build_Steps_repository_single_project_027() {

        searchTab.verifyBuildSteps();
    }


}
