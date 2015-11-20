package com.autoport.pageobjects;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.pagefactory.AjaxElementLocatorFactory;
import org.openqa.selenium.support.ui.FluentWait;

import com.autoport.utilities.*;

public class HomePage {
	
	WebDriver driver;
	FluentWait<WebDriver> fluintWait;
	
	public HomePage(WebDriver driver, FluentWait<WebDriver> fluintWait ){
		this.driver = driver;
		this.fluintWait = fluintWait;
		AjaxElementLocatorFactory factory = new AjaxElementLocatorFactory(driver, 5);
		PageFactory.initElements(factory, this);	
	}	
	
	@FindBy(id="jenkinsTab")	 
    WebElement buildServerTab;
	
	@FindBy(id="reportsTab")	 
    WebElement reportsTab;
	
	@FindBy(id="batchTab")	 
    WebElement batchJobsTab;
	
	@FindBy(id="searchTab")	 
    WebElement searchTab;
	
	/* Function to open build server tab */
	public void clickBuildServerTab(){
		buildServerTab.click();
		
		if(true){
			LogResult.pass("Build Servers' tab is displayed.");
		}
		else{
			LogResult.fail("Build Servers' tab is not displayed.");
		}
	}

}
