package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.CommonFunctions;

public class SCH_Use_Case_3 {

    WebDriver driver;

    HomePage homePage;

    @BeforeTest
    public void beforeTest() throws Exception {

        // CommonFunctions.launchBrowser();
        driver = CommonFunctions.driver;
        homePage = CommonFunctions.homePage;

    }

    @Test
    public void SCH_Hide_Help_007() {
        homePage.clickOnHideHelpBtn();
    }

}
