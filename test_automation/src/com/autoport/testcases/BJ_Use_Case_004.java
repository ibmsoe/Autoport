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

public class BJ_Use_Case_004 {

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

		// homePage = new HomePage(driver);
		// searchTab = new SearchTab(driver);
		// batchJobsTab = new BatchJobsTab(driver);

		homePage = CommonFunctions.homePage;
		searchTab = CommonFunctions.searchTab;
		batchJobsTab = CommonFunctions.batchJobsTab;

		// function.openAutoport();

		// homePage.clickBatchJobsTab();

	}

	@Test(priority = 0)
	public void BJ_Batch_file_detail_UI_009() throws InterruptedException {

		// batchJobsTab.clickListSelectBtn();

		batchJobsTab.clickOnListLocalBtn();

		// batchJobsTab.clickOnDateModifiedHeader();

		batchJobsTab.selectFirstRow();

		batchJobsTab.clickOnDetailsBtn();

		batchJobsTab.verifyBatchFileDetailsUI("spring-framework-3");

		batchJobsTab.verifyBatchConfigTableHeaders();

		batchJobsTab.verifyBatchConfigActionsColumn();

		batchJobsTab.verifyBatchRepoHeaders();

		batchJobsTab.verifyBatchRepoActionsColumn();
		
		batchJobsTab.clickOnListLocalBtn();
		
		batchJobsTab.selectFirstRow();
		
		batchJobsTab.clickOnArchiveBtn();
		
		batchJobsTab.clickOnAlertCloseBtn();

		batchJobsTab.clickOnListArchivedBtn();

		batchJobsTab.selectFirstRow();

		batchJobsTab.clickOnDetailsBtn();

		batchJobsTab.verifyBatchFileDetailsUI("spring-framework-3");

		batchJobsTab.verifyBatchConfigTableHeaders();

		batchJobsTab.verifyBatchConfigActionsColumn();

		batchJobsTab.verifyBatchRepoHeaders();

		batchJobsTab.verifyBatchRepoActionsColumn();

		batchJobsTab.clickOnListAllBtn();

		batchJobsTab.selectFirstRow();

		batchJobsTab.clickOnDetailsBtn();

		batchJobsTab.verifyBatchFileDetailsUI("spring-framework-3");

		batchJobsTab.verifyBatchConfigTableHeaders();

		batchJobsTab.verifyBatchConfigActionsColumn();

		batchJobsTab.verifyBatchRepoHeaders();

		batchJobsTab.verifyBatchRepoActionsColumn();
	}

	@Test(priority = 1)
	public void BJ_Save_batch_file_detailed_view_010() throws InterruptedException {
		batchJobsTab.clickOnListLocalBtn();

		batchJobsTab.selectFirstRow();

		batchJobsTab.clickOnDetailsBtn();

		batchJobsTab.saveBatchFileAs("spring-framework-03");

		batchJobsTab.clickOnSaveBatchDetailsBtn();
		
		batchJobsTab.clickOnAlertCloseBtn();

		batchJobsTab.verifyBatchFileNameChangeInConfig();

		batchJobsTab.clickOnListLocalBtn();

		batchJobsTab.newBatchFileCreationConfirmation("spring-framework-03");

		batchJobsTab.clickOnListArchivedBtn();

		batchJobsTab.selectFirstRow();

		batchJobsTab.clickOnDetailsBtn();

		batchJobsTab.saveBatchFileAs("spring-framework-13");

		batchJobsTab.clickOnSaveBatchDetailsBtn();
		
		batchJobsTab.clickOnAlertCloseBtn();

		batchJobsTab.verifyBatchFileNameChangeInConfig();

		batchJobsTab.clickOnListLocalBtn();

		batchJobsTab.newBatchFileCreationConfirmation("spring-framework-13");
	}

	@Test(priority = 2)
	public void BJ_Back_detailed_view_011() throws InterruptedException {

		batchJobsTab.selectFirstRow();

		batchJobsTab.clickOnDetailsBtn();

		batchJobsTab.clickOnDetailsBackBtn();

		batchJobsTab.clickOnListArchivedBtn();

		batchJobsTab.selectFirstRow();

		batchJobsTab.clickOnDetailsBtn();

		batchJobsTab.clickOnDetailsBackBtn();

		batchJobsTab.clickOnListAllBtn();

		batchJobsTab.selectFirstRow();

		batchJobsTab.clickOnDetailsBtn();

		batchJobsTab.clickOnDetailsBackBtn();

	}

	@Test(priority = 3)
	public void BJ_Batch_file_settings_012() throws InterruptedException {

		batchJobsTab.clickOnListLocalBtn();

		batchJobsTab.selectFirstRow();

		batchJobsTab.clickOnDetailsBtn();

		batchJobsTab.clickOnSettingsBtn();

		batchJobsTab.verifyBatchConfigSettingsUI();

	}

	@Test(priority = 4)
	public void BJ_Close_Reset_Save_batch_file_settings_013() throws InterruptedException {

		batchJobsTab.clickOnBatchConfigSettingsSaveBtn();

		batchJobsTab.clickOnSettingsBtn();

		batchJobsTab.clickOnBatchConfigSettingsResetBtn();

		batchJobsTab.clickOnBatchConfigSettingsCloseBtn();

	}

	@Test(priority = 5)
	public void BJ_Move_delete_repository_batch_file_014() {

		batchJobsTab.verifyRepoUpMove();

		batchJobsTab.verifyRepoDownMove();

		batchJobsTab.verifyRepoDelete();

	}

	@Test(priority = 6)
	public void BJ_Archive_local_batch_file_015() throws InterruptedException {

		batchJobsTab.clickOnListLocalBtn();

		batchJobsTab.selectFirstRow();

		batchJobsTab.clickOnArchiveBtn();
		
		batchJobsTab.clickOnAlertCloseBtn();

	}

	@Test(priority = 7)
	public void BJ_Remove_batch_file_016() {

		batchJobsTab.clickOnRemoveBtn();

		batchJobsTab.clickOnListArchivedBtn();

		batchJobsTab.selectFirstRow();

		batchJobsTab.clickOnRemoveBtn();

		batchJobsTab.clickOnListAllBtn();

		batchJobsTab.selectFirstRow();

		batchJobsTab.clickOnRemoveBtn();

	}

	// @AfterTest
	// public void afterTest() {
	// driver.quit();
	// }

}
