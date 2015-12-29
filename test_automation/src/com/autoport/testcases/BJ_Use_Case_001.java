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

public class BJ_Use_Case_001 {

	WebDriver driver;
	// CommonFunctions function;
	HomePage homePage;
	BatchJobsTab batchJobsTab;

	// @Parameters({ "browser" })
	@BeforeTest
	public void beforeTest() throws Exception {

		// function = new CommonFunctions();
		// CommonFunctions.launchBrowser();

		driver = CommonFunctions.driver;
		homePage = CommonFunctions.homePage;
		batchJobsTab = CommonFunctions.batchJobsTab;

		// function.openAutoport();

		homePage.clickBatchJobsTab();
	}

	@Test
	public void BJ_Batch_Jobs_UI_001() {

		batchJobsTab.verifyBatchJobsTabUI();

	}

	// @AfterTest
	// public void afterTest() {
	// driver.quit();
	// }
}
