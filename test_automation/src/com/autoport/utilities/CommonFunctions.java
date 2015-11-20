package com.autoport.utilities;

import java.util.concurrent.TimeUnit;

import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxProfile;
import org.openqa.selenium.firefox.internal.ProfilesIni;
import org.openqa.selenium.ie.InternetExplorerDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.openqa.selenium.support.ui.WebDriverWait;

import com.autoport.pageobjects.*;

public class CommonFunctions {
	
	public WebDriver driver;
	public FluentWait<WebDriver> fluentWait;
	public WebDriverWait explicitWait;
	
	public HomePage homePage;
	public SearchTab searchTab;
	public BuildServersTab buildServerTab;	
	public BatchJobsTab batchJobsTab;
	public ReportsTab reportsTab;	
	
	public void launchBrowser(String browser) throws Exception{
		
		String uesrDir = System.getProperty("user.dir");
	
		if (browser.equalsIgnoreCase("Firefox")) {
			
			  ProfilesIni ffprofile = new ProfilesIni();
              FirefoxProfile autoprofile = ffprofile.getProfile("AutoPortFirefox");
              driver = new FirefoxDriver(autoprofile);

			/*DesiredCapabilities capability = DesiredCapabilities.firefox();
			 capability.setBrowserName("firefox");				
			 driver = new FirefoxDriver(capability);*/
		} 
		
	 	else if (browser.equalsIgnoreCase("chrome")) {
	 		
			System.setProperty("webdriver.chrome.driver", uesrDir + "/drivers/chromedriver.exe");
			driver =  new ChromeDriver();
		}
		
	 	else if (browser.equalsIgnoreCase("IE")) {
	 		
			System.setProperty("webdriver.ie.driver", uesrDir + "/drivers/IEDriverServer.exe");
			driver = new InternetExplorerDriver();
		}
		
		driver.manage().timeouts().implicitlyWait(10, TimeUnit.SECONDS);
		driver.manage().window().maximize();		  
		explicitWait  = new WebDriverWait(driver, 20);
		fluentWait = new FluentWait<WebDriver>(driver).withTimeout(40,TimeUnit.SECONDS).pollingEvery(5, TimeUnit.SECONDS).ignoring(NoSuchElementException.class);
	  
		homePage = new HomePage(driver, fluentWait);
		buildServerTab = new BuildServersTab(driver, fluentWait);
		searchTab = new SearchTab(driver, fluentWait);		
	}
	
	public void openAutoport(){
		
		driver.get("http://10.44.189.55:5601/autoport/");
	}
	
	public void goTo_ListInstallSingleSoftwarSection(){
		
		 homePage.clickBuildServerTab();
		  
		 buildServerTab.clickManageJenkinsSlaveNodesBtnToOpen();
		  
		 buildServerTab.clickmanageSingleSlaveButtonToOpen();	
	}

}

