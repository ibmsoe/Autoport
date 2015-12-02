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

public class SCH_Use_Case_8 {

	WebDriver driver;
	CommonFunctions function;

	SearchTab searchTab;
	HomePage homePage;
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
	public void SCH_Save_Batch_File_common_projects_041() throws InterruptedException {

		searchTab.clickOnMostCommonlyUsedProjectsBtn();

		searchTab.clickOnCommonlyUsedProjectSearch();

		searchTab.clickOnBatchFileSaveBtnForCommonProjects();

		homePage.clickBatchJobsTab();

		batchJobsTab.clickListSelectBtn();

		batchJobsTab.clickOnListLocalBtn();

		batchJobsTab.verifyLocallySavedBatchFile("bootstrap-25");

	}

	@Test(priority = 1)
	public void SCH_Export_Batch_File_common_projects_042() throws InterruptedException {

		homePage.clickSearchTab();

		searchTab.clickOnCommonlyUsedProjectSearch();

		searchTab.clickOnBatchFileExportBtnForCommonProjects();

		Thread.sleep(2000);

		searchTab.confirmFileDownload("bootstrap-25");
	}

	@Test(priority = 2)
	public void SCH_Remove_repository_batch_file_043() {

		searchTab.clickOnCommonlyUsedProjectSearch();

		searchTab.commonProjectRemoveRepository();
	}

	@AfterTest
	public void afterTest() {
		 driver.quit();
	}

}
