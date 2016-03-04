package com.autoport.utilities;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;

import java.util.Properties;
import java.util.concurrent.TimeUnit;

import org.openqa.selenium.NoSuchElementException;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxProfile;
import org.openqa.selenium.firefox.internal.ProfilesIni;
import org.openqa.selenium.ie.InternetExplorerDriver;
import org.openqa.selenium.remote.CapabilityType;
import org.openqa.selenium.remote.DesiredCapabilities;
import org.openqa.selenium.remote.RemoteWebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.openqa.selenium.support.ui.WebDriverWait;

import com.autoport.pageobjects.BatchJobsTab;
import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.pageobjects.SearchTab;

public class CommonFunctions {

    public static WebDriver driver;

    public static FluentWait<WebDriver> fluentWait;
    public static WebDriverWait explicitWait;

    public static HomePage homePage;
    public static SearchTab searchTab;
    public static BuildServersTab buildServerTab;
    public static BatchJobsTab batchJobsTab;
    public static ReportsTab reportsTab;

    public static void launchBrowser() throws Exception {

        try {

            Properties prop = new Properties();
            String userDir = System.getProperty("user.dir");
            String filePath = userDir + "/config.properties";

            InputStream is = new FileInputStream(filePath);

            prop.load(is);

            String url = prop.getProperty("URL");
            String browser = prop.getProperty("browser");
            long implicitWaitTime = Integer.parseInt(prop.getProperty("implicitWait"));
            long explicitWaitTime = Integer.parseInt(prop.getProperty("explicitWait"));
            long fluentWaitTime = Integer.parseInt(prop.getProperty("fluentWait"));

            /*String proxyurl = prop.getProperty("proxy");
            String port = prop.getProperty("port");

            String PROXY = proxyurl + ":" + port;

            Proxy proxy = new Proxy();
            proxy.setHttpProxy(PROXY).setFtpProxy(PROXY).setSslProxy(PROXY).setSocksProxy(PROXY)
                    .setNoProxy("*.ibm.com");*/

            if (browser.equalsIgnoreCase("Firefox")) {

                FirefoxProfile ffProfile = new FirefoxProfile();

                /*ProfilesIni allProfiles = new ProfilesIni();
                FirefoxProfile ffProfile = allProfiles.getProfile("default");*/
                ffProfile.setAcceptUntrustedCertificates(true);
                ffProfile.setAssumeUntrustedCertificateIssuer(true);
                ffProfile.setEnableNativeEvents(true);

                ffProfile.setPreference("browser.download.folderList", 1);
                ffProfile.setPreference("browser.helperApps.neverAsk.openFile","text/plain");
                ffProfile.setPreference("browser.helperApps.neverAsk.saveToDisk", "text/plain");
                ffProfile.setPreference("browser.helperApps.alwaysAsk.force", false);
                /*ffProfile.setPreference("privacy.popups.policy", true);
                ffProfile.setPreference("browser.popups.showPopupBlocker", false);*/

                driver = new FirefoxDriver(ffProfile);

            } else if (browser.equalsIgnoreCase("chrome")) {

                System.setProperty("webdriver.chrome.driver", userDir + "/Drivers/chromedriver.exe");

                ChromeOptions options = new ChromeOptions();
                options.addArguments("test-type");
                options.addArguments("--disable-popup-blocking");
                DesiredCapabilities capabilities = DesiredCapabilities.chrome();
                capabilities.setCapability(ChromeOptions.CAPABILITY, options);

                driver = new ChromeDriver(capabilities);

            } else if (browser.equalsIgnoreCase("IE")) {

                System.setProperty("webdriver.ie.driver", userDir + "/Drivers/IEDriverServer.exe");
                driver = new InternetExplorerDriver();
            }

            driver.manage().timeouts().implicitlyWait(implicitWaitTime, TimeUnit.SECONDS);
            driver.manage().window().maximize();
            explicitWait = new WebDriverWait(driver, explicitWaitTime);
            fluentWait = new FluentWait<WebDriver>(driver).withTimeout(fluentWaitTime, TimeUnit.SECONDS)
                    .pollingEvery(5, TimeUnit.SECONDS).ignoring(NoSuchElementException.class);

            homePage = new HomePage(driver, fluentWait);
            searchTab = new SearchTab(driver, fluentWait);
            batchJobsTab = new BatchJobsTab(driver, fluentWait);
            reportsTab = new ReportsTab(driver, fluentWait);
            buildServerTab = new BuildServersTab(driver, fluentWait);

            driver.get(url);

        } catch (FileNotFoundException ex) {
            ex.printStackTrace();
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }

    public static void goTo_ListInstallSingleSoftwarSection() {

        homePage.openBuildServerTab();

        buildServerTab.clickManageJenkinsSlaveNodesBtnToOpen();

        buildServerTab.clickListInstallRemoveSoftwareBtnToOpen();
    }

    public static void goTo_ListInstallUsingManagedServicesSection() {

        homePage.openBuildServerTab();

        buildServerTab.clickManageJenkinsSlaveNodesBtnToOpen();

        buildServerTab.clickListInstallRemoveSoftwareUsingManagedServicesBtnToOpen();
    }

    public static void goTo_ShowCleanSlavesUsingManagedServicesSection() {

        homePage.openBuildServerTab();

        buildServerTab.clickManageJenkinsSlaveNodesBtnToOpen();

        buildServerTab.clickShowCleanBuildSlavesUsingManagedServicesBtnToOpen();

    }

    public static void goTo_UploadPackageToRepositorySection() {

        homePage.openBuildServerTab();

        buildServerTab.clickuploadPackagesToRepositoryBtnToOpen();
    }

}
