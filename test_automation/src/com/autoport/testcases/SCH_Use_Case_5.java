package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BatchJobsTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.SearchTab;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class SCH_Use_Case_5 {

    WebDriver driver;

    HomePage homePage;
    SearchTab searchTab;
    BatchJobsTab batchJobsTab;

    String listOfRepositories;

    // String savedBatchFileName;

    @BeforeTest
    public void beforeTest() throws Exception {

        //CommonFunctions.launchBrowser();
        driver = CommonFunctions.driver;

        homePage = CommonFunctions.homePage;
        searchTab = CommonFunctions.searchTab;
        batchJobsTab = CommonFunctions.batchJobsTab;

        listOfRepositories = ReadTestData.readParameter("searchTabData",
                "listOfRepositories");
        // savedBatchFileName = ReadTestData.readParameter("SCH_Use_Case_5",
        // "savedBatchFileName");

        searchTab.clickOnSingleProjectBtn();

    }

    @Test(priority = 0)
    public void SCH_Adding_repositories_batch_file_single_project_019() {

        searchTab.searchForRepository(listOfRepositories);

        searchTab.pressEnterKey();

        searchTab.verifyResultsSortByRelavance();

        searchTab.clickOnAddToBatchBtn();

        searchTab.verifyBatchFileSaveExportCloseUI();

        searchTab.verifyBatchFileRepositoryPanelUI();
    }

    @Test(priority = 1)
    public void SCH_Save_batch_file_single_project_020()
            throws InterruptedException {

        searchTab.clickOnBatchFileSaveBtn();

        homePage.clickBatchJobsTab();

        batchJobsTab.clickListSelectBtn();

        batchJobsTab.clickOnListLocalBtn();

        batchJobsTab.verifyLocallySavedBatchFile(searchTab
                .getRepositoryNameAddedToBatch() + "-1");// cassandra-1

    }

    @Test(priority = 2)
    public void SCH_Export_batch_file_single_project_021()
            throws InterruptedException {

        homePage.clickSearchTab();

        Thread.sleep(1000);

        searchTab.verifyResultsSortByPopularityStars();

        searchTab.clickOnAddToBatchBtn();

        searchTab.clickOnBatchFileExportBtn();

        Thread.sleep(2000);

        searchTab.confirmFileDownload(searchTab.getRepositoryNameAddedToBatch()
                + "-1");// cassandra-1

    }

    @Test(priority = 3)
    public void SCH_Clear_batch_file_single_project_022() {

        searchTab.verifyResultsSortByRelavance();

        searchTab.clickOnAddToBatchBtn();

        searchTab.clickOnBatchFileClearBtn();
    }

    @Test(priority = 4)
    public void SCH_Batch_File_Repository_UI_023() throws InterruptedException {

        searchTab.verifyResultsSortByPopularityStars();

        searchTab.clickOnAddToBatchBtn();

        searchTab.verifyBatchFileRepositoryPanelUI();

        searchTab.verifyBatchFileRepositoryDescription();

        searchTab.clickOnBatchFileClearBtn();

    }


}
