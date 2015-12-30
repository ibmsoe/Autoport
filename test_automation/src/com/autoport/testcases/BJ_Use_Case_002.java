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

public class BJ_Use_Case_002 {

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
	public void BJ_Import_UI_002() {

		batchJobsTab.clickImportBtn();
		
		batchJobsTab.verifyDisplayOfImportSection();

		batchJobsTab.verifyUploadDisplayBox();

		batchJobsTab.verifyPlaceHolderTextForUploadFileDisplayBox();

		batchJobsTab.verifySelectFileBtn();

		batchJobsTab.verifyUploadBtn();
	}

	@Test(priority = 1)
	public void BJ_Browse_batch_file_upload_003() {

		batchJobsTab.selectFileToUpload("C:\\Users\\manish_kane\\Downloads\\spring-framework-3");
		// For Linux /root/Downloads/spring-framework-3
	}

	@Test(priority = 2)
	public void BJ_Upload_batch_file_004() throws InterruptedException {
		batchJobsTab.clickOnUploadBtn();
		
		batchJobsTab.clickOnAlertCloseBtn();

		batchJobsTab.clickListSelectBtn();

		batchJobsTab.clickOnListLocalBtn();

		batchJobsTab.verifyLocallySavedBatchFile("spring-framework-3");

		batchJobsTab.clickImportBtn();
	}

	// @AfterTest
	// public void afterTest() {
	// driver.quit();
	// }

}
