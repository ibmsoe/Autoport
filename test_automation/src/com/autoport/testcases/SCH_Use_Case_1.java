package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.AfterTest;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;

import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.CommonFunctions;

public class SCH_Use_Case_1 {

	WebDriver driver;
	CommonFunctions function;
	HomePage homePage;

	@Parameters({ "browser" })
	@BeforeTest
	public void beforeTest(String browser) throws Exception {

		function = new CommonFunctions();
		function.launchBrowser(browser);
		driver = function.driver;

		homePage = function.homePage;

		function.openAutoport();

	}

	@Test(priority = 0)
	public void SCH_AutoPort_Initialization_001() {

		homePage.initializeText();

	}

	@Test(priority = 1)
	public void SCH_Home_UI_002() {

		homePage.verifyHomePageUI();
		homePage.verifySearchTabContents();

	}

	@AfterTest
	public void afterTest() {
		driver.quit();
	}

}
