package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BatchJobsTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.CommonFunctions;

public class BJ_Use_Case_001 {

    WebDriver driver;

    HomePage homePage;
    BatchJobsTab batchJobsTab;

    @BeforeTest
    public void beforeTest() throws Exception {

        // CommonFunctions.launchBrowser();

        driver = CommonFunctions.driver;
        homePage = CommonFunctions.homePage;
        batchJobsTab = CommonFunctions.batchJobsTab;

        homePage.clickBatchJobsTab();
    }

    @Test
    public void BJ_Batch_Jobs_UI_001() {

        batchJobsTab.verifyBatchJobsTabUI();

    }


}
