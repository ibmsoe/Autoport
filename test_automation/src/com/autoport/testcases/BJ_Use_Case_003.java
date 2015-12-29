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

public class BJ_Use_Case_003 {

	WebDriver driver;
	// CommonFunctions function;
	HomePage homePage;
	SearchTab searchTab;
	BatchJobsTab batchJobsTab;

	// @Parameters({ "browser" })
	@BeforeTest
	public void beforeTest() throws Exception {

		// function = new CommonFunctions();
		// CommonFunctions.launchBrowser();
		driver = CommonFunctions.driver;

		homePage = CommonFunctions.homePage;
		searchTab = CommonFunctions.searchTab;
		batchJobsTab = CommonFunctions.batchJobsTab;

		// function.openAutoport();

		// homePage.clickBatchJobsTab();
	}

	@Test(priority = 0)
	public void BJ_List_Select_UI_005() {

		// batchJobsTab.clickListSelectBtn();

		batchJobsTab.verifySelectListUI();

	}

	@Test(priority = 1)
	public void BJ_Search_Local_batch_files_006() {
//		batchJobsTab.clickOnListLocalBtn();

		batchJobsTab.verifyListBatchResultsUI();
	
		batchJobsTab.verifyBatchListTableHeaders();

		batchJobsTab.verifyMaxRecordsPerPage();

		batchJobsTab.verifyLocalBatchFileLocation();

		batchJobsTab.clearBatchFileSearchTbx();

		batchJobsTab.enterBatchSearchTerm("spring-framework");

		batchJobsTab.clickOnListLocalBtn();

		batchJobsTab.verifyResultForBatchFileSearch("spring-framework");

		batchJobsTab.clearBatchFileSearchTbx();
	
	}
		@Test(priority = 2)
	public void BJ_Search_Archived_batch_files_007() {
		batchJobsTab.clickOnListArchivedBtn();

		batchJobsTab.verifyListBatchResultsUI();

		batchJobsTab.verifyBatchListTableHeaders();

		batchJobsTab.verifyMaxRecordsPerPage();

		batchJobsTab.verifyArchivedBatchFileLocation();

		batchJobsTab.clearBatchFileSearchTbx();

		batchJobsTab.enterBatchSearchTerm("spring-framework");

		batchJobsTab.clickOnListArchivedBtn();

		batchJobsTab.verifyResultForBatchFileSearch("spring-framework");

		batchJobsTab.clearBatchFileSearchTbx();
	}

		@Test(priority = 3)
	public void BJ_Search_all_batch_files_008() {
		batchJobsTab.clickOnListAllBtn();

		batchJobsTab.verifyListBatchResultsUI();

		batchJobsTab.verifyBatchListTableHeaders();

		batchJobsTab.verifyMaxRecordsPerPage();

		batchJobsTab.clearBatchFileSearchTbx();

		batchJobsTab.enterBatchSearchTerm("spring-framework");

		batchJobsTab.clickOnListAllBtn();

		batchJobsTab.verifyResultForBatchFileSearch("spring-framework");

		batchJobsTab.clearBatchFileSearchTbx();

	}

	// @AfterTest
	// public void afterTest() {
	// driver.quit();
	// }

}
