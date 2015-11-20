package com.autoport.pageobjects;

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
	FluentWait<WebDriver> fluintWait;
	
	public ReportsTab(WebDriver driver, FluentWait<WebDriver> fluintWait ){
		this.driver = driver;
		this.fluintWait = fluintWait;
		AjaxElementLocatorFactory factory = new AjaxElementLocatorFactory(driver, 5);
		PageFactory.initElements(factory, this);			 
	}	
	
	/* */
	@FindBy(id="jobManageButton")	 
    WebElement manageProjectResults;
	
	@FindBy(id="projectFilter")	 
    WebElement projectResultTextBox;
	
	@FindBy(xpath="//div[@id='jobManagePanel']/div[1]/div[2]/a[1]/button")	 
    WebElement listLocalBtn;
	
	@FindBy(xpath="//div[@id='jobManagePanel']/div[1]/div[2]/a[2]/button")	 
    WebElement listArchivedBtn;
	
	@FindBy(xpath="//div[@id='jobManagePanel']/div[1]/div[2]/a[3]/button")	 
    WebElement listAllBtn;
	
	/* */
	@FindBy(id="testResultsButton")	 
    WebElement manageBatchJobResults;
	
	
}


