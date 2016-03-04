package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BatchJobsTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.SearchTab;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class SCH_Use_Case_4 {

    WebDriver driver;

    HomePage homePage;
    SearchTab searchTab;
    BatchJobsTab batchJobsTab;

    String autoSelectedRepository;
    String listOfRepositories;
    String ownerForOwnerRepositorySearch;
    String repositoryForOwnerRepositorySearch;
    String numOfRepositories;

    @BeforeTest
    public void beforeTest() throws Exception {

        // CommonFunctions.launchBrowser();
        driver = CommonFunctions.driver;
        homePage = CommonFunctions.homePage;
        searchTab = CommonFunctions.searchTab;
        batchJobsTab = CommonFunctions.batchJobsTab;

        autoSelectedRepository = ReadTestData.readParameter("searchTabData",
                "autoSelectedRepository");
        listOfRepositories = ReadTestData.readParameter("searchTabData",
                "listOfRepositories");
        ownerForOwnerRepositorySearch = ReadTestData.readParameter(
                "searchTabData", "ownerForOwnerRepositorySearch");
        repositoryForOwnerRepositorySearch = ReadTestData.readParameter(
                "searchTabData", "repositoryForOwnerRepositorySearch");
        numOfRepositories = ReadTestData.readParameter("searchTabData",
                "numOfRepositories");

    }

    @Test(priority = 0)
    public void SCH_Search_Tab_UI_008() {

        homePage.verifySearchTabContents();
    }

    @Test(priority = 1)
    public void SCH_Search_single_project_UI_009() {

        searchTab.clickOnSingleProjectBtn();

        searchTab.verifySingleProjectUI();
    }

    //This is a system test case
    @Test(priority = 2)
    public void SCH_Search_Results_verification_owner_010() {

        searchTab.searchForRepository(listOfRepositories);

        searchTab.pressEnterKey();

        searchTab.verifyResultsSortByRelavance();

        searchTab.waitingForResultPanel();

        searchTab.verifyResultsSortByPopularityStars();

        searchTab.waitingForResultPanel();

        searchTab.verifyResultsSortByForks();

        searchTab.waitingForResultPanel();

        searchTab.verifyResultsSortByUpdated();

        searchTab.waitingForResultPanel();

        searchTab.verifyResultsSortByRelavance();

        searchTab.waitingForResultPanel();
    }

    //This is a system test case
    @Test(priority = 3)
    public void SCH_Search_Results_verification_owner_repository_010a() {

        searchTab.searchForRepository(ownerForOwnerRepositorySearch + "/"
                + repositoryForOwnerRepositorySearch);

        searchTab.pressEnterKey();

        searchTab.verifyResultsSortByRelavance();

        searchTab.verifyOwnerRepositorySearch(ownerForOwnerRepositorySearch,
                repositoryForOwnerRepositorySearch);
    }

    @Test(priority = 4)
    public void SCH_Search_Results_UI_auto_selected_repository_011() {

        searchTab.searchForRepository(autoSelectedRepository);

        searchTab.pressEnterKey();

        searchTab.verifyResultsSortByRelavance();

        searchTab.waitingForSingleProjectResultPanel();

        searchTab.verifyAutoSelectSection();

        searchTab.verifyAutoSelectedRepoUI();

    }

    @Test(priority = 5)
    public void SCH_See_all_results_012() {

        searchTab.clickOnSeeAllResultsBtn();

        searchTab.waitingForResultPanel();

        searchTab.verifyNumOfRepositories(Integer.parseInt(numOfRepositories));

        searchTab.verifyRepositoryHeader();

        searchTab.verifyRepositoryColumnListUI();

        searchTab.verifyActionsColumnListUI();
    }

    @Test(priority = 6)
    public void SCH_Search_Result_UI_list_repositories_013() {

        searchTab.searchForRepository(listOfRepositories);

        searchTab.pressEnterKey();

        searchTab.verifyResultsSortByRelavance();

        searchTab.waitingForResultPanel();

        searchTab.verifyRepositoryHeader();

        searchTab.verifyRepositoryColumnListUI();

        searchTab.verifyActionsColumnListUI();

    }

    //This is a system test case
    @Test(priority = 7)
    public void SCH_Owner_Repository_single_project_014()
            throws InterruptedException {

        searchTab.searchForRepository(autoSelectedRepository);

        searchTab.pressEnterKey();

        searchTab.verifyResultsSortByRelavance();

        searchTab.waitingForSingleProjectResultPanel();

        searchTab.clickOnOwner();

        searchTab.clickOnRepository();

    }

    @Test(priority = 8)
    public void SCH_Tooltip_single_project_015() {

        searchTab.verifyRepositoryDetailsTooltip();

        searchTab.clickOnSeeAllResultsBtn();

        searchTab.verifyRepositoryListTooltip();

    }

    @Test(priority = 9)
    public void SCH_Repository_description_single_project_016() throws InterruptedException{

        searchTab.verifyRepositoryDescription();
    }

    @Test(priority = 10)
    public void SCH_Repository_details_single_project_017() {

        searchTab.clickOnRepositoryDetailsBtn();

        searchTab.waitingForSingleProjectResultPanel();

        searchTab.verifyAutoSelectedRepoUI();

        searchTab.verifyBackToResultsBtn();

    }

    @Test(priority = 11)
    public void SCH_back_to_results_single_project_018() {

        searchTab.clickOnBackToResults();
    }


}
