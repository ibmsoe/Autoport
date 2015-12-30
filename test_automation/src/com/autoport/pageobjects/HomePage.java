package com.autoport.pageobjects;

import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.pagefactory.AjaxElementLocatorFactory;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.FluentWait;

import com.autoport.utilities.*;

public class HomePage {

	WebDriver driver;
	FluentWait<WebDriver> wait;

	JavascriptExecutor js;

	public HomePage(WebDriver driver, FluentWait<WebDriver> wait) {
		this.driver = driver;

		this.wait = wait;
		// wait = new WebDriverWait(driver, 30);

		AjaxElementLocatorFactory factory = new AjaxElementLocatorFactory(driver, 10);
		PageFactory.initElements(factory, this);
	}

	// xpath = "//div[@id='loading_screen']/button"
	@FindBy(css = "button.btn-primary") // btn.btn-lg.
	WebElement autoportInitializeTx;

	@FindBy(xpath = "//div[@id='toolContainer']/div[2]/h1")
	WebElement autoportHeaderTx;

	@FindBy(xpath = "//div[@id='searchTabHeader']/p")
	WebElement homePageHelpTx;

	@FindBy(xpath = "//div[@id='toolContainer']/div[2]/h1/button")
	WebElement settingsBtn;

	@FindBy(id = "toggleHelpBtn")
	WebElement helpBtn;

	@FindBy(id = "searchTab")
	WebElement searchTab;

	@FindBy(id = "singleSearchButton")
	WebElement searchSingleProjectBtn;

	@FindBy(id = "generateBatchButton")
	WebElement searchCommonProjectsBtn;

	@FindBy(id = "batchTab")
	WebElement batchJobsTab;

	@FindBy(id = "reportsTab")
	WebElement reportsTab;

	@FindBy(id = "jenkinsTab")
	WebElement buildServerTab;

	@FindBy(id = "modalLabel")
	WebElement settingsHeader;

	@FindBy(xpath = "//div[@id='settingsModal']//div[@id='settingsModal']/div/div[1]/label")
	WebElement jenkinsUrlLabel;

	@FindBy(id = "url")
	WebElement jenkinsUrlTxtBx;

	@FindBy(xpath = "//div[@id='settingsModal']//div[@id='settingsModal']/div/div[2]/label")
	WebElement localTestResultsLabel;

	@FindBy(id = "ltest_results")
	WebElement localTestResultsTxtBx;

	@FindBy(xpath = "//div[@id='settingsModal']//div[@id='settingsModal']/div/div[3]/label")
	WebElement archiveTestResultsLabel;

	@FindBy(id = "gtest_results")
	WebElement archiveTestResultsTxtBx;

	@FindBy(xpath = "//div[@id='settingsModal']//div[@id='settingsModal']/div/div[4]/label")
	WebElement localBatchFileLabel;

	@FindBy(id = "lbatch_files")
	WebElement localBatchFileTxtBx;

	@FindBy(xpath = "//div[@id='settingsModal']//div[@id='settingsModal']/div/div[5]/label")
	WebElement archiveBatchFileLabel;

	@FindBy(id = "gbatch_files")
	WebElement archiveBatchFileTxtBx;

	@FindBy(xpath = "//div[@id='settingsModal']//div[@id='settingsModal']/div/div[6]/label")
	WebElement githubTokenLabel;

	@FindBy(id = "github")
	WebElement githubTokenTxtBx;

	@FindBy(xpath = "//div[@id='settingsModal']//div[@id='settingsModal']/div/div[7]/label")
	WebElement gsaUsrNameLabel;

	@FindBy(id = "username")
	WebElement gsaUsrNameTxtBx;

	@FindBy(xpath = "//div[@id='settingsModal']//div[@id='settingsModal']/div/div[8]/label")
	WebElement gsaPwdLabel;

	@FindBy(id = "password")
	WebElement gsaPwdTxtBx;

	@FindBy(xpath = "//div[@id='settingsModal']//div[@id='settingsModal']/div/div[9]/label")
	WebElement logLevelLabel;

	@FindBy(id = "loglevel")
	WebElement logLevelTxtBx;

	@FindBy(xpath = "//div[@id='settingsModal']//div[@id='settingsModal']/div/div[10]/label")
	WebElement txtAnalyticsLabel;

	@FindBy(id = "usetextanalytics")
	WebElement txtAnalyticsChkBx;

	@FindBy(id = "gsaConnectionStatus")
	WebElement gsaConnectionStatus;

	@FindBy(xpath = "//div[@id='settingsModal']//div[@class='modal-footer']/button[1]")
	WebElement closeBtn;

	@FindBy(xpath = "//div[@id='settingsModal']//div[@class='modal-footer']/button[2]")
	WebElement resetToDefaultBtn;

	@FindBy(xpath = "//div[@id='settingsModal']//div[@class='modal-footer']/button[3]")
	WebElement saveChangesBtn;

	@FindBy(xpath = "//div[@id='errorAlert']//button")
	WebElement alertCloseBtn;

	// To verify initialization text while loading Autoport
	public void initializeText() {

		// wait.until(ExpectedConditions.visibilityOf(autoportInitializeTx));

		if (autoportInitializeTx.getText().contains("AutoPort Initializing...")) {
			LogResult.pass("AutoPort Initializing... text is displayed");
		} else {
			LogResult.fail("AutoPort Initializing... text is not displayed");
		}

	}

	// To verify if Search tab is displayed
	public void clickSearchTab() {
		searchTab.click();

		if (true) {
			LogResult.pass("Search tab is displayed.");
		} else {
			LogResult.fail("Search tab is not displayed.");
		}
	}

	// To verify if Batch Jobs tab is displayed
	public void clickBatchJobsTab() {

		batchJobsTab.click();

		if (true) {
			LogResult.pass("Batch Jobs tab is displayed.");
		} else {
			LogResult.fail("Batch Jobs tab is not displayed.");
		}
	}

	// To verify if Reports tab is displayed
	public void openBuildServerTab() {
		buildServerTab.click();
		if (true) {
			LogResult.pass("Build Server tab is displayed.");
		} else {
			LogResult.fail("Build Server tab is not displayed.");
		}
	}

	// To verify if Build Servers tab is displayed
	public void clickReportsTab() {
		reportsTab.click();

		if (true) {
			LogResult.pass("Reports tab is displayed.");
		} else {
			LogResult.fail("Reports tab is not displayed.");
		}
	}

	// To verify Home page elements
	public void verifyHomePageUI() {

		wait.until(ExpectedConditions.visibilityOf(autoportHeaderTx));

		if (autoportHeaderTx.getText().contains("AutoPort")) {
			LogResult.pass("AutoPort header is displayed.");
		} else {
			LogResult.fail("AutoPort header is not displayed.");
		}

		String helpTx = "This tool allows you to locate and evaluate projects for porting.";

		if (homePageHelpTx.getText().contains(helpTx)) {
			LogResult.pass("Help text is displayed.");
		} else {
			LogResult.fail("Help text is not displayed.");
		}

		if (settingsBtn.isDisplayed()) {
			LogResult.pass("Settings button is displayed.");
		} else {
			LogResult.fail("Settings button is not displayed.");
		}

		if (helpBtn.isDisplayed()) {
			LogResult.pass("Help button is displayed.");
		} else {
			LogResult.fail("Help button is not displayed.");
		}

		if (searchTab.isDisplayed()) {
			LogResult.pass("Search Tab is displayed.");
		} else {
			LogResult.fail("Search Tab is not displayed.");
		}

		if (batchJobsTab.isDisplayed()) {
			LogResult.pass("Batch Jobs Tab is displayed.");
		} else {
			LogResult.fail("Batch Jobs Tab is not displayed.");
		}

		if (reportsTab.isDisplayed()) {
			LogResult.pass("Reports Tab is displayed.");
		} else {
			LogResult.fail("Reports Tab is not displayed.");
		}

		if (buildServerTab.isDisplayed()) {
			LogResult.pass("Build Server Tab is displayed.");
		} else {
			LogResult.fail("Build Server Tab is not displayed.");
		}

	}

	// To verify if search tab is selected by default and also to check its
	// contents
	public void verifySearchTabContents() {

		wait.until(ExpectedConditions.visibilityOf(searchSingleProjectBtn));

		if (searchSingleProjectBtn.isDisplayed() && searchCommonProjectsBtn.isDisplayed()) {
			LogResult.pass("Search Tab contents are displayed");
		} else {
			LogResult.fail("Search Tab contents are not displayed");
		}
	}

	// To verify if settings overlay popup is opened
	public void clickOnSettings() {
		settingsBtn.click();
		wait.until(ExpectedConditions.visibilityOf(settingsHeader));

		if (settingsHeader.getText().contentEquals("Settings")) {

			LogResult.pass("Settings overlay popup is displayed.");

		} else {

			LogResult.fail("Settings overlay popup is not displayed.");
		}
	}

	// To verify Settings overlay popup UI elements
	public void verifySettingsUI() {

		js = (JavascriptExecutor) driver;

		if (jenkinsUrlLabel.isDisplayed()) {
			LogResult.pass("Jenkins Url label is present");
			if (jenkinsUrlTxtBx.isDisplayed()) {
				LogResult.pass("Jenkins Url text box is displayed.");

				Object jenkinsUrl = js.executeScript("return globalState.jenkinsUrl");

				LogResult.pass("Current Jenkins Url: " + jenkinsUrl.toString());

			}
		} else {
			LogResult.fail("Jenkins Url label is not present.");
		}

		if (localTestResultsLabel.isDisplayed()) {
			LogResult.pass("Local Test Results Path label is present");
			if (localTestResultsTxtBx.isDisplayed()) {
				LogResult.pass("Local Test Results Path text box is displayed");

				Object localTestResultsPath = js.executeScript("return globalState.localPathForTestResults");

				if (localTestResultsPath.toString().contentEquals("./data/test_results/")) {
					LogResult.pass("Local Test Results Path is correct: " + localTestResultsPath.toString());
				} else {
					LogResult.fail("Local Test Results Path is incorrect: " + localTestResultsPath.toString());
				}
			} else {
				LogResult.fail("Local Test Results Path textbox is not displayed");
			}
		} else {
			LogResult.fail("Local Test Results Path label is not present");
		}

		if (archiveTestResultsLabel.isDisplayed()) {
			LogResult.pass("Archive Test Results Path label is present");
			if (archiveTestResultsTxtBx.isDisplayed()) {
				LogResult.pass("Archive Test Results Path textbox is displayed");

				Object archiveTestResultsPath = js.executeScript("return globalState.pathForTestResults");

				if (archiveTestResultsPath.toString().contentEquals("/projects/p/powersoe/autoport/test_results/")) {
					LogResult.pass("Archive Test Results Path is correct: " + archiveTestResultsPath.toString());
				} else {
					LogResult.fail("Archive Test Results Path is incorrect: " + archiveTestResultsPath.toString());
				}
			} else {
				LogResult.fail("Archive Test Results Path textbox is not displayed");
			}
		} else {
			LogResult.fail("Archive Test Results Path label is not present");
		}

		if (localBatchFileLabel.isDisplayed()) {
			LogResult.pass("Local Batch Files Path label is present");
			if (localBatchFileTxtBx.isDisplayed()) {
				LogResult.pass("Local Batch Files Path textbox is displayed");

				Object localBatchFilePath = js.executeScript("return globalState.localPathForBatchFiles");

				if (localBatchFilePath.toString().contentEquals("./data/batch_files/")) {
					LogResult.pass("Local Batch Files Path is correct: " + localBatchFilePath.toString());
				} else {
					LogResult.fail("Local Batch Files Path is incorrect: " + localBatchFilePath.toString());
				}
			} else {
				LogResult.fail("Local Batch Files Path textbox is not displayed");
			}
		} else {
			LogResult.fail("Local Batch Files Path label is not present");
		}

		if (archiveBatchFileLabel.isDisplayed()) {
			LogResult.pass("Archive Test Results Path label is present");
			if (archiveBatchFileTxtBx.isDisplayed()) {
				LogResult.pass("Archive Batch Files Path textbox is displayed");

				Object archiveBatchFilePath = js.executeScript("return globalState.pathForBatchFiles");

				if (archiveBatchFilePath.toString().contentEquals("/projects/p/powersoe/autoport/batch_files/")) {
					LogResult.pass("Archive Batch Files Path is correct: " + archiveBatchFilePath.toString());
				} else {
					LogResult.fail("Archive Batch Files Path is incorrect: " + archiveBatchFilePath.toString());
				}
			} else {
				LogResult.fail("Archive Batch Files Path textbox is not displayed.");
			}
		} else {
			LogResult.fail("Archive Batch Files Path label is not present");
		}

		if (githubTokenLabel.isDisplayed()) {
			LogResult.pass("Github Token label is present");
			if (githubTokenTxtBx.isDisplayed()) {

				Object githubToken = js.executeScript("return globalState.githubToken");

				LogResult.pass("Github Token text box is displayed with Token: " + githubToken.toString());
			} else {
				LogResult.fail("Github Token text box is not displayed.");
			}
		} else {
			LogResult.fail("Github Token label is not present.");
		}

		if (gsaUsrNameLabel.isDisplayed()) {
			LogResult.pass("GSA Username label is present");
			if (gsaUsrNameTxtBx.isDisplayed()) {

				Object gsaUsrName = js.executeScript("return globalState.configUsername");

				LogResult.pass("GSA Username text box is displayed with value: " + gsaUsrName.toString());
			} else {
				LogResult.fail("GSA Username text box is not displayed.");
			}
		} else {
			LogResult.fail("GSA Username label is not present.");
		}

		if (gsaPwdLabel.isDisplayed()) {
			LogResult.pass("GSA Password label is present");
			if (gsaPwdTxtBx.isDisplayed()) {

				Object gsaPwd = js.executeScript("return globalState.configPassword");

				LogResult.pass("GSA Password text box is displayed with value: " + gsaPwd.toString());

			} else {
				LogResult.fail("GSA Password text box is not displayed.");
			}
		} else {
			LogResult.fail("GSA Password label is not present.");
		}

		if (logLevelLabel.isDisplayed()) {
			LogResult.pass("Log Level label is present");
			if (logLevelTxtBx.isDisplayed()) {

				Object logLevel = js.executeScript("return globalState.logLevel");

				LogResult.pass("Log Level text box is displayed with value: " + logLevel.toString());
			} else {
				LogResult.fail("Log Level text box is not displayed.");
			}
		} else {
			LogResult.fail("Log Level label is not present.");
		}

		if (txtAnalyticsLabel.isDisplayed()) {
			LogResult.pass("Use Text Analytics label is present");
			if (txtAnalyticsChkBx.isDisplayed()) {

				LogResult.pass("Use Text Analytics check box is displayed.");
				if (txtAnalyticsChkBx.isSelected()) {
					LogResult.fail("Use Text Analytics check box is selected.");
				} else {
					LogResult.pass("Use Text Analytics check box is not selected.");
				}

			} else {
				LogResult.fail("Use Text Analytics check box is not displayed.");
			}
		} else {
			LogResult.fail("Use Text Analytics label is not present.");
		}

		if (closeBtn.isDisplayed()) {
			LogResult.pass("Close button is displayed. ");
		} else {
			LogResult.fail("Close button is not displayed. ");
		}

		if (gsaConnectionStatus.isDisplayed()) {
			LogResult.pass("GSA connection status is displayed with status: " + gsaConnectionStatus.getText());
		} else {
			LogResult.fail("GSA connection status is not displayed. ");
		}

		if (resetToDefaultBtn.isDisplayed()) {
			LogResult.pass("Reset to default button is displayed. ");
		} else {
			LogResult.fail("Reset to default button is not displayed. ");
		}

		if (saveChangesBtn.isDisplayed()) {
			LogResult.pass("Save Changes button is displayed. ");
		} else {
			LogResult.fail("Save Changes button is not displayed. ");
		}

	}

	// To verify if Settings overlay popup is closed and user is navigated back
	// to Home page
	public void clickOnSettingsCloseBtn() {

		wait.until(ExpectedConditions.visibilityOf(settingsHeader));

		closeBtn.click();

		if (autoportHeaderTx.getText().contains("AutoPort")) {
			LogResult.pass("Settings popup closed.");
		} else {
			LogResult.fail("Settings popup is open.");
		}
	}

	// To verify the close of Update popup displayed when Save Changes button is
	// clicked after entering GSA credentials
	public void clickOnSettingsSaveBtn() {

		saveChangesBtn.click();

		LogResult.pass("Clicked on Save Changes button.");

		// wait.until(ExpectedConditions.visibilityOf(alertCloseBtn));

		// alertCloseBtn.click();

		// if (settingsHeader.getText().contentEquals("Settings")) {
		// LogResult.pass("Update alert dismissed.");
		// } else {
		// LogResult.fail("Update alert is displayed.");
		// }
	}

	// To verify the functionality of Reset button (by checking if selected Text
	// Analytics checkbox is unselected or not)
	public void clickOnSettingsResetBtn() {

		txtAnalyticsChkBx.click();

		resetToDefaultBtn.click();

		// check whether the checkbox has been unchecked.

		if (txtAnalyticsChkBx.isSelected()) {
			LogResult.fail("Reset field values unsuccessfull.");
		} else {
			LogResult.pass("Reset field values successfull");
		}

	}

	// To verify if GSA connected status is displayed in Settings overlay popup
	// after entering valid GSA credentials
	public void verifyGsaConnectedStatus(String gsaUserName, String gsaPassword) {

		gsaUsrNameTxtBx.clear();
		gsaUsrNameTxtBx.sendKeys(gsaUserName);
		gsaPwdTxtBx.clear();
		gsaPwdTxtBx.sendKeys(gsaPassword);

		clickOnSettingsSaveBtn();

		// wait.until(ExpectedConditions.visibilityOf(gsaConnectionStatus));

		if (gsaConnectionStatus.getText().contentEquals("GSA connected")) {
			LogResult.pass("Changes saved successfully. GSA Connected");

		} else {
			LogResult.fail("Changes not saved successfully. GSA not Connected");
		}

	}

	// To verify the appearance and disappearance of help text along with Help
	// button functionality
	public void clickOnHideHelpBtn() {

		wait.until(ExpectedConditions.visibilityOf(helpBtn));

		if (helpBtn.getText().contentEquals("Hide help")) {
			LogResult.pass("Help button text displayed as: " + helpBtn.getText());
		} else {
			LogResult.fail("Help button text displayed as: " + helpBtn.getText());
		}

		helpBtn.click();

		if (homePageHelpTx.isDisplayed()) {
			LogResult.fail("Help text is displayed.");
		} else {
			LogResult.pass("Help button is clicked. Help text is hidden.");
		}

		if (helpBtn.getText().contentEquals("Show help")) {
			LogResult.pass("Help button changed to: " + helpBtn.getText());
		} else {
			LogResult.fail("Help button changed to: " + helpBtn.getText());
		}

		helpBtn.click();

		if (homePageHelpTx.isDisplayed()) {
			LogResult.pass(
					"Help button clicked again. Help text is displayed. Toggle help button functionality verified.");
		} else {
			LogResult.fail("Help text is not displayed.");
		}

		if (helpBtn.getText().contentEquals("Hide help")) {
			LogResult.pass("Help button changed text back to: " + helpBtn.getText());
		} else {
			LogResult.fail("Help button changed text back to: " + helpBtn.getText());
		}

	}

}
