package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.FluentWait;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.ReportsTab;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class Reports_UseCase_3 {
	WebDriver driver;
	FluentWait<WebDriver> fluentWait;
	CommonFunctions functions;
	HomePage homePage;
	ReportsTab reportsTab;	
	String localProjectResultToArchive;
	String localProjectResultToRemove;
	String archivedProjectResultToRemove;
	 
	 @BeforeTest
	  public void beforeTest() throws Exception {
		 
		 //CommonFunctions.launchBrowser(); 
		 driver = CommonFunctions.driver; 
		 homePage = CommonFunctions.homePage;
		 
		 homePage = CommonFunctions.homePage;
		 reportsTab = CommonFunctions.reportsTab;	
		 
		 localProjectResultToArchive = ReadTestData.readParameter("Reports_UseCase_3", "localProjectResultToArchive");
		 localProjectResultToRemove = ReadTestData.readParameter("Reports_UseCase_3", "localProjectResultToRemove");
		 archivedProjectResultToRemove = ReadTestData.readParameter("Reports_UseCase_3", "archivedProjectResultToRemove");
		 
		 homePage.openReportsTab();
		 
		 reportsTab.clickManageCompareProjectResultsButton();
	  }
	 
	 @Test(priority=0)
	 public void Reports_Archive_Local_Project_Result_008() throws Exception{			 
		 
		  reportsTab.enterProjectResultToSearch(localProjectResultToArchive); 
		  
		  reportsTab.clickListLocalProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject(localProjectResultToArchive);	
		  
		  reportsTab.selectCheckboxForPackage(localProjectResultToArchive);
		  
		  reportsTab.verifyButtonsAreEnabled();
		  
		  reportsTab.clickArchiveProjectResultsBtn();
		   
		  reportsTab.verifyArchivedSuccessfullyMsg();
		  
		  reportsTab.clearSearchedProjectResult();
	 }
	 
	 @Test(priority=1)
	 public void Reports_Remove_Local_Project_Result_009() throws Exception{		  
		 
		  reportsTab.enterProjectResultToSearch(localProjectResultToRemove); 
		  
		  reportsTab.clickListLocalProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject(localProjectResultToRemove);	
		  
		  reportsTab.selectCheckboxForPackage(localProjectResultToRemove);
		  
		  reportsTab.verifyButtonsAreEnabled();
		  
		  reportsTab.clickRemoveProjectResultsBtn();
		  
		  reportsTab.verifyDeletedSuccessfullyMsg();
		  
		  reportsTab.clearSearchedProjectResult();
	 }	 
	 
	 @Test(priority=2)
	 public void Reports_Remove_Archived_Project_Result_010() throws Exception{		  
		 
		  reportsTab.enterProjectResultToSearch(archivedProjectResultToRemove); 
		  
		  reportsTab.clickListArchivedProjectResultsButton();
		  
		  reportsTab.verifySearchResultsforProject(archivedProjectResultToRemove);	
		  
		  reportsTab.selectCheckboxForPackage(archivedProjectResultToRemove);
		  
		  reportsTab.verifyButtonsAreEnabled();
		  
		  reportsTab.clickRemoveProjectResultsBtn();
		  
		  reportsTab.verifyDeletedSuccessfullyMsg();
		  
		  reportsTab.clearSearchedProjectResult();
	 }	 
}
