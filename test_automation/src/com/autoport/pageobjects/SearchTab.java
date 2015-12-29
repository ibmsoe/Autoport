package com.autoport.pageobjects;

import java.io.File;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.TimeZone;

import org.openqa.selenium.Keys;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.interactions.Actions;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.pagefactory.AjaxElementLocatorFactory;

import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.FluentWait;
import org.openqa.selenium.support.ui.Select;

import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.LogResult;

public class SearchTab {

	WebDriver driver;
	FluentWait<WebDriver> wait;
	// CommonFunctions functions;

	Actions action;
	
	private String buildClickTime; 
	
	private int selectedBuildServersCount;
	// HomePage homePage;

	
	public SearchTab(WebDriver driver, FluentWait<WebDriver> wait) {

		// functions= new CommonFunctions();
		this.driver = driver;

		this.wait = wait;
		// wait = new WebDriverWait(driver, 30);

		AjaxElementLocatorFactory factory = new AjaxElementLocatorFactory(driver, 10);
		PageFactory.initElements(factory, this);

		action = new Actions(driver);

		// homePage = new HomePage(driver);

		// homePage = functions.homePage;

	}
	

	@FindBy(id = "singleSearchButton")
	WebElement searchSingleProjectTab;

	@FindBy(id = "query")
	WebElement searchSingleProjectQueryTbx;

	@FindBy(xpath = "//div[@id='searchBox']/div[1]//button")
	WebElement sortByBtn;

	@FindBy(xpath = "//div[@id='searchBox']/div[1]//li")
	List<WebElement> sortDropDownValues;

	@FindBy(linkText = "Relevance")
	WebElement relevance;

	@FindBy(linkText = "Popularity Stars")
	WebElement popularityStars;

	@FindBy(linkText = "Forks")
	WebElement forks;

	@FindBy(linkText = "Updated")
	WebElement updated;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div")
	WebElement singleDetailPanel;

	@FindBy(xpath = "//div[@id='resultsPanel']")
	WebElement resultsPanel;

	@FindBy(xpath = "//div[@id='searchBox']/div[5]/span")
	WebElement autoRepoMsg;

	@FindBy(xpath = "//div[@id='searchBox']/div[5]/a")
	WebElement seeAllResultsBtn;

	@FindBy(xpath = "//div[@id='singleDetailPanel']//h1/a[1]")
	WebElement ownerDetail;

	@FindBy(xpath = "//div[@id='singleDetailPanel']//h1/a[2]")
	WebElement repositoryDetail;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/span[1]")
	WebElement starCountDetail;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/span[2]")
	WebElement forkCountDetail;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/span[3]")
	WebElement primaryLanguageDetail;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/span[4]")
	WebElement repositorySizeDetail;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/span[5]")
	WebElement lastUpdatedDetail;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/h3")
	WebElement descriptionHeader;

	@FindBy(xpath = "//div[@id='singleDetailPanel']//blockquote/p")
	WebElement descriptionText;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/span[6]/h3")
	WebElement languageCompositionHeader;

	@FindBy(id = "langChart")
	WebElement languagePieChart;

	@FindBy(id = "langLegend")
	WebElement languageLegend;

	@FindBy(xpath = "//ul[@id='langLegend']/li")
	List<WebElement> langLegendValues;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/h1/div/div[2]/button")
	WebElement useJDK;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/h1/div/div[2]/ul//a")
	List<WebElement> useJDKOptions;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/h1/div/div[1]/button")
	WebElement useNodeJs;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/h1/div/div[1]/ul//a")
	List<WebElement> useNodeJsOptions;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/h1/div/a/button")
	WebElement addToBatchBtnForAutoResult;

	// Not working hence commented
	// @FindBy(id = "singleVersions")
	// WebElement currentVersionForAutoResult;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/h1/div/div[3]/button")
	WebElement currentVersionForAutoResult;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/h1/div/div[2]/ul//a")
	List<WebElement> currentVersionValues;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/h1/div/div[4]/div/button")
	WebElement selectBuildServerForAutoResult;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/h1/div/div[4]/div/ul//label")
	List<WebElement> buildServerList;

	@FindBy(xpath = "//div[@id='singleDetailPanel']//li//input")
	List<WebElement> buildServerListChkbx;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/h1/div/button")
	WebElement buildAndTestBtnForAutoResult;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/span[7]/h3")
	WebElement buildStepsHeader;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/span[7]/div[1]/button")
	WebElement selectBuildOptions;

	@FindBy(id = "singleSelectedBuild")
	WebElement buildOptionsTbx;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/span[7]/div[2]/button")
	WebElement selectTestOptions;

	@FindBy(id = "singleSelectedTest")
	WebElement testOptionsTbx;

	@FindBy(xpath = "//div[@id='singleDetailPanel']/div/span[7]/div[3]/button")
	WebElement selectEnvironmentOptions;

	@FindBy(id = "singleSelectedEnv")
	WebElement environmentOptionsTbx;

	// @FindBy(xpath = "//div[@id='resultsPanel']/table/thead/tr/th[1]")
	@FindBy(xpath = "//div[@rv-show='searchState.single.ready']/table/thead/tr/th[1]")
	WebElement repositoriesColHeader;

	// @FindBy(xpath = "//div[@id='resultsPanel']/table/thead/tr/th[2]")
	@FindBy(xpath = "//div[@rv-show='searchState.single.ready']/table/thead/tr/th[2]")
	WebElement actionsColHeader;

	@FindBy(xpath = "//tbody[@id='resultsTable']//td[1]/a[1]")
	WebElement ownerList;

	@FindBy(xpath = "//tbody[@id='resultsTable']//td[1]/a[2]")
	WebElement repositoryList;

	@FindBy(xpath = "//tbody[@id='resultsTable']//td[1]/span[1]")
	WebElement starCountList;

	@FindBy(xpath = "//tbody[@id='resultsTable']//td[1]/span[2]")
	WebElement forkCountList;

	@FindBy(xpath = "//tbody[@id='resultsTable']//td[1]/span[3]")
	WebElement primaryLanguageList;

	@FindBy(xpath = "//tbody[@id='resultsTable']//td[1]/span[4]")
	WebElement repositorySizeList;

	@FindBy(xpath = "//tbody[@id='resultsTable']//td[1]/span[5]")
	WebElement lastUpdatedList;

	@FindBy(xpath = "//tbody[@id='resultsTable']//td[2]/a/button")
	WebElement addToBatchList;

	@FindBy(xpath = "//tbody[@id='resultsTable']//td[3]/a/button")
	WebElement repositoryDetailsList;

	@FindBy(xpath = "//div[@id='resultsPanel']/table/tbody[1]//td[3]//button")
	WebElement firstRepositoryDetailsList;

	@FindBy(xpath = "//tbody[@id='resultsTable']/tr")
	List<WebElement> numOfResultRows;

	@FindBy(xpath = "//tbody[@id='resultsTable'][1]/tr/td[1]")
	WebElement mouseHoverDescription;

	@FindBy(xpath = "//tbody[@id='resultsTable'][1]//p")
	WebElement repoDescription;

	@FindBy(xpath = "//tbody[@id='resultsTable'][1]//td[3]/a/button")
	WebElement repositoryDetailBtn;

	@FindBy(id = "singleDetailBackButton")
	WebElement backToResultsBtn;

	@FindBy(xpath = "//tbody[@id='resultsTable'][1]//td[2]//button")
	WebElement addToBatchBtn;

	@FindBy(xpath = "//div[@id='searchBox']/div[3]")
	WebElement batchSaveExportClearSection;

	@FindBy(xpath = "//div[@id='searchBox']/div[3]/span/div[1]")
	WebElement batchFileHelpTx;

	@FindBy(xpath = "//div[@id='searchBox']/div[3]//input")
	WebElement batchFileNameTbx;

	@FindBy(xpath = "//div[@id='searchBox']/div[3]//a[1]/button")
	WebElement saveBatchFileBtn;

	@FindBy(xpath = "//div[@id='searchBox']/div[3]//a[2]/button")
	WebElement exportBatchFileBtn;

	@FindBy(xpath = "//div[@id='searchBox']/div[3]//a[3]/button")
	WebElement clearBatchFileBtn;

	@FindBy(id = "batchFilePanel")
	WebElement batchFilePanel;

	@FindBy(xpath = "//div[@id='batchFilePanel']//th")
	WebElement batchFilePanelHeader;

	@FindBy(xpath = "//div[@id='batchFilePanel']//a[1]")
	WebElement batchFileRepoOwner;

	@FindBy(xpath = "//div[@id='batchFilePanel']//a[2]")
	WebElement batchFileRepoName;

	@FindBy(xpath = "//div[@id='batchFilePanel']//td/span[1]")
	WebElement batchFileRepoStarCount;

	@FindBy(xpath = "//div[@id='batchFilePanel']//td/span[2]")
	WebElement batchFileRepoForkCount;

	@FindBy(xpath = "//div[@id='batchFilePanel']//td/span[3]")
	WebElement batchFileRepoPrimaryLanguage;

	@FindBy(xpath = "//div[@id='batchFilePanel']//td/span[4]")
	WebElement batchFileRepoSize;

	@FindBy(xpath = "//div[@id='batchFilePanel']//td/span[5]")
	WebElement batchFileRepoLastUpdated;

	@FindBy(xpath = "//div[@id='batchFilePanel']//tbody")
	WebElement batchFilemouseHoverDescription;

	@FindBy(xpath = "//div[@id='batchFilePanel']//tbody//p")
	WebElement batchFilerepoDescription;

	// ------------------ Most commonly used projects----------------

	@FindBy(id = "generateBatchButton")
	WebElement searchCommonlyUsedProjectsTab;

	@FindBy(xpath = "//div[@id='generateBox']/div[1]/div[1]/div")
	WebElement commonProjectsTopRepositories;

	@FindBy(xpath = "//div[@id='generateBox']/div[1]/div[1]/div/span[1]")
	WebElement preCommonProjectsTopRepositoriesLabelTx;

	@FindBy(xpath = "//div[@id='generateBox']/div[1]/div[1]/div/input")
	WebElement commonProjectsTopRepositoriesValue;

	@FindBy(xpath = "//div[@id='generateBox']/div[1]/div[1]/div/span[2]")
	WebElement postCommonProjectsTopRepositoriesLabelTx;

	@FindBy(xpath = "//div[@id='generateBox']/div[1]/div[2]/div")
	WebElement commonProjectsSortBy;

	@FindBy(xpath = "//div[@id='generateBox']/div[1]/div[2]/div/span")
	WebElement commonProjectsSortByLabelTx;

	@FindBy(xpath = "//div[@id='generateBox']/div[1]/div[2]/div/select")
	WebElement commonProjectsSortByDropDown;

	@FindBy(xpath = "//div[@id='generateBox']/div[1]/div[3]/select")
	WebElement commonProjectsProgrammingLanguage;

	@FindBy(xpath = "//div[@id='generateBox']/div[2]/div[1]/select")
	WebElement commonProjectsRelease;

	@FindBy(xpath = "//div[@id='generateBox']/div[2]/div[2]/div")
	WebElement commonProjectsPopularityStars;

	@FindBy(xpath = "//div[@id='generateBox']/div[2]/div[2]/div/span[1]")
	WebElement preCommonProjectsPopularityStarsLabelTx;

	@FindBy(xpath = "//div[@id='generateBox']/div[2]/div[2]/div/input")
	WebElement greaterThanPopularityStarsTxBx;

	@FindBy(xpath = "//div[@id='generateBox']/div[2]/div[2]/div/span[2]")
	WebElement postCommonProjectsPopularityStarsLabelTx;

	@FindBy(xpath = "//div[@id='generateBox']/div[2]/div[3]/div")
	WebElement commonProjectsForks;

	@FindBy(xpath = "//div[@id='generateBox']/div[2]/div[3]/div/span[1]")
	WebElement preCommonProjectsForksLabelTx;

	@FindBy(xpath = "//div[@id='generateBox']/div[2]/div[3]/div/input")
	WebElement greaterThanForksTxBx;

	@FindBy(xpath = "//div[@id='generateBox']/div[2]/div[3]/div/span[2]")
	WebElement postCommonProjectsForksLabelTx;

	@FindBy(xpath = "//div[@id='generateBox']/div[2]//button")
	WebElement commonProjectsSearchBtn;

	@FindBy(xpath = "//div[@id='generateBox']/div[5]")
	WebElement commonProjectSaveExportSection;

	@FindBy(xpath = "//div[@id='generateBox']/div[5]/span/div[1]")
	WebElement commonProjectBatchFileHelpTx;

	@FindBy(xpath = "//div[@id='generateBox']/div[5]//input")
	WebElement commonProjectBatchFileNameTbx;

	@FindBy(xpath = "//div[@id='generateBox']/div[5]//a[1]/button")
	WebElement commonProjectSaveBatchBtn;

	@FindBy(xpath = "//div[@id='generateBox']/div[5]//a[2]/button")
	WebElement commonProjectExportBatchBtn;

	@FindBy(xpath = "//div[@rv-show='searchState.multiple.ready']/table/thead/tr/th[1]")
	WebElement commonProjectRepositoriesColHeader;

	@FindBy(xpath = "//div[@rv-show='searchState.multiple.ready']/table/thead/tr/th[2]")
	WebElement commonProjectActionsColHeader;

	@FindBy(xpath = "//div[@id='generateDetailPanel']//h1/a[1]")
	WebElement commonProjectOwnerDetail;

	@FindBy(xpath = "//div[@id='generateDetailPanel']//h1/a[2]")
	WebElement commonProjectRepositoryDetail;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/span[1]")
	WebElement commonProjectStarCountDetail;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/span[2]")
	WebElement commonProjectForkCountDetail;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/span[3]")
	WebElement commonProjectPrimaryLanguageDetail;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/span[4]")
	WebElement commonProjectRepositorySizeDetail;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/span[5]")
	WebElement commonProjectLastUpdatedDetail;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/h3")
	WebElement commonProjectDescriptionHeader;

	@FindBy(xpath = "//div[@id='generateDetailPanel']//blockquote/p")
	WebElement commonProjectDescriptionText;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/span[6]/h3")
	WebElement commonProjectLanguageCompositionHeader;

	@FindBy(id = "generateLangChart")
	WebElement commonProjectLanguagePieChart;

	@FindBy(id = "generateLangLegend")
	WebElement commonProjectLanguageLegend;

	@FindBy(xpath = "//ul[@id='generateLangLegend']/li")
	List<WebElement> commonProjectLangLegendValues;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/h1/div/div[2]/button")
	WebElement commonProjectUseJDK;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/h1/div/div[2]/ul//a")
	List<WebElement> commonProjectUseJDKOptions;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/h1/div/div[1]/button")
	WebElement commonProjectUseNodeJs;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/h1/div/div[1]/ul//a")
	List<WebElement> commonProjectUseNodeJsOptions;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/h1/div/div[3]/button")
	WebElement commonProjectCurrentVersion;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/h1/div/div[3]/ul//a")
	List<WebElement> commonProjectCurrentVersionValues;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/h1/div/div[3]/ul/li[2]/a")
	WebElement commonProjectCurrentVersionValue;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/h1/div/div[3]/ul/li[3]/a")
	WebElement commonProjectRecentVersionValue;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/h1/div/div[4]/div/button")
	WebElement commonProjectSelectBuildServer;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/h1/div/div[4]/div/ul//label")
	List<WebElement> commonProjectBuildServerList;

	@FindBy(xpath = "//div[@id='generateDetailPanel']//li//input")
	List<WebElement> commonProjectBuildServerListChkbx;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/h1/div/button")
	WebElement commonProjectBuildAndTestBtn;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/span[7]/h3")
	WebElement commonProjectBuildStepsHeader;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/span[7]/div[1]/button")
	WebElement commonProjectSelectBuildOptions;

	@FindBy(id = "generateSelectedBuild")
	WebElement commonProjectBuildOptionsTbx;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/span[7]/div[2]/button")
	WebElement commonProjectSelectTestOptions;

	@FindBy(id = "generateSelectedTest")
	WebElement commonProjectTestOptionsTbx;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div/span[7]/div[3]/button")
	WebElement commonProjectSelectEnvironmentOptions;

	@FindBy(id = "generateSelectedEnv")
	WebElement commonProjectEnvironmentOptionsTbx;

	@FindBy(xpath = "//tbody[@id='resultsTable']//td[2]/a/button")
	WebElement commonProjectRepositoryDetailsList;
	
//	@FindBy(xpath = "//tbody[@id='resultsTable'][1]//td[2]/a/button")
//	WebElement commonProjectFirstRepositoryDetailsList;

	@FindBy(xpath = "//tbody[@id='resultsTable']//td[3]/a/button")
	WebElement commonProjectRemoveList;

	@FindBy(id = "generateDetailBackButton")
	WebElement commonProjectBackToResultsBtn;

	@FindBy(xpath = "//div[@id='resultsPanel'][@rv-show='searchState.multiple.ready']//tbody[1]//td[2]//button") 
	WebElement commonProjectRepositoryDetailBtn; // //tbody[@id='resultsTable'][1]/tr/td[2]/a/button

	@FindBy(xpath = "//div[@id='resultsPanel'][@rv-show='searchState.multiple.ready']//tbody[1]//td[3]//button") // //tbody[@id='resultsTable'][1]/tr/td[3]/a/button
	WebElement commonProjectRepositoryRemoveBtn;

	@FindBy(xpath = "//div[@id='generateDetailPanel']/div")
	WebElement commonProjectSingleDetailPanel;

	@FindBy(xpath = "//div[@id='resultsPanel'][@rv-show='searchState.multiple.ready']")
	WebElement commonProjectResultsPanel;

	@FindBy(xpath = "//tbody[@id='resultsTable'][1]//td[1]/a[2]")
	WebElement topRepositoryName;

	@FindBy(xpath = "//div[@rv-show='searchState.multiple.ready']//tbody[@id='resultsTable'][1]/tr/td[1]/a[1]")
	WebElement commonProjectOwnerList;

	@FindBy(xpath = "//div[@rv-show='searchState.multiple.ready']//tbody[@id='resultsTable'][1]/tr/td[1]/a[2]")
	WebElement commonProjectRepositoryList;

	@FindBy(xpath = "//div[@id='errorAlert']/div/div/div[1]")
	WebElement alertMessage;

	@FindBy(xpath = "//div[@id='errorAlert']//button")
	WebElement alertCloseBtn;

	// To get the title
	public String getPageTitle() {
		return driver.getTitle();
	}

	// Clicking on browser refresh button for refreshing page
	public void browserPageRefresh() {
		driver.navigate().refresh();
	}

	// Clicking on browser back button for navigating back to previous page
	public void browserNavigateBack() {
		driver.navigate().back();

		if (getPageTitle().contains("AutoPort")) {
			LogResult.pass("Navigated back to AutoPort application");
		} else {
			LogResult.fail("Navigation back to AutoPort application failed.");
		}
	}

	// Waiting for Detail panel to appear
	public void waitingForSingleProjectResultPanel() {
		wait.until(ExpectedConditions.visibilityOf(singleDetailPanel));
	}

	// Waiting for Result panel to appear
	public void waitingForResultPanel() {
		wait.until(ExpectedConditions.visibilityOf(resultsPanel));
	}

	// To verify expansion of Search for a single project button
	public void clickOnSingleProjectBtn() {
		searchSingleProjectTab.click();

		if (searchSingleProjectQueryTbx.isDisplayed()) {
			LogResult.pass("Search for a single project button is expanded.");
		} else {
			LogResult.fail("Search for a single project button is not expanded.");
		}
	}

	// To verify Single project button contents
	public void verifySingleProjectUI() {

		if (searchSingleProjectQueryTbx.isDisplayed()) {
			LogResult.pass("Search for single project query text box is displayed with place holder text as: "
					+ searchSingleProjectQueryTbx.getAttribute("placeholder"));
		} else {
			LogResult.fail("Search for single project query text box is not displayed.");
		}

		if (sortByBtn.isDisplayed()) {
			LogResult.pass("Sort by button is displayed containing values: ");

			LogResult.pass(sortByBtn.getText());

			sortByBtn.click();

			List<WebElement> sortValues = sortDropDownValues;

			for (int i = 1; i < sortValues.size(); i++) {

				LogResult.pass(sortValues.get(i).getText());

			}
		} else {
			LogResult.fail("Sort by button is not displayed.");
		}
		sortByBtn.click();
	}

	// Clear and enter text in Single project text field
	public void searchForRepository(String query) {

		searchSingleProjectQueryTbx.clear();

		searchSingleProjectQueryTbx.sendKeys(query);

		searchSingleProjectQueryTbx.sendKeys(Keys.ENTER);
		
		
	}

	// To verify results when sorted by relevance
	public void verifyResultsSortByRelavance() {

		if (sortByBtn.getText().contentEquals("Sort by relevance")) {
			searchSingleProjectQueryTbx.sendKeys(Keys.ENTER);
		} else {

			action.click(sortByBtn).moveToElement(relevance).click().build().perform();

		}

		if (sortByBtn.getText().contentEquals("Sort by relevance")) {
			LogResult.pass("Results sorted by Relevance.");
		} else {
			LogResult.fail("Results not sorted by Relevance.");
		}
	}

	// To verify results when sorted by popularity stars
	public void verifyResultsSortByPopularityStars() {

		action.click(sortByBtn).moveToElement(popularityStars).click().build().perform();

		if (sortByBtn.getText().contentEquals("Sort by popularity stars")) {
			LogResult.pass("Results sorted by Popularity Stars.");
		} else {
			LogResult.fail("Results not sorted by Popularity Stars.");
		}
	}

	// To verify results when sorted by forks
	public void verifyResultsSortByForks() {

		action.click(sortByBtn).moveToElement(forks).click().build().perform();

		if (sortByBtn.getText().contentEquals("Sort by forks")) {
			LogResult.pass("Results sorted by Forks.");
		} else {
			LogResult.fail("Results sorted by Forks.");
		}
	}

	// To verify results when sorted by updated
	public void verifyResultsSortByUpdated() {

		action.click(sortByBtn).moveToElement(updated).click().build().perform();

		if (sortByBtn.getText().contentEquals("Sort by updated")) {
			LogResult.pass("Results sorted by Updated.");
		} else {
			LogResult.fail("Results sorted by Updated.");
		}
	}

	// To verify top section UI when Auto selected repository is displayed
	public void verifyAutoSelectSection() {
		if ((sortByBtn.getText().contentEquals("Sort by relevance")) && (singleDetailPanel.isDisplayed())) {
			LogResult.pass("Auto-selected repository displayed sorted by relevance");
		} else {

			LogResult.fail("Repositories displayed sorted by relevance");
		}

		if (autoRepoMsg.isDisplayed()) {
			LogResult.pass("Auto-selected repository message is displayed: " + autoRepoMsg.getText());
		} else {
			LogResult.fail("Auto-selected repository message is not displayed.");
		}

		if (seeAllResultsBtn.isDisplayed()) {
			LogResult.pass("See all results button is displayed.");
			if (seeAllResultsBtn.getText().contentEquals("See all results")) {
				LogResult.pass("See all results button has text: " + seeAllResultsBtn.getText());
			} else {
				LogResult.fail("See all results button has text: " + seeAllResultsBtn.getText());
			}
		} else {
			LogResult.fail("See all results button is not displayed.");
		}
	}

	// To verify detail panel UI when Auto selected repository is displayed
	public void verifyAutoSelectedRepoUI() {

		if (ownerDetail.isDisplayed()) {
			LogResult.pass("Owner name is displayed: " + ownerDetail.getText());
		} else {
			LogResult.fail("Owner name is not displayed");
		}

		if (repositoryDetail.isDisplayed()) {
			LogResult.pass("Repository name is displayed: " + repositoryDetail.getText());
		} else {
			LogResult.fail("Repository name is not displayed.");
		}

		if (starCountDetail.isDisplayed()) {
			LogResult.pass("Star count is displayed: " + starCountDetail.getText());
		} else {
			LogResult.fail("Star count is not displayed.");
		}

		if (forkCountDetail.isDisplayed()) {
			LogResult.pass("Fork count is displayed: " + forkCountDetail.getText());
		} else {
			LogResult.fail("Fork count is not displayed.");
		}

		if (primaryLanguageDetail.isDisplayed()) {
			LogResult.pass("Primary language is displayed: " + primaryLanguageDetail.getText());
		} else {
			LogResult.fail("Primary language is not displayed.");
		}

		if (repositorySizeDetail.isDisplayed()) {
			LogResult.pass("Repository size is displayed: " + repositorySizeDetail.getText());
		} else {
			LogResult.fail("Repository size is not displayed.");
		}

		if (lastUpdatedDetail.isDisplayed()) {
			LogResult.pass("Last updated detail is displayed: " + lastUpdatedDetail.getText());
		} else {
			LogResult.fail("Last updated detail is not displayed.");
		}

		if (descriptionHeader.isDisplayed()) {
			LogResult.pass("Description header is displayed.");
			if (descriptionHeader.getText().contentEquals("Description")) {
				LogResult.pass("Description header has text as: " + descriptionHeader.getText());
			} else {
				LogResult.fail("Description header has text as: " + descriptionHeader.getText());
			}
		} else {
			LogResult.fail("Description header is not displayed.");
		}

		if (descriptionText.isDisplayed()) {
			LogResult.pass("Description text is displayed with text as: " + descriptionText.getText());
		} else {
			LogResult.fail("Description text is not displayed.");
		}

		if (languageCompositionHeader.isDisplayed()) {
			LogResult.pass("Language composition header is displayed.");
			if (languageCompositionHeader.getText().contentEquals("Language Composition")) {
				LogResult.pass("Language composition header has text as: " + languageCompositionHeader.getText());
			} else {
				LogResult.fail("Language composition header has text as: " + languageCompositionHeader.getText());
			}
		} else {
			LogResult.fail("Language composition header is not displayed.");
		}

		if (languagePieChart.isDisplayed()) {
			LogResult.pass("Language pie chart is displayed.");
		} else {
			LogResult.fail("Language pie chart is not displayed.");
		}

		if (languageLegend.isDisplayed()) {
			LogResult.pass("Language legends are displayed: ");

			List<WebElement> legends = langLegendValues;

			for (WebElement item : legends) {

				LogResult.pass(item.getText());

			}

		} else {
			LogResult.fail("Language legends are not displayed.");
		}

		// In case of Java Primary language, check for JDK drop down
		if (primaryLanguageDetail.getText().contentEquals("Java")) {

			if (useJDK.isDisplayed()) {
				LogResult.pass("Use JDK option drop down is displayed with options: ");

				useJDK.click();

				List<WebElement> jdks = useJDKOptions;

				for (WebElement item : jdks) {

					LogResult.pass(item.getText());

				}

				useJDK.click();

			} else {
				LogResult.fail("Use JDK option drop down is not displayed.");

			}
		}

		// In case of JavaScript Primary language, check for NodeJs drop down
		if (primaryLanguageDetail.getText().contentEquals("JavaScript")) {

			if (useNodeJs.isDisplayed()) {
				LogResult.pass("Use NodeJs option drop down is displayed with options: ");

				useNodeJs.click();

				List<WebElement> nodejs = useNodeJsOptions;

				for (WebElement item : nodejs) {

					LogResult.pass(item.getText());

				}

				useNodeJs.click();
			} else {
				LogResult.fail("Use NodeJs option drop down is not displayed.");

			}

		}

		if (addToBatchBtnForAutoResult.isDisplayed()) {
			LogResult.pass("Add to Batch button is displayed");
			if (addToBatchBtnForAutoResult.getText().contentEquals("Add to Batch")) {
				LogResult.pass("Add to Batch button has text: " + addToBatchBtnForAutoResult.getText());
			} else {
				LogResult.fail("Add to Batch button has text: " + addToBatchBtnForAutoResult.getText());
			}
		} else {
			LogResult.fail("Add to Batch button is not displayed");
		}

		if (currentVersionForAutoResult.isDisplayed()) {
			LogResult.pass("Use current version drop down is displayed.");
			if (currentVersionForAutoResult.getText().contentEquals("Use current version")) {
				LogResult.pass("Use current version drop down has text: " + currentVersionForAutoResult.getText());

			} else {
				LogResult.fail("Use current version drop down has text: " + currentVersionForAutoResult.getText());
			}

			currentVersionForAutoResult.click();

			for (WebElement item : currentVersionValues) {
				if (item.getText().contentEquals("Current"))
					break;
			}

			LogResult.pass("Different versions in the drop down displayed ");
			currentVersionForAutoResult.click();

		} else {
			LogResult.fail("Use current version drop down is not displayed.");
		}

		if (selectBuildServerForAutoResult.isDisplayed()) {
			LogResult.pass("Select build servers drop down is displayed with values: ");

			selectBuildServerForAutoResult.click();

			List<WebElement> buildServer = buildServerList;

			for (WebElement item : buildServer) {

				LogResult.pass(item.getText());

			}

			selectBuildServerForAutoResult.click();

		} else {
			LogResult.fail("Select build servers drop down is not displayed.");
		}

		if (buildAndTestBtnForAutoResult.isDisplayed()) {
			LogResult.pass("Build and Test button is displayed.");
			if (buildAndTestBtnForAutoResult.getText().contentEquals("Build + Test")) {
				LogResult.pass("Build and Test button has text: " + buildAndTestBtnForAutoResult.getText());
			} else {
				LogResult.fail("Build and Test button has text: " + buildAndTestBtnForAutoResult.getText());
			}
		} else {
			LogResult.fail("Build and Test button is not displayed.");
		}

		if (buildStepsHeader.isDisplayed()) {
			LogResult.pass("Build Steps header is displayed.");
			if (buildStepsHeader.getText().contentEquals("Build steps")) {
				LogResult.pass("Build Steps header has text: " + buildStepsHeader.getText());
			} else {
				LogResult.fail("Build Steps header has text: " + buildStepsHeader.getText());
			}
		} else {
			LogResult.fail("Build Steps header is not displayed.");
		}

		if (selectBuildOptions.isDisplayed()) {
			if (selectBuildOptions.getText().contentEquals("Select build options")) {
				LogResult.pass("Select build options drop down has text: " + selectBuildOptions.getText());
			} else {
				LogResult.fail("Select Build options drop down has text: " + selectBuildOptions.getText());
			}

		} else {
			LogResult.fail("Select Build options drop down is not displayed.");
		}

		if (buildOptionsTbx.isDisplayed()) {
			LogResult.pass("Select build options text box is displayed");
		} else {
			LogResult.fail("Select build options text box is not displayed");
		}

		if (selectTestOptions.isDisplayed()) {
			if (selectTestOptions.getText().contentEquals("Select test options")) {
				LogResult.pass("Select test options drop down has text: " + selectTestOptions.getText());
			} else {
				LogResult.fail("Select test options drop down has text: " + selectTestOptions.getText());
			}
		} else {
			LogResult.fail("Select test options drop down is not displayed.");
		}

		if (testOptionsTbx.isDisplayed()) {
			LogResult.pass("Select test options text box is displayed");
		} else {
			LogResult.fail("Select test options text box is not displayed");
		}

		if (selectEnvironmentOptions.isDisplayed()) {
			if (selectEnvironmentOptions.getText().contentEquals("Select environment options")) {
				LogResult.pass("Select environment options drop down has text: " + selectEnvironmentOptions.getText());
			} else {
				LogResult.fail("Select environment options drop down has text: " + selectEnvironmentOptions.getText());
			}
		} else {
			LogResult.fail("Select environment options drop down is not displayed.");
		}

		if (environmentOptionsTbx.isDisplayed()) {
			LogResult.pass("Select environment options text box is displayed");
		} else {
			LogResult.fail("Select environment options text box is not displayed");
		}
	}

	// To verify appearance of Back to results button
	public void verifyBackToResultsBtn() {
		if (backToResultsBtn.isDisplayed()) {
			LogResult.pass("Back to results button is displayed.");
		} else {
			LogResult.fail("Back to results button is not displayed.");
		}
	}

	// To verify back to results button functionality
	public void clickOnBackToResults() {
		backToResultsBtn.click();

		if (resultsPanel.isDisplayed()) {
			LogResult.pass("Navigated back to results");
		} else {
			LogResult.fail("Not navigated back to results");
		}
	}

	// Clicking on See all result button
	public void clickOnSeeAllResultsBtn() {
		seeAllResultsBtn.click();

	}

	// To verify count for the number of repositories displayed
	public void verifyNumOfRepositories(int numOfRows) {

		if (numOfResultRows.size() == numOfRows) {
			LogResult.pass("Number of repositories displayed are: " + numOfResultRows.size());
		} else {
			LogResult.pass("Number of repositories displayed are: " + numOfResultRows.size());
		}

	}

	// To verify Repository header text in results table
	public void verifyRepositoryHeader() {
		if (repositoriesColHeader.isDisplayed()) {
			LogResult.pass("Repositories column is displayed.");
			if (repositoriesColHeader.getText().contentEquals("Repositories")) {
				LogResult.pass("Repositories column header text is displayed as: " + repositoriesColHeader.getText());
			} else {
				LogResult.fail("Repositories column header text is displayed as: " + repositoriesColHeader.getText());
			}
		} else {
			LogResult.fail("Repositories column is not displayed.");
		}
	}

	// To verify Repository column UI elements
	public void verifyRepositoryColumnListUI() {

		if (ownerList.isDisplayed()) {
			LogResult.pass("Owners are displayed.");
		} else {
			LogResult.fail("Owners are not displayed.");
		}

		if (repositoryList.isDisplayed()) {
			LogResult.pass("Repositories are displayed.");
		} else {
			LogResult.fail("Repositories are not displayed.");
		}

		if (starCountList.isDisplayed()) {
			LogResult.pass("Star counts are displayed.");
		} else {
			LogResult.fail("Star counts are not displayed.");
		}

		if (forkCountList.isDisplayed()) {
			LogResult.pass("Fork counts are displayed.");
		} else {
			LogResult.fail("Fork counts are not displayed.");
		}

		if (primaryLanguageList.isDisplayed()) {
			LogResult.pass("Primary languages are displayed.");
		} else {
			LogResult.fail("Primary languages are not displayed.");
		}

		if (repositorySizeList.isDisplayed()) {
			LogResult.pass("Repository sizes are displayed.");
		} else {
			LogResult.fail("Repository sizes are not displayed.");
		}

		if (lastUpdatedList.isDisplayed()) {
			LogResult.pass("Last updated details are displayed");
		} else {
			LogResult.fail("Last updated details are not displayed.");
		}
	}

	// To verify Actions column header and UI elements for Search for a Single
	// Project button
	public void verifyActionsColumnListUI() {

		if (actionsColHeader.isDisplayed()) {
			LogResult.pass("Actions column is displayed.");
			if (actionsColHeader.getText().contentEquals("Actions")) {
				LogResult.pass("Actions column header text is displayed as: " + actionsColHeader.getText());
			} else {
				LogResult.fail("Actions column header text is displayed as: " + actionsColHeader.getText());
			}
		} else {
			LogResult.fail("Actions column is not displayed.");
		}

		if (addToBatchList.isDisplayed()) {
			LogResult.pass("Add to batch buttons are displayed");
		} else {
			LogResult.fail("Add to batch buttons are not displayed.");
		}

		if (repositoryDetailsList.isDisplayed()) {
			LogResult.pass("Detail buttons are displayed.");
		} else {
			LogResult.fail("Detail buttons are not displayed.");
		}
	}

	// Verify Github website navigation upon owner click from detail view for
	// Single project
	public void clickOnOwner() {

		ownerDetail.click();

		wait.until(ExpectedConditions.titleContains("Git"));

		if (getPageTitle().contains("Git")) {
			LogResult.pass("Owner details are displayed on GitHub website.");
		} else {
			LogResult.fail("Owner details are not displayed on GitHub website.");
		}

	}

	// verify Github website navigation upon repository click from detail view
	// for Single project
	public void clickOnRepository() {
		repositoryDetail.click();

		wait.until(ExpectedConditions.titleContains("Git"));

		if (getPageTitle().contains("Git")) {
			LogResult.pass("Repository details are displayed on Git.");
		} else {
			LogResult.fail("Repository details are not displayed on Git.");
		}
	}

	// To verify repository tooltips in detail panel
	public void verifyRepositoryDetailsTooltip() {
		if (starCountDetail.getAttribute("title").contains("Star count")) {
			LogResult.pass("Star count tooltip is displayed.");
		} else {
			LogResult.fail("Star count tooltip is not displayed.");
		}

		if (forkCountDetail.getAttribute("title").contains("Fork count")) {
			LogResult.pass("Fork count tooltip is displayed.");
		} else {
			LogResult.fail("Fork count tooltip is not displayed.");
		}

		if (primaryLanguageDetail.getAttribute("title").contains("Primary language")) {
			LogResult.pass("Primary language tooltip is displayed.");
		} else {
			LogResult.fail("Primary language tooltip is not displayed.");
		}

		if (repositorySizeDetail.getAttribute("title").contains("Repository size")) {
			LogResult.pass("Repository size tooltip is displayed.");
		} else {
			LogResult.fail("Repository size tooltip is not displayed.");
		}

		if (lastUpdatedDetail.getAttribute("title").contains("Last updated")) {
			LogResult.pass("Last updated tooltip is displayed.");
		} else {
			LogResult.fail("Last updated tooltip is not displayed.");
		}

	}

	// To verify repository tooltips for repository listing in result panel
	public void verifyRepositoryListTooltip() {
		if (starCountList.getAttribute("title").contains("Star count")) {
			LogResult.pass("Star count tooltips are displayed.");
		} else {
			LogResult.fail("Star count tooltips are not displayed.");
		}

		if (forkCountList.getAttribute("title").contains("Fork count")) {
			LogResult.pass("Fork count tooltips are displayed.");
		} else {
			LogResult.fail("Fork count tooltips are not displayed.");
		}

		if (primaryLanguageList.getAttribute("title").contains("Primary language")) {
			LogResult.pass("Primary language tooltips are displayed.");
		} else {
			LogResult.fail("Primary language tooltips are not displayed.");
		}

		if (repositorySizeList.getAttribute("title").contains("Repository size")) {
			LogResult.pass("Repository size tooltips are displayed.");
		} else {
			LogResult.fail("Repository size tooltips are not displayed.");
		}

		if (lastUpdatedList.getAttribute("title").contains("Last updated")) {
			LogResult.pass("Last updated tooltips are displayed.");
		} else {
			LogResult.fail("Last updated tooltips are not displayed.");
		}
	}

	// To verify the description of repository by hovering mouse over results
	public void verifyRepositoryDescription() {
		action.moveToElement(mouseHoverDescription).perform();

		wait.until(ExpectedConditions.visibilityOf(mouseHoverDescription));

		if (repoDescription.isDisplayed()) {
			LogResult.pass("Repository description displayed as: " + repoDescription.getText());
		} else {
			LogResult.fail("Repository description is not displayed.");
		}
	}

	// Clicking on repository details button
	public void clickOnRepositoryDetailsBtn() {
		repositoryDetailBtn.click();

		waitingForSingleProjectResultPanel();

		if (singleDetailPanel.isDisplayed()) {
			LogResult.pass("Repository detail is displayed.");
		} else {
			LogResult.fail("Repository detail is not displayed.");
		}
	}

	// Clicking on Add to Batch button
	public void clickOnAddToBatchBtn() {

		wait.until(ExpectedConditions.visibilityOf(addToBatchBtn));

		addToBatchBtn.click();

		if (batchFilePanel.isDisplayed()) {
			LogResult.pass("Add to batch button is clicked.");
		} else {
			LogResult.fail("Add to batch button is not clicked.");
		}
	}

	// To verify UI elements for batch file Save,Export and Close section
	public void verifyBatchFileSaveExportCloseUI() {

		if (batchFileHelpTx.getText().contains(
				"You can Save the Batch File Repository List to a batch file enabling the projects listed within to be built and tested later with a single command.")) {
			LogResult.pass("Batch file creation help text is displayed.");
		} else {
			LogResult.fail("Batch file creation help text is not displayed.");
		}

		if (batchFileNameTbx.isDisplayed()) {
			LogResult.pass("Batch file text box is displayed.");

			if (batchFileNameTbx.getAttribute("placeholder").contentEquals("(e.g. mybatch-java)")) {
				LogResult.pass(
						"Batch file text box has placeholder text as: " + batchFileNameTbx.getAttribute("placeholder"));
			} else {
				LogResult.fail(
						"Batch file text box has placeholder text as: " + batchFileNameTbx.getAttribute("placeholder"));
			}
		} else {
			LogResult.fail("Batch file text box is not displayed.");
		}

		if (saveBatchFileBtn.isDisplayed()) {
			LogResult.pass("Save batch file button is displayed.");
		} else {
			LogResult.fail("Save batch file button is not displayed.");
		}

		if (exportBatchFileBtn.isDisplayed()) {
			LogResult.pass("Export batch file button is displayed.");
		} else {
			LogResult.fail("Export batch file button is not displayed.");
		}

		if (clearBatchFileBtn.isDisplayed()) {
			LogResult.pass("Clear batch file button is displayed.");
		} else {
			LogResult.fail("Clear batch file button is not displayed.");
		}

	}

	// To verify UI elements for Batch file repository panel after the file has
	// been added to Batch file
	public void verifyBatchFileRepositoryPanelUI() {
		if (batchFilePanelHeader.isDisplayed()) {
			LogResult.pass("Batch file panel header is displayed.");
			if (batchFilePanelHeader.getText().contentEquals("Batch File Repositories")) {
				LogResult.pass("Batch file panel header text is displayed as: " + batchFilePanelHeader.getText());
			} else {
				LogResult.fail("Batch file panel header text is displayed as: " + batchFilePanelHeader.getText());
			}
		} else {
			LogResult.fail("Batch file panel header is not displayed.");
		}

		if (batchFileRepoOwner.isDisplayed()) {
			LogResult.pass("Owners are displayed.");
		} else {
			LogResult.fail("Owners are not displayed.");
		}

		if (batchFileRepoName.isDisplayed()) {
			LogResult.pass("Repositories are displayed.");
		} else {
			LogResult.fail("Repositories are not displayed.");
		}

		if (batchFileRepoStarCount.isDisplayed()) {
			LogResult.pass("Star counts are displayed.");
		} else {
			LogResult.fail("Star counts are not displayed.");
		}

		if (batchFileRepoForkCount.isDisplayed()) {
			LogResult.pass("Fork counts are displayed.");
		} else {
			LogResult.fail("Fork counts are not displayed.");
		}

		if (batchFileRepoPrimaryLanguage.isDisplayed()) {
			LogResult.pass("Primary languages are displayed.");
		} else {
			LogResult.fail("Primary languages are not displayed.");
		}

		if (batchFileRepoSize.isDisplayed()) {
			LogResult.pass("Repository sizes are displayed.");
		} else {
			LogResult.fail("Repository sizes are not displayed.");
		}

		if (batchFileRepoLastUpdated.isDisplayed()) {
			LogResult.pass("Last updated details are displayed");
		} else {
			LogResult.fail("Last updated details are not displayed.");
		}

	}

	// To verify the description of added Repository in Batch file repository
	// panel
	public void verifyBatchFileRepositoryDescription() {
		action.moveToElement(batchFilemouseHoverDescription).perform();

		wait.until(ExpectedConditions.visibilityOf(batchFilerepoDescription));

		if (batchFilerepoDescription.isDisplayed()) {
			LogResult.pass("Repository description displayed as: " + batchFilerepoDescription.getText());
		} else {
			LogResult.fail("Repository description is not displayed.");
		}
	}

	// Clicking on Batch file Save button
	public void clickOnBatchFileSaveBtn() {
		wait.until(ExpectedConditions.visibilityOf(saveBatchFileBtn));

		saveBatchFileBtn.click();

		if (searchSingleProjectTab.isDisplayed()) { // batchSaveExportClearSection
			LogResult.pass("Save button clicked.");
		} else {
			LogResult.fail("Save button not clicked.");
		}

	}

	// Clicking on Batch file Export button
	public void clickOnBatchFileExportBtn() {
		exportBatchFileBtn.click();

		if (batchSaveExportClearSection.isDisplayed()) {
			LogResult.fail("Export button not clicked.");
		} else {
			LogResult.pass("Export button clicked.");
		}

	}

	// For obtaining latest modified file within the directory
	public File getLastModifiedFile() {
		File file = new File("C:\\Users\\manish_kane\\Downloads"); // for linux
																	// /root/Downloads
		File[] files = file.listFiles();
		if (files == null || files.length == 0) {
			return null;
		}

		File lastModifiedFile = files[0];
		for (int i = 1; i < files.length; i++) {
			if (lastModifiedFile.lastModified() < files[i].lastModified()) {
				lastModifiedFile = files[i];
			}
		}
		return lastModifiedFile;
	}

	// To verify whether recently exported file is downloaded in respective
	// location
	public void confirmFileDownload(String exportedBatchFileName) {

		if (getLastModifiedFile().getName().contains(exportedBatchFileName)) {
			LogResult.pass("File downloaded successfully.");
		} else {
			LogResult.fail("File not downloaded successfully.");
		}

	}

	// Clicking on Batch file Clear button
	public void clickOnBatchFileClearBtn() {
		clearBatchFileBtn.click();

		if (batchSaveExportClearSection.isDisplayed()) {
			LogResult.fail("Batch Files not cleared.");
		} else {
			LogResult.pass("Batch Files cleared.");
		}

	}

	// To verify if clicking on Use Current Version drop down displays different
	// versions
	public void verifyUseCurrentVersion() {

		wait.until(ExpectedConditions.visibilityOf(currentVersionForAutoResult));

		if (currentVersionForAutoResult.getText().contentEquals("Use current version")) {
			LogResult.pass("Use current version drop down is displayed.");

			currentVersionForAutoResult.click();

			for (WebElement item : currentVersionValues) {
				if (item.getText().contentEquals("Current"))
					break;
			}

			LogResult.pass("Different versions in the drop down displayed ");

			currentVersionForAutoResult.click();

		} else {
			LogResult.fail("Use current version drop down is not displayed.");
		}

	}

	// To verify the values in Select build servers drop down along with
	// selection/unselection of build servers
	public void verifySelectBuildServer() {

		if (selectBuildServerForAutoResult.isDisplayed()) {
			LogResult.pass("Select build servers drop down is displayed with values: ");

			selectBuildServerForAutoResult.click();

			List<WebElement> buildServer = buildServerList;

			for (WebElement item : buildServer) {

				LogResult.pass(item.getText());

			}

			List<WebElement> buildServerChkbx = buildServerListChkbx;

			for (WebElement item : buildServerChkbx) {

				item.click();

			}

			if (selectBuildServerForAutoResult.getText().contentEquals("None selected")) {
				LogResult.pass("All Build servers are unselected.");
			} else {
				LogResult.fail("All Build servers are not unselected. Unselected servers are: "
						+ selectBuildServerForAutoResult.getText());
			}

			List<WebElement> buildServerChkbx1 = buildServerListChkbx;
		
			int i=0;
			
			for (WebElement item : buildServerChkbx1) {

				item.click();
				i++;
			}
			
			this.setBuildServersCount(i);
			
			// Currently the build servers are dynamic hence checking for
			// partial text and omitting the number in brackets
			if (selectBuildServerForAutoResult.getText().contains("All selected")) {
				LogResult.pass("All Build servers are selected.");
			} else {
				LogResult.fail("All Build servers are not selected. Selected servers are: "
						+ selectBuildServerForAutoResult.getText());
			}

			selectBuildServerForAutoResult.click();

		} else {
			LogResult.fail("Select build servers drop down is not displayed.");
		}

	}
	
	
	public void setBuildServersCount(int buildServersCount){
		this.selectedBuildServersCount=buildServersCount;
		System.out.println(buildServersCount);
	}
	
	public int getBuildServersCount(){
		return this.selectedBuildServersCount;
	}
	
	

	// Clicking on Build+Test button
	public void clickOnBuildAndTestBtn() throws InterruptedException {

		selectBuildServerForAutoResult.click();

		ArrayList<String> buildServersArray = new ArrayList<String>();

		for (int i = 0; i < buildServerList.size(); i++) {

			buildServersArray.add(i, buildServerList.get(i).getText());
		}

		// for (int i=0;i< buildServerList.size();i++) {
		//
		// System.out.println("Value @ index: "+i+" is: "+
		// buildServerList.get(i).getText());
		//
		// }

		String currentWindow = driver.getWindowHandle();

		this.setBuildClickTime(getSystemTime());
		
		buildAndTestBtnForAutoResult.click();

		Thread.sleep(5000);

		driver.switchTo().window(currentWindow);

		wait.until(ExpectedConditions.visibilityOf(alertCloseBtn));

		if (alertCloseBtn.isDisplayed()) {
			LogResult.pass("Build+Test button is clicked.");

			if (alertMessage.getText().contentEquals("Build job submitted")) {
				LogResult.pass("Jobs successfully triggered on jenkins.");
			} else {
				LogResult.fail("Jobs failed to get triggered on jenkins.");
			}
		} else {
			LogResult.fail("Build+Test button is not clicked.");
		}

		Set<String> windowHandles = driver.getWindowHandles();

		for (String window : windowHandles) {
			// eliminate switching to current window
			if (!window.equals(currentWindow)) {
				// Now switchTo new Tab.
				driver.switchTo().window(window);

				for (String item : buildServersArray) {

					if (driver.getTitle().contains(item)) {

						LogResult.pass("Jenkins page opened for build server: " + item);
					}

				}

			}

		}

		Thread.sleep(10000); // wait till the job is completed

		for (String window : windowHandles) {

			// eliminate switching to current window
			if (!window.equals(currentWindow)) {
				// Now switchTo new Tab.
				driver.switchTo().window(window);

				driver.close();

			}
		}

		driver.switchTo().window(currentWindow);

	}
	
	public void setBuildClickTime(String buildClickTime){
		this.buildClickTime=buildClickTime;
		System.out.println(buildClickTime);
	}
	
	public String getBuildClickTime(){
		return this.buildClickTime;
	}

	
	
	// public String getJenkinsServerTime() {
	//
	// Date d = new Date();
	// DateFormat format = new SimpleDateFormat("yyyy-MM-dd-'h'HH-'m'mm-'s'ss");
	// format.setTimeZone(TimeZone.getTimeZone("CST")); //put server time zone
	// return format.format(d);
	// }
	
	public String getSystemTime(){
		Date d = new Date();
		DateFormat format = new SimpleDateFormat("yyyy-MM-dd-'h'HH-'m'mm-'s'ss");
		String buildTime = format.format(d);
		return buildTime;
	}

	// Clicking on Close button for dismissing alert
	public void clickOnAlertCloseBtn() throws InterruptedException {

		alertCloseBtn.click();

		Thread.sleep(2000);

		if (alertCloseBtn.isDisplayed()) {
			LogResult.fail("Close button is not clicked. Alert not dismissed.");
		} else {
			LogResult.pass("Close button is clicked. Alert dismissed.");
		}

	}

	// To verify Build Steps section (i.e Build, Test and Environment options)
	public void verifyBuildSteps() {

		wait.until(ExpectedConditions.visibilityOf(selectBuildOptions));

		if (selectBuildOptions.isDisplayed()) {
			if (selectBuildOptions.getText().contentEquals("Select build options")) {
				LogResult.pass("Select build options drop down has text: " + selectBuildOptions.getText());
			} else {
				LogResult.fail("Select Build options drop down has text: " + selectBuildOptions.getText());
			}

		} else {
			LogResult.fail("Select Build options drop down is not displayed.");
		}

		if (buildOptionsTbx.isDisplayed()) {

			LogResult.pass(
					"Select build options text box is displayed with value: " + buildOptionsTbx.getAttribute("value"));
		} else {
			LogResult.fail("Select build options text box is not displayed");
		}

		if (selectTestOptions.isDisplayed()) {
			if (selectTestOptions.getText().contentEquals("Select test options")) {
				LogResult.pass("Select test options drop down has text: " + selectTestOptions.getText());
			} else {
				LogResult.fail("Select test options drop down has text: " + selectTestOptions.getText());
			}
		} else {
			LogResult.fail("Select test options drop down is not displayed.");
		}

		if (testOptionsTbx.isDisplayed()) {
			LogResult.pass(
					"Select test options text box is displayed with value: " + testOptionsTbx.getAttribute("value"));
		} else {
			LogResult.fail("Select test options text box is not displayed");
		}

		if (selectEnvironmentOptions.isDisplayed()) {
			if (selectEnvironmentOptions.getText().contentEquals("Select environment options")) {
				LogResult.pass("Select environment options drop down has text: " + selectEnvironmentOptions.getText());
			} else {
				LogResult.fail("Select environment options drop down has text: " + selectEnvironmentOptions.getText());
			}
		} else {
			LogResult.fail("Select environment options drop down is not displayed.");
		}

		if (environmentOptionsTbx.isDisplayed()) {
			LogResult.pass("Select environment options text box is displayed with value: "
					+ environmentOptionsTbx.getAttribute("value"));
		} else {
			LogResult.fail("Select environment options text box is not displayed");
		}
	}

	// -----------Most commonly used projects------------

	// To verify expansion of Search for Most commonly used projects button
	public void clickOnMostCommonlyUsedProjectsBtn() {

		if (searchSingleProjectQueryTbx.isDisplayed()) {

			searchSingleProjectTab.click();
		}

		searchCommonlyUsedProjectsTab.click();

		if (searchCommonlyUsedProjectsTab.isDisplayed()) {
			LogResult.pass("Search for most commonly used project tab is expanded.");
		} else {
			LogResult.fail("Search for most commonly used project tab is not expanded.");
		}
	}

	// To verify Most commonly used projects button contents
	public void verifyCommonlyUsedProjectsUI() {
		if (commonProjectsTopRepositories.isDisplayed()) {
			LogResult.pass("Top repositories field is displayed.");
		} else {
			LogResult.fail("Top repositories field is not displayed");
		}

		if (commonProjectsSortBy.isDisplayed()) {
			LogResult.pass("Sort By field is displayed.");
		} else {
			LogResult.fail("Sort By field is not displayed");
		}

		if (commonProjectsProgrammingLanguage.isDisplayed()) {
			LogResult.pass("Programming languages field is displayed.");
		} else {
			LogResult.fail("Programming languages field is not displayed");
		}

		if (commonProjectsRelease.isDisplayed()) {
			LogResult.pass("Release field is displayed.");
		} else {
			LogResult.fail("Release field is not displayed");
		}

		if (commonProjectsPopularityStars.isDisplayed()) {
			LogResult.pass("Popularity Stars field is displayed.");
		} else {
			LogResult.fail("Popularity Stars field is not displayed");
		}

		if (commonProjectsForks.isDisplayed()) {
			LogResult.pass("Forks field is displayed.");
		} else {
			LogResult.fail("Forks field is not displayed");
		}

		if (commonProjectsSearchBtn.isDisplayed()) {
			LogResult.pass("Search button is displayed.");
		} else {
			LogResult.fail("Search button is not displayed.");
		}

	}

	// To verify Top Repositories text box UI
	public void verifyTopRepositoriesTxBx() {
		if (commonProjectsTopRepositories.isDisplayed()) {
			LogResult.pass("Top repositories is displayed.");

			if (preCommonProjectsTopRepositoriesLabelTx.getText().contentEquals("Top")
					&& postCommonProjectsTopRepositoriesLabelTx.getText().contentEquals("Repositories")) {
				LogResult.pass("Top repositories label is displayed.");
			} else {
				LogResult.fail("Top repositories label is not displayed. Label is displayed as: "
						+ preCommonProjectsTopRepositoriesLabelTx.getText() + " "
						+ postCommonProjectsTopRepositoriesLabelTx.getText());
			}

			if (commonProjectsTopRepositoriesValue.getAttribute("value").contentEquals("25")) {
				LogResult.pass("Top repositories field is displayed with value as: "
						+ commonProjectsTopRepositoriesValue.getAttribute("value"));
			} else {
				LogResult.fail("Top repositories field is displayed with value as: "
						+ commonProjectsTopRepositoriesValue.getAttribute("value"));
			}
		} else {
			LogResult.fail("Top repositories is not displayed.");
		}
	}

	// To verify Sort By drop down values along with result verification for
	// each value
	public void verifySortByDropDown() {

		Select s = new Select(commonProjectsSortByDropDown);

		if (commonProjectsSortBy.isDisplayed()) {

			LogResult.pass("Sort By drop down is displayed.");

			if (commonProjectsSortByLabelTx.getText().contentEquals("Sort by")) {
				LogResult.pass("Sort by label is displayed. Values in the drop down are: ");
			} else {
				LogResult.fail("Sort by label is not displayed. Label displayed is: "
						+ commonProjectsSortByLabelTx.getText() + " Values in the drop down are: ");
			}

			List<WebElement> sortByOptions = s.getOptions();

			for (WebElement item : sortByOptions) {
				LogResult.pass(item.getText());

			}

			for (int i = 0; i < sortByOptions.size(); i++) {

				s.selectByIndex(i);

				commonProjectsSearchBtn.click();
				wait.until(ExpectedConditions.visibilityOf(commonProjectSaveExportSection));

				if (commonProjectSaveExportSection.isDisplayed()) {
					LogResult.pass("Results sorted by: " + sortByOptions.get(i).getText());
				} else {
					LogResult.fail("Results sorted by: " + sortByOptions.get(i).getText());
				}
			}

			s.selectByIndex(0);

		} else {

			LogResult.pass("Sort By drop down is not displayed.");

		}

		if (s.getFirstSelectedOption().getText().contains("Popularity Stars")) {
			LogResult.pass("Default selected is: " + s.getFirstSelectedOption().getText());

		} else {
			LogResult.fail(
					"Popularity Stars is not selected. Value selected is: " + s.getFirstSelectedOption().getText());

		}
	}

	// To verify Programming Languages drop down values along with result
	// verification for each value
	public void verifyProgrammingLanguagesDropDown() {

		Select s = new Select(commonProjectsProgrammingLanguage);

		if (commonProjectsProgrammingLanguage.isDisplayed()) {
			LogResult.pass(
					"Programming Language drop down is displayed. Values in programming languages drop down are: ");

			List<WebElement> programmingLanguagesOptions = s.getOptions();

			for (WebElement item : programmingLanguagesOptions) {
				LogResult.pass(item.getText());
			}

			for (int i = 0; i < programmingLanguagesOptions.size(); i++) {

				s.selectByIndex(i);

				commonProjectsSearchBtn.click();
				wait.until(ExpectedConditions.visibilityOf(commonProjectSaveExportSection));

				if (commonProjectSaveExportSection.isDisplayed()
						|| primaryLanguageList.getText().contentEquals(programmingLanguagesOptions.get(i).getText())) {
					LogResult.pass("Results sorted by: " + programmingLanguagesOptions.get(i).getText());
				} else {
					LogResult.fail("Results sorted by: " + programmingLanguagesOptions.get(i).getText());
				}
			}

			s.selectByIndex(0);

		} else {
			LogResult.fail("Programming languages drop down is not displayed.");

		}

		if (s.getFirstSelectedOption().getText().contentEquals("Any programming language")) {
			LogResult.pass("Default selected value in Programming languages drop down is: "
					+ s.getFirstSelectedOption().getText());

		} else {
			LogResult.fail("Default selected value in Programming languages drop down is: "
					+ s.getFirstSelectedOption().getText());

		}
	}

	// To verify Release drop down values along with result verification for
	// each value
	public void verifyReleaseDropDown() {

		Select s = new Select(commonProjectsRelease);

		if (commonProjectsRelease.isDisplayed()) {
			LogResult.pass("Release drop down is not displayed. Values in release drop down are: ");

			List<WebElement> releaseOptions = s.getOptions();

			for (WebElement item : releaseOptions) {
				LogResult.pass(item.getText());
			}

			for (int i = 0; i < releaseOptions.size(); i++) {

				s.selectByIndex(i);

				commonProjectsSearchBtn.click();
				wait.until(ExpectedConditions.visibilityOf(commonProjectSaveExportSection));

				if (commonProjectSaveExportSection.isDisplayed()) {
					LogResult.pass("Results sorted by: " + releaseOptions.get(i).getText());
				} else {
					LogResult.fail("Results sorted by: " + releaseOptions.get(i).getText());
				}

				wait.until(ExpectedConditions.visibilityOf(commonProjectRepositoryDetailsList));

				commonProjectRepositoryDetailBtn.click();

				wait.until(ExpectedConditions.visibilityOf(commonProjectSingleDetailPanel));

				commonProjectCurrentVersion.click();

				String currentVersion = commonProjectCurrentVersionValue.getText().toLowerCase();
				String recentVersion = commonProjectRecentVersionValue.getText().toLowerCase();

				if (commonProjectCurrentVersion.getText().contains(currentVersion)) {
					LogResult.pass("Version selected in repository details is: " + currentVersion);
				} else if (commonProjectCurrentVersion.getText().contains(recentVersion)) {
					LogResult.pass("Version selected in repository details is: " + recentVersion);
				} else {
					LogResult.fail("Selected release version does not appear in repository details.");
				}

				commonProjectCurrentVersion.click();

				commonProjectBackToResultsBtn.click();

			}

			s.selectByIndex(0);

		} else {
			LogResult.fail("Release drop down is not displayed.");
		}

		if (s.getFirstSelectedOption().getText().contentEquals("Current")) {
			LogResult.pass("Default selected value in Release drop down is: " + s.getFirstSelectedOption().getText());

		} else {
			LogResult.fail("Default selected value in Release drop down is: " + s.getFirstSelectedOption().getText());
		}

	}

	// To verify >Popularity Stars text box
	public void verifyGreaterThanPopularityStars() {
		if (commonProjectsPopularityStars.isDisplayed()) {

			LogResult.pass("> Popularity Stars is displayed.");

			if (preCommonProjectsPopularityStarsLabelTx.getText().contentEquals(">")
					&& postCommonProjectsPopularityStarsLabelTx.getText().contentEquals("Popularity Stars")) {
				LogResult.pass("> Popularity Stars label is displayed.");
			} else {
				LogResult.fail("> Popularity Stars label is not displayed. Label is displayed as: "
						+ preCommonProjectsPopularityStarsLabelTx.getText() + " "
						+ postCommonProjectsPopularityStarsLabelTx.getText());
			}

			if (greaterThanPopularityStarsTxBx.getAttribute("value").contentEquals("0")) {
				LogResult.pass("> Popularity Stars field is displayed with value as: "
						+ greaterThanPopularityStarsTxBx.getAttribute("value"));
			} else {
				LogResult.fail("> Popularity Stars field is displayed with value as: "
						+ greaterThanPopularityStarsTxBx.getAttribute("value"));
			}
		} else {
			LogResult.fail("> Popularity Stars is not displayed.");
		}
	}

	// To verify >Forks text box
	public void verifyGreaterThanForks() {
		if (commonProjectsForks.isDisplayed()) {

			LogResult.pass("> Forks is displayed.");

			if (preCommonProjectsForksLabelTx.getText().contentEquals(">")
					&& postCommonProjectsForksLabelTx.getText().contentEquals("Forks")) {
				LogResult.pass("> Forks label is displayed.");
			} else {
				LogResult.fail("> Forks label is not displayed. Label is displayed as: "
						+ preCommonProjectsForksLabelTx.getText() + " " + postCommonProjectsForksLabelTx.getText());
			}

			if (greaterThanForksTxBx.getAttribute("value").contentEquals("0")) {
				LogResult.pass(
						"> Forks field is displayed with value as: " + greaterThanForksTxBx.getAttribute("value"));
			} else {
				LogResult.fail(
						"> Forks field is displayed with value as: " + greaterThanForksTxBx.getAttribute("value"));
			}
		} else {
			LogResult.fail("> Forks is not displayed.");
		}
	}

	// To enter number of repositories for searching Most commonly used projects
	public void enterNumOfTopRepositories(String num) throws InterruptedException {
		commonProjectsTopRepositoriesValue.clear();

		commonProjectsTopRepositoriesValue.sendKeys(num);

		Thread.sleep(3000);

		if (commonProjectsTopRepositoriesValue.getAttribute("value").contentEquals(num)) {
			LogResult.pass("Top Repositories value entered as: " + num);
		} else {
			LogResult.fail("Top Repositories value not entered.");
		}
	}

	// To select Sort By value
	public void selectSortByValue(String sortByValue) {
		Select s = new Select(commonProjectsSortByDropDown);

		s.selectByVisibleText(sortByValue);

		if (s.getFirstSelectedOption().getText().contentEquals(sortByValue)) {
			LogResult.pass("Selected Sort By value is: " + sortByValue);
		} else {
			LogResult.fail("Selected Sort By value is: " + sortByValue);
		}
	}

	// To select Programming Language value
	public void selectProgrammingLanguage(String prgmLanguage) {
		Select s = new Select(commonProjectsProgrammingLanguage);

		s.selectByVisibleText(prgmLanguage);

		if (s.getFirstSelectedOption().getText().contentEquals(prgmLanguage)) {
			LogResult.pass("Selected Programming Language value is: " + prgmLanguage);
		} else {
			LogResult.fail("Selected Programming Language value is: " + prgmLanguage);
		}
	}

	// To select Release value
	public void selectRelease(String release) {
		Select s = new Select(commonProjectsRelease);

		s.selectByVisibleText(release);

		if (s.getFirstSelectedOption().getText().contentEquals(release)) {
			LogResult.pass("Selected Release value is: " + release);
		} else {
			LogResult.fail("Selected Release value is: " + release);
		}
	}

	// To enter Popularity Stars value
	public void enterPopularityStars(String popularityStars) {
		greaterThanPopularityStarsTxBx.clear();

		greaterThanPopularityStarsTxBx.sendKeys(popularityStars);

		if (greaterThanPopularityStarsTxBx.getAttribute("value").contentEquals(popularityStars)) {
			LogResult.pass("Popularity Stars value entered as: " + popularityStars);
		} else {
			LogResult.fail("Popularity Stars value not entered.");
		}
	}

	// To enter Forks value
	public void enterForks(String forks) {
		greaterThanForksTxBx.clear();

		greaterThanForksTxBx.sendKeys(forks);

		if (greaterThanForksTxBx.getAttribute("value").contentEquals(forks)) {
			LogResult.pass("Popularity Stars value entered as: " + forks);
		} else {
			LogResult.fail("Popularity Stars value not entered.");
		}
	}

	// Clicking on Search button
	public void clickOnCommonlyUsedProjectSearch() {
		wait.until(ExpectedConditions.visibilityOf(commonProjectsSearchBtn));

		commonProjectsSearchBtn.click();

		 wait.until(ExpectedConditions.elementToBeClickable(commonProjectResultsPanel));

		if (commonProjectSaveExportSection.isDisplayed()) {
			LogResult.pass("Search button clicked.");
		} else {
			LogResult.fail("Search button not clicked.");
		}
	}

	// To verify Batch File Save, Export UI for Most commonly used projects
	public void verifyCommonProjectBatchFileSaveExportUI() {

		if (commonProjectBatchFileHelpTx.getText().contains("This is the list of most popular projects")) {
			LogResult.pass("Batch file help text is displayed.");
		} else {
			LogResult.fail("Batch file help text is not displayed.");
		}

		if (commonProjectBatchFileNameTbx.isDisplayed()) {
			LogResult.pass("Batch file text box is displayed.");

			if (commonProjectBatchFileNameTbx.getAttribute("placeholder").contentEquals("(e.g. mybatch-java)")) {
				LogResult.pass("Batch file text box has placeholder text as: "
						+ commonProjectBatchFileNameTbx.getAttribute("placeholder"));
			} else {
				LogResult.fail("Batch file text box has placeholder text as: "
						+ commonProjectBatchFileNameTbx.getAttribute("placeholder"));
			}
		} else {
			LogResult.fail("Batch file text box is not displayed.");
		}

		if (commonProjectSaveBatchBtn.isDisplayed()) {
			LogResult.pass("Save batch file button is displayed.");
		} else {
			LogResult.fail("Save batch file button is not displayed.");
		}

		if (commonProjectExportBatchBtn.isDisplayed()) {
			LogResult.pass("Export batch file button is displayed.");
		} else {
			LogResult.fail("Export batch file button is not displayed.");
		}

	}

	// To verify Actions column header in search results panel
	public void verifyCommonProjectRepositoryHeader() {
		if (commonProjectRepositoriesColHeader.isDisplayed()) {
			LogResult.pass("Repositories column is displayed.");
			if (commonProjectRepositoriesColHeader.getText().contentEquals("Repositories")) {
				LogResult.pass("Repositories column header text is displayed as: "
						+ commonProjectRepositoriesColHeader.getText());
			} else {
				LogResult.fail("Repositories column header text is displayed as: "
						+ commonProjectRepositoriesColHeader.getText());
			}
		} else {
			LogResult.fail("Repositories column is not displayed.");
		}
	}

	// To verify Actions column header along with UI in search results panel
	public void verifyActionsColumnListUIForCommonProjects() {

		if (commonProjectActionsColHeader.isDisplayed()) {
			LogResult.pass("Actions column is displayed.");
			if (commonProjectActionsColHeader.getText().contentEquals("Actions")) {
				LogResult
						.pass("Actions column header text is displayed as: " + commonProjectActionsColHeader.getText());
			} else {
				LogResult
						.fail("Actions column header text is displayed as: " + commonProjectActionsColHeader.getText());
			}
		} else {
			LogResult.fail("Actions column is not displayed.");
		}

		if (commonProjectRepositoryDetailsList.isDisplayed()) {
			LogResult.pass("Detail buttons are displayed");
		} else {
			LogResult.fail("Detail buttons are not displayed.");
		}

		if (commonProjectRemoveList.isDisplayed()) {
			LogResult.pass("Remove buttons are displayed.");
		} else {
			LogResult.fail("Remove buttons are not displayed.");
		}

	}

	// Clicking on repository details button for Most commonly used project
	public void clickOnRepositoryDetailsBtnForCommonProjects() throws InterruptedException {

		Thread.sleep(1000);

		commonProjectRepositoryDetailBtn.click();

		wait.until(ExpectedConditions.visibilityOf(commonProjectSingleDetailPanel));

		if (commonProjectSingleDetailPanel.isDisplayed()) {
			LogResult.pass("Repository detail is displayed.");
		} else {
			LogResult.fail("Repository detail is not displayed.");
		}
	}

	// To verify repository detail UI elements for Most commonly used project
	public void verifyProjectDetailRepoUIForCommonProjects() {

		wait.until(ExpectedConditions.visibilityOf(commonProjectSingleDetailPanel));

		if (commonProjectOwnerDetail.isDisplayed()) {
			LogResult.pass("Owner name is displayed: " + ownerDetail.getText());
		} else {
			LogResult.fail("Owner name is not displayed");
		}

		if (commonProjectRepositoryDetail.isDisplayed()) {
			LogResult.pass("Repository name is displayed: " + repositoryDetail.getText());
		} else {
			LogResult.fail("Repository name is not displayed.");
		}

		if (commonProjectStarCountDetail.isDisplayed()) {
			LogResult.pass("Star count is displayed: " + starCountDetail.getText());
		} else {
			LogResult.fail("Star count is not displayed.");
		}

		if (commonProjectForkCountDetail.isDisplayed()) {
			LogResult.pass("Fork count is displayed: " + forkCountDetail.getText());
		} else {
			LogResult.fail("Fork count is not displayed.");
		}

		if (commonProjectPrimaryLanguageDetail.isDisplayed()) {
			LogResult.pass("Primary language is displayed: " + primaryLanguageDetail.getText());
		} else {
			LogResult.fail("Primary language is not displayed.");
		}

		if (commonProjectRepositorySizeDetail.isDisplayed()) {
			LogResult.pass("Repository size is displayed: " + repositorySizeDetail.getText());
		} else {
			LogResult.fail("Repository size is not displayed.");
		}

		if (commonProjectLastUpdatedDetail.isDisplayed()) {
			LogResult.pass("Last updated detail is displayed: " + lastUpdatedDetail.getText());
		} else {
			LogResult.fail("Last updated detail is not displayed.");
		}

		if (commonProjectDescriptionHeader.isDisplayed()) {
			LogResult.pass("Description header is displayed.");
			if (commonProjectDescriptionHeader.getText().contentEquals("Description")) {
				LogResult.pass("Description header has text as: " + commonProjectDescriptionHeader.getText());
			} else {
				LogResult.fail("Description header has text as: " + commonProjectDescriptionHeader.getText());
			}
		} else {
			LogResult.fail("Description header is not displayed.");
		}

		if (commonProjectDescriptionText.isDisplayed()) {
			LogResult.pass("Description text is displayed with text as: " + commonProjectDescriptionText.getText());
		} else {
			LogResult.fail("Description text is not displayed.");
		}

		if (commonProjectLanguageCompositionHeader.isDisplayed()) {
			LogResult.pass("Language composition header is displayed.");
			if (commonProjectLanguageCompositionHeader.getText().contentEquals("Language Composition")) {
				LogResult.pass(
						"Language composition header has text as: " + commonProjectLanguageCompositionHeader.getText());
			} else {
				LogResult.fail(
						"Language composition header has text as: " + commonProjectLanguageCompositionHeader.getText());
			}
		} else {
			LogResult.fail("Language composition header is not displayed.");
		}

		if (commonProjectLanguagePieChart.isDisplayed()) {
			LogResult.pass("Language pie chart is displayed.");
		} else {
			LogResult.fail("Language pie chart is not displayed.");
		}

		if (commonProjectLanguageLegend.isDisplayed()) {
			LogResult.pass("Language legends are displayed: ");

			List<WebElement> legends = commonProjectLangLegendValues;

			for (WebElement item : legends) {

				LogResult.pass(item.getText());

			}

		} else {
			LogResult.fail("Language legends are not displayed.");
		}

		// In case of Java Primary language, check for JDK drop down
		if (commonProjectPrimaryLanguageDetail.getText().contentEquals("Java")) {

			if (commonProjectUseJDK.isDisplayed()) {
				LogResult.pass("Use JDK option drop down is displayed with options: ");

				commonProjectUseJDK.click();

				List<WebElement> jdks = commonProjectUseJDKOptions;

				for (WebElement item : jdks) {

					LogResult.pass(item.getText());

				}

				commonProjectUseJDK.click();

			} else {
				LogResult.fail("Use JDK option drop down is not displayed.");

			}
		}

		// In case of JavaScript Primary language, check for NodeJs drop down
		if (commonProjectPrimaryLanguageDetail.getText().contentEquals("JavaScript")) {

			if (commonProjectUseNodeJs.isDisplayed()) {
				LogResult.pass("Use NodeJs option drop down is displayed with options: ");

				commonProjectUseNodeJs.click();

				List<WebElement> nodejs = commonProjectUseNodeJsOptions;

				for (WebElement item : nodejs) {

					LogResult.pass(item.getText());

				}

				commonProjectUseNodeJs.click();

			} else {
				LogResult.fail("Use NodeJs option drop down is not displayed.");

			}
		}

		if (commonProjectCurrentVersion.isDisplayed()) {
			LogResult.pass("Use current version drop down is displayed.");
			if (commonProjectCurrentVersion.getText().contentEquals("Use current version")) {
				LogResult.pass("Use current version drop down has text: " + commonProjectCurrentVersion.getText());

			} else {
				LogResult.fail("Use current version drop down has text: " + commonProjectCurrentVersion.getText());
			}

			commonProjectCurrentVersion.click();

			for (WebElement item : commonProjectCurrentVersionValues) {
				if (item.getText().contentEquals("Current"))
					break;
			}

			LogResult.pass("Different versions in the drop down displayed ");
			commonProjectCurrentVersion.click();

		} else {
			LogResult.fail("Use current version drop down is not displayed.");
		}

		if (commonProjectSelectBuildServer.isDisplayed()) {
			LogResult.pass("Select build servers drop down is displayed with values: ");

			commonProjectSelectBuildServer.click();

			List<WebElement> buildServer = commonProjectBuildServerList;

			for (WebElement item : buildServer) {

				LogResult.pass(item.getText());

			}

			commonProjectSelectBuildServer.click();

		} else {
			LogResult.fail("Select build servers drop down is not displayed.");
		}

		if (commonProjectBuildAndTestBtn.isDisplayed()) {
			LogResult.pass("Build and Test button is displayed.");
			if (commonProjectBuildAndTestBtn.getText().contentEquals("Build + Test")) {
				LogResult.pass("Build and Test button has text: " + commonProjectBuildAndTestBtn.getText());
			} else {
				LogResult.fail("Build and Test button has text: " + commonProjectBuildAndTestBtn.getText());
			}
		} else {
			LogResult.fail("Build and Test button is not displayed.");
		}

		if (commonProjectBuildStepsHeader.isDisplayed()) {
			LogResult.pass("Build Steps header is displayed.");
			if (commonProjectBuildStepsHeader.getText().contentEquals("Build steps")) {
				LogResult.pass("Build Steps header has text: " + commonProjectBuildStepsHeader.getText());
			} else {
				LogResult.fail("Build Steps header has text: " + commonProjectBuildStepsHeader.getText());
			}
		} else {
			LogResult.fail("Build Steps header is not displayed.");
		}

		if (commonProjectSelectBuildOptions.isDisplayed()) {
			if (commonProjectSelectBuildOptions.getText().contentEquals("Select build options")) {
				LogResult.pass("Select build options drop down has text: " + commonProjectSelectBuildOptions.getText());
			} else {
				LogResult.fail("Select Build options drop down has text: " + commonProjectSelectBuildOptions.getText());
			}

		} else {
			LogResult.fail("Select Build options drop down is not displayed.");
		}

		if (commonProjectBuildOptionsTbx.isDisplayed()) {
			LogResult.pass("Select build options text box is displayed");
		} else {
			LogResult.fail("Select build options text box is not displayed");
		}

		if (commonProjectSelectTestOptions.isDisplayed()) {
			if (commonProjectSelectTestOptions.getText().contentEquals("Select test options")) {
				LogResult.pass("Select test options drop down has text: " + commonProjectSelectTestOptions.getText());
			} else {
				LogResult.fail("Select test options drop down has text: " + commonProjectSelectTestOptions.getText());
			}
		} else {
			LogResult.fail("Select test options drop down is not displayed.");
		}

		if (commonProjectTestOptionsTbx.isDisplayed()) {
			LogResult.pass("Select test options text box is displayed");
		} else {
			LogResult.fail("Select test options text box is not displayed");
		}

		if (commonProjectSelectEnvironmentOptions.isDisplayed()) {
			if (commonProjectSelectEnvironmentOptions.getText().contentEquals("Select environment options")) {
				LogResult.pass("Select environment options drop down has text: "
						+ commonProjectSelectEnvironmentOptions.getText());
			} else {
				LogResult.fail("Select environment options drop down has text: "
						+ commonProjectSelectEnvironmentOptions.getText());
			}
		} else {
			LogResult.fail("Select environment options drop down is not displayed.");
		}

		if (commonProjectEnvironmentOptionsTbx.isDisplayed()) {
			LogResult.pass("Select environment options text box is displayed");
		} else {
			LogResult.fail("Select environment options text box is not displayed");
		}
	}

	// To verify appearance of Back to Results button for Most commonly used
	// project
	public void verifyBackToResultsBtnForCommonProjects() {
		if (commonProjectBackToResultsBtn.isDisplayed()) {
			LogResult.pass("Back to results button is displayed.");
		} else {
			LogResult.fail("Back to results button is not displayed.");
		}
	}

	// Clicking on Back to Results
	public void clickOnBackToResultsForCommonProjects() {
		commonProjectBackToResultsBtn.click();

		if (commonProjectResultsPanel.isDisplayed()) {
			LogResult.pass("Navigated back to results");
		} else {
			LogResult.fail("Not navigated back to results");
		}
	}

	// Clicking on Save button for Batch File creation
	public void clickOnBatchFileSaveBtnForCommonProjects() throws InterruptedException {
		wait.until(ExpectedConditions.visibilityOf(commonProjectSaveBatchBtn));

		commonProjectSaveBatchBtn.click();

		Thread.sleep(1000);

		if (commonProjectSaveExportSection.isDisplayed()) {
			LogResult.fail("Save button not clicked.");
		} else {
			LogResult.pass("Save button clicked.");
		}

	}

	// Clicking on Export button for Batch File
	public void clickOnBatchFileExportBtnForCommonProjects() {
		commonProjectExportBatchBtn.click();

		if (commonProjectSaveExportSection.isDisplayed()) {
			LogResult.fail("Export button not clicked.");
		} else {
			LogResult.pass("Export button clicked.");
		}

	}

	// To verify removal of batch file in results panel
	public void commonProjectRemoveRepository() {

		String repoName = topRepositoryName.getText();

		commonProjectRepositoryRemoveBtn.click();

		if (topRepositoryName.getText().contentEquals(repoName)) {
			LogResult.fail("Repository not removed");
		} else {
			LogResult.pass("Repository removed successfully.");
		}

	}

	// To verify Use current version drop down values for Most commonly used
	// project
	public void verifyUseCurrentVersionForCommonProject() {

		if (commonProjectCurrentVersion.getText().contentEquals("Use current version")) {
			LogResult.pass("Use current version drop down is displayed.");

			commonProjectCurrentVersion.click();

			for (WebElement item : commonProjectCurrentVersionValues) {
				if (item.getText().contentEquals("Current"))
					break;
			}

			LogResult.pass("Different versions in the drop down displayed ");

			commonProjectCurrentVersion.click();

		} else {
			LogResult.fail("Use current version drop down is not displayed.");
		}

	}

	// To verify Select build servers value along with selection/unselection of
	// build servers
	public void verifySelectBuildServerForCommonProject() {

		if (commonProjectSelectBuildServer.isDisplayed()) {
			LogResult.pass("Select build servers drop down is displayed with values: ");

			commonProjectSelectBuildServer.click();

			List<WebElement> buildServer = commonProjectBuildServerList;

			for (WebElement item : buildServer) {

				LogResult.pass(item.getText());

			}

			List<WebElement> buildServerChkbx = commonProjectBuildServerListChkbx;

			for (WebElement item : buildServerChkbx) {

				item.click();

			}

			if (commonProjectSelectBuildServer.getText().contentEquals("None selected")) {
				LogResult.pass("All Build servers are unselected.");
			} else {
				LogResult.fail("All Build servers are not unselected. Unselected servers are: "
						+ commonProjectSelectBuildServer.getText());
			}

			List<WebElement> buildServerChkbx1 = commonProjectBuildServerListChkbx;

			int i=0;
			
			for (WebElement item : buildServerChkbx1) {

				item.click();
				i++;
			}
			
			this.setBuildServersCount(i);

			// Currently the build servers are dynamic hence checking for
			// partial text and omitting the number in brackets
			if (commonProjectSelectBuildServer.getText().contains("All selected")) {
				LogResult.pass("All Build servers are selected.");
			} else {
				LogResult.fail("All Build servers are not selected. Selected servers are: "
						+ commonProjectSelectBuildServer.getText());
			}

			commonProjectSelectBuildServer.click();

		} else {
			LogResult.fail("Select build servers drop down is not displayed.");
		}

	}

	// Clicking on Build+Test button for Most commonly used project
	public void clickOnBuildAndTestBtnForCommonProject() throws InterruptedException {

		commonProjectSelectBuildServer.click();

		ArrayList<String> buildServersArray = new ArrayList<String>();

		for (int i = 0; i < commonProjectBuildServerList.size(); i++) {

			buildServersArray.add(i, commonProjectBuildServerList.get(i).getText());
		}
	

//		 for (int i=0;i< buildServerList.size();i++) {
//		
//		 System.out.println("Value @ index: "+i+" is: "+commonProjectBuildServerList.get(i).getText());
//		
//		 }

		String currentWindow = driver.getWindowHandle();

		this.setBuildClickTime(getSystemTime());
		
		commonProjectBuildAndTestBtn.click();

		Thread.sleep(5000);

		driver.switchTo().window(currentWindow);

		wait.until(ExpectedConditions.visibilityOf(alertCloseBtn));

		if (alertCloseBtn.isDisplayed()) {
			LogResult.pass("Build+Test button is clicked.");

			if (alertMessage.getText().contentEquals("Build job submitted")) {
				LogResult.pass("Jobs successfully triggered on jenkins.");
			} else {
				LogResult.fail("Jobs failed to get triggered on jenkins.");
			}
		} else {
			LogResult.fail("Build+Test button is not clicked.");
		}

		Set<String> windowHandles = driver.getWindowHandles();

		for (String window : windowHandles) {
			// eliminate switching to current window
			if (!window.equals(currentWindow)) {
				// Now switchTo new Tab.
				driver.switchTo().window(window);

				for (String item : buildServersArray) {

					if (driver.getTitle().contains(item)) {

						LogResult.pass("Jenkins page opened for build server: " + item);
					}

				}

			}

		}

		Thread.sleep(10000); // wait till the job is completed

		for (String window : windowHandles) {

			// eliminate switching to current window
			if (!window.equals(currentWindow)) {
				// Now switchTo new Tab.
				driver.switchTo().window(window);

				driver.close();

			}
		}

		driver.switchTo().window(currentWindow);

	}

	// To verify Build Steps section (i.e Build, Test and Environment options)
	// for Most commonly used project
	public void verifyBuildStepsForCommonProject() {

		wait.until(ExpectedConditions.visibilityOf(commonProjectSelectBuildOptions));
		
		if (commonProjectSelectBuildOptions.isDisplayed()) {
			if (commonProjectSelectBuildOptions.getText().contentEquals("Select build options")) {
				LogResult.pass("Select build options drop down has text: " + commonProjectSelectBuildOptions.getText());
			} else {
				LogResult.fail("Select Build options drop down has text: " + commonProjectSelectBuildOptions.getText());
			}

		} else {
			LogResult.fail("Select Build options drop down is not displayed.");
		}

		if (commonProjectBuildOptionsTbx.isDisplayed()) {

			LogResult.pass("Select build options text box is displayed with value: "
					+ commonProjectBuildOptionsTbx.getAttribute("value"));
		} else {
			LogResult.fail("Select build options text box is not displayed");
		}

		if (commonProjectSelectTestOptions.isDisplayed()) {
			if (commonProjectSelectTestOptions.getText().contentEquals("Select test options")) {
				LogResult.pass("Select test options drop down has text: " + commonProjectSelectTestOptions.getText());
			} else {
				LogResult.fail("Select test options drop down has text: " + commonProjectSelectTestOptions.getText());
			}
		} else {
			LogResult.fail("Select test options drop down is not displayed.");
		}

		if (commonProjectTestOptionsTbx.isDisplayed()) {
			LogResult.pass("Select test options text box is displayed with value: "
					+ commonProjectTestOptionsTbx.getAttribute("value"));
		} else {
			LogResult.fail("Select test options text box is not displayed");
		}

		if (commonProjectSelectEnvironmentOptions.isDisplayed()) {
			if (commonProjectSelectEnvironmentOptions.getText().contentEquals("Select environment options")) {
				LogResult.pass("Select environment options drop down has text: "
						+ commonProjectSelectEnvironmentOptions.getText());
			} else {
				LogResult.fail("Select environment options drop down has text: "
						+ commonProjectSelectEnvironmentOptions.getText());
			}
		} else {
			LogResult.fail("Select environment options drop down is not displayed.");
		}

		if (commonProjectEnvironmentOptionsTbx.isDisplayed()) {
			LogResult.pass("Select environment options text box is displayed with value: "
					+ commonProjectEnvironmentOptionsTbx.getAttribute("value"));
		} else {
			LogResult.fail("Select environment options text box is not displayed");
		}
	}

	// Verify Github website navigation upon owner click from List view for Most
	// commonly used project
	public void clickOnOwnerForCommonProject() {

		commonProjectOwnerList.click();

		wait.until(ExpectedConditions.titleContains("Git"));

		if (getPageTitle().contains("Git")) {
			LogResult.pass("Owner details are displayed on GitHub website.");
		} else {
			LogResult.fail("Owner details are not displayed on GitHub website.");
		}

	}

	// verify Github website navigation upon repository click from list view
	// Most commonly used project
	public void clickOnRepositoryForCommonProject() {
		commonProjectRepositoryList.click();

		wait.until(ExpectedConditions.titleContains("Git"));

		if (getPageTitle().contains("Git")) {
			LogResult.pass("Repository details are displayed on GitHub website.");
		} else {
			LogResult.fail("Repository details are not displayed on GitHub website.");
		}
	}

	public void clickOnFirstRepositoryDetailsBtn() {

		firstRepositoryDetailsList.click();

	}

}
