package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.AfterTest;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;

import com.autoport.pageobjects.SearchTab;
import com.autoport.utilities.CommonFunctions;

public class SCH_Use_Case_7 {

	WebDriver driver;
	CommonFunctions function;
	SearchTab searchTab;

	@Parameters({ "browser" })
	@BeforeTest
	public void beforeTest(String browser) throws Exception {

		function = new CommonFunctions();
		function.launchBrowser(browser);
		driver = function.driver;

		searchTab = function.searchTab;

		function.openAutoport();
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

	@Test(priority = 7)
	public void SCH_Search_common_projects_035() {

		searchTab.enterNumOfTopRepositories("15");

		searchTab.selectSortByValue("Forks");

		searchTab.selectProgrammingLanguage("Java");

		searchTab.selectRelease("Current");

		searchTab.enterPopularityStars("100");

		searchTab.enterForks("100");

		searchTab.clickOnCommonlyUsedProjectSearch();

		searchTab.verifyCommonProjectBatchFileSaveExportUI();

		searchTab.verifyNumOfRepositories(15);

		searchTab.verifyCommonProjectRepositoryHeader();

		searchTab.verifyRepositoryColumnListUI();

		searchTab.verifyActionsColumnListUIForCommonProjects();

	}

	@Test(priority = 8)
	public void SCH_Owner_Repository_common_projects_036() {

		searchTab.clickOnOwnerForCommonProject();

		searchTab.browserNavigateBack();

		searchTab.clickOnMostCommonlyUsedProjectsBtn();

		searchTab.enterNumOfTopRepositories("15");

		searchTab.selectSortByValue("Forks");

		searchTab.selectProgrammingLanguage("Java");

		searchTab.selectRelease("Current");

		searchTab.enterPopularityStars("100");

		searchTab.enterForks("100");

		searchTab.clickOnCommonlyUsedProjectSearch();

		searchTab.clickOnRepositoryForCommonProject();

		searchTab.browserNavigateBack();

		searchTab.clickOnMostCommonlyUsedProjectsBtn();

		searchTab.enterNumOfTopRepositories("15");

		searchTab.selectSortByValue("Forks");

		searchTab.selectProgrammingLanguage("Java");

		searchTab.selectRelease("Current");

		searchTab.enterPopularityStars("100");

		searchTab.enterForks("100");

		searchTab.clickOnCommonlyUsedProjectSearch();

	}

	@Test(priority = 9)
	public void SCH_Tooltip_common_projects_037() {
		searchTab.verifyRepositoryListTooltip();
	}

	@Test(priority = 10)
	public void SCH_Repository_Description_common_projects_038() {
		searchTab.verifyRepositoryDescription();
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

	@AfterTest
	public void afterTest() {
		driver.quit();
	}

}
