package com.autoport.pageobjects;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Set;

import org.openqa.selenium.Alert;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.pagefactory.AjaxElementLocatorFactory;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.FluentWait;

import com.autoport.utilities.LogResult;

public class BatchJobsTab {

	WebDriver driver;
	FluentWait<WebDriver> wait;

	private String buildClickTime;

	private int selectedBuildServersCount;

	public BatchJobsTab(WebDriver driver, FluentWait<WebDriver> wait) {

		this.driver = driver;
		this.wait = wait;

		AjaxElementLocatorFactory factory = new AjaxElementLocatorFactory(driver, 10);
		PageFactory.initElements(factory, this);
	}

	@FindBy(xpath = "//div[@id='batchTabHeader']/p[1]")
	WebElement batchJobHelpTx;

	@FindBy(xpath = "//div[@id='batchPanel']/div[1]/div[1]")
	WebElement importBtn;

	@FindBy(id = "uploadFilename")
	WebElement uploadFileDisplayBox;

	@FindBy(xpath = "/html/body/div[2]/div[3]/div/div[2]/div[1]/div[2]/div[1]/div/input")
	WebElement selectFileBtn;

	@FindBy(xpath = "//div[@id='batchPanel']/div[1]/div[2]/div[2]/div")
	WebElement uploadBtn;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[1]")
	WebElement listSelectBtn;

	@FindBy(id = "batchFileFilter")
	WebElement batchFileTbx;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/div[1]/div[2]/div[1]")
	WebElement listLocalBtn;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/div[1]/div[2]/div[2]")
	WebElement listArchivedBtn;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/div[1]/div[2]/div[3]")
	WebElement listAllBtn;

	@FindBy(xpath = "//div[@id='batchListSelectToolbar']/a[1]/button")
	WebElement listDetailsBtn;

	@FindBy(xpath = "//div[@id='batchListSelectToolbar']/div/button")
	WebElement listBuildServersBtn;

	@FindBy(xpath = "//div[@id='batchListSelectToolbar']/div/ul//label")
	List<WebElement> listBuildServersNodes;

	@FindBy(xpath = "//div[@id='batchListSelectToolbar']//li//input")
	List<WebElement> listBuildServersChkbx;

	@FindBy(xpath = "//div[@id='batchListSelectToolbar']/a[2]/button")
	WebElement listBuildAndTestBtn;

	@FindBy(xpath = "//div[@id='batchListSelectToolbar']/a[3]/button")
	WebElement listArchiveBtn;

	@FindBy(xpath = "//div[@id='batchListSelectToolbar']/a[4]/button")
	WebElement listRemoveBtn;

	@FindBy(id = "batchListSelectTable")
	WebElement batchFilesPanel;

	@FindBy(xpath = "//table[@id='batchListSelectTable']//th[2]/div[1]")
	WebElement listNameTableHeader;

	@FindBy(xpath = "//table[@id='batchListSelectTable']//th[3]/div[1]")
	WebElement listLocationTableHeader;

	@FindBy(xpath = "//table[@id='batchListSelectTable']//th[4]/div[1]")
	WebElement listEnvironmentTableHeader;

	@FindBy(xpath = "//table[@id='batchListSelectTable']//th[5]/div[1]")
	WebElement listOwnerTableHeader;

	@FindBy(xpath = "//table[@id='batchListSelectTable']//th[6]/div[1]")
	WebElement listSizeTableHeader;

	@FindBy(xpath = "//table[@id='batchListSelectTable']//th[7]/div[1]")
	WebElement listDateModifiedTableHeader;

	@FindBy(xpath = "//table[@id='batchListSelectTable']/tbody/tr[1]/td[1]/input")
	WebElement firstRowCheckbx;

	@FindBy(xpath = "//table[@id='batchListSelectTable']/tbody/tr[1]/td[2]")
	WebElement firstRowLocalBatchFileName;

	@FindBy(xpath = "//table[@id='batchListSelectTable']/tbody/tr[1]/td[3]")
	WebElement firstRowLocalBatchFileLocation;

	@FindBy(xpath = "//table[@id='batchListSelectTable']/tbody/tr[1]/td[7]")
	WebElement firstRowLocalBatchFileDate;

	@FindBy(xpath = "//table[@id='batchListSelectTable']/tbody/tr")
	List<WebElement> listNoRows;

	@FindBy(xpath = "//table[@id='batchListSelectTable']/tbody/tr/td[2]")
	List<WebElement> listBatchFileNameColumnValues;

	@FindBy(xpath = "//table[@id='batchListSelectTable']/tbody/tr/td[3]")
	List<WebElement> listLocationColumnValues;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/div[2]/div[1]/div[2]/div[4]/div[1]/span[1]")
	WebElement numOfRowsShowingTx;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/div[2]/div[1]/div[2]/div[4]/div[1]/span[2]/span/button")
	WebElement currentRecordsPerPage;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/div[2]/div[1]/div[2]/div[4]/div[1]/span[2]/span//li/a")
	List<WebElement> recordsPerPageValues;

	@FindBy(xpath = "div[@id='batchPanel']/div[2]/div[2]/div[2]/div[1]/div[2]/div[4]/div[1]/span[2]")
	WebElement recordsPerPageTx;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/div[5]")
	WebElement batchFileDetailsPanel;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/div[5]/span/div[1]")
	WebElement detailsHelpTxt;

	@FindBy(id = "saveBatchFileFilter")
	WebElement saveDetailsTbx;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/div[5]/span/div[2]/a[1]/button")
	WebElement saveDetailsBtn;

	// @FindBy(xpath =
	// "//div[@id='batchPanel']/div[2]/div[2]/div[5]/span/div[2]/div[2]/button")
	// WebElement detailBuildServersBtn;

	// @FindBy(xpath =
	// "//div[@id='batchPanel']/div[2]/div[2]/div[5]/span/div[2]/a[2]/button")
	// WebElement detailBuildAndTestBtn;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/div[5]/span/div[3]/a/button")
	WebElement detailBackBtn;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[1]//th[1]")
	WebElement batchConfigFileNameHeader;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[1]//td[1]")
	WebElement batchConfigFileName;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[1]//th[2]")
	WebElement batchConfigOwnerHeader;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[1]//td[2]")
	WebElement batchConfigOwner;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[1]//th[3]")
	WebElement batchConfigJavaHeader;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[1]//td[3]")
	WebElement batchConfigJava;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[1]//th[4]")
	WebElement batchConfigJsHeader;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[1]//td[4]")
	WebElement batchConfigJs;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[1]//th[5]")
	WebElement batchConfigActionsHeader;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[1]//td[5]/button")
	WebElement batchConfigSettingsBtn;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]//th[1]")
	WebElement batchRepoNameHeader;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]//th[2]")
	WebElement batchRepoVersionHeader;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]//th[3]")
	WebElement batchRepoActionsHeader;

	// Up button for all repositories in batch file
	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]//td[3]/a[1]/button")
	WebElement batchRepoUpArrowBtn;

	// Down button for all repositories in batch file
	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]//td[3]/a[2]/button")
	WebElement batchRepoDownArrowBtn;

	// Remove button for all repositories in batch file
	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]//td[3]/a[3]/button")
	WebElement batchRepoCrossBtn;

	// First repository name in batch file
	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]/tbody[1]/tr/td[1]")
	WebElement batchFirstRepoName;

	// Up(Arrow) button for first repository in batch file
	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]/tbody[1]//td[3]/a[1]/button")
	WebElement batchFirstRepoUpBtn;

	// Down(Arrow) button for first repository in batch file
	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]/tbody[1]//td[3]/a[2]/button")
	WebElement batchFirstRepoDownBtn;

	// Remove(Cross) button for first repository in batch file
	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]/tbody[1]//td[3]/a[3]/button")
	WebElement batchFirstRepoRemoveBtn;

	// Second repository name in batch file
	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]/tbody[2]/tr/td[1]")
	WebElement batchSecondRepoName;

	// Up(Arrow) button for Second repository in batch file
	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]/tbody[2]//td[3]/a[1]/button")
	WebElement batchSecondRepoUpBtn;

	// Down(Arrow) button for Second repository in batch file
	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]/tbody[2]//td[3]/a[2]/button")
	WebElement batchSecondRepoDownBtn;

	// Remove(Cross) button for Second repository in batch file
	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]/tbody[2]//td[3]/a[3]/button")
	WebElement batchSecondRepoRemoveBtn;

	@FindBy(id = "batch_file_archive")
	WebElement batchFileArchiveBtn;

	@FindBy(xpath = "//div[@id='errorAlert']/div/div/div[1]")
	WebElement alertMessage;

	@FindBy(xpath = "//div[@id='errorAlert']//button")
	WebElement alertCloseBtn;

	@FindBy(xpath = "//table[@id='batchListSelectTable']/tbody/tr/td")
	WebElement noRecordsFound;

	@FindBy(xpath = "//div[@id='settingsBatchModal']//h2")
	WebElement batchConfigSettingsHeader;

	@FindBy(xpath = "//div[@id='settingsBatchModal1']/div/div[1]//h4")
	WebElement batchConfigSettingsEnvironmentHeader;

	@FindBy(xpath = "//div[@id='settingsBatchModal1']/div/div[4]//h4")
	WebElement batchConfigSettingsOptionsHeader;

	@FindBy(xpath = "//div[@id='settingsBatchModal1']/div/div[2]/div/div[1]//button")
	WebElement batchConfigSettingsJDK;

	@FindBy(xpath = "//div[@id='settingsBatchModal1']/div/div[2]/div/div[2]//button")
	WebElement batchConfigSettingsJs;

	// Changed as per new UI
	// @FindBy(xpath = "//div[@id='settingsBatchModal']/div/div/div[2]//li/a")
	// List<WebElement> batchConfigSettingsJDKValues;

	@FindBy(xpath = "//div[@id='settingsBatchModal1']/div/div[2]/div/div[1]//a")
	List<WebElement> batchConfigSettingsJDKValues;

	@FindBy(xpath = "//div[@id='settingsBatchModal1']/div/div[2]/div/div[1]//li[1]/a")
	WebElement batchConfigSettingsOpenJDK7; // batchConfigSettingsOpenJDK

	@FindBy(xpath = "//div[@id='settingsBatchModal1']/div/div[2]/div/div[1]//li[4]/a")
	WebElement batchConfigSettingsOpenJDK8; // batchConfigSettingsIBMJDK

	@FindBy(xpath = "//div[@id='settingsBatchModal1']/div/div[2]/div/div[2]//a")
	List<WebElement> batchConfigSettingsNodeJsValues;

	@FindBy(xpath = "//div[@id='settingsBatchModal1']/div/div[2]/div/div[2]//li[1]/a")
	WebElement batchConfigSettingsNodeJs;

	@FindBy(xpath = "//div[@id='settingsBatchModal1']/div/div[2]/div/div[2]//li[2]/a")
	WebElement batchConfigSettingsIBMNodeJs;

	@FindBy(xpath = "//div[@id='settingsBatchModal1']/div/div[5]//label")
	WebElement batchConfigSettingsEnableTestLabel;

	@FindBy(id = "batchSettingsTestCkBox")
	WebElement batchConfigSettingsEnableTestChkBx;

	@FindBy(xpath = "//div[@id='settingsBatchModal1']/div/div[5]//label")
	WebElement batchConfigSettingsEnableInstallLabel;

	@FindBy(id = "batchSettingsInstallCkBox")
	WebElement batchConfigSettingsEnableInstallChkBx;

	@FindBy(xpath = "//div[@id='settingsBatchModal1']/div/div[7]//label")
	WebElement batchConfigSettingsOwnerLabel;

	@FindBy(id = "batchSettingsOwner")
	WebElement batchConfigSettingsOwnerTbx;

	// New UI change, hence commented
	// @FindBy(xpath =
	// "//div[@id='settingsBatchModal']/div/div/div[3]/button[3]")
	// WebElement batchConfigSettingsSaveBtn;

	@FindBy(xpath = "//div[@id='settingsBatchModal']/div/div/div[4]/button[3]")
	WebElement batchConfigSettingsContinueBtn;

	// New UI change, hence commented
	// @FindBy(xpath =
	// "//div[@id='settingsBatchModal']/div/div/div[3]/button[2]")
	// WebElement batchConfigSettingsResetBtn;

	@FindBy(xpath = "//div[@id='settingsBatchModal']/div/div/div[4]/button[2]")
	WebElement batchConfigSettingsResetBtn;

	// New UI change, hence commented
	// @FindBy(xpath =
	// "//div[@id='settingsBatchModal']/div/div/div[3]/button[1]")
	// WebElement batchConfigSettingsCloseBtn;

	@FindBy(id = "showModifyButton")
	WebElement batchConfigSettingsShowModifyCommandsBtn;

	@FindBy(xpath = "//div[@id='batchCommandsTableContanier']//tr[1]/td[1]")
	WebElement batchConfigSettingsShowModifyCommandsPackageNameLabel;

	@FindBy(xpath = "//div[@id='batchCommandsTableContanier']//tr[2]/td[1]")
	WebElement batchConfigSettingsShowModifyCommandsBuildCommandLabel;

	@FindBy(xpath = "//div[@id='batchCommandsTableContanier']//tr[3]/td[1]")
	WebElement batchConfigSettingsShowModifyCommandsTestCommandLabel;

	@FindBy(xpath = "//div[@id='batchCommandsTableContanier']//tr[4]/td[1]")
	WebElement batchConfigSettingsShowModifyCommandsInstallCommandLabel;

	@FindBy(xpath = "//div[@id='batchCommandsTableContanier']//tr[5]/td[1]")
	WebElement batchConfigSettingsShowModifyCommandsEnvironmentVariableLabel;

	@FindBy(xpath = "//div[@id='batchCommandsTableContanier']//tr[1]//a")
	WebElement batchConfigSettingsShowModifyCommandsPackageName;

	@FindBy(xpath = "//div[@id='batchCommandsTableContanier']//tr[2]//textarea") 
	WebElement batchConfigSettingsShowModifyCommandsBuildCommandTxtArea;

	@FindBy(xpath = "//div[@id='batchCommandsTableContanier']//tr[3]//textarea")
	WebElement batchConfigSettingsShowModifyCommandsTestCommandTxtArea;

	@FindBy(xpath = "//div[@id='batchCommandsTableContanier']//tr[4]//textarea")
	WebElement batchConfigSettingsShowModifyCommandsInstallCommandTxtArea;

	@FindBy(xpath = "//div[@id='batchCommandsTableContanier']//tr[5]//textarea")
	WebElement batchConfigSettingsShowModifyCommandsEnvironmentVariableTxtArea;

	@FindBy(xpath = "//div[@id='batchCommandsTableContanier']//a")
	List<WebElement> batchConfigSettingsShowModifyCommandsPackageNameList;

	@FindBy(id = "batchBuildCommandBackButton")
	WebElement batchConfigSettingsShowModifyCommandsBackBtn;

	@FindBy(xpath = "//div[@id='settingsBatchModal']//button[2]")
	WebElement batchConfigSettingsShowModifyCommandsResetBtn;

	@FindBy(xpath = "//div[@id='settingsBatchModal']//button[3]")
	WebElement batchConfigSettingsShowModifyCommandsContinueBtn;

	// To verify expansion of 'Import' button
	public void clickImportBtn() {

		importBtn.click();
	}

	public void verifyDisplayOfImportSection() {
		if (uploadFileDisplayBox.isDisplayed()) {
			LogResult.pass("Import button is clicked.");
		} else {
			LogResult.fail("Import button is not clicked.");
		}

	}

	// To verify expansion of 'List/Select' button
	public void clickListSelectBtn() {

		// wait.until(ExpectedConditions.visibilityOf(listSelectBtn));

		if (batchFileTbx.isDisplayed()) {
			LogResult.pass("List/Select button is open.");
		} else {
			listSelectBtn.click();

			wait.until(ExpectedConditions.visibilityOf(batchFileTbx));

			if (batchFileTbx.isDisplayed()) {
				LogResult.pass("List/Select button is clicked.");
			} else {
				LogResult.fail("List/Select button is not clicked.");
			}
		}

	}

	// To verify placeholder text for Batch File Text Box
	public void verifyPlaceHolderTextForBatchFileTbx() {

		String displayBoxText = batchFileTbx.getAttribute("placeholder");

		if (displayBoxText.contains("Enter batch file name.")) {
			LogResult.pass("Batch file name text box has placeholder text as: " + displayBoxText);
		} else {
			LogResult.fail("Batch file name text box has placeholder text as: " + displayBoxText);
		}
	}

	// Clicking on List Local button
	public void clickOnListLocalBtn() throws InterruptedException {

		// wait.until(ExpectedConditions.visibilityOf(listLocalBtn));

		listLocalBtn.click();

		Thread.sleep(2000);

		// checking here if list out of index messsage is displayed or not, if
		// displayed closing the alert and then again clicking on List Local
		// button
		if (alertCloseBtn.isDisplayed()) {

			alertCloseBtn.click();

			Thread.sleep(2000);

			listLocalBtn.click();
			
			wait.until(ExpectedConditions.visibilityOf(batchFilesPanel));
		}

		if (batchFilesPanel.isDisplayed()) {
			LogResult.pass("List local button is clicked.");
		} else {
			LogResult.fail("List local button is not clicked.");
		}
	}

	// To verify if saved Batch file is present in first row in Batch Jobs local
	// listing
	public void verifyLocallySavedBatchFile(String batchFileString) {

		wait.until(ExpectedConditions.visibilityOf(listDateModifiedTableHeader));

		listDateModifiedTableHeader.click();

		if (firstRowLocalBatchFileName.getText().contains(batchFileString)
				&& firstRowLocalBatchFileLocation.getText().contentEquals("local")) {
			LogResult.pass("Batch file is saved/uploaded locally.");
		} else {
			LogResult.fail("Batch file is not saved/uploaded locally.");
		}
	}

	// Clicking on List Archived button
	public void clickOnListArchivedBtn() {
		listArchivedBtn.click();

		wait.until(ExpectedConditions.visibilityOf(batchFilesPanel));

		if (batchFilesPanel.isDisplayed()) {
			LogResult.pass("List archived button is clicked.");
		} else {
			LogResult.fail("List archived button is not clicked.");
		}
	}

	// To verify the presence of archived file
	public void verifyArchivedBatchFile(String batchFileName) {

		if (firstRowLocalBatchFileName.getText().contains(batchFileName)) {
			LogResult.pass("Batch file successfully archived.");
		} else {
			LogResult.fail("Batch file not archived.");
		}

	}

	// Clicking on List All button
	public void clickOnListAllBtn() {
		listAllBtn.click();

		wait.until(ExpectedConditions.visibilityOf(batchFilesPanel));

		if (batchFilesPanel.isDisplayed()) {
			LogResult.pass("List all button is clicked.");
		} else {
			LogResult.fail("List all button is not clicked.");
		}
	}

	// To verify Batch Jobs tab UI elements
	public void verifyBatchJobsTabUI() {

		wait.until(ExpectedConditions.visibilityOf(importBtn));

		String helpTx = "Import - Allows you to select a local batch file and upload it to the server";

		if (batchJobHelpTx.getText().contains(helpTx)) {
			LogResult.pass("Batch Job help text is displayed.");
		} else {
			LogResult.fail("Batch Job help text is not displayed.");
		}

		if (importBtn.isDisplayed()) {
			LogResult.pass("Import button is displayed");
			if (importBtn.getText().contentEquals("Import")) {
				LogResult.pass("Import button is displayed with text as: " + importBtn.getText());
			} else {
				LogResult.fail("Import button is displayed with text as: " + importBtn.getText());
			}
		} else {
			LogResult.fail("Import button is not displayed");
		}

		if (listSelectBtn.isDisplayed()) {
			LogResult.pass("List/Select button is displayed");
			if (listSelectBtn.getText().contentEquals("List/Select")) {
				LogResult.pass("List/Select button is displayed with text as: " + listSelectBtn.getText());
			} else {
				LogResult.fail("List/Select button is displayed with text as: " + listSelectBtn.getText());
			}
		} else {
			LogResult.fail("List/Select button is not displayed");
		}

	}

	// To verify if upload file display box is displayed
	public void verifyUploadDisplayBox() {
		if (uploadFileDisplayBox.isDisplayed()) {
			LogResult.pass("Upload File display box is displayed.");
		} else {
			LogResult.fail("Upload File display box is not displayed.");
		}

	}

	// To verify placeholder text for Upload text Box
	public void verifyPlaceHolderTextForUploadFileDisplayBox() {

		String displayBoxText = uploadFileDisplayBox.getAttribute("placeholder");

		if (displayBoxText.contains("No file selected for uploading.")) {
			LogResult.pass("Import display box has placeholder text as: " + displayBoxText);
		} else {
			LogResult.fail("Import display box has placeholder text as: " + displayBoxText);
		}
	}

	// To verify Select File button
	public void verifySelectFileBtn() {

		if (selectFileBtn.isDisplayed()) {

			if (selectFileBtn.getText().contentEquals("Select File")) {
				LogResult.pass("Select File button is displayed with text as: " + selectFileBtn.getText());
			} else {
				LogResult.fail("Select File button is displayed with text as: " + selectFileBtn.getText());
			}

		}
	}

	// To verify Upload button
	public void verifyUploadBtn() {
		if (uploadBtn.isDisplayed()) {

			if (uploadBtn.getText().contentEquals("Upload")) {
				LogResult.pass("Upload button is displayed with text as: " + uploadBtn.getText());
			} else {
				LogResult.fail("Upload button is displayed with text as: " + uploadBtn.getText());
			}
		}
	}

	// Selecting a file for uploading
	public void selectFileToUpload(String filePath) {
		// selectFileBtn.click();

		selectFileBtn.sendKeys(filePath);

		if (uploadFileDisplayBox.getAttribute("value").contains("File selected:")) {
			LogResult.pass("File selected for uploading: " + uploadFileDisplayBox.getAttribute("value"));
		} else {
			LogResult.fail("File selected for uploading: " + uploadFileDisplayBox.getAttribute("value"));
		}
	}

	// Clicking Upload button and verifying appearance of alert along with
	// message
	public void clickOnUploadBtn() {
		uploadBtn.click();

		wait.until(ExpectedConditions.visibilityOf(alertCloseBtn));

		if (alertCloseBtn.isDisplayed()) {
			LogResult.pass("Upload button is clicked.");

			if (alertMessage.getText().contentEquals("Batch file uploaded successfully!")) {
				LogResult.pass("Batch file uploaded successfully! alert message is displayed.");
			} else {
				LogResult.fail("Improper message is displayed. Displayed message is: " + alertMessage.getText());
			}
		} else {
			LogResult.fail("Upload button is not clicked.");
		}

	}

	// To verify List/Select UI
	public void verifySelectListUI() {
		if (batchFileTbx.isDisplayed()) {
			LogResult.pass("Batch file name text box is displayed.");
		} else {
			LogResult.fail("Batch file name text box is not displayed.");
		}

		if (listLocalBtn.isDisplayed()) {
			LogResult.pass("List Local button is displayed.");
		} else {
			LogResult.fail("List Local button is not displayed.");
		}

		if (listArchivedBtn.isDisplayed()) {
			LogResult.pass("List Archived button is displayed.");
		} else {
			LogResult.fail("List Archived button is not displayed.");
		}

		if (listAllBtn.isDisplayed()) {
			LogResult.pass("List All button is displayed.");
		} else {
			LogResult.fail("List All button is not displayed.");
		}
	}

	// To verify results UI after clicking on List local/List all buttons
	public void verifyListBatchResultsUI() {
		if (listDetailsBtn.isDisplayed()) {
			LogResult.pass("Details button is displayed.");
		} else {
			LogResult.fail("Details button is not displayed.");
		}

		if (listBuildServersBtn.isDisplayed()) {
			LogResult.pass("Build Servers button is displayed.");
		} else {
			LogResult.fail("Build Servers button is not displayed.");
		}

		if (listBuildAndTestBtn.isDisplayed()) {
			LogResult.pass("Build+Test button is displayed.");

			if (listBuildAndTestBtn.isEnabled()) {
				// boolean removeBtnStatus = listRemoveBtn.isEnabled();
				// System.out.println(removeBtnStatus);

				LogResult.fail("Build+Test button is enabled.");
			} else {
				LogResult.pass("Build+Test button is disabled.");
			}

		} else {
			LogResult.fail("Build+Test button is not displayed.");
		}

		if (listArchiveBtn.isDisplayed()) {
			LogResult.pass("Archive button is displayed.");

			if (listArchiveBtn.isEnabled()) {
				LogResult.fail("Archive button is enabled.");
			} else {
				LogResult.pass("Archive button is disabled.");
			}
		} else {
			LogResult.fail("Archive button is not displayed.");
		}

		if (listRemoveBtn.isDisplayed()) {
			LogResult.pass("Remove button is displayed.");

			if (listRemoveBtn.isEnabled()) {

				LogResult.fail("Remove button is enabled.");
			} else {
				LogResult.pass("Remove button is disabled.");
			}
		} else {
			LogResult.fail("Remove button is not displayed.");
		}

		selectFirstRow();

		if (listBuildAndTestBtn.isEnabled()) {
			LogResult.pass("Build+Test button is enabled.");
		} else {
			LogResult.fail("Build+Test button is disabled.");
		}

		if (listArchiveBtn.isEnabled()) {
			LogResult.pass("Archive button is enabled.");
		} else {
			LogResult.fail("Archive button is disabled.");
		}

		if (listRemoveBtn.isEnabled()) {

			LogResult.pass("Remove button is enabled.");
		} else {
			LogResult.fail("Remove button is disabled.");
		}

	}

	// To verify results UI after clicking on List Archived button
	public void verifyListArchivedBatchResultsUI() {
		if (listDetailsBtn.isDisplayed()) {
			LogResult.pass("Details button is displayed.");
		} else {
			LogResult.fail("Details button is not displayed.");
		}

		if (listBuildServersBtn.isDisplayed()) {
			LogResult.pass("Build Servers button is displayed.");
		} else {
			LogResult.fail("Build Servers button is not displayed.");
		}

		if (listBuildAndTestBtn.isDisplayed()) {
			LogResult.pass("Build+Test button is displayed.");

			if (listBuildAndTestBtn.isEnabled()) {
				LogResult.fail("Build+Test button is enabled.");
			} else {
				LogResult.pass("Build+Test button is disabled.");
			}

		} else {
			LogResult.fail("Build+Test button is not displayed.");
		}

		if (listRemoveBtn.isDisplayed()) {
			LogResult.pass("Remove button is displayed.");

			if (listRemoveBtn.isEnabled()) {

				LogResult.fail("Remove button is enabled.");
			} else {
				LogResult.pass("Remove button is disabled.");
			}
		} else {
			LogResult.fail("Remove button is not displayed.");
		}

		selectFirstRow();

		if (listBuildAndTestBtn.isEnabled()) {
			LogResult.pass("Build+Test button is enabled.");
		} else {
			LogResult.fail("Build+Test button is disabled.");
		}

		if (listRemoveBtn.isEnabled()) {

			LogResult.pass("Remove button is enabled.");
		} else {
			LogResult.fail("Remove button is disabled.");
		}

	}

	// To verify Batch file listing table headers
	public void verifyBatchListTableHeaders() {
		if (listNameTableHeader.isDisplayed()) {
			LogResult.pass("Name header is displayed.");
			if (listNameTableHeader.getText().contentEquals("Name")) {
				LogResult.pass("Name header text is displayed as: " + listNameTableHeader.getText());
			} else {
				LogResult.fail("Name header text is displayed as: " + listNameTableHeader.getText());
			}
		} else {
			LogResult.fail("Name header is not displayed.");
		}

		if (listLocationTableHeader.isDisplayed()) {
			LogResult.pass("Location header is displayed.");
			if (listLocationTableHeader.getText().contentEquals("Location")) {
				LogResult.pass("Location header text is displayed as: " + listLocationTableHeader.getText());
			} else {
				LogResult.fail("Location header text is displayed as: " + listLocationTableHeader.getText());
			}
		} else {
			LogResult.fail("Location header is not displayed.");
		}

		if (listEnvironmentTableHeader.isDisplayed()) {
			LogResult.pass("Environment header is displayed.");
			if (listEnvironmentTableHeader.getText().contentEquals("Environment")) {
				LogResult.pass("Environment header text is displayed as: " + listEnvironmentTableHeader.getText());
			} else {
				LogResult.fail("Environment header text is displayed as: " + listEnvironmentTableHeader.getText());
			}
		} else {
			LogResult.fail("Environment header is not displayed.");
		}

		if (listOwnerTableHeader.isDisplayed()) {
			LogResult.pass("Owner header is displayed.");
			if (listOwnerTableHeader.getText().contentEquals("Owner")) {
				LogResult.pass("Owner header text is displayed as: " + listOwnerTableHeader.getText());
			} else {
				LogResult.fail("Owner header text is displayed as: " + listOwnerTableHeader.getText());
			}
		} else {
			LogResult.fail("Owner header is not displayed.");
		}

		if (listSizeTableHeader.isDisplayed()) {
			LogResult.pass("Size header is displayed.");
			if (listSizeTableHeader.getText().contentEquals("Size")) {
				LogResult.pass("Size header text is displayed as: " + listSizeTableHeader.getText());
			} else {
				LogResult.fail("Size header text is displayed as: " + listSizeTableHeader.getText());
			}
		} else {
			LogResult.fail("Size header is not displayed.");
		}

		if (listDateModifiedTableHeader.isDisplayed()) {
			LogResult.pass("Date Modified header is displayed.");
			if (listDateModifiedTableHeader.getText().contentEquals("Date Modified")) {
				LogResult.pass("Date Modified header text is displayed as: " + listDateModifiedTableHeader.getText());
			} else {
				LogResult.fail("Date Modified header text is displayed as: " + listDateModifiedTableHeader.getText());
			}
		} else {
			LogResult.fail("Date Modified header is not displayed.");
		}
	}

	// Clearing value entered in Batch file search text field
	public void clearBatchFileSearchTbx() {
		batchFileTbx.clear();
	}

	// Entering value in Batch file search text field
	public void enterBatchSearchTerm(String searchTerm) {

		batchFileTbx.sendKeys(searchTerm);

		if (batchFileTbx.getAttribute("value").contains(searchTerm)) {
			LogResult.pass("Search term entered in the text box: " + searchTerm);
		} else {
			LogResult.fail("Search term not entered in the text box.");
		}
	}

	// To check if search term is present in all the column values
	public void verifyResultForBatchFileSearch(String searchTerm) {
		int j = 0;

		if (numOfRowsShowingTx.isDisplayed()) {

			for (WebElement item : listBatchFileNameColumnValues) {
				if (item.getText().contains(searchTerm)) {
					j++;
					continue;
				} else {
					LogResult.fail("Search term does not match batch file names in the result.");
					break;
				}
			}
		} else {
			LogResult.pass("No results found matching search term.");
		}

		if (j == listNoRows.size()) {
			LogResult.pass("Search term matches all the batch file names in the result.");
		}

	}

	// Verify number of batch files
	public int verifyListOfRows() {

		return listNoRows.size();

	}

	// Selecting maximum records for displaying per page
	public void verifyMaxRecordsPerPage() {

		if (currentRecordsPerPage.isDisplayed()) {
			LogResult.pass("Records per page drop down is displayed");

			currentRecordsPerPage.click();

			int maxValue = recordsPerPageValues.size();

			for (int i = maxValue; i <= maxValue; i++) {

				recordsPerPageValues.get(i - 1).click();

			}

			LogResult.pass("Records per page value is selected as: " + currentRecordsPerPage.getText());
		} else {
			LogResult.pass("Records per page drop down is not displayed");

			LogResult.pass("Records displayed per page are: " + listNoRows.size());
		}

	}

	// To verify if Location column has value as 'local' for all rows
	public void verifyLocalBatchFileLocation() {

		int j = 0;

		for (int i = 0; i < listLocationColumnValues.size(); i++) {

			if (listLocationColumnValues.get(i).getText().contentEquals("local")) {
				j++;
				continue;
			} else {
				LogResult.fail("Some values in Location column don't have value as local.");
				break;
			}

		}

		if (j == listLocationColumnValues.size()) {
			LogResult.pass("All values in Location column has value as local.");
		}
	}

	// To verify if Location column has value as 'gsa' for all rows
	public void verifyArchivedBatchFileLocation() {

		int j = 0;
		for (int i = 0; i < listLocationColumnValues.size(); i++) {

			if (listLocationColumnValues.get(i).getText().contentEquals("gsa")) {
				j++;
				continue;
			} else {
				LogResult.fail("Some values in Location column don't have value as gsa.");
				break;
			}

		}

		if (j == listLocationColumnValues.size()) {
			LogResult.pass("All values in Location column has value as gsa.");
		}
	}

	// Clicking on Date Modified header column
	public void clickOnDateModifiedHeader() {
		listDateModifiedTableHeader.click();
	}

	// Selecting first row
	public void selectFirstRow() {

		wait.until(ExpectedConditions.visibilityOf(batchFilesPanel));

		if (firstRowCheckbx.isDisplayed()) {

			firstRowCheckbx.click();
		}

		if (firstRowCheckbx.isSelected()) {
			LogResult.pass("First row is selected");
		} else {
			LogResult.fail("First row is not selected");
		}

	}

	// Clicking on Details button
	public void clickOnDetailsBtn() throws InterruptedException {

		listDetailsBtn.click();

		// Thread.sleep(50000);

		wait.until(ExpectedConditions.visibilityOf(batchFileDetailsPanel));

		if (batchFileDetailsPanel.isDisplayed()) {
			LogResult.pass("Details button is clicked.");
		} else {
			LogResult.fail("Details button is not clicked.");
		}
	}

	// To verify Batch file details UI
	public void verifyBatchFileDetailsUI(String firstRowBatchfileName) {

		// commented as changed per new UI
		// String batchDetailsHelpTx = "The following packages will be submitted
		// to be built and tested in order.";

		String batchDetailsHelpTx = "The Settings Menu below allows you to customize the selected batch file.";

		if (detailsHelpTxt.getText().contains(batchDetailsHelpTx)) {
			LogResult.pass("Details help text is displayed.");
		} else {
			LogResult.fail("Details help text is not displayed.");
		}

		if (saveDetailsTbx.isDisplayed()) {
			LogResult.pass("Details text box is displayed.");
		} else {
			LogResult.fail("Details text box is not displayed.");
		}

		String saveDetailsTbxValue = saveDetailsTbx.getAttribute("value");

		if (firstRowBatchfileName.contentEquals(saveDetailsTbxValue)) {
			LogResult.pass("Correct value is populated in details text box.");
		} else {
			LogResult.fail("Incorrect value is populated in details text box.");
		}

		if (saveDetailsBtn.isDisplayed()) {
			LogResult.pass("Save button is displayed.");
		} else {
			LogResult.fail("Save button is not displayed.");
		}

		// Buttons removed in new UI hence commenting functions

		// if (detailBuildServersBtn.isDisplayed()) {
		// LogResult.pass("Build Servers button is displayed.");
		// } else {
		// LogResult.fail("Build Servers button is not displayed.");
		// }
		//
		// if (detailBuildAndTestBtn.isDisplayed()) {
		// LogResult.pass("Build+Test button is displayed.");
		// } else {
		// LogResult.fail("Build+Test button is not displayed.");
		// }

		if (detailBackBtn.isDisplayed()) {
			LogResult.pass("Back button is displayed.");
		} else {
			LogResult.fail("Back button is not displayed.");
		}

	}

	// To verify Batch config headers
	public void verifyBatchConfigTableHeaders() {
		if (batchConfigFileNameHeader.isDisplayed()) {
			LogResult.pass("File Name header is displayed.");
			if (batchConfigFileNameHeader.getText().contentEquals("File name")) {
				LogResult.pass("File Name header text is displayed as: " + batchConfigFileNameHeader.getText());
			} else {
				LogResult.fail("File Name header text is displayed as: " + batchConfigFileNameHeader.getText());
			}
		} else {
			LogResult.fail("File Name header is not displayed.");
		}

		if (batchConfigFileNameHeader.isDisplayed()) {
			LogResult.pass("Owner header is displayed.");
			if (batchConfigOwnerHeader.getText().contentEquals("Owner")) {
				LogResult.pass("Owner header text is displayed as: " + batchConfigOwnerHeader.getText());
			} else {
				LogResult.fail("Owner header text is displayed as: " + batchConfigOwnerHeader.getText());
			}
		} else {
			LogResult.fail("Owner header is not displayed.");
		}

		if (batchConfigFileNameHeader.isDisplayed()) {
			LogResult.pass("Java header is displayed.");
			if (batchConfigJavaHeader.getText().contentEquals("Java")) {
				LogResult.pass("Java header text is displayed as: " + batchConfigJavaHeader.getText());
			} else {
				LogResult.fail("Java header text is displayed as: " + batchConfigJavaHeader.getText());
			}
		} else {
			LogResult.fail("Java header is not displayed.");
		}

		if (batchConfigFileNameHeader.isDisplayed()) {
			LogResult.pass("Java header is displayed.");
			if (batchConfigJavaHeader.getText().contentEquals("Java")) {
				LogResult.pass("Java header text is displayed as: " + batchConfigJavaHeader.getText());
			} else {
				LogResult.fail("Java header text is displayed as: " + batchConfigJavaHeader.getText());
			}
		} else {
			LogResult.fail("Java header is not displayed.");
		}

		if (batchConfigFileNameHeader.isDisplayed()) {
			LogResult.pass("Actions header is displayed.");
			if (batchConfigActionsHeader.getText().contentEquals("Actions")) {
				LogResult.pass("Actions header text is displayed as: " + batchConfigActionsHeader.getText());
			} else {
				LogResult.fail("Actions header text is displayed as: " + batchConfigActionsHeader.getText());
			}
		} else {
			LogResult.fail("Actions header is not displayed.");
		}

	}

	// To verify the presence of Settings button
	public void verifyBatchConfigActionsColumn() {
		if (batchConfigSettingsBtn.isDisplayed()) {
			LogResult.pass("Settings button is displayed in Actions.");
		} else {
			LogResult.fail("Settings button is not displayed in Actions.");
		}
	}

	// To verify Batch repository headers
	public void verifyBatchRepoHeaders() {
		if (batchRepoNameHeader.isDisplayed()) {
			LogResult.pass("Name header is displayed.");
			if (batchRepoNameHeader.getText().contentEquals("Name")) {
				LogResult.pass("Name header text is displayed as: " + batchRepoNameHeader.getText());
			} else {
				LogResult.fail("Name header text is displayed as: " + batchRepoNameHeader.getText());
			}
		} else {
			LogResult.fail("Name header is not displayed.");
		}

		if (batchRepoVersionHeader.isDisplayed()) {
			LogResult.pass("Version header is displayed.");
			if (batchRepoVersionHeader.getText().contentEquals("Version")) {
				LogResult.pass("Version header text is displayed as: " + batchRepoVersionHeader.getText());
			} else {
				LogResult.fail("Version header text is displayed as: " + batchRepoVersionHeader.getText());
			}
		} else {
			LogResult.fail("Version header is not displayed.");
		}

		if (batchRepoActionsHeader.isDisplayed()) {
			LogResult.pass("Actions header is displayed.");
			if (batchRepoActionsHeader.getText().contentEquals("Actions")) {
				LogResult.pass("Actions header text is displayed as: " + batchRepoActionsHeader.getText());
			} else {
				LogResult.fail("Actions header text is displayed as: " + batchRepoActionsHeader.getText());
			}
		} else {
			LogResult.fail("Actions header is not displayed.");
		}
	}

	// To verify presence of Up, Down and Remove button
	public void verifyBatchRepoActionsColumn() {
		if (batchRepoUpArrowBtn.isDisplayed()) {
			LogResult.pass("Up button is displayed in Actions.");
		} else {
			LogResult.fail("Up button is not displayed in Actions.");
		}

		if (batchRepoDownArrowBtn.isDisplayed()) {
			LogResult.pass("Down button is displayed in Actions.");
		} else {
			LogResult.fail("Down button is not displayed in Actions.");
		}

		if (batchRepoCrossBtn.isDisplayed()) {
			LogResult.pass("Remove button is displayed in Actions.");
		} else {
			LogResult.fail("Remove button is not displayed in Actions.");
		}
	}

	// Clicking on archived button and verifying appearance of alert along with
	// message
	public void clickOnArchiveBtn() {
		listArchiveBtn.click();

		wait.until(ExpectedConditions.visibilityOf(alertCloseBtn));

		if (alertCloseBtn.isDisplayed()) {
			LogResult.pass("Archive button is clicked.");

			if (alertMessage.getText().contentEquals("Archived successfully")) {
				LogResult.pass("Archived successfully alert message is displayed.");
			} else {
				LogResult.fail("Improper message is displayed. Displayed message is: " + alertMessage.getText());
			}
		} else {

			LogResult.fail("Archive button is not clicked.");
		}

	}

	// Closing the alert pop up
	public void clickOnAlertCloseBtn() throws InterruptedException {

		alertCloseBtn.click();

		Thread.sleep(2000);

		if (alertCloseBtn.isDisplayed()) {
			LogResult.fail("Close button is not clicked.");
		} else {
			LogResult.pass("Close button is clicked. Alert is dismissed.");
		}

	}

	// To enter different batch file name in details
	public void saveBatchFileAs(String batchFileNameAs) {
		saveDetailsTbx.clear();

		saveDetailsTbx.sendKeys(batchFileNameAs);
	}

	// Clicking on Save button in batch file details
	public void clickOnSaveBatchDetailsBtn() {
		saveDetailsBtn.click();

		wait.until(ExpectedConditions.visibilityOf(alertCloseBtn));

		if (alertCloseBtn.isDisplayed()) {
			LogResult.pass("Save button is clicked");

			if (alertMessage.getText().contentEquals("Batch file saved successfully")) {
				LogResult.pass("Batch file saved successfully alert message is displayed.");
			} else {
				LogResult.fail("Improper message is displayed. Displayed message is: " + alertMessage.getText());
			}
		} else {

			LogResult.fail("Save button is not clicked");
		}
	}

	/*// To verify for change in batch file name in config settings
	public void verifyBatchFileNameChangeInListing() {

		wait.until(ExpectedConditions.visibilityOf(batchConfigFileName));

		String batchFileName = saveDetailsTbx.getAttribute("value");
		
		if (batchConfigFileName.getText().contentEquals(batchFileName)) {
			LogResult.pass("Batch file name in configuration settings changed successfully.");
		} else {
			LogResult.fail("Batch file name in configuration settings not changed. Save button functionality failed.");
		}
		
	}*/

	// To verify if new Batch file is created after batch file name change
	public void newBatchFileCreationConfirmation(String newBatchFileName) {
		if (firstRowLocalBatchFileName.getText().contentEquals(newBatchFileName)) {
			LogResult.pass("New Batch file is created successfully.");
		} else {
			LogResult.fail("New Batch file is not created.");
		}

	}

	// Clicking on Back button in Batch file details UI
	public void clickOnDetailsBackBtn() {
		detailBackBtn.click();

		if (firstRowLocalBatchFileLocation.isDisplayed()) {
			LogResult.pass("Back button is clicked.");
		} else {
			LogResult.fail("Back button is not clicked.");
		}

		if (firstRowLocalBatchFileLocation.getText().contentEquals("local")
				|| firstRowLocalBatchFileLocation.getText().contentEquals("gsa")) {
			LogResult.pass("Navigated back to batch listing.");
		} else {
			LogResult.fail("Navigated back to batch listing failed.");
		}

	}

	// Clicking on Batch config settings button
	public void clickOnSettingsBtn() {

		batchConfigSettingsBtn.click();

		wait.until(ExpectedConditions.visibilityOf(batchConfigSettingsHeader));

		if (batchConfigSettingsHeader.isDisplayed()) {
			LogResult.pass("Batch config settings button is clicked. Batch Settings pop up is displayed.");
		} else {
			LogResult.fail("Batch config settings button is not clicked.");
		}

	}

	// To veify Batch config settings pop up UI
	public void verifyBatchConfigSettingsUI() {
		if (batchConfigSettingsHeader.isDisplayed()) {
			LogResult.pass("Batch config settings pop up header is displayed.");
			if (batchConfigSettingsHeader.getText().contentEquals("Batch Settings")) {
				LogResult.pass("Batch config settings pop up header is displayed as Batch Settings");
			} else {
				LogResult.fail(
						"Batch config settings pop up header is displayed as: " + batchConfigSettingsHeader.getText());
			}
		} else {
			LogResult.fail("Batch config settings pop up header is not displayed.");
		}

		if (batchConfigSettingsEnvironmentHeader.isDisplayed()) {
			LogResult.pass("Batch config settings Set Environment section header is displayed.");
			if (batchConfigSettingsEnvironmentHeader.getText().contentEquals("Set Environment")) {
				LogResult.pass("Batch config settings Set Environment section header is displayed as Set Environment");
			} else {
				LogResult.fail("Batch config settings Set Environment section header is displayed as: "
						+ batchConfigSettingsEnvironmentHeader.getText());
			}
		} else {
			LogResult.fail("Batch config settings Set Environment section header is not displayed.");
		}

		if (batchConfigSettingsJDK.isDisplayed()) {
			LogResult.pass("Use JDK drop down is displayed with values: ");

			batchConfigSettingsJDK.click();

			for (WebElement item : batchConfigSettingsJDKValues) {
				LogResult.pass(item.getText());
			}

			batchConfigSettingsJDK.click();

		} else {
			LogResult.fail("Use JDK drop down is not displayed");
		}

		if (batchConfigSettingsJs.isDisplayed()) {
			LogResult.pass("Use Node.js drop down is displayed with values: ");

			batchConfigSettingsJs.click();

			for (WebElement item : batchConfigSettingsNodeJsValues) {
				LogResult.pass(item.getText());
			}

			batchConfigSettingsNodeJs.click();

		} else {
			LogResult.fail("Use Node.js drop down is not displayed.");
		}

		if (batchConfigSettingsOptionsHeader.isDisplayed()) {
			LogResult.pass("Batch config settings Set Batch Options section header is displayed.");
			if (batchConfigSettingsOptionsHeader.getText().contentEquals("Set Batch Options")) {
				LogResult.pass(
						"Batch config settings Set Batch Options section header is displayed as Set Batch Options");
			} else {
				LogResult.fail("Batch config settings Set Batch Options section header is displayed as: "
						+ batchConfigSettingsOptionsHeader.getText());
			}
		} else {
			LogResult.fail("Batch config settings Set Batch Options section header is not displayed.");
		}

		if (batchConfigSettingsEnableTestLabel.isDisplayed()) {
			LogResult.pass("Enable test label is displayed.");
		} else {
			LogResult.fail("Enable test label is not displayed.");
		}

		if (batchConfigSettingsEnableTestChkBx.isDisplayed()) {
			LogResult.pass("Enable test check box is displayed.");
			if (batchConfigSettingsEnableTestChkBx.isSelected()) {
				LogResult.pass("Enable test check box is selected.");
			} else {
				LogResult.fail("Enable test check box is not selected.");
			}
		} else {
			LogResult.fail("Enable test label is not displayed.");
		}

		if (batchConfigSettingsEnableInstallLabel.isDisplayed()) {
			LogResult.pass("Enable install label is displayed.");
		} else {
			LogResult.fail("Enable install label is not displayed.");
		}

		if (batchConfigSettingsEnableInstallChkBx.isDisplayed()) {
			LogResult.pass("Enable install check box is displayed.");
			if (batchConfigSettingsEnableInstallChkBx.isSelected()) {
				LogResult.fail("Enable install check box is selected.");
			} else {
				LogResult.pass("Enable install check box is not selected.");
			}
		} else {
			LogResult.fail("Enable install check box is not displayed.");
		}

		if (batchConfigSettingsOwnerLabel.isDisplayed()) {
			LogResult.pass("Owner label is displayed.");
		} else {
			LogResult.fail("Owner label is not displayed.");
		}

		if (batchConfigSettingsOwnerTbx.isDisplayed()) {
			LogResult.pass("Owner text box is displayed with values as: " + batchConfigSettingsOwnerTbx.getText());

		} else {
			LogResult.fail("Owner text box is not selected.");
		}

		if (batchConfigSettingsContinueBtn.isDisplayed()) {
			LogResult.pass("Continue button is displayed.");
		} else {
			LogResult.fail("Continue button is not displayed.");
		}

		if (batchConfigSettingsResetBtn.isDisplayed()) {
			LogResult.pass("Reset button is displayed.");
		} else {
			LogResult.fail("Reset button is not displayed.");
		}

		if (batchConfigSettingsShowModifyCommandsBtn.isDisplayed()) {
			LogResult.pass("Show/Modify Commands button is displayed.");
		} else {
			LogResult.fail("Show/Modify Commands button is not displayed.");
		}

	}

	// Clicking on Continue button for Batch config settings pop up
	public void clickOnBatchConfigSettingsContinueBtn() throws InterruptedException {// clickOnBatchConfigSettingsSaveBtn()

		batchConfigSettingsJDK.click();

		batchConfigSettingsOpenJDK8.click();

		if (batchConfigSettingsJDK.getText().contentEquals("Use openjdk 8")) {
			LogResult.pass("Environment is set to openjdk 8.");
		} else {
			LogResult.fail("Environment is not set to openjdk 8.");
		}

		batchConfigSettingsJs.click();

		batchConfigSettingsIBMNodeJs.click();

		if (batchConfigSettingsJs.getText().contentEquals("Use ibm-sdk-nodejs 4.2.2")) {
			LogResult.pass("Environment is set to IBM SDK for Node.js.");
		} else {
			LogResult.fail("Environment is not set to IBM SDK for Node.js.");
		}

		batchConfigSettingsContinueBtn.click();

		if (batchConfigJava.getText().contentEquals("openjdk 8")
				&& batchConfigJs.getText().contentEquals("ibm-sdk-nodejs 4.2.2")) {
			LogResult.pass("Continue button is clicked and functionality verified.");
		} else {
			LogResult.fail("Continue button is not clicked.");
		}

		Thread.sleep(2000);
	}

	// Clicking on Reset button for Batch config settings pop up
	public void clickOnBatchConfigSettingsResetBtn() throws InterruptedException {

		batchConfigSettingsResetBtn.click();

		batchConfigSettingsContinueBtn.click();

		Thread.sleep(2000);

		// checking only for node instead of node.js since value is saved as
		// nodejs instead of Node.js
		if (batchConfigJava.getText().contentEquals("openjdk 7") && batchConfigJs.getText().contains("node")) {
			LogResult.pass("Reset button is clicked and functionality verified.");
		} else {
			LogResult.fail("Reset button is not clicked.");
		}

	}

	// Clicking on Show/Modify Commands button for Batch config settings pop up
	public void clickOnBatchConfigSettingsShowModifyCommandsBtn() {// clickOnBatchConfigSettingsCloseBtn

		wait.until(ExpectedConditions.visibilityOf(batchConfigSettingsShowModifyCommandsBtn));

		batchConfigSettingsShowModifyCommandsBtn.click();

		// Commented for new UI changes and to ensure that flow is continued
		// wait.until(ExpectedConditions.visibilityOf(batchConfigSettingsBtn));
		//
		// if (batchConfigSettingsBtn.isDisplayed()) {
		// LogResult.pass("Close button is clicked. User is navigated back to
		// batch file details.");
		// } else {
		// LogResult.fail("Close button is not clicked.");
		// }

		// batchConfigSettingsContinueBtn.click();
	}

	
	//To verify UI for Show/Modify Commands for Batch config settings pop up 
	public void verifyBatchConfigSettingsShowModifyCommandsUI() {

		if (batchConfigSettingsShowModifyCommandsPackageNameLabel.getText().contentEquals("Package Name")) {
			LogResult.pass("Package Name label is displayed.");
		} else {
			LogResult.fail("Package Name label is not displayed. Label is: "
					+ batchConfigSettingsShowModifyCommandsPackageNameLabel.getText());
		}

		if (batchConfigSettingsShowModifyCommandsPackageName.isDisplayed()) {
			LogResult.pass("Package Name is displayed.");
		} else {
			LogResult.fail("Package Name is not displayed.");
		}

		if (batchConfigSettingsShowModifyCommandsBuildCommandLabel.getText().contentEquals("Build Command")) {
			LogResult.pass("Build Command label is displayed.");
		} else {
			LogResult.fail("Build Command label is not displayed. Label is: "
					+ batchConfigSettingsShowModifyCommandsBuildCommandLabel.getText());
		}

		if (batchConfigSettingsShowModifyCommandsBuildCommandTxtArea.isDisplayed()) {
			LogResult.pass("Build Command text box is displayed.");
		} else {
			LogResult.fail("Build Command text box is not displayed.");
		}

		if (batchConfigSettingsShowModifyCommandsTestCommandLabel.getText().contentEquals("Test Command")) {
			LogResult.pass("Test Command label is displayed.");
		} else {
			LogResult.fail("Test Command label is not displayed. Label is: "
					+ batchConfigSettingsShowModifyCommandsTestCommandLabel.getText());
		}

		if (batchConfigSettingsShowModifyCommandsTestCommandTxtArea.isDisplayed()) {
			LogResult.pass("Test Command text box is displayed.");
		} else {
			LogResult.fail("Test Command text box is not displayed.");
		}

		if (batchConfigSettingsShowModifyCommandsInstallCommandLabel.getText().contentEquals("Install Command")) {
			LogResult.pass("Install Command label is displayed.");
		} else {
			LogResult.fail("Install Command label is not displayed. Label is: "
					+ batchConfigSettingsShowModifyCommandsInstallCommandLabel.getText());
		}

		if (batchConfigSettingsShowModifyCommandsInstallCommandTxtArea.isDisplayed()) {
			LogResult.pass("Install Command text box is displayed.");
		} else {
			LogResult.fail("Install Command text box is not displayed.");
		}

		if (batchConfigSettingsShowModifyCommandsEnvironmentVariableLabel.getText()
				.contentEquals("Environment Variable")) {
			LogResult.pass("Environment Variable label is displayed.");
		} else {
			LogResult.fail("Environment Variable label is not displayed. Label is: "
					+ batchConfigSettingsShowModifyCommandsEnvironmentVariableLabel.getText());
		}

		if (batchConfigSettingsShowModifyCommandsEnvironmentVariableTxtArea.isDisplayed()) {
			LogResult.pass("Environment Variable text area is displayed.");
		} else {
			LogResult.fail("Environment Variable text area is not displayed.");
		}

		LogResult.pass("Packages displayed are:");

		for (WebElement item : batchConfigSettingsShowModifyCommandsPackageNameList) {
			LogResult.pass(item.getText());
		}

		if (batchConfigSettingsShowModifyCommandsBackBtn.isDisplayed()) {
			LogResult.pass("Back button is displayed.");
		} else {
			LogResult.fail("Back button is not displayed.");
		}

		if (batchConfigSettingsShowModifyCommandsResetBtn.isDisplayed()) {
			LogResult.pass("Reset button is displayed.");
		} else {
			LogResult.fail("Reset button is not displayed.");
		}

		if (batchConfigSettingsShowModifyCommandsContinueBtn.isDisplayed()) {
			LogResult.pass("Continue button is displayed.");
		} else {
			LogResult.fail("Continue button is not displayed.");
		}

	}

	// Clicking Show/Modify Commands button on Batch Config settings pop up
	public void clickOnShowModifyCommandsBackBtn() {

		batchConfigSettingsShowModifyCommandsBackBtn.click();

		if (batchConfigSettingsShowModifyCommandsBtn.isDisplayed()) {
			LogResult.pass("Show/Modify Commands UI Back button is clicked.");
		} else {
			LogResult.fail("Show/Modify Commands UI Back button is clicked.");
		}
	}

	// To verify for Show/Modify Commands Reset button functionality on Batch
	// Config settings pop up
	public void clickOnShowModifyCommandsResetBtn() {

		String testCommandTxt = batchConfigSettingsShowModifyCommandsTestCommandTxtArea.getText();

		batchConfigSettingsShowModifyCommandsTestCommandTxtArea.clear();

		batchConfigSettingsShowModifyCommandsTestCommandTxtArea.sendKeys("abc");

		batchConfigSettingsShowModifyCommandsResetBtn.click();

		if (batchConfigSettingsShowModifyCommandsTestCommandTxtArea.getText().contentEquals(testCommandTxt)) {
			LogResult.pass("Show/Modify Commands UI Reset button is clicked and functionality verified.");
		} else {
			LogResult.fail("Show/Modify Commands UI Reset button is not clicked.");
		}

	}

	// Clicking on Show/Modify Commands Continue button on Batch Config settings
	// pop up
	public void clickOnShowModifyCommandsContinueBtn() {

		batchConfigSettingsShowModifyCommandsContinueBtn.click();

		if (batchConfigSettingsBtn.isDisplayed()) {
			LogResult.pass("Show/Modify Commands UI Continue button is clicked.");
		} else {
			LogResult.fail("Show/Modify Commands UI Continue button is clicked.");
		}
		
		
	}

	// To verify repository movement upwards
	public void verifyRepoUpMove() throws InterruptedException {
		
		Thread.sleep(2000);

		String secondRepository = batchSecondRepoName.getText();

		// System.out.println(secondRepository);

		batchSecondRepoUpBtn.click();

		if (batchFirstRepoName.getText().contentEquals(secondRepository)) {
			LogResult.pass("Second repository moved Up.");
		} else {
			LogResult.fail("Second repository not moved Up.");
		}
	}

	// To verify repository movement downwards
	public void verifyRepoDownMove() {

		wait.until(ExpectedConditions.visibilityOf(batchFirstRepoDownBtn));
		
		String firstRepository = batchFirstRepoName.getText();

		// System.out.println(firstRepository);

		batchFirstRepoDownBtn.click();

		if (batchSecondRepoName.getText().contentEquals(firstRepository)) {
			LogResult.pass("First repository moved Down.");
		} else {
			LogResult.fail("Second repository not moved Down.");
		}

	}

	// To verify repository deletion in batch file
	public void verifyRepoDelete() {

		String firstRepository = batchFirstRepoName.getText();
		String secondRepository = batchSecondRepoName.getText();

		// System.out.println(firstRepository);
		// System.out.println(secondRepository);

		batchFirstRepoRemoveBtn.click();

		if (batchFirstRepoName.getText().contentEquals(secondRepository)) {
			LogResult.pass("First repository deleted successfully.");
		} else {
			LogResult.fail("First repository not deleted successfully.");
		}

	}

	// To verify remove button functionality
	public void clickOnRemoveBtn() throws InterruptedException {

		String batchFileDate = firstRowLocalBatchFileDate.getText();

		listRemoveBtn.click();

		wait.until(ExpectedConditions.alertIsPresent());

		Alert alert = driver.switchTo().alert();

		alert.accept();
		
		Thread.sleep(2000);

		alertCloseBtn.click();
		
		Thread.sleep(2000);

		if (firstRowLocalBatchFileDate.getText().contentEquals(batchFileDate)) {
			LogResult.fail("Batch file not deleted successfully.");
		} else {
			LogResult.pass("Batch file deleted successfully.");
		}
	}

	// Clicking Build Servers dropd down
	public void clickOnBuildServers() {
		listBuildServersBtn.click();
	}

	// To verify Build Server nodes present in Build Servers drop down
	public void verifyBuildServersNodes() {

		LogResult.pass("Build servers drop down contains following values: ");

		for (WebElement item : listBuildServersNodes) {

			LogResult.pass(item.getText());

		}

	}

	// To verify selection of all selected build servers
	public void verifySelectionOfAllBuildServers() {

		int i = 0;

		for (WebElement item : listBuildServersChkbx) {

			item.click();
			i++;
		}

		// Currently the build servers are dynamic hence checking for
		// partial text and omitting the number in brackets
		if (listBuildServersBtn.getText().contains("All selected")) {
			LogResult.pass("All Build servers are selected.");
		} else {
			LogResult
					.fail("All Build servers are not selected. Selected servers are: " + listBuildServersBtn.getText());
		}

		this.setBuildServersCount(i);

	}

	// To verify deselection of all selected build servers
	public void verifyDeSelectionOfAllBuildServers() {

		for (WebElement item : listBuildServersChkbx) {

			item.click();

		}

		if (listBuildServersBtn.getText().contentEquals("None selected")) {
			LogResult.pass("All Build servers are unselected.");
		} else {
			LogResult.fail(
					"All Build servers are not unselected. Unselected servers are: " + listBuildServersBtn.getText());
		}

	}

	// Setting value for selected build server count
	public void setBuildServersCount(int buildServersCount) {
		this.selectedBuildServersCount = buildServersCount;
		// System.out.println(buildServersCount);
	}

	// Fetching value for selected build server count
	public int getBuildServersCount() {
		return this.selectedBuildServersCount;
	}

	// Clicking on Build+Test button
	public void verifyBuildAndTestBtn() throws InterruptedException {

		clickOnBuildServers();

		verifySelectionOfAllBuildServers();

		this.setBuildClickTime(getSystemTime());

		listBuildAndTestBtn.click();

		Thread.sleep(60000); // wait till the job is submitted

		wait.until(ExpectedConditions.visibilityOf(alertCloseBtn));

		if (alertCloseBtn.isDisplayed()) {
			LogResult.pass("Build+Test button is clicked.");

			if (alertMessage.getText().contentEquals("Build job submitted")
					|| alertMessage.getText().contentEquals("Batch job submitted")) {
				LogResult.pass("Jobs successfully triggered on jenkins.");
			} else {
				LogResult.fail("Jobs failed to get triggered on jenkins.");
			}
		} else {
			LogResult.fail("Build+Test button is not clicked.");
		}

	}

	// Setting time before clicking Build+Test button
	public void setBuildClickTime(String buildClickTime) {
		this.buildClickTime = buildClickTime;
		// System.out.println(buildClickTime);
	}

	// Fetching time set before clicking Build+Test button
	public String getBuildClickTime() {
		return this.buildClickTime;
	}

	// Fetching current system time
	public String getSystemTime() {

		Date d = new Date();
		DateFormat format = new SimpleDateFormat("EEE MMM dd HH:mm:ss yyyy");// yyyy-MM-dd-'h'HH-'m'mm-'s'ss
		String buildTime = format.format(d);
		return buildTime;
	}

}
