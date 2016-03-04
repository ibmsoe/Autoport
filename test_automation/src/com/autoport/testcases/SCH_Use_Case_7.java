package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.SearchTab;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class SCH_Use_Case_7 {

    WebDriver driver;

    SearchTab searchTab;

    String topRepositoryValue;
    String sortByValue;
    String programmingLanguageValue;
    String releaseValue;
    String popularityStarsValue;
    String forksValue;

    @BeforeTest
    public void beforeTest() throws Exception {

        // CommonFunctions.launchBrowser();
        driver = CommonFunctions.driver;
        searchTab = CommonFunctions.searchTab;

        topRepositoryValue = ReadTestData.readParameter("searchTabData", "topRepositoryValue");
        sortByValue = ReadTestData.readParameter("searchTabData", "sortByValue");
        programmingLanguageValue = ReadTestData.readParameter("searchTabData", "programmingLanguageValue");
        releaseValue = ReadTestData.readParameter("searchTabData", "releaseValue");
        popularityStarsValue = ReadTestData.readParameter("searchTabData", "popularityStarsValue");
        forksValue = ReadTestData.readParameter("searchTabData", "forksValue");
    }

    @Test(priority = 0)
    public void SCH_Search_common_projects_UI_028() {

        searchTab.clickOnMostCommonlyUsedProjectsBtn();

        searchTab.verifyCommonlyUsedProjectsUI();
    }

    @Test(priority = 1)
    public void SCH_Top_Repositories_common_projects_029() {

        searchTab.verifyTopRepositoriesTxBx();

    }

    @Test(priority = 2)
    public void SCH_Sort_By_common_projects_030() {
        searchTab.verifySortByDropDown();
    }

    @Test(priority = 3)
    public void SCH_Programming_Language_common_project_031() {
        searchTab.verifyProgrammingLanguagesDropDown();
    }

    @Test(priority = 4)
    public void SCH_Release_common_projects_032() {
        searchTab.verifyReleaseDropDown();
    }

    @Test(priority = 5)
    public void SCH_Popularity_Stars_common_projects_033() {
        searchTab.verifyGreaterThanPopularityStars();
    }

    @Test(priority = 6)
    public void SCH_Forks_common_projects_034() {
        searchTab.verifyGreaterThanForks();
    }

    //This is a system test case
    @Test(priority = 7)
    public void SCH_Search_common_projects_035() throws InterruptedException {

        searchTab.enterNumOfTopRepositories(topRepositoryValue);

        searchTab.selectSortByValue(sortByValue);

        searchTab.selectProgrammingLanguage(programmingLanguageValue);

        searchTab.selectRelease(releaseValue);

        searchTab.enterPopularityStars(popularityStarsValue);

        searchTab.enterForks(forksValue);

        searchTab.clickOnCommonlyUsedProjectSearch();

        searchTab.verifyCommonProjectBatchFileSaveExportUI();

        searchTab.verifyNumOfRepositories(Integer.valueOf(topRepositoryValue));

        searchTab.verifyCommonProjectRepositoryHeader();

        searchTab.verifyRepositoryColumnListUIForCommonProjects();

        searchTab.verifyActionsColumnListUIForCommonProjects();

    }

    //This is a system test case
    @Test(priority = 8)
    public void SCH_Owner_Repository_common_projects_036() throws InterruptedException {

        searchTab.clickOnOwnerForCommonProject();

        searchTab.browserNavigateBack();

        searchTab.clickOnMostCommonlyUsedProjectsBtn();

        searchTab.enterNumOfTopRepositories(topRepositoryValue);

        searchTab.selectSortByValue(sortByValue);

        searchTab.selectProgrammingLanguage(programmingLanguageValue);

        searchTab.selectRelease(releaseValue);

        searchTab.enterPopularityStars(popularityStarsValue);

        searchTab.enterForks(forksValue);

        searchTab.clickOnCommonlyUsedProjectSearch();

        searchTab.clickOnRepositoryForCommonProject();

        searchTab.browserNavigateBack();

        searchTab.clickOnMostCommonlyUsedProjectsBtn();

        searchTab.enterNumOfTopRepositories(topRepositoryValue);

        searchTab.selectSortByValue(sortByValue);

        searchTab.selectProgrammingLanguage(programmingLanguageValue);

        searchTab.selectRelease(releaseValue);

        searchTab.enterPopularityStars(popularityStarsValue);

        searchTab.enterForks(forksValue);

        searchTab.clickOnCommonlyUsedProjectSearch();

    }

    @Test(priority = 9)
    public void SCH_Tooltip_common_projects_037() {
        searchTab.verifyRepositoryListTooltip();
    }

    @Test(priority = 10)
    public void SCH_Repository_Description_common_projects_038() throws InterruptedException {
        searchTab.verifyRepositoryDescriptionForCommonProjects();
    }

    @Test(priority = 11)
    public void SCH_Repository_Details_common_projects_039() throws InterruptedException {

        searchTab.clickOnRepositoryDetailsBtnForCommonProjects();

        searchTab.verifyProjectDetailRepoUIForCommonProjects();

        searchTab.verifyBackToResultsBtnForCommonProjects();
    }

    @Test(priority = 12)
    public void SCH_back_to_results_common_projects_040() {
        searchTab.clickOnBackToResultsForCommonProjects();
    }


}
