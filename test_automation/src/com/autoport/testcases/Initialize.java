package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.AfterSuite;
import org.testng.annotations.BeforeSuite;

import com.autoport.utilities.CommonFunctions;

public class Initialize {

	public WebDriver driver;

	@BeforeSuite
	public void beforeTest() throws Exception {

		CommonFunctions.launchBrowser();
		driver = CommonFunctions.driver;

	}

	@AfterSuite
	public void afterTest() {
		driver.quit();
	}

}
