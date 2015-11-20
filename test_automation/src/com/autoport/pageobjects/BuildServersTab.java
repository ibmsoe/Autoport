package com.autoport.pageobjects;

import java.util.List;

import org.openqa.selenium.Alert;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.pagefactory.AjaxElementLocatorFactory;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.FluentWait;

import com.autoport.utilities.LogResult;

public class BuildServersTab {
	
	WebDriver driver;
	FluentWait<WebDriver> wait;
	
	public BuildServersTab(WebDriver driver, FluentWait<WebDriver> wait ){
		this.driver = driver;
		this.wait = wait;
		AjaxElementLocatorFactory factory = new AjaxElementLocatorFactory(driver, 5);
		PageFactory.initElements(factory, this);		 
	}	
	
	@FindBy(id="jenkinsSlaveButton")	 
    WebElement manageJenkinsSlaveNodesBtn;
	
	/* List / Install / Remove software */
	
	@FindBy(id="manageSingleSlaveButton")	 
    WebElement listInstallRemoveSoftwareBtn;
		
	@FindBy(id="packageFilter_Single")	 
    WebElement searchPkgSingleTxtBox;	
	
	@FindBy(xpath="//div[@id='manageSingleSlavePanel']/div[1]/div[2]/span/div/button")	 
    WebElement buildServerBtn;	
	
	@FindBy(xpath="//div[@id='manageSingleSlavePanel']/div[1]/div[2]/a/button")	 
    WebElement listBtn;
	
	@FindBy(id="singlePanelInstallBtn")	 
    WebElement singlePanelInstallBtn;
	
	@FindBy(id="singlePanelRemoveBtn")	 
    WebElement singlePanelRemoveBtn;
	
	@FindBy(id="singleServerPackageListTable")	 
    WebElement singleServerPackageListTable;
	
	@FindBy(xpath="//div[@id='manageSingleSlavePanel']/div[3]//span[@class='page-list']/span/button")	 
    WebElement noOfRecordsBtn;
	
	@FindBy(xpath="//div[@id='manageSingleSlavePanel']/div[3]/div[1]/div")	 
    WebElement notificationMsg;
	
	@FindBy(xpath="//table[@id='singleServerPackageListTable']/tbody/tr/td[6]")	 
    List<WebElement> packageSummaryColumnRows;
	
	@FindBy(xpath="//table[@id='singleServerPackageListTable']/tbody/tr/td[2]")	 
    WebElement packageColumnRows;
		
	/* List / Install / Remove software using managed runtime services */
	
	@FindBy(id="manageMultipleSlaveButton")	 
    WebElement listInstallRemoveSoftwareUsingManagedServicesBtn;
	
	@FindBy(id="packageFilter_Multiple")	 
    WebElement searchPkgMultipleTxtBox;
	
	@FindBy(id="mlRHEL")	 
    WebElement listRHELBtn;
	
	@FindBy(id="mlUbuntu")	 
    WebElement listUbuntuBtn;
	
	@FindBy(id="mlAll")	 
    WebElement listAllBtn;
	
	/* Upload Packages To Repository */
	
	@FindBy(xpath="//div[@id='jenkinsStatus']/div[3]/div[1]")	 
    WebElement uploadPackagesToRepositoryBtn;
	
	@FindBy(id="uploadPackageName")	 
    WebElement uploadPackageTextBox;
	
	@FindBy(xpath="//div[@id='jenkinsStatus']/div[3]/div[2]/div[5]/div")	 
    WebElement uploadBtn;	
	
	/* Function to open Manage Jenkins Slave Nodes section */
	public void clickManageJenkinsSlaveNodesBtnToOpen(){
		
		manageJenkinsSlaveNodesBtn.click();
		
		if(listInstallRemoveSoftwareBtn.isDisplayed()){
			LogResult.pass("Manage Jenkins Slave Nodes section' is expanded.");
		}
		else{
			LogResult.fail("Manage Jenkins Slave Nodes section' is expanded.");
		}
		
	}
	
	/* Function to open List / Install / Remove software section */
	public void clickmanageSingleSlaveButtonToOpen(){
		
		listInstallRemoveSoftwareBtn.click();
		
		if(searchPkgSingleTxtBox.isDisplayed()){
			LogResult.pass("List / Install / Remove software on a given build server' section is expanded.");
		}
		else{
			LogResult.fail("List / Install / Remove software on a given build server' section is expanded.");
		}
		
	}
	
	/* Function to verify Placeholder text for Searchbox*/
	public void verifyPlaceHolderTextForSearchBox(){
		String placeholderText = searchPkgSingleTxtBox.getAttribute("placeholder");
		
		if (placeholderText.contains("(e.g. firefox or leave blank to see which packages are installed"))
			LogResult.pass("placeholder text is correct for search box.");		
		else
			LogResult.fail("placeholder text is not correct for search box.");
	}
	
	/*Function to enter packagename to search */
	public void enterPackageToSearch(String packageName) throws InterruptedException{
		
		searchPkgSingleTxtBox.clear();
		searchPkgSingleTxtBox.sendKeys(packageName);	
		Thread.sleep(1000);
		
		if(searchPkgSingleTxtBox.getAttribute("value").contains(packageName)){
			LogResult.pass("user is able to enter packagename in search box.");
		}
		else{
			LogResult.fail("user is not able to enter packagename in search box.");
		}
	}
	
	/* Function to select Buildserver from dropdown */
	public void selectBuildServer(String buildServerName){
		
		buildServerBtn.click();
		
		String xpath = "//div[@id='manageSingleSlavePanel']//ul/li/a/label[text()[contains(.,'" + buildServerName + "')]]/input";
		driver.findElement(By.xpath(xpath)).click();
		
		LogResult.pass(buildServerName + " Build Server is selected");		
	}
	
	/*Function to list down packages by clicking list button*/
	public void clickListBtn(){
		
		listBtn.click();
		
		wait.until(ExpectedConditions.visibilityOfElementLocated(By.xpath("//div[@id='manageSingleSlavePanel']/div[3]/div[1]/div")));
				
		if(singleServerPackageListTable.isDisplayed()){
			LogResult.pass("Packages with different available versions are displayed in table");
		}
		else{
			LogResult.fail("Packages with different available versions are not displayed in table");
		}
	}
	
	/* Function to verify the search results for the packagename entered in search box */
	public void verifySearchResultsforPackage(String searchedPackage){
		
		List<WebElement> packagenames = driver.findElements(By.xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[2]"));
		int noOfpackages = 0;
		
		for (WebElement packagename : packagenames){			
			
			if (packagename.getText().contains(searchedPackage)){
				noOfpackages++;				
			}
			else{
				LogResult.fail("Search Results are not correct for package searched.");
				break;
			}
		}
		
		if (noOfpackages == packagenames.size()){
			LogResult.pass("Search Results are correct for package searched.");
		}
	}
	
	/* Function to select the package to install from the search result list */
	public String selectRandomPackageToInstall(){
		
		WebElement NApackagecheckbox =	driver.findElement(By.xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[3][text()[contains(.,'N/A')]]/preceding-sibling::td[2]/input"));
		
		WebElement packagename = driver.findElement(By.xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[3][text()[contains(.,'N/A')]]/preceding-sibling::td[1]"));;
				
		NApackagecheckbox.click();
		
		String packageSelected = packagename.getText();
		
		if(NApackagecheckbox.isSelected()){
			LogResult.pass(packageSelected + " Package is selected for installation");
		}
		else{
			LogResult.fail("Package is not selected for installation");
		}	
		
		return packageSelected;
	}
	
	/* Function to select already installed package to install */
	public void selectAlreadyInstalledPackageToInstall(){
		
		WebElement alreadyInstalledPackage =	driver.findElement(By.xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[5][text()[contains(.,'No')]]/preceding-sibling::td[4]/input"));
		alreadyInstalledPackage.click();
	}
	
	/* Function to select the two versions of the package to install */
	public String selectTwoVersionsToInstall(String packagename){
		
		List<WebElement> rows  =	driver.findElements(By.xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[2][text()[contains(.,'"+ packagename + "')]]//ancestor::tr[1]"));
		
		String firstVersion = rows.get(0).findElement(By.xpath("//td[4]")).getText();
		
		rows.get(0).findElement(By.xpath("//td[1]/input")).click();
		
		rows.get(1).findElement(By.xpath("//td[1]/input")).click();
		
		return firstVersion;		
	}
	
	/* Function to select the installed package to update */
	public String selectPackageToUpdate(){
		
		return "";
	} 
	
	/* Function to verify the If the Install/Remove button is enabled or disabled */
	public void verifyInstallRemoveButtons(String buttonStatus){
		
		if(buttonStatus.equalsIgnoreCase("enabled")){
			if(singlePanelInstallBtn.isEnabled() && singlePanelRemoveBtn.isEnabled())
				LogResult.pass("Install/Update and Remove buttons are enabled");
			else
				LogResult.fail("Install/Update and Remove buttons are not enabled");
		}
		
		if(buttonStatus.equalsIgnoreCase("disabled")){
			if((!singlePanelInstallBtn.isEnabled()) && (!singlePanelRemoveBtn.isEnabled()))
				LogResult.pass("Install/Update and Remove buttons are disabled");
			else
				LogResult.fail("Install/Update and Remove buttons are not disabled");
		}		
	}
	
	/* Function to click on install update button */
	public void clickInstallUpdateBtn(){
		singlePanelInstallBtn.click();
	}
	
	/* Function to verify that the installation success pop up is displayed correctly */
	public void verifyInstallationSuccessPopUp(String packagename){
		
		wait.until(ExpectedConditions.visibilityOfElementLocated(By.xpath("//div[@id='errorAlert']//tbody/tr[@class='success']")));
		
		String installedPackageName = driver.findElement(By.xpath("//div[@id='errorAlert']//tbody/tr[2]/td[1]")).getText();
		
		String actionname = driver.findElement(By.xpath("//div[@id='errorAlert']//tbody/tr[2]/td[2]")).getText();
		
		String status = driver.findElement(By.xpath("//div[@id='errorAlert']//tbody/tr[2]/td[3]")).getText();
		
		if(installedPackageName.contains(packagename))
			LogResult.pass("Package name is correct in installaton success message");		
		else
			LogResult.fail("Package name is not correct in installaton success message");
		
		if(actionname.contains("install/update"))
			LogResult.pass("Action name is correct in installaton success message");		
		else
			LogResult.fail("Action name is not correct in installaton success message");
		
		if(status.contains("SUCCESS"))
			LogResult.pass("Status is correct in installaton success message");		
		else
			LogResult.fail("Status is not correct in installaton success message");		

		driver.findElement(By.xpath("//div[@id='errorAlert']/div/div/div[3]/button")).click();
	}
	
	/* Function to verify that the package is already installed and the correct pop up message is displayed */
	public void verifyAlreadyInstalledMessage(){
		
		wait.until(ExpectedConditions.visibilityOfElementLocated(By.xpath("//div[@id='errorAlert']/div/div/div[1]")));
		String alreadyInstalledMsg = driver.findElement(By.xpath("//div[@id='errorAlert']/div/div/div[1]")).getText();
		
		if(alreadyInstalledMsg.contains("The selected package(s) is/are already installed"))
			LogResult.pass("Package is already installed message is displayed correctly");		
		else
			LogResult.fail("Package is already installed message is not displayed correctly");	
		
		driver.findElement(By.xpath("//div[@id='errorAlert']/div/div/div[3]/button")).click();
	}
	
	/* Function to verify that correct message is displayed when two versions of same package are selected for installation */
	public void verifyTwoVersionMessage(String packagename, String version){
		
		Alert alert = driver.switchTo().alert();
		String alertmsg = alert.getText();
		
		if(alertmsg.contains(version) && alertmsg.contains(packagename))
			LogResult.pass("Correct Pop up message is displayed stating that Only the first selected entry is marked for instalation");		
		else
			LogResult.fail("Correct Pop up message is not displayed stating that Only the first selected entry is marked for instalation");	
				
		alert.accept();
	}
	
	/* Function to verify that Installed version column is naot diaplayed as N/A for installed package*/
	public void verifyInstalledVersionIsNotNA(String packagename){
		
		String version =  driver.findElement(By.xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[text() = '" + packagename + "']/following-sibling::td[1]")).getText();
		
		if(version.contains("N/A") ){
			LogResult.fail("Installed version is displayed as N/A for installed package");
		}
		else{			
			LogResult.pass("Installed version for package "+ packagename + " is " + version);
		}
	}
	
	/* Function to verify that correct notification message is displayed above search results table*/
	public void verifyNotificationMessage(String message){
				
		if (notificationMsg.getText().contains(message)){
						
			LogResult.pass("Expected notification message is displayed.");
		}
		else{
			LogResult.fail("Expected notification message is not displayed.");
		}
	}
	
	/* Function to verify that only installed packages are displayed in search results */
	public void verifyOnlyInstalledPackagesareDisplayed() throws InterruptedException{
		
		noOfRecordsBtn.click();
		Thread.sleep(1000);
		
		driver.findElement(By.xpath("//div[@id='manageSingleSlavePanel']/div[3]//span[@class='page-list']/span/ul/li[last()]/a")).click();
		Thread.sleep(4000);
		
		List<WebElement> installedVersions = driver.findElements(By.xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[3]"));
		
		int noOfpackages = 0;
		for (WebElement installedVersion : installedVersions){
			
			noOfpackages++;
			if (installedVersion.getText() == "N/A"){
				LogResult.fail("Uninstalled packages are listed also.");
				break;
			}
		}
		
		if (noOfpackages == installedVersions.size()){
			LogResult.pass("Only installed packages are displayed in serch result");
		}
	}
	
}
