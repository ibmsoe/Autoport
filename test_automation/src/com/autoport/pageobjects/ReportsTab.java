package com.autoport.pageobjects;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.pagefactory.AjaxElementLocatorFactory;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.FluentWait;

import com.autoport.utilities.LogResult;

public class ReportsTab {
	WebDriver driver;
	FluentWait<WebDriver> wait;

	public ReportsTab(WebDriver driver, FluentWait<WebDriver> wait) {
		this.driver = driver;
		this.wait = wait;
		AjaxElementLocatorFactory factory = new AjaxElementLocatorFactory(driver, 5);
		PageFactory.initElements(factory, this);
	}

	@FindBy(id = "jobManageButton")
	WebElement manageProjectResults;

	@FindBy(id = "projectFilter")
	WebElement projectResultTextBox;

	@FindBy(id = "batchReportFilter")
	WebElement batchResultTextBox;

	@FindBy(xpath = "//div[@id='jobManagePanel']/div[1]/div[2]/a[1]/button")
	WebElement listLocalBtn;

	@FindBy(xpath = "//div[@id='testResultsPanel']/div[1]/div[2]/a[1]/button")
	WebElement batchlistLocalBtn;

	@FindBy(xpath = "//div[@id='jobManagePanel']/div[1]/div[2]/a[2]/button")
	WebElement listArchivedBtn;

	@FindBy(xpath = "//div[@id='jobManagePanel']/div[1]/div[2]/a[3]/button")
	WebElement listAllBtn;

	@FindBy(xpath = "//table[@id='testCompareSelectPanel']/thead/tr/th[7]/div[1]")
	WebElement dateCompletedHeader;

	@FindBy(xpath = "//table[@id='batchReportListSelectTable']/thead/tr/th[8]/div[1]")
	WebElement dateSubmittedHeader;

	@FindBy(xpath = "//table[@id='testCompareSelectPanel']//td[7]")
	List<WebElement> dateCompletedColumnValues;

	@FindBy(xpath = "//table[@id='batchReportListSelectTable']//td[8]")
	List<WebElement> dateSubmittedColumnValues;

	@FindBy(id = "testResultsButton")
	WebElement manageBatchJobResults;

	@FindBy(xpath = "//table[@id='testCompareSelectPanel']/tbody/tr")
	List<WebElement> manageBatchJobResultsRows;

	@FindBy(xpath = "//table[@id='testCompareSelectPanel']/tbody/tr/td[5]")
	List<WebElement> manageProjectJobResultsBuildServerColumnValue;

	@FindBy(xpath = "//table[@id='testCompareSelectPanel']/tbody/tr/td[2]")
	List<WebElement> manageProjectJobResultsProjectColumnValue;

	@FindBy(xpath = "//table[@id='testCompareSelectPanel']/tbody/tr/td[3]")
	List<WebElement> manageProjectJobResultsVersionColumnValue;

	@FindBy(xpath = "//table[@id='batchReportListSelectTable']/tbody/tr/td[4]")
	List<WebElement> manageBatchJobResultsVersionColumnValue;

	@FindBy(xpath = "//table[@id='batchReportListSelectTable']/tbody/tr/td[3]")
	List<WebElement> manageBatchJobResultsBuildServerColumnValue;

	@FindBy(xpath = "//table[@id='batchReportListSelectTable']/tbody/tr/td[2]")
	List<WebElement> manageBatchJobResultsBatchNameColumnValue;

	public void enterProjectNameForSearch(String searchTerm) {
		wait.until(ExpectedConditions.visibilityOf(projectResultTextBox));

		projectResultTextBox.sendKeys(searchTerm);
	}

	public void enterBatchNameForSearch(String searchTerm) {
		wait.until(ExpectedConditions.visibilityOf(batchResultTextBox));

		batchResultTextBox.sendKeys(searchTerm);
	}

	public void clickOnManageCompareProjectResultsBtn() {
		manageProjectResults.click();

		LogResult.pass("Manage/Compare Project Results button is clicked.");

	}

	public void clickOnManageCompareBatchJobsResultsBtn() {

		manageBatchJobResults.click();

		LogResult.pass("Manage/Compare Batch Jobs Results button is clicked.");
	}

	public void clickOnListLocalBtn() {

		wait.until(ExpectedConditions.visibilityOf(listLocalBtn));

		listLocalBtn.click();

		LogResult.pass("List Local button is clicked.");
	}

	public void clickOnBatchListLocalBtn() {

		wait.until(ExpectedConditions.visibilityOf(batchlistLocalBtn));

		batchlistLocalBtn.click();

		LogResult.pass("List Local button is clicked.");
	}

	public void clickOnDateCompletedHeader() {

		dateCompletedHeader.click();

		LogResult.pass("Date Completed header is clicked.");
	}

	public void clickOnDateSubmittedHeader() {

		dateSubmittedHeader.click();

		LogResult.pass("Date Submitted header is clicked.");
	}

	// To verify completion of Jenkins job in case of Project
	public void verifyJenkinsJobCompletion(String buildClickTime, int buildServersCount) throws ParseException {

		int i = 0;

		Date temp = new SimpleDateFormat("yyyy-MM-dd-'h'HH-'m'mm-'s'ss").parse(buildClickTime);

		for (WebElement item : dateCompletedColumnValues) {

			Date temp1 = new SimpleDateFormat("yyyy-MM-dd-'h'HH-'m'mm-'s'ss").parse(item.getText());

			if (temp.before(temp1)) {
				i++;
			}

		}

		if (i == 0) {
			LogResult.fail("None of the project jobs got completed.");
		}

		else if (i < buildServersCount) {
			LogResult.fail("Some of the project jobs are still running. Project jobs that got completed are: ");

			for (int j = 0; j < i; j++) {

				LogResult.pass(manageProjectJobResultsVersionColumnValue.get(j).getText() + " version of" + " Project "
						+ manageProjectJobResultsProjectColumnValue.get(j).getText()
						+ " got completed on build servers: "
						+ manageProjectJobResultsBuildServerColumnValue.get(j).getText());
			}

		}

		else if (i == buildServersCount) {

			LogResult.pass("All project jobs got completed. Project jobs that got completed are: ");

			for (int j = 0; j < i; j++) {

				LogResult.pass(manageProjectJobResultsVersionColumnValue.get(j).getText() + " version of" + " Project "
						+ manageProjectJobResultsProjectColumnValue.get(j).getText()
						+ " got completed on build servers: "
						+ manageProjectJobResultsBuildServerColumnValue.get(j).getText());
			}
		}

		else if (i > buildServersCount) {
			LogResult.fail(
					"Completed project jobs count exceeds that of selected build servers. Project jobs that got completed are: ");

			for (int j = 0; j < i; j++) {

				LogResult.pass(manageProjectJobResultsVersionColumnValue.get(j).getText() + " version of" + " Project "
						+ manageProjectJobResultsProjectColumnValue.get(j).getText()
						+ " got completed on build servers: "
						+ manageProjectJobResultsBuildServerColumnValue.get(j).getText());
			}
		}

	}

	// To verify completion of Jenkins job in case of Batch
	public void verifyJenkinsJobCompletionForBatch(String buildClickTime, int buildServersCount) throws ParseException {

		int i = 0;

		Date temp = new SimpleDateFormat("yyyy-MM-dd-'h'HH-'m'mm-'s'ss").parse(buildClickTime);

		for (WebElement item : dateSubmittedColumnValues) {

			Date temp1 = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").parse(item.getText());

			if (temp.before(temp1)) {
				i++;
			}

		}

		if (i == 0) {
			LogResult.fail("None of the batch jobs got submitted.");
		}

		else if (i < buildServersCount) {
			LogResult.fail("Some of the batch jobs got submitted. Batch jobs that got submitted are: ");

			for (int j = 0; j < i; j++) {

				LogResult.pass(manageBatchJobResultsVersionColumnValue.get(j).getText() + " version of" + " Batch "
						+ manageBatchJobResultsBatchNameColumnValue.get(j).getText()
						+ " got submitted on build servers: "
						+ manageBatchJobResultsBuildServerColumnValue.get(j).getText());
			}

		}

		else if (i == buildServersCount) {

			LogResult.pass("All batch jobs got completed. Batch jobs that got submitted are: ");

			for (int j = 0; j < i; j++) {

				LogResult.pass(manageBatchJobResultsVersionColumnValue.get(j).getText() + " version of" + " Batch "
						+ manageBatchJobResultsBatchNameColumnValue.get(j).getText()
						+ " got submitted on build servers: "
						+ manageBatchJobResultsBuildServerColumnValue.get(j).getText());
			}
		}

		else if (i > buildServersCount) {
			LogResult.fail(
					"Submitted batch jobs count exceeds that of selected build servers. Batch jobs that got submitted are: ");

			for (int j = 0; j < i; j++) {

				LogResult.pass(manageBatchJobResultsVersionColumnValue.get(j).getText() + " version of" + " Batch "
						+ manageBatchJobResultsBatchNameColumnValue.get(j).getText()
						+ " got submitted on build servers: "
						+ manageBatchJobResultsBuildServerColumnValue.get(j).getText());
			}
		}

	}

}
