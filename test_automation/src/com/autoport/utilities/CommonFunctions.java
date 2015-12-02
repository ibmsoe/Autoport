package com.autoport.utilities;

import java.io.File;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.concurrent.TimeUnit;

import org.apache.commons.io.FileUtils;
import org.openqa.selenium.By;
import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.Platform;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxProfile;
import org.openqa.selenium.firefox.internal.ProfilesIni;
import org.openqa.selenium.ie.InternetExplorerDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import org.openqa.selenium.remote.RemoteWebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Reporter;

import com.autoport.pageobjects.BatchJobsTab;
import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.pageobjects.SearchTab;

public class CommonFunctions {

	public WebDriver driver;

	public FluentWait<WebDriver> fluentWait;
	public WebDriverWait explicitWait;

	public HomePage homePage;
	public SearchTab searchTab;
	public BuildServersTab buildServerTab;
	public BatchJobsTab batchJobsTab;
	public ReportsTab reportsTab;

	public void launchBrowser(String browser) throws Exception {

		String userDir = System.getProperty("user.dir");

		if (browser.equalsIgnoreCase("Firefox")) {

			FirefoxProfile ffProfile = new FirefoxProfile();
			ffProfile.setPreference("browser.helperApps.neverAsk.saveToDisk", "text/plain");
			driver = new FirefoxDriver(ffProfile);

			/*
			 * DesiredCapabilities capability = DesiredCapabilities.firefox();
			 * capability.setBrowserName("firefox"); driver = new
			 * FirefoxDriver(capability);
			 */

		} else if (browser.equalsIgnoreCase("chrome")) {

			System.setProperty("webdriver.chrome.driver", userDir + "/Drivers/chromedriver.exe");
			driver = new ChromeDriver();
		} else if (browser.equalsIgnoreCase("IE")) {

			System.setProperty("webdriver.ie.driver", userDir + "/Drivers/IEDriverServer.exe");
			driver = new InternetExplorerDriver();
		}

		driver.manage().timeouts().implicitlyWait(10, TimeUnit.SECONDS);
		driver.manage().window().maximize();
		explicitWait = new WebDriverWait(driver, 30);
		fluentWait = new FluentWait<WebDriver>(driver).withTimeout(60, TimeUnit.SECONDS)
				.pollingEvery(5, TimeUnit.SECONDS).ignoring(NoSuchElementException.class);

		homePage = new HomePage(driver, fluentWait);
		searchTab = new SearchTab(driver, fluentWait);
		batchJobsTab = new BatchJobsTab(driver, fluentWait);
	    reportsTab = new ReportsTab(driver, fluentWait);
		buildServerTab = new BuildServersTab(driver, fluentWait);
		
	
	}

	public void openAutoport() {

		driver.get("http://10.44.189.55:5600/autoport/");
	}
	
	public void goTo_ListInstallSingleSoftwarSection(){
		
		 homePage.clickBuildServerTab();
		  
		 buildServerTab.clickManageJenkinsSlaveNodesBtnToOpen();
		  
		 buildServerTab.clickmanageSingleSlaveButtonToOpen();	
	}

}
