package com.autoport.testcases;

import java.text.ParseException;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BatchJobsTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.pageobjects.SearchTab;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class BJ_Use_Case_005 {

	WebDriver driver;

	HomePage homePage;
	SearchTab searchTab;
	BatchJobsTab batchJobsTab;
	ReportsTab reportsTab;

	String topRepositoryName;
	String topRepositoryValue;

	@BeforeTest
	public void beforeTest() throws Exception {

		// CommonFunctions.launchBrowser();
		driver = CommonFunctions.driver;

		homePage = CommonFunctions.homePage;
		searchTab = CommonFunctions.searchTab;
		batchJobsTab = CommonFunctions.batchJobsTab;
		reportsTab = CommonFunctions.reportsTab;

		topRepositoryName = ReadTestData.readParameter("batchJobsTabData", "topRepositoryName");
		topRepositoryValue = ReadTestData.readParameter("searchTabData", "topRepositoryValue");

		homePage.clickBatchJobsTab();
	}

	@Test(priority = 0)
	public void BJ_Build_Server_batch_file_results_view_017() throws InterruptedException {

		batchJobsTab.clickListSelectBtn();

		batchJobsTab.clickOnListLocalBtn();

		batchJobsTab.clickOnBuildServers();

		batchJobsTab.verifyBuildServersNodes();

		batchJobsTab.verifySelectionOfAllBuildServers();

		batchJobsTab.verifyDeSelectionOfAllBuildServers();

		batchJobsTab.clickOnBuildServers();
	}

	@Test(priority = 1)
	public void BJ_Build_Test_batch_file_result_view_018() throws InterruptedException, ParseException {

		batchJobsTab.selectFirstRow();

		batchJobsTab.verifyBuildAndTestBtn();

		searchTab.clickOnAlertCloseBtn();

		homePage.openReportsTab();

		reportsTab.clickOnManageCompareBatchJobsResultsBtn();

		reportsTab.enterBatchNameForSearch(topRepositoryName);// spring-framework

		reportsTab.clickOnBatchListLocalBtn();

		reportsTab.clickOnDateSubmittedHeader();

		reportsTab.verifyJenkinsJobCompletionForBatch(batchJobsTab.getBuildClickTime(),
				batchJobsTab.getBuildServersCount());

	}

	
}
