package com.autoport.testcases;

import java.text.ParseException;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.AfterTest;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BatchJobsTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.pageobjects.SearchTab;
import com.autoport.utilities.CommonFunctions;

public class BJ_Use_Case_005 {

	WebDriver driver;
	// CommonFunctions function;
	HomePage homePage;
	SearchTab searchTab;
	BatchJobsTab batchJobsTab;
	ReportsTab reportsTab;

	// @Parameters({ "browser" })
	@BeforeTest
	public void beforeTest() throws Exception {

		// function = new CommonFunctions();
		// CommonFunctions.launchBrowser();
		driver = CommonFunctions.driver;

		homePage = CommonFunctions.homePage;
		searchTab = CommonFunctions.searchTab;
		batchJobsTab = CommonFunctions.batchJobsTab;
		reportsTab = CommonFunctions.reportsTab;
		// function.openAutoport();

		// homePage.clickBatchJobsTab();
	}

	@Test(priority = 0)
	public void BJ_Build_Server_batch_file_results_view_017() {

		// batchJobsTab.clickListSelectBtn();

		batchJobsTab.clickOnListLocalBtn();

		batchJobsTab.clickOnBuildServers();

		batchJobsTab.verifyBuildServersNodes();

		batchJobsTab.verifySelectionOfAllBuildServers();

		batchJobsTab.verifyDeSelectionOfAllBuildServers();

		batchJobsTab.clickOnBuildServers();
	}

	@Test(priority = 1)
	public void BJ_Build_Test_batch_file_result_view_018() throws InterruptedException, ParseException {

		// batchJobsTab.clickOnBuildServers();

		// batchJobsTab.verifySelectionOfAllBuildServers();

		// batchJobsTab.clickOnBuildServers();

		// batchJobsTab.clickOnDateModifiedHeader();

		batchJobsTab.selectFirstRow();

		batchJobsTab.verifyBuildAndTestBtn();

		searchTab.clickOnAlertCloseBtn();

		homePage.clickReportsTab();

		reportsTab.clickOnManageCompareBatchJobsResultsBtn();

		reportsTab.enterBatchNameForSearch("spring-framework");

		reportsTab.clickOnBatchListLocalBtn();

		reportsTab.clickOnDateSubmittedHeader();

		reportsTab.verifyJenkinsJobCompletionForBatch(batchJobsTab.getBuildClickTime(),
				batchJobsTab.getBuildServersCount());

	}

	// Buttons removed as per new UI

	// @Test(priority = 2)
	// public void BJ_Build_Server_batch_file_details_view_019() {
	//
	// }

	// @Test(priority = 3)
	// public void BJ_Build_Test_batch_file_detailed_view_020() {
	//
	// }

	// @AfterTest
	// public void afterTest() {
	// driver.quit();
	// }

}
