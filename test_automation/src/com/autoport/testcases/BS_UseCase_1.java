package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class BS_UseCase_1 {
    WebDriver driver;
    CommonFunctions functions;
    HomePage homePage;
    BuildServersTab buildServerTab;
    String jenkinsUrl;

     @BeforeTest
      public void beforeTest() throws Exception {

         //CommonFunctions.launchBrowser();
         driver = CommonFunctions.driver;
         homePage = CommonFunctions.homePage;
         buildServerTab = CommonFunctions.buildServerTab;
         jenkinsUrl = ReadTestData.readParameter("BS_UseCase_1", "JenkinsUrl");

         homePage.openBuildServerTab();
      }

     @Test(priority=0)
     public void BS_View_Jenkins_Status_001() throws Exception{

         buildServerTab.openShowJenkinsStatusSection();

         buildServerTab.verifyJenkinsPageUrl(jenkinsUrl);

         buildServerTab.clickCheckProgressBtn();

         buildServerTab.verifyJenkinsStatus();

         buildServerTab.VerifyProgressBar();

         buildServerTab.closeShowJenkinsStatusSection();
     }
}
