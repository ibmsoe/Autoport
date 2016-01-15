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

public class BJ_Use_Case_002 {

	WebDriver driver;

	HomePage homePage;
	SearchTab searchTab;
	BatchJobsTab batchJobsTab;

	String topRepositoryValue;
	String downloadFilePath;
	String topRepositoryName;

	@BeforeTest
	public void beforeTest() throws Exception {

		// CommonFunctions.launchBrowser();
		driver = CommonFunctions.driver;

		homePage = CommonFunctions.homePage;
		searchTab = CommonFunctions.searchTab;
		batchJobsTab = CommonFunctions.batchJobsTab;

		downloadFilePath = ReadTestData.readParameter("searchTabData", "downloadFilePath");
		topRepositoryName = ReadTestData.readParameter("batchJobsTabData", "topRepositoryName");
		topRepositoryValue = ReadTestData.readParameter("searchTabData", "topRepositoryValue");

		homePage.clickBatchJobsTab();
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

		// For Windows
		batchJobsTab.selectFileToUpload(downloadFilePath + topRepositoryName + "-" + topRepositoryValue);
		// e.g C:\\Users\\manish_kane\\Downloads\\spring-framework-3

		// For Linux
		// e.g /root/Downloads/spring-framework-3
	}

	@Test(priority = 2)
	public void BJ_Upload_batch_file_004() throws InterruptedException {

		batchJobsTab.clickOnUploadBtn();

		batchJobsTab.clickOnAlertCloseBtn();

		batchJobsTab.clickListSelectBtn();

		batchJobsTab.clickOnListLocalBtn();

		batchJobsTab.verifyLocallySavedBatchFile(topRepositoryName + "-" + topRepositoryValue);// spring-framework-3

	}

	// @AfterTest
	// public void afterTest() {
	// driver.quit();
	// }

}
