package com.autoport.pageobjects;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.pagefactory.AjaxElementLocatorFactory;
import org.openqa.selenium.support.ui.FluentWait;

public class SearchTab {
	WebDriver driver;
	FluentWait<WebDriver> fluintWait;
	
	public SearchTab(WebDriver driver, FluentWait<WebDriver> fluintWait ){
		this.driver = driver;
		this.fluintWait = fluintWait;
		AjaxElementLocatorFactory factory = new AjaxElementLocatorFactory(driver, 5);
		PageFactory.initElements(factory, this);
	}

}
