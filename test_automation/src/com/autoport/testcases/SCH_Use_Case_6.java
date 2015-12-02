package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.AfterTest;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;

import com.autoport.pageobjects.SearchTab;
import com.autoport.utilities.CommonFunctions;

public class SCH_Use_Case_6 {

	WebDriver driver;
	CommonFunctions function;

	SearchTab searchTab;

	@Parameters({ "browser" })
	@BeforeTest
	public void beforeTest(String browser) throws Exception {

		function = new CommonFunctions();
		function.launchBrowser(browser);
		driver = function.driver;

		searchTab = function.searchTab;

		function.openAutoport();
	}

	@Test(priority = 0)
	public void SCH_Use_current_version_repository_details_single_project_024() {
		searchTab.clickOnSingleProjectBtn();

		searchTab.searchForRepository("cassandra");

		searchTab.verifyResultsSortByRelavance();

		searchTab.waitingForSingleProjectResultPanel();

		searchTab.verifyUseCurrentVersion();
	}

	@Test(priority = 1)
	public void SCH_Select_build_servers_repository_details_single_project_025() {

		searchTab.verifySelectBuildServer();
	}

	@Test(priority = 2)
	public void SCH_Build_Test_repository_single_project_026() {
		searchTab.clickOnBuildAndTestBtn();

	}

	@Test(priority = 3)
	public void SCH_Build_Steps_repository_single_project_027() {
		searchTab.verifyBuildSteps();
	}

	@AfterTest
	public void afterTest() {
		driver.quit();
	}

}
