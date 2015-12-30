package com.autoport.testcases;

import java.text.ParseException;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.AfterTest;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;

import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.pageobjects.SearchTab;
import com.autoport.utilities.CommonFunctions;

public class SCH_Use_Case_6 {

	WebDriver driver;
	// CommonFunctions function;
	HomePage homePage;
	SearchTab searchTab;
	ReportsTab reportsTab;

	// @Parameters({ "browser" })
	@BeforeTest
	public void beforeTest() throws Exception {

		// function = new CommonFunctions();
		// CommonFunctions.launchBrowser();
		driver = CommonFunctions.driver;

		homePage = CommonFunctions.homePage;
		searchTab = CommonFunctions.searchTab;
		reportsTab = CommonFunctions.reportsTab;
		// function.openAutoport();
	}

	@Test(priority = 0)
	public void SCH_Use_current_version_repository_details_single_project_024() {
		// searchTab.clickOnSingleProjectBtn();

		searchTab.searchForRepository("bson");

		searchTab.verifyResultsSortByRelavance();

		searchTab.waitingForResultPanel();

		searchTab.clickOnFirstRepositoryDetailsBtn();

		searchTab.verifyUseCurrentVersion();
	}

	@Test(priority = 1)
	public void SCH_Select_build_servers_repository_details_single_project_025() {

		searchTab.verifySelectBuildServer();
	}

	@Test(priority = 2)
	public void SCH_Build_Test_repository_single_project_026() throws InterruptedException, ParseException {

		searchTab.clickOnBuildAndTestBtn();

		searchTab.clickOnAlertCloseBtn();

		homePage.clickReportsTab();

		reportsTab.clickOnManageCompareProjectResultsBtn();

		reportsTab.enterProjectNameForSearch("rabl");

		reportsTab.clickOnListLocalBtn();

		reportsTab.clickOnDateCompletedHeader();

		reportsTab.verifyJenkinsJobCompletion(searchTab.getBuildClickTime(), searchTab.getBuildServersCount());

		homePage.clickSearchTab();

	}

	@Test(priority = 3)
	public void SCH_Build_Steps_repository_single_project_027() {
		searchTab.verifyBuildSteps();
	}

	// @AfterTest
	// public void afterTest() {
	// driver.quit();
	// }

}
