package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BatchJobsTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.SearchTab;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class SCH_Use_Case_8 {

	WebDriver driver;
	CommonFunctions function;

	SearchTab searchTab;
	HomePage homePage;
	BatchJobsTab batchJobsTab;

	String topRepositoryValue;

	@BeforeTest
	public void beforeTest() throws Exception {

		// CommonFunctions.launchBrowser();
		driver = CommonFunctions.driver;

		homePage = CommonFunctions.homePage;
		searchTab = CommonFunctions.searchTab;
		batchJobsTab = CommonFunctions.batchJobsTab;

		searchTab.clickOnMostCommonlyUsedProjectsBtn();

		topRepositoryValue = ReadTestData.readParameter("searchTabData", "topRepositoryValue");

	}

	@Test(priority = 0)
	public void SCH_Save_Batch_File_common_projects_041() throws InterruptedException {

		searchTab.clickOnCommonlyUsedProjectSearch();

		searchTab.clickOnBatchFileSaveBtnForCommonProjects();

		homePage.clickBatchJobsTab();

		batchJobsTab.clickListSelectBtn();

		batchJobsTab.clickOnListLocalBtn();

		batchJobsTab
				.verifyLocallySavedBatchFile(searchTab.getRepositoryNameForCommonProject() + "-" + topRepositoryValue);

	}

	@Test(priority = 1)
	public void SCH_Export_Batch_File_common_projects_042() throws InterruptedException {

		homePage.clickSearchTab();

		searchTab.clickOnCommonlyUsedProjectSearch();

		searchTab.clickOnBatchFileExportBtnForCommonProjects();

		Thread.sleep(2000);

		searchTab.confirmFileDownload(searchTab.getRepositoryNameForCommonProject() + "-" + topRepositoryValue);
	}

	@Test(priority = 2)
	public void SCH_Remove_repository_batch_file_043() {

		searchTab.clickOnCommonlyUsedProjectSearch();

		searchTab.commonProjectRemoveRepository();
	}

	
}
