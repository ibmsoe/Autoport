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

public class SCH_Use_Case_5 {

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
	public void SCH_Adding_repositories_batch_file_single_project_019() {
		searchTab.clickOnSingleProjectBtn();

		searchTab.searchForRepository("Cassandra");

		searchTab.verifyResultsSortByRelavance();

		searchTab.clickOnAddToBatchBtn();

		searchTab.verifyBatchFileSaveExportCloseUI();

		searchTab.verifyBatchFileRepositoryPanelUI();
	}

	@Test(priority = 1)
	public void SCH_Save_batch_file_single_project_020() throws InterruptedException {

		searchTab.clickOnBatchFileSaveBtn();

		homePage.clickBatchJobsTab();

		batchJobsTab.clickListSelectBtn();

		batchJobsTab.clickOnListLocalBtn();

		batchJobsTab.verifyLocallySavedBatchFile("cassandra-1");
	}

	@Test(priority = 2)
	public void SCH_Export_batch_file_single_project_021() throws InterruptedException {

		homePage.clickSearchTab();

		Thread.sleep(1000);

		searchTab.verifyResultsSortByPopularityStars();

		searchTab.clickOnAddToBatchBtn();

		searchTab.clickOnBatchFileExportBtn();

		Thread.sleep(2000);

		searchTab.confirmFileDownload("cassandra-1");

	}

	@Test(priority = 3)
	public void SCH_Clear_batch_file_single_project_022() {

		searchTab.verifyResultsSortByRelavance();

		searchTab.clickOnAddToBatchBtn();

		searchTab.clickOnBatchFileClearBtn();
	}

	@Test(priority = 4)
	public void SCH_Batch_File_Repository_UI_023() {

		searchTab.verifyResultsSortByPopularityStars();

		searchTab.clickOnAddToBatchBtn();

		searchTab.verifyBatchFileRepositoryPanelUI();

		searchTab.verifyBatchFileRepositoryDescription();

	}

	@AfterTest
	public void afterTest() {
		driver.quit();
	}

}
