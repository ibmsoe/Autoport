package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeSuite;
import org.testng.annotations.AfterSuite;
import com.autoport.utilities.CommonFunctions;

public class Initialize {

    public WebDriver driver;

    @BeforeSuite
    public void beforeSuite() throws Exception {

     CommonFunctions.launchBrowser();
     driver = CommonFunctions.driver;
  }

      @AfterSuite
      public void afterSuite() {
          driver.quit();
      }

}
