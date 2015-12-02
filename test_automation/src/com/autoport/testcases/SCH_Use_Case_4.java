package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.AfterTest;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BatchJobsTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.SearchTab;
import com.autoport.utilities.CommonFunctions;

public class SCH_Use_Case_4 {

	WebDriver driver;
	CommonFunctions function;
	HomePage homePage;
	SearchTab searchTab;
	BatchJobsTab batchJobsTab;

	@Parameters({ "browser" })
	@BeforeTest
	public void beforeTest(String browser) throws Exception {

		function = new CommonFunctions();
		function.launchBrowser(browser);
		driver = function.driver;

		homePage = function.homePage;
		searchTab = function.searchTab;
		batchJobsTab = function.batchJobsTab;

		function.openAutoport();
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

	@Test(priority = 2)
	public void SCH_Search_Results_verification_010() {

		searchTab.searchForRepository("Cassandra");

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

	@Test(priority = 3)
	public void SCH_Search_Results_UI_auto_selected_repository_011() {

		searchTab.searchForRepository("cassandra");

		searchTab.verifyResultsSortByRelavance();

		searchTab.waitingForSingleProjectResultPanel();

		searchTab.verifyAutoSelectSection();

		searchTab.verifyAutoSelectedRepoUI();

	}

	@Test(priority = 4)
	public void SCH_See_all_results_012() {

		searchTab.clickOnSeeAllResultsBtn();

		searchTab.waitingForResultPanel();

		searchTab.verifyNumOfRepositories(10);

		searchTab.verifyRepositoryHeader();

		searchTab.verifyRepositoryColumnListUI();

		searchTab.verifyActionsColumnListUI();
	}

	@Test(priority = 5)
	public void SCH_Search_Result_UI_list_repositories_013() {

		searchTab.searchForRepository("Cassandra");

		searchTab.verifyResultsSortByRelavance();

		searchTab.waitingForResultPanel();

		searchTab.verifyRepositoryHeader();

		searchTab.verifyRepositoryColumnListUI();

		searchTab.verifyActionsColumnListUI();

	}

	@Test(priority = 6)
	public void SCH_Owner_Repository_single_project_014() {

		searchTab.searchForRepository("cassandra");

		searchTab.verifyResultsSortByRelavance();

		searchTab.waitingForSingleProjectResultPanel();

		searchTab.clickOnOwner();

		searchTab.browserNavigateBack();

		// searchTab.browserPageRefresh();

		searchTab.clickOnSingleProjectBtn();

		// searchTab.searchForRepository("cassandra");

		searchTab.verifyResultsSortByPopularityStars();

		searchTab.waitingForSingleProjectResultPanel();

		searchTab.clickOnRepository();

		searchTab.browserNavigateBack();

	}

	@Test(priority = 7)
	public void SCH_Tooltip_single_project_015() {
		// searchTab.browserPageRefresh();

		searchTab.clickOnSingleProjectBtn();

		// searchTab.searchForRepository("cassandra");

		searchTab.verifyResultsSortByPopularityStars();

		searchTab.waitingForSingleProjectResultPanel();

		searchTab.verifyRepositoryDetailsTooltip();

		searchTab.clickOnSeeAllResultsBtn();

		searchTab.verifyRepositoryListTooltip();

	}

	@Test(priority = 8)
	public void SCH_Repository_description_single_project_016() {
		searchTab.verifyRepositoryDescription();
	}

	@Test(priority = 9)
	public void SCH_Repository_details_single_project_017() {

		searchTab.clickOnRepositoryDetailsBtn();

		searchTab.waitingForSingleProjectResultPanel();

		searchTab.verifyAutoSelectedRepoUI();

		searchTab.verifyBackToResultsBtn();

	}

	@Test(priority = 10)
	public void SCH_back_to_results_single_project_018() {
		searchTab.clickOnBackToResults();
	}

	@AfterTest
	public void afterTest() {
		driver.quit();
	}

}
