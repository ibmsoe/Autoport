package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.AfterTest;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Parameters;
import org.testng.annotations.Test;

import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.CommonFunctions;

public class SCH_Use_Case_2 {

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

		homePage.clickOnSettings();
	}

	@Test(priority = 0)
	public void SCH_Settings_UI_003() {

		homePage.verifySettingsUI();
	}

	@Test(priority = 1)
	public void SCH_Reset_to_Default_Settings_004() {
		homePage.clickOnSettingsResetBtn();
	}

	@Test(priority = 2)
	public void SCH_Saving_Changes_Settings_005() {
		homePage.verifyGsaConnectedStatus("mkane", "ZCpWbh0SYh8f");
	}

	@Test(priority = 3)
	public void SCH_Close_Settings_006() {
		homePage.clickOnSettingsCloseBtn();
	}

	@AfterTest
	public void afterTest() {
		driver.quit();
	}
}
