package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class SCH_Use_Case_2 {

	WebDriver driver;

	HomePage homePage;

	String gsaUserName;
	String gsaPassword;
	String envType;

	@BeforeTest
	public void beforeTest() throws Exception {

		// CommonFunctions.launchBrowser();
		driver = CommonFunctions.driver;
		homePage = CommonFunctions.homePage;

		gsaUserName = ReadTestData.readParameter("searchTabData", "gsaUserName");
		gsaPassword = ReadTestData.readParameter("searchTabData", "gsaPassword");
		envType = ReadTestData.readParameter("../config", "envType");
	}

	@Test(priority = 0)
	public void SCH_Settings_UI_003() {

		homePage.clickOnSettings();
	
		homePage.verifySettingsUI(envType);
	}

	@Test(priority = 1)
	public void SCH_Reset_to_Default_Settings_004() {

		homePage.clickOnSettingsResetBtn();
	}

	@Test(priority = 2)
	public void SCH_Saving_Changes_Settings_005() {

		homePage.verifyGsaConnectedStatus(gsaUserName, gsaPassword);
	}

	@Test(priority = 3)
	public void SCH_Close_Settings_006() throws InterruptedException {

		homePage.clickOnSettingsCloseBtn();
	}

}
