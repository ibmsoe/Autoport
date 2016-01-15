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
import com.autoport.utilities.ReadTestData;

public class BJ_Use_Case_003 {

	WebDriver driver;

	HomePage homePage;
	SearchTab searchTab;
	BatchJobsTab batchJobsTab;
	
	String topRepositoryName;
	String topRepositoryValue;

	@BeforeTest
	public void beforeTest() throws Exception {

		// CommonFunctions.launchBrowser();
		driver = CommonFunctions.driver;

		homePage = CommonFunctions.homePage;
		searchTab = CommonFunctions.searchTab;
		batchJobsTab = CommonFunctions.batchJobsTab;
		
		topRepositoryName = ReadTestData.readParameter("batchJobsTabData", "topRepositoryName");
		topRepositoryValue = ReadTestData.readParameter("searchTabData", "topRepositoryValue");

		homePage.clickBatchJobsTab();
	}

	@Test(priority = 0)
	public void BJ_List_Select_UI_005() {

		batchJobsTab.clickListSelectBtn();

		batchJobsTab.verifySelectListUI();

	}

	@Test(priority = 1)
	public void BJ_Search_Local_batch_files_006() throws InterruptedException {
		// batchJobsTab.clickOnListLocalBtn();

		batchJobsTab.verifyListBatchResultsUI();

		batchJobsTab.verifyBatchListTableHeaders();

		batchJobsTab.verifyMaxRecordsPerPage();

		batchJobsTab.verifyLocalBatchFileLocation();

		batchJobsTab.clearBatchFileSearchTbx();

		batchJobsTab.enterBatchSearchTerm(topRepositoryName+"-"+topRepositoryValue);//spring-framework

		batchJobsTab.clickOnListLocalBtn();

		batchJobsTab.verifyResultForBatchFileSearch(topRepositoryName+"-"+topRepositoryValue);//spring-framework

		batchJobsTab.clearBatchFileSearchTbx();

		batchJobsTab.selectFirstRow();

		batchJobsTab.clickOnArchiveBtn();

		batchJobsTab.clickOnAlertCloseBtn();
	}

	@Test(priority = 2)
	public void BJ_Search_Archived_batch_files_007() {

		batchJobsTab.clickOnListArchivedBtn();

		batchJobsTab.verifyListArchivedBatchResultsUI();

		batchJobsTab.verifyBatchListTableHeaders();

		batchJobsTab.verifyMaxRecordsPerPage();

		batchJobsTab.verifyArchivedBatchFileLocation();

		batchJobsTab.clearBatchFileSearchTbx();

		batchJobsTab.enterBatchSearchTerm(topRepositoryName+"-"+topRepositoryValue);//spring-framework

		batchJobsTab.clickOnListArchivedBtn();

		batchJobsTab.verifyResultForBatchFileSearch(topRepositoryName+"-"+topRepositoryValue);//spring-framework

		batchJobsTab.clearBatchFileSearchTbx();
	}

	@Test(priority = 3)
	public void BJ_Search_all_batch_files_008() {

		batchJobsTab.clickOnListAllBtn();

		batchJobsTab.verifyListBatchResultsUI();

		batchJobsTab.verifyBatchListTableHeaders();

		batchJobsTab.verifyMaxRecordsPerPage();

		batchJobsTab.clearBatchFileSearchTbx();

		batchJobsTab.enterBatchSearchTerm(topRepositoryName+"-"+topRepositoryValue);//spring-framework

		batchJobsTab.clickOnListAllBtn();

		batchJobsTab.verifyResultForBatchFileSearch(topRepositoryName+"-"+topRepositoryValue);//spring-framework

		batchJobsTab.clearBatchFileSearchTbx();

	}

	// @AfterTest
	// public void afterTest() {
	// driver.quit();
	// }

}
