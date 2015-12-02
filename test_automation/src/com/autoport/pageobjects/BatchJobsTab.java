package com.autoport.pageobjects;

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

	public BatchJobsTab(WebDriver driver, FluentWait<WebDriver> wait) {

		this.driver = driver;
		this.wait = wait;
		// wait = new WebDriverWait(driver, 30);

		AjaxElementLocatorFactory factory = new AjaxElementLocatorFactory(driver, 10);
		PageFactory.initElements(factory, this);
	}

	// @FindBy(className="btn btn-default btn-block")
	@FindBy(xpath = "//div[@id='batchTabHeader']/p[1]")
	WebElement batchJobHelpTx;

	@FindBy(xpath = "//div[@id='batchPanel']/div[1]/div[1]")
	WebElement importBtn;

	@FindBy(id = "uploadFilename")
	WebElement uploadFileDisplayBox;

	//// div[@id='batchPanel']/div[1]/div[2]/div[1]/div
	@FindBy(xpath = "/html/body/div[2]/div[3]/div/div[2]/div[1]/div[2]/div[1]/div/input")
	WebElement selectFileBtn;

	@FindBy(xpath = "//div[@id='batchPanel']/div[1]/div[2]/div[2]/div")
	WebElement uploadBtn;

	@FindBy(id = "batchFileFilter")
	WebElement batchFileTbx;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[1]")
	WebElement listSelectBtn;

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

	@FindBy(xpath = "//div[@id='batchListSelectToolbar']/a[2]/button")
	WebElement listBuildAndTestBtn;

	@FindBy(xpath = "//div[@id='batchListSelectToolbar']/a[3]/button")
	WebElement listArchiveBtn;

	@FindBy(xpath = "//div[@id='batchListSelectToolbar']/a[4]/button")
	WebElement listRemoveBtn;

	@FindBy(id = "batchListSelectTable")
	WebElement batchFilesPanel;

	@FindBy(xpath = "//table[@id='batchListSelectTable']/tbody/tr[1]//td[1]/input")
	WebElement firstRowCheckbx;

	@FindBy(xpath = "//table[@id='batchListSelectTable']/tbody/tr[1]//td[2]")
	WebElement firstRowLocalBatchFileName;

	@FindBy(xpath = "//table[@id='batchListSelectTable']/tbody/tr[1]//td[3]")
	WebElement firstRowLocalBatchFileLocation;

	@FindBy(xpath = "//table[@id='batchListSelectTable']//th[7]/div[1]")
	WebElement dateModifiedTableHeader;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/div[2]/div[1]/div[2]/div[4]/div[1]/span[1]")
	WebElement numOfRowsShowingTx;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/div[2]/div[1]/div[2]/div[4]/div[1]/span[2]/span/button")
	WebElement currentRecordsPerPage;

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

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/div[5]/span/div[2]/div[2]/button")
	WebElement detailBuildServersBtn;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/div[5]/span/div[2]/a[2]/button")
	WebElement detailBuildAndTestBtn;

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
	WebElement batchConfigActionsHeader;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[1]//td[4]/button")
	WebElement batchConfigSettings;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]//th[1]")
	WebElement batchRepoNameHeader;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]//th[2]")
	WebElement batchRepoVersionHeader;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]//th[3]")
	WebElement batchRepoActionsHeader;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]/tbody[1]//td[3]/a[1]/button")
	WebElement batchRepoUpBtn;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]/tbody[1]//td[3]/a[2]/button")
	WebElement batchRepoDownBtn;

	@FindBy(xpath = "//div[@id='batchPanel']/div[2]/div[2]/table[2]/tbody[1]//td[3]/a[3]/button")
	WebElement batchRepoRemoveBtn;

	// div[starts-with(@class, 'btn btn'-)]/h2

	// To verify expansion of 'Import' button
	public void clickImportBtn() {

		importBtn.click();

		if (uploadFileDisplayBox.isDisplayed()) {
			LogResult.pass("Import section is expanded.");
		} else {
			LogResult.fail("Import section is not expanded.");
		}

	}

	// To verify expansion of 'List/Select' button
	public void clickListSelectBtn() {

		wait.until(ExpectedConditions.visibilityOf(listSelectBtn));

		listSelectBtn.click();

		if (batchFileTbx.isDisplayed()) {
			LogResult.pass("List/Select section is expanded.");
		} else {
			LogResult.fail("List/Select section is not expanded.");
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
	public void clickOnListLocalBtn() {
		listLocalBtn.click();

		wait.until(ExpectedConditions.visibilityOf(batchFilesPanel));

		if (batchFilesPanel.isDisplayed()) {
			LogResult.pass("List local button is clicked.");
		} else {
			LogResult.fail("List local button is not clicked.");
		}
	}

	// To verify if saved Batch file is present in first row in Batch Jobs local
	// listing
	public void verifyLocallySavedBatchFile(String batchFileString) {

		wait.until(ExpectedConditions.visibilityOf(dateModifiedTableHeader));

		dateModifiedTableHeader.click();

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

		String helpTx = "Import - Allows you to select a local batch file and upload it to the server";

		if (batchJobHelpTx.getText().contains(helpTx)) {
			LogResult.pass("Batch Job help text is displayed.");
		} else {
			LogResult.fail("Batch Job help text is not displayed.");
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

	// Clicking Upload button
	public void clickOnUploadBtn() {
		uploadBtn.click();
	}

	// Selecting first row
	public void selectFirstRow() {

		dateModifiedTableHeader.click();

		firstRowCheckbx.click();

		if (firstRowCheckbx.isSelected()) {
			LogResult.pass("First row is selected");
		} else {
			LogResult.fail("First row is not selected");
		}
	}

	// Clicking on Details button
	public void clickOnDetailsBtn() throws InterruptedException {

		listDetailsBtn.click();

		Thread.sleep(50000);

		wait.until(ExpectedConditions.visibilityOf(batchFileDetailsPanel));

		if (batchFileDetailsPanel.isDisplayed()) {
			LogResult.pass("Details button is clicked.");
		} else {
			LogResult.fail("Details button is not clicked.");
		}
	}

	// To verify Batch file details UI
	public void verifyBatchFileDetailsUI(String firstRowBatchfileName) {

		String batchDetailsHelpTx = "The following packages will be submitted to be built and tested in order.";

		if (detailsHelpTxt.getText().contains(batchDetailsHelpTx)) {
			LogResult.pass("Details help text is displayed.");
		} else {
			LogResult.fail("Details help text is not clicked.");
		}

		if (saveDetailsTbx.isDisplayed()) {
			LogResult.pass("Details text box is displayed.");
		} else {
			LogResult.fail("Details text box is not clicked.");
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

		if (detailBuildServersBtn.isDisplayed()) {
			LogResult.pass("Build Servers button is displayed.");
		} else {
			LogResult.fail("Build Servers button is not displayed.");
		}

		if (detailBuildAndTestBtn.isDisplayed()) {
			LogResult.pass("Build+Test button is displayed.");
		} else {
			LogResult.fail("Build+Test button is not displayed.");
		}

		if (detailBackBtn.isDisplayed()) {
			LogResult.pass("Back button is displayed.");
		} else {
			LogResult.fail("Back button is not displayed.");
		}

	}

	// To verify Batch config headers
	public void verifyBatchConfigHeaders() {
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
		if (batchConfigSettings.isDisplayed()) {
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
		if (batchRepoUpBtn.isDisplayed()) {
			LogResult.pass("Up button is displayed in Actions.");
		} else {
			LogResult.fail("Up button is not displayed in Actions.");
		}

		if (batchRepoDownBtn.isDisplayed()) {
			LogResult.pass("Down button is displayed in Actions.");
		} else {
			LogResult.fail("Down button is not displayed in Actions.");
		}

		if (batchRepoRemoveBtn.isDisplayed()) {
			LogResult.pass("Remove button is displayed in Actions.");
		} else {
			LogResult.fail("Remove button is not displayed in Actions.");
		}
	}
}
