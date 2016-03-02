package com.autoport.pageobjects;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

import org.openqa.selenium.Alert;
import org.openqa.selenium.By;
import org.openqa.selenium.NoAlertPresentException;
import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.pagefactory.AjaxElementLocatorFactory;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.FluentWait;
import org.testng.Assert;

import com.autoport.utilities.LogResult;

public class ReportsTab {
	WebDriver driver;
	FluentWait<WebDriver> wait;
	
	public ReportsTab(WebDriver driver, FluentWait<WebDriver> fluintWait ){
		this.driver = driver;
		this.wait = fluintWait;
		AjaxElementLocatorFactory factory = new AjaxElementLocatorFactory(driver, 5);
		PageFactory.initElements(factory, this);
	}
	
	@FindBy(id="jobManageButton")
    WebElement manageCompareProjectResults;
	
	@FindBy(id="projectFilter")
    WebElement projectResultTextBox;
	
	@FindBy(xpath="//div[@id='jobManagePanel']/div[1]/div[2]/a[1]/button")
    WebElement projectListLocalBtn;
	
	@FindBy(xpath="//div[@id='jobManagePanel']/div[1]/div[2]/a[2]/button")
    WebElement projectListArchivedBtn;
	
	@FindBy(xpath="//div[@id='jobManagePanel']/div[1]/div[2]/a[3]/button")
    WebElement projectListAllBtn;
	
	@FindBy(id="testCompareRunAlert")
    WebElement listInformationMessage;
	
	@FindBy(id="testCompareSelectPanel")
    WebElement projectResultsTable;
	
	@FindBy(xpath="//div[@id='jobManagePanel']//span[@class='page-list']/span/button")
    WebElement noOfRecordsBtn;
	
	@FindBy(id="testHistoryBtn")
    WebElement projectTestHistoryBtn;
	
	@FindBy(id="testDetailBtn")
    WebElement projectTestDetailBtn;
	
	@FindBy(id="compareResultsBtn")
    WebElement projectTestCompareBtn;
	
	@FindBy(id="testResultsTable")
    WebElement ProjectTestCompareTable;
	
	@FindBy(id="compareBuildLogsBtn")
    WebElement projectBuildLogCompareBtn;
	
	@FindBy(id="logdiffModal")
    WebElement projectBuildLogCompareTable;
	
	@FindBy(id="compareTestLogsBtn")
    WebElement projectTestLogCompareBtn;
	
	@FindBy(id="logdiffModal")
    WebElement projectTestLogCompareTable;
	
	@FindBy(id="resultArchiveBtn")
    WebElement projectResultArchiveBtn;
	
	@FindBy(id="resultRemoveBtn")
    WebElement projectResultRemoveBtn;
	
	@FindBy(id="testResultsTable")
    WebElement ProjectTestHistoryTable;
	
	@FindBy(id="testResultsTable")
    WebElement ProjectTestDetailTable;
	
	@FindBy(xpath="//div[@id='testCompareTablePanel']/div[2]/div[1]/a/button")
    WebElement backToListBtn;
	
	@FindBy(xpath="//div[@id='errorAlert']/div/div/div[3]/button")
    WebElement errorCloseBtn;
	
	@FindBy(id="viewBuildLogBtn")
    WebElement viewBuildLogBtn;
	
	@FindBy(id="logdiffModal")
    WebElement projectBuildLogTable;
	
	@FindBy(id="viewTestLogBtn")
    WebElement viewTestLogBtn;
	
	@FindBy(id="logdiffModal")
    WebElement projectTestLogTable;
	
	/* WebElements for batch job section */
	@FindBy(id="testResultsButton")
    WebElement manageCompareBatchJobResults;
	
	@FindBy(id="batchReportFilter")
    WebElement BatchJobResultsTextBox;
		
	@FindBy(xpath="//div[@id='testResultsPanel']/div[1]/div[2]/a[1]/button")
    WebElement batchJobListLocalBtn;
	
	@FindBy(xpath="//div[@id='testResultsPanel']/div[1]/div[2]/a[2]/button")
    WebElement batchJobListArchivedBtn;
	
	@FindBy(xpath="//div[@id='testResultsPanel']/div[1]/div[2]/a[3]/button")
    WebElement batchJobListAllBtn;
	
	@FindBy(id="batchReportListSelectTable")
    WebElement batchJobsSearchResultsTable;
	
	@FindBy(id="batch_report_history")	 
    WebElement batchJobsTestHistoryBtn;
	
	@FindBy(id="batch_report_detail")	 
    WebElement batchJobsTestDetailsBtn;
	
	@FindBy(id="batch_report_compare")	 
    WebElement batchJobsTestCompareBtn;
	
	@FindBy(id="batch_report_compare_build_log")	 
    WebElement batchJobsBuildLogCompareBtn;
	
	@FindBy(id="batch_report_compare_test_log")	 
    WebElement batchJobsTestLogCompareBtn;
	
	@FindBy(id="batch_report_archive")	 
    WebElement batchJobsArchiveBtn;
	
	@FindBy(id="batch_report_remove")	 
    WebElement batchJobsRemoveBtn;
	
	@FindBy(id="testBatchResultsTable")	 
    WebElement batchJobsTestHistoryTable;
	
	@FindBy(id="testBatchResultsTable")	 
    WebElement batchJobsTestDetailsTable;
	
	@FindBy(id="testBatchResultsTable")	 
    WebElement batchJobsTestCompareTable;
	
	@FindBy(id="testBatchLogResultsTable")	 
    WebElement batchJobsBuildLogCompareTable;
	
	@FindBy(id="testBatchLogResultsTable")	 
    WebElement batchJobsTestLogCompareTable;
	
	@FindBy(xpath="//div[@id='testBatchCompareTablePanel']/div[2]/div[1]/a/button")	 
    WebElement batchJobsBackToListBtn;
	
	@FindBy(xpath="//div[@id='testBatchCompareLog']/a/button")	 
    WebElement batchJobsBackToComparisonBtn;
	
	@FindBy(id = "jobManageButton")
	WebElement manageProjectResults;

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

	
	/***********************************************************************/
	
	/* Function to click on Manage/Compare project results section */
	public void clickManageCompareProjectResultsButton(){
		if(projectResultTextBox.isDisplayed()){
			LogResult.pass("Manage/Compare project results is opened");
		}
		else{
			manageCompareProjectResults.click();
			if(projectResultTextBox.isDisplayed()){
				LogResult.pass("Manage/Compare project results is opened");
			}
			else{
				LogResult.fail("Manage/Compare project results is not opened");
			}			
		}
	}
	
	/* Function to enter project results to search in Search project results text box*/
	public void enterProjectResultToSearch(String projectResult) throws InterruptedException{		
		projectResultTextBox.clear();
		projectResultTextBox.sendKeys(projectResult);	
		Thread.sleep(1000);
		
		if(projectResultTextBox.getAttribute("value").contains(projectResult)){
			LogResult.pass("user is able to enter project Result in search box.");
		}
		else{
			LogResult.fail("user is not able to enter project Result in search box.");
		}
	}
	
	/* Function to enter project results to search in Search project results text box*/
	public void clearSearchedProjectResult(){
//		projectResultTextBox.click();
		projectResultTextBox.clear();
	}
	
	/* Function to verify the search results for the packagename entered in search box */
	public void verifySearchResultsforProject(String EnteredProjectname){
		
		List<WebElement> projectnames = driver.findElements(By.xpath("//table[@id='testCompareSelectPanel']/tbody/tr/td[2]"));
		int noOfProjects = 0;
		
		for (WebElement projectname : projectnames){			
			
			if (projectname.getText().contains(EnteredProjectname)){
				noOfProjects++;				
			}
			else{
				LogResult.fail("Search Results are not correct for project searched.");
				break;
			}
		}
		
		if (noOfProjects == projectnames.size()){
			LogResult.pass("Search Results are correct for project searched.");
		}
	}
		
	/* Function to click on List Local Project ResultsButton */
	public void clickListLocalProjectResultsButton(){
		projectListLocalBtn.click();
		
		wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("testCompareRunAlert")));
				
		if(projectResultsTable.isDisplayed()){
			LogResult.pass("Project results are displayed in table");
		}
		else{
			LogResult.fail("Project results are not displayed in table");
		}
	}
		
	/* Function to click on List Archived Project Results Button */
	public void clickListArchivedProjectResultsButton(){
		projectListArchivedBtn.click();
		try{
			wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("testCompareRunAlert")));
					
			if(projectResultsTable.isDisplayed()){
				LogResult.pass("Project results are displayed in table");
			}
			else{
				LogResult.fail("Project results are not displayed in table");
			}
		}
		
		catch(Exception e)
		{
			if(errorCloseBtn.isDisplayed()){
				
				String errorMessage = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div")).getText();
				LogResult.fail(errorMessage);
				errorCloseBtn.click();
				Assert.fail(errorMessage);
			}
		}
	}
	
	/* Function to click on List All Project Results Button */
	public void clickListAllProjectResultsButton(){
		projectListAllBtn.click();
		try{
		wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("testCompareRunAlert")));
				
		if(projectResultsTable.isDisplayed()){
			LogResult.pass("Project results are displayed in table");
		}
		else{
			LogResult.fail("Project results are not displayed in table");
		}
		}
		catch(Exception e)
		{
			if(errorCloseBtn.isDisplayed()){
				
				String errorMessage = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div")).getText();
				LogResult.fail(errorMessage);
				errorCloseBtn.click();
				Assert.fail(errorMessage);
			}
		}
	}
	
	/*Function to verify only local project results are displayed */
	public void verifyOnlyLocalProjectResultsDisplayed() throws InterruptedException{
		
		selectMaximumRecordsToDisplay();
		
		List<WebElement> repositoryTypes = driver.findElements(By.xpath("//table[@id='testCompareSelectPanel']/tbody/tr/td[6]"));
		
		int noOfrepositoryTypes = 0;
		for (WebElement repositoryType : repositoryTypes){			
			noOfrepositoryTypes++;
			if (!(repositoryType.getText().equals("local"))){
				LogResult.fail("Only Local project results are not displayed");
				break;
			}
		}
		
		if (noOfrepositoryTypes == repositoryTypes.size()){
			LogResult.pass("Only Local project results are displayed");
		}
	}
	
	/*Function to verify only Archived project results are displayed */
	public void verifyOnlyArchivedProjectResultsDisplayed() throws InterruptedException{
		
		selectMaximumRecordsToDisplay();
		
		List<WebElement> repositoryTypes = driver.findElements(By.xpath("//table[@id='testCompareSelectPanel']/tbody/tr/td[6]"));
		
		int noOfrepositoryTypes = 0;
		for (WebElement repositoryType : repositoryTypes){			
			noOfrepositoryTypes++;
			if (!(repositoryType.getText().equals("sftp"))){
				LogResult.fail("Only Archived project results are not displayed");
				break;
			}
		}
		
		if (noOfrepositoryTypes == repositoryTypes.size()){
			LogResult.pass("Only Archived project results are displayed");
		}
	}
		
	/*Function to verify All project results are displayed */
	public void verifyAllProjectResultsDisplayed() throws InterruptedException{
		
		selectMaximumRecordsToDisplay();
		
		List<WebElement> repositoryTypes = driver.findElements(By.xpath("//table[@id='testCompareSelectPanel']/tbody/tr/td[6]"));
		
		int noOfrepositoryTypes = 0;
		for (WebElement repositoryType : repositoryTypes){			
			noOfrepositoryTypes++;
			
			String strRepositoryType = repositoryType.getText();
			if (!(strRepositoryType.equals("local") || strRepositoryType.equals("sftp"))){
				LogResult.fail(strRepositoryType + " results are also displayed");
				break;
			}
		}
		
		if (noOfrepositoryTypes == repositoryTypes.size()){
			LogResult.pass("All project results are displayed");
		}
	}
	
	/* Function to select maximum records to display */
	public void selectMaximumRecordsToDisplay() throws InterruptedException{
		
		if(noOfRecordsBtn.isDisplayed()){
			noOfRecordsBtn.click();
		Thread.sleep(1000);
		
		driver.findElement(By.xpath("//div[@id='jobManagePanel']//span[@class='page-list']/span/ul/li[last()]/a")).click();
		Thread.sleep(5000);
		}
	}
	
	/* Function to select the the checkbox for package */
	public void selectCheckboxForPackage(String packagename){
		String xpath = "//table[@id='testCompareSelectPanel']/tbody/tr/td[2][text()[contains(.,'" + packagename + "')]]/ancestor::tr[1]/td[1]/input";
		driver.findElement(By.xpath(xpath)).click();
	}
	
	/*Function to verify if buttons are enabled */
	public void verifyButtonsAreEnabled(){
		
		if(projectTestHistoryBtn.isEnabled() && projectTestDetailBtn.isEnabled() && projectResultRemoveBtn.isEnabled() && projectResultArchiveBtn.isEnabled()){
			LogResult.pass("Test History, Test Detail, Archive and Remeve buttons are enabled");
		}
		else{
			LogResult.fail("Test History, Test Detail, Archive and Remeve buttons are not enabled");
		}
	}
	
	/*Function to verify if buttons are disabled*/
	public void verifyButtonsAreDisabled(){
		
		if(projectTestHistoryBtn.isEnabled() || projectTestDetailBtn.isEnabled() || projectResultRemoveBtn.isEnabled() || projectListArchivedBtn.isEnabled()){
			LogResult.fail("Test History, Test Detail, Archive and Remeve buttons are not disabled.");
		}
		else{			
			LogResult.pass("Test History, Test Detail, Archive and Remeve buttons are disabled");
		}
	}
	
	/*Function to click on TestHistory Button */
	public void clickTestHistoryButton(){
		
		projectTestHistoryBtn.click();		
		try{
			wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("testResultsTable")));
			
			if(ProjectTestHistoryTable.isDisplayed()){
				LogResult.pass("Project Test History is displayed in table");
			}
			else
				LogResult.fail("Project Test History is not displayed in table");			
		}
		catch(Exception e)
		{
			if(errorCloseBtn.isDisplayed()){
				
				String errorMessage = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div")).getText();
				LogResult.fail(errorMessage);
				errorCloseBtn.click();
				Assert.fail(errorMessage);
			}
		}
	}
	
	/*Function to click on Test Detail Button */
	public void clickTestDetailButton(){
		
		projectTestDetailBtn.click();	
		
		try{
			wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("testResultsTable")));
			
			if(ProjectTestDetailTable.isDisplayed()){
				LogResult.pass("Project Test Details are displayed in table");
			}
			else
				LogResult.fail("Project Test Details are displayed in table");			
		}
		catch(Exception e)
		{
			if(errorCloseBtn.isDisplayed()){
				
				String errorMessage = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div")).getText();
				LogResult.fail(errorMessage);
				errorCloseBtn.click();
				Assert.fail(errorMessage);
			}
		}
	}
	
	public void clickBackToListButton(){		
		
		if(backToListBtn.isDisplayed()){
			backToListBtn.click();
		}		
	}	
	
	/*Function to click on Archive Projects results button */
	public void clickArchiveProjectResultsBtn(){
		
		projectResultArchiveBtn.click();
	}
	
	
	
	
	/*Function to click on remove Projects results button*/
	public void clickRemoveProjectResultsBtn() throws InterruptedException{
		
		projectResultRemoveBtn.click();
		Thread.sleep(2000);
		
		try{
			Alert alert = driver.switchTo().alert();
			String alertmsg = alert.getText();
			alert.accept();		
		}
		catch(NoAlertPresentException e){
			e.printStackTrace();
		}		
	}
	
	/* Function to verify if deleted successfully pop up message is displayed correctly */	
	public void verifyDeletedSuccessfullyMsg(){
		
		wait.until(ExpectedConditions.visibilityOfElementLocated(By.xpath("//div[@id='errorAlert']/div/div/div[1]")));
		
		String message = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div/div[1]")).getText();
		
		if(message.contains("Deleted Successfully")){
			LogResult.pass("Deleted Successfully message is displayed correctly.");
		}
		else{
			LogResult.fail("Deleted Successfully message is not displayed correctly.");
		}		
		driver.findElement(By.xpath("//div[@id='errorAlert']/div/div/div[3]/button")).click();
	}
	
	/*Function to sort results by date completed */
	public void sortResultsByDateCompletedDescending() throws InterruptedException{
		
		driver.findElement(By.xpath("//table[@id='testCompareSelectPanel']/thead/tr/th[7]/div[1]")).click();	
		Thread.sleep(3000);
		
		String firstdatestring = driver.findElement(By.xpath("//table[@id='testCompareSelectPanel']/tbody/tr[1]/td[7]")).getText();
		String lastdatestring = driver.findElement(By.xpath("//table[@id='testCompareSelectPanel']/tbody/tr[last()]/td[7]")).getText();
		
		SimpleDateFormat formatter = new SimpleDateFormat("EEE MMM dd HH:mm:ss yyyy");
		try {

			Date date1 = formatter.parse(firstdatestring);
			Date date2 = formatter.parse(lastdatestring);
			
			if(date1.after(date2) || date1.equals(date2)){				
				
			}
			else{				
				driver.findElement(By.xpath("//table[@id='testCompareSelectPanel']/thead/tr/th[7]/div[1]")).click();
				Thread.sleep(3000);				
			}
		} catch (ParseException e) {
			e.printStackTrace();
		}
	}
	
	/* Function to select the Project Results to compare */
	public void selectProjectResultsToCompare(String packagename){
		
		List<WebElement> pkgCheckbox  =	driver.findElements(By.xpath("//table[@id='testCompareSelectPanel']/tbody/tr/td[2][text()[contains(.,'" + packagename + "')]]/ancestor::tr[1]/td[1]/input"));
				
		pkgCheckbox.get(0).click();
		
		pkgCheckbox.get(1).click();
		
	}
	
	/*Function to verify if compare buttons are enabled for projectResults */
	public void verifyCompareButtonsAreEnabledForProjectResults(){
		
		if(projectTestCompareBtn.isEnabled() && projectBuildLogCompareBtn.isEnabled() && projectTestLogCompareBtn.isEnabled()){
			LogResult.pass("Test compare, Build Log Compare and test log compare buttons are enabled");
		}
		else{
			LogResult.fail("Test compare, Build Log Compare and test log compare buttons are not enabled");
		}
	}
	
	/* Function to click on Test compare button for project results */
	public void clickTestCompareForProjectresults(){
		projectTestCompareBtn.click();		
		try{
			wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("testResultsTable")));
			if(ProjectTestDetailTable.isDisplayed()){
				LogResult.pass("Project Test Compare Details are displayed in table");
			}
			else
				LogResult.fail("Project Test Compare Details are not displayed in table");			
		}
		catch(Exception e)
		{
			if(errorCloseBtn.isDisplayed()){
				
				String errorMessage = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div")).getText();
				LogResult.fail(errorMessage);
				errorCloseBtn.click();
				Assert.fail(errorMessage);
			}
		}	
	}
	
	/* Function to click on Build Log compare button for project results */
	public void clickBuildLogCompareForProjectresults(){
		projectBuildLogCompareBtn.click();	
		
		try{
			wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("logdiffModal")));
			
			if(projectBuildLogCompareTable.isDisplayed()){
				LogResult.pass("Project Build Log Compare Details are displayed in Panel");
			}
			else
				LogResult.fail("Project Test Compare Details are not displayed in table");
			
		}
		catch(Exception e)
		{
			if(errorCloseBtn.isDisplayed()){
				
				String errorMessage = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div")).getText();
				LogResult.fail(errorMessage);
				errorCloseBtn.click();
				Assert.fail(errorMessage);
			}
		}
	}
	
	/* Function to click on Build Log compare button for project results */
	public void clickTestLogCompareForProjectresults(){
		projectTestLogCompareBtn.click();
		
		try{
			wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("logdiffModal")));
			
			if(projectTestLogCompareTable.isDisplayed()){
				LogResult.pass("Project Test Log Compare Details are displayed in Panel");
			}
			else
				LogResult.fail("Project Test Log Compare Details are not displayed in Panel");
			
		}
		catch(Exception e)
		{
			if(errorCloseBtn.isDisplayed()){
				
				String errorMessage = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div")).getText();
				LogResult.fail(errorMessage);
				errorCloseBtn.click();
				Assert.fail(errorMessage);
			}
		}		
	}
	
	/* Function to to verify log comparision for project results and close the panel*/
	 public void verifyAndCloseLogCompareForProjectresults(){
		driver.findElement(By.xpath("//div[@id='logdiffModal']/div/div/div[3]/button")).click();		 
	}
	 
	 /*Function to click on View Build Logs Button*/
	 public void clickViewBuildLogBtn() throws InterruptedException{
	 viewBuildLogBtn.click(); 
	 Thread.sleep(4000);
	 	try{
	 		wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("logdiffModal")));
			
			if(projectBuildLogTable.isDisplayed()){
				LogResult.pass("Project Build Logs are displayed in the table.");
			}
			else
				LogResult.fail("Project Build Logs are not displayed in the table.");
			
		}
		catch(Exception e)
		{
			if(errorCloseBtn.isDisplayed()){
				
				String errorMessage = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div")).getText();
				LogResult.fail(errorMessage);
				errorCloseBtn.click();
				Assert.fail(errorMessage);
			}
		}
			
	 }	 
	 
	 /*Function to click on View Test Logs Button*/
	 public void clickViewTestLogBtn() throws InterruptedException{
		viewTestLogBtn.click();
		 Thread.sleep(4000);
		try{
			wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("logdiffModal")));
			
			if(projectTestLogTable.isDisplayed()){
				LogResult.pass("Project Test Logs are displayed in the table.");
			}
			else
				LogResult.fail("Project Test Logs are not displayed in the table.");			
		}
		catch(Exception e)
		{
			if(errorCloseBtn.isDisplayed()){
				
				String errorMessage = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div")).getText();
				LogResult.fail(errorMessage);
				errorCloseBtn.click();
				Assert.fail(errorMessage);
			}
		}
	 }
	 
	 /* Function to to close log table for project results*/
	 public void closeLogTableForProject(){
		driver.findElement(By.xpath("//div[@id='logdiffModal']/div/div/div[3]/button")).click();
		 
	}
	 
	 /*************************************************************/
	 
	 /* Function to click on Manage/Compare project results section */
	public void clickManageCompareBatchJobsResultsButton(){		
		if(BatchJobResultsTextBox.isDisplayed()){
			LogResult.pass("Manage/Compare batch jobs results is opened");
		}
		else{
			manageCompareBatchJobResults.click();
			if(BatchJobResultsTextBox.isDisplayed()){
				LogResult.pass("Manage/Compare batch jobs results is opened");
			}
			else{
				LogResult.fail("Manage/Compare batch jobs results is not opened");
			}			
		}
	}
	
	/* Function to enter Batch Job results to search in Search batch job results text box*/
	public void enterBatchJobResultToSearch(String BatchJobResult) throws InterruptedException{
			
		BatchJobResultsTextBox.clear();
		BatchJobResultsTextBox.sendKeys(BatchJobResult);	
		Thread.sleep(1000);
		
		if(BatchJobResultsTextBox.getAttribute("value").contains(BatchJobResult)){
			LogResult.pass("user is able to enter Batch Job Result in search box.");
		}
		else{
			LogResult.fail("user is not able to enter Batch Job Result in search box.");
		}
	}
	
	/* Function to clear batch Job results entered in Search project results text box*/
	public void clearSearchedBatchJobResult(){
//		BatchJobResultsTextBox.click();
		BatchJobResultsTextBox.clear();
	}
	
	/* Function to verify the search results for the batch Job entered in search box */
	public void verifySearchResultsforBatchJob(String enteredBatchJobname){
		
		List<WebElement> batchJobnames = driver.findElements(By.xpath("//table[@id='batchReportListSelectTable']/tbody/tr/td[2]"));
		int noOfProjects = 0;
		
		for (WebElement batchJobname : batchJobnames){			
			
			if (batchJobname.getText().contains(enteredBatchJobname)){
				noOfProjects++;				
			}
			else{
				LogResult.fail("Search Results are not correct for Batch Job searched.");
				break;
			}
		}
		
		if (noOfProjects == batchJobnames.size()){
			LogResult.pass("Search Results are correct for Batch Job searched.");
		}
	}
		
	/* Function to click on List Local batch jobs ResultsButton */
	public void clickListLocalBatchJobResultsButton(){
		batchJobListLocalBtn.click();
		
		wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("batchReportListSelectTable")));
				
		if(batchJobsSearchResultsTable.isDisplayed()){
			LogResult.pass("batch jobs results are displayed in table");
		}
		else{
			LogResult.fail("batch jobs results are not displayed in table");
		}
	}
		
	/* Function to click on List Archived Batch Jobs Results Button */
	public void clickListArchivedBatchJobsResultsButton(){
		batchJobListArchivedBtn.click();
		try{
		wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("batchReportListSelectTable")));
				
		if(batchJobsSearchResultsTable.isDisplayed()){
			LogResult.pass("batch jobs results are displayed in table");
		}
		else{
			LogResult.fail("batch jobs results are not displayed in table");
		}
		}
		
		catch(Exception e)
		{
			if(errorCloseBtn.isDisplayed()){
				
				String errorMessage = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div")).getText();
				LogResult.fail(errorMessage);
				errorCloseBtn.click();
				Assert.fail(errorMessage);
			}
		}
	}
	
	/* Function to click on List All Batch Jobs Results Button */
	public void clickListAllBatchJobsResultsButton(){
		batchJobListAllBtn.click();
		
		wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("batchReportListSelectTable")));
		try{		
		if(batchJobsSearchResultsTable.isDisplayed()){
			LogResult.pass("batch job results are displayed in table");
		}
		else{
			LogResult.fail("batch job results are not displayed in table");
		}
		}
		
		catch(Exception e)
		{
			if(errorCloseBtn.isDisplayed()){
				
				String errorMessage = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div")).getText();
				LogResult.fail(errorMessage);
				errorCloseBtn.click();
				Assert.fail(errorMessage);
			}
		}
	}
	
	/*Function to verify only local Batch Jobs results are displayed */
	public void verifyOnlyLocalBatchJobResultsDisplayed() throws InterruptedException{
		
		selectMaximumBatchJobRecordsToDisplay();
		
		List<WebElement> repositoryTypes = driver.findElements(By.xpath("//table[@id='batchReportListSelectTable']/tbody/tr/td[4]"));
		
		int noOfrepositoryTypes = 0;
		for (WebElement repositoryType : repositoryTypes){			
			noOfrepositoryTypes++;
			if (!(repositoryType.getText().equals("local"))){
				LogResult.fail("Only Local batch Job results are not displayed");
				break;
			}
		}
		
		if (noOfrepositoryTypes == repositoryTypes.size()){
			LogResult.pass("Only Local batch Job results are displayed");
		}
	}
	
	/*Function to verify only Archived batch Job results are displayed */
	public void verifyOnlyArchivedBatchJobResultsDisplayed() throws InterruptedException{
		
		selectMaximumBatchJobRecordsToDisplay();
		
		List<WebElement> repositoryTypes = driver.findElements(By.xpath("//table[@id='batchReportListSelectTable']/tbody/tr[3]/td[6]"));
		
		int noOfrepositoryTypes = 0;
		for (WebElement repositoryType : repositoryTypes){			
			noOfrepositoryTypes++;
			if (!(repositoryType.getText().equals("sftp"))){
				LogResult.fail("Only Archived batch Job results are not displayed");
				break;
			}
		}
		
		if (noOfrepositoryTypes == repositoryTypes.size()){
			LogResult.pass("Only Archived batch Job results are displayed");
		}
	}
		
	/*Function to verify All batch Job results are displayed */
	public void verifyAllBatchJObResultsDisplayed() throws InterruptedException{
		
		selectMaximumBatchJobRecordsToDisplay();
		
		List<WebElement> repositoryTypes = driver.findElements(By.xpath("//table[@id='batchReportListSelectTable']/tbody/tr/td[4]"));
		
		int noOfrepositoryTypes = 0;
		for (WebElement repositoryType : repositoryTypes){			
			noOfrepositoryTypes++;
			
			String strRepositoryType = repositoryType.getText();
			if (!(strRepositoryType.equals("local") || strRepositoryType.equals("sftp"))){
				LogResult.fail(strRepositoryType + " results are also displayed");
				break;
			}
		}
		
		if (noOfrepositoryTypes == repositoryTypes.size()){
			LogResult.pass("All batch Job results are displayed");
		}
	}
	
	/* Function to select maximum records to display */
	public void selectMaximumBatchJobRecordsToDisplay() throws InterruptedException{
		try{
			WebElement noOfRecordsBtn = driver.findElement(By.xpath("//div[@id='testResultsPanel']//span[@class='page-list']/span/button"));
			
			if(noOfRecordsBtn.isDisplayed()){
				noOfRecordsBtn.click();
			Thread.sleep(1000);
			
			driver.findElement(By.xpath("//div[@id='testResultsPanel']//span[@class='page-list']/span/ul/li[last()]/a")).click();
			Thread.sleep(5000);
			}
		}
		catch(NoSuchElementException e){
			e.printStackTrace();			
		}
	}
	
	
	/*   */
	/* Function to select the the checkbox for Batch Job */
	public void selectCheckboxForBatchJob(String batchJobName){
		String xpath = "//table[@id='batchReportListSelectTable']/tbody/tr/td[2][text()[contains(.,'" + batchJobName + "')]]/ancestor::tr[1]/td[1]/input";
		driver.findElement(By.xpath(xpath)).click();
	}
	
	/*Function to verify if buttons are enabled to Manage batch Jobs */
	public void verifyButtonsAreEnabledToManageBatchJobs(){
		
		if(batchJobsTestHistoryBtn.isEnabled() && batchJobsTestDetailsBtn.isEnabled() && batchJobsRemoveBtn.isEnabled() && batchJobsArchiveBtn.isEnabled()){
			LogResult.pass("Test History, Test Detail, Archive and Remeve buttons are enabled for batch Jobs");
		}
		else{
			LogResult.fail("Test History, Test Detail, Archive and Remeve buttons are not enabled for batch jobs");
		}
	}
	
	/*Function to verify if buttons are disabled for batch jobs*/
	public void verifyButtonsAreDisabledToManageBatchJobs(){
		
		if(batchJobsTestHistoryBtn.isEnabled() || batchJobsTestDetailsBtn.isEnabled() || batchJobsRemoveBtn.isEnabled() || batchJobsArchiveBtn.isEnabled()){
			LogResult.fail("Test History, Test Detail, Archive and Remeve buttons are not disabled for batch jobs.");
		}
		else{			
			LogResult.pass("Test History, Test Detail, Archive and Remeve buttons are disabled for batch jobs");
		}
	}
	
	/*Function to click on TestHistory Button for batch job */
	public void clickTestHistoryButtonForBatchJobs(){
		
		batchJobsTestHistoryBtn.click();		
		try{
			wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("testBatchResultsTable")));
			
			if(batchJobsTestHistoryTable.isDisplayed()){
				LogResult.pass("Batch Job Test History is displayed in table");
			}
			else
				LogResult.fail("Batch Job Test History is not displayed in table");
			
		}
		catch(Exception e)
		{
			if(errorCloseBtn.isDisplayed()){
				
				String errorMessage = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div")).getText();
				LogResult.fail(errorMessage);
				errorCloseBtn.click();
				Assert.fail(errorMessage);
			}
		}
	}
	
	/*Function to click on Test Detail Button for batch Jobs */
	public void clickTestDetailButtonForBatchJobs(){
		
		batchJobsTestDetailsBtn.click();
		
		try{
			wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("testBatchResultsTable")));
			
			if(batchJobsTestDetailsTable.isDisplayed()){
				LogResult.pass("Batch Job Test Details are displayed in table");
			}
			else
				LogResult.fail("Batch Job Test Details are displayed in table");
			
		}
		catch(Exception e)
		{
			if(errorCloseBtn.isDisplayed()){
				
				String errorMessage = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div")).getText();
				LogResult.fail(errorMessage);
				errorCloseBtn.click();
				Assert.fail(errorMessage);
			}
		}
	}
	
	public void clickBackToListButtonForBatchJobs(){		
		
		if(batchJobsBackToListBtn.isDisplayed()){
			batchJobsBackToListBtn.click();
		}		
	}	
	
	/*Function to click on Archive Batch Jobs results button */
	public void clickArchiveBatchJobsResultsBtn(){
		
		batchJobsArchiveBtn.click();		
	}
	
	/*Function to click on remove Batch Jobs results button*/
	public void clickRemoveBatchJobsResultsBtn() throws InterruptedException{
		
		batchJobsRemoveBtn.click();
		Thread.sleep(2000);
		
		try{
			Alert alert = driver.switchTo().alert();
			String alertmsg = alert.getText();
			alert.accept();		
		}
		catch(NoAlertPresentException e){
			e.printStackTrace();
			Assert.fail();
		}		
	}
	
	/* Function to verify if Batch job deleted successfully pop up message is displayed correctly */	
	public void verifyBatchJobDeletedSuccessfullyMsg(){
		
		wait.until(ExpectedConditions.visibilityOfElementLocated(By.xpath("//div[@id='errorAlert']/div/div/div[1]")));
		
		String message = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div/div[1]")).getText();
		
		if(message.contains("Deleted Successfully")){
			LogResult.pass("Deleted Successfully message is displayed correctly.");
		}
		else{
			LogResult.fail("Deleted Successfully message is not displayed correctly.");
		}		
		driver.findElement(By.xpath("//div[@id='errorAlert']/div/div/div[3]/button")).click();
	}
	
	/* Function to verify if Batch job archived successfully pop up message is displayed correctly */	
	public void verifyArchivedSuccessfullyMsg() throws InterruptedException{ 
		
		Thread.sleep(3000);
		
		wait.until(ExpectedConditions.visibilityOfElementLocated(By.xpath("//div[@id='errorAlert']/div/div/div[1]")));
		
		String message = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div/div[1]")).getText();
		
		if(message.contains("Archived successfully") || message.contains("Archived Successfully!")){
			LogResult.pass("Archived Successfully message is displayed correctly.");
		}
		else{
			LogResult.fail("Archived Successfully message is not displayed correctly.");
		}		
		driver.findElement(By.xpath("//div[@id='errorAlert']/div/div/div[3]/button")).click();
	}
	
	
	
	/*Function to sort Batch jobs results by date completed */
	public void sortBatchJobsResultsByDateCompletedDescending() throws InterruptedException{
		
		driver.findElement(By.xpath("//table[@id='batchReportListSelectTable']/thead/tr/th[8]/div[1]")).click();
		
		Thread.sleep(3000);
		
		String firstdatestring = driver.findElement(By.xpath("//table[@id='batchReportListSelectTable']/tbody/tr[1]/td[8]")).getText();
		String lastdatestring = driver.findElement(By.xpath("//table[@id='batchReportListSelectTable']/tbody/tr[last()]/td[8]")).getText();
		
		SimpleDateFormat formatter = new SimpleDateFormat("EEE MMM dd HH:mm:ss yyyy");
		//SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");	
			
		try {

			Date date1 = formatter.parse(firstdatestring);
			Date date2 = formatter.parse(lastdatestring);
			
			if(date1.after(date2) || date1.equals(date2)){				
				
			}
			else{				
				driver.findElement(By.xpath("//table[@id='batchReportListSelectTable']/thead/tr/th[8]/div[1]")).click();
				Thread.sleep(3000);				
			}

		} catch (ParseException e) {
			e.printStackTrace();
		}
	}
	
	/* Function to select the Batch Job Results to compare */
	public void selectBatchJobResultsToCompare(String batchJobsName){
		
		List<WebElement> pkgCheckbox  =	driver.findElements(By.xpath("//table[@id='batchReportListSelectTable']/tbody/tr/td[2][text()[contains(.,'" + batchJobsName + "')]]/ancestor::tr[1]/td[1]/input"));
				
		pkgCheckbox.get(0).click();
		
		pkgCheckbox.get(1).click();
		
	}
	
	/*Function to verify if compare buttons are enabled for Batch Jobs Results */
	public void verifyCompareButtonsAreEnabledForBatchJobsResults(){
		
		if(batchJobsTestCompareBtn.isEnabled() && batchJobsBuildLogCompareBtn.isEnabled() && batchJobsTestLogCompareBtn.isEnabled()){
			LogResult.pass("Test compare, Build Log Compare and test log compare buttons are enabled for batch jobs");
		}
		else{
			LogResult.fail("Test compare, Build Log Compare and test log compare buttons are not enabled for batch jobs");
		}
	}
	
	/* Function to click on Test compare button for Batch Jobs results */
	public void clickTestCompareForBatchJobresults() throws InterruptedException{
		batchJobsTestCompareBtn.click();
		Thread.sleep(4000); 
		try{
			wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("testBatchResultsTable")));
			
			if(batchJobsTestCompareTable.isDisplayed()){
				LogResult.pass("Batch Jobs Test Compare Details are displayed in table");
			}
			else
				LogResult.fail("Batch Jobs Test Compare Details are not displayed in table");			
		}
		catch(Exception e)
		{
			if(errorCloseBtn.isDisplayed()){
				
				String errorMessage = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div")).getText();
				LogResult.fail(errorMessage);
				errorCloseBtn.click();
				Assert.fail(errorMessage);
			}
		}
	}
	
	/* Function to click on Build Log compare button for Batch Jobs results */
	public void clickBuildLogCompareForBatchJobsresults() throws InterruptedException{
		batchJobsBuildLogCompareBtn.click();
		Thread.sleep(4000);
		try{
			wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("testBatchLogResultsTable")));
			
			if(batchJobsBuildLogCompareTable.isDisplayed()){
				LogResult.pass("Batch Jobs Build Log Compare Details are displayed in Panel");
			}
			else
				LogResult.fail("Batch Jobs Build Log Compare Details are not displayed in Panel");			
		}
		catch(Exception e)
		{
			if(errorCloseBtn.isDisplayed()){
				
				String errorMessage = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div")).getText();
				LogResult.fail(errorMessage);
				errorCloseBtn.click();
				Assert.fail(errorMessage);
			}
		}
	}
	
	/* Function to click on Test Log compare button for project results */
	public void clickTestLogCompareForBatchJobsresults() throws InterruptedException{
		batchJobsTestLogCompareBtn.click();
		Thread.sleep(4000);
        
		try{
			wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("testBatchLogResultsTable")));
			
			if(batchJobsTestLogCompareTable.isDisplayed()){
				LogResult.pass("Batch Jobs Test Log Compare Details are displayed in Panel");
			}
			else
				LogResult.fail("Batch Jobs Test Log Compare Details are not displayed in Panel");
		}
		catch(Exception e)
		{
			if(errorCloseBtn.isDisplayed()){
				
				String errorMessage = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div")).getText();
				LogResult.fail(errorMessage);
				errorCloseBtn.click();
				Assert.fail(errorMessage);
			}
		}
	}
	
	/* Function to to click back to comparison button*/
	 public void clickBackToComparisionBtnForBatchJobs() throws InterruptedException{
		 batchJobsBackToComparisonBtn.click();
		 Thread.sleep(3000);
	}
	 /************************ Manish Functions **************************************/

		public void enterProjectNameForSearch(String searchTerm) {
			wait.until(ExpectedConditions.visibilityOf(projectResultTextBox));

			projectResultTextBox.clear();

			projectResultTextBox.sendKeys(searchTerm);
		}

		public void enterBatchNameForSearch(String searchTerm) {
			wait.until(ExpectedConditions.visibilityOf(batchResultTextBox));

			batchResultTextBox.clear();

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

		public void clickOnDateCompletedHeader() throws InterruptedException {

			wait.until(ExpectedConditions.visibilityOf(dateCompletedHeader));
			
			dateCompletedHeader.click();

			LogResult.pass("Date Completed header is clicked.");
		}

		public void clickOnDateSubmittedHeader() {
			
			wait.until(ExpectedConditions.visibilityOf(dateSubmittedHeader));

			dateSubmittedHeader.click();

			LogResult.pass("Date Submitted header is clicked.");
		}

		// To verify completion of Jenkins job in case of Project
		public void verifyJenkinsJobCompletion(String buildClickTime, int buildServersCount) throws ParseException {

			int i = 0;

			Date temp = new SimpleDateFormat("EEE MMM dd HH:mm:ss yyyy").parse(buildClickTime); // yyyy-MM-dd-'h'HH-'m'mm-'s'ss
			for (WebElement item : dateCompletedColumnValues) {

				Date temp1 = new SimpleDateFormat("EEE MMM dd HH:mm:ss yyyy").parse(item.getText()); // yyyy-MM-dd-'h'HH-'m'mm-'s'ss
				if (temp.before(temp1) || temp.equals(temp1)) {
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

			Date temp = new SimpleDateFormat("EEE MMM dd HH:mm:ss yyyy").parse(buildClickTime);// yyyy-MM-dd-'h'HH-'m'mm-'s'ss
			for (WebElement item : dateSubmittedColumnValues) {

				Date temp1 = new SimpleDateFormat("EEE MMM dd HH:mm:ss yyyy").parse(item.getText());// yyyy-MM-dd
				// HH:mm:ss
				if (temp.equals(temp1) || temp.before(temp1)) {
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

				LogResult.pass("All batch jobs got submitted. Batch jobs that got submitted are: ");

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
	 
	 /************************************************************************/
}


