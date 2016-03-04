package com.autoport.testcases;

import java.text.ParseException;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.pageobjects.SearchTab;
import com.autoport.utilities.CommonFunctions;


public class SCH_Use_Case_9 {

    WebDriver driver;

    HomePage homePage;
    SearchTab searchTab;
    ReportsTab reportsTab;

    @BeforeTest
    public void beforeTest() throws Exception {

        // CommonFunctions.launchBrowser();
        driver = CommonFunctions.driver;
        homePage = CommonFunctions.homePage;
        searchTab = CommonFunctions.searchTab;
        reportsTab = CommonFunctions.reportsTab;
    }

    @Test(priority = 0)
    public void SCH_Use_current_version_repository_details_common_projects_044() throws InterruptedException {

        // searchTab.clickOnMostCommonlyUsedProjectsBtn();

        searchTab.clickOnCommonlyUsedProjectSearch();

        searchTab.clickOnRepositoryDetailsBtnForCommonProjects();

        searchTab.verifyUseCurrentVersionForCommonProject();
    }

    @Test(priority = 1)
    public void SCH_Select_build_servers_repository_details_common_projects_045() throws InterruptedException {

        searchTab.verifySelectBuildServerForCommonProject();

    }

    //This is a system test case
    @Test(priority = 2)
    public void SCH_Build_Test_repository_common_projects_046() throws InterruptedException, ParseException {

        searchTab.clickOnBuildAndTestBtnForCommonProject();

        searchTab.clickOnAlertCloseBtn();

        homePage.openReportsTab();

        reportsTab.clickOnManageCompareProjectResultsBtn();

        reportsTab.enterProjectNameForSearch(searchTab.getRepositoryNameForCommonProject());// bootstrap

        reportsTab.clickOnListLocalBtn();

        reportsTab.clickOnDateCompletedHeader();

        reportsTab.verifyJenkinsJobCompletion(searchTab.getBuildClickTime(), searchTab.getBuildServersCount());

        homePage.clickSearchTab();
    }

    @Test(priority = 3)
    public void SCH_Build_Steps_repository_common_project_047() {
        searchTab.verifyBuildStepsForCommonProject();
    }

    
}
