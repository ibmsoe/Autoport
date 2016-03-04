package com.autoport.pageobjects;

import java.util.List;
import java.util.Set;

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

    public BuildServersTab(WebDriver driver, FluentWait<WebDriver> wait) {
        this.driver = driver;
        this.wait = wait;
        AjaxElementLocatorFactory factory = new AjaxElementLocatorFactory(
                driver, 5);
        PageFactory.initElements(factory, this);
    }

    /********************* Show Jenkins Status *****************************/

    @FindBy(id = "jenkinsManageButton")
    WebElement showJenkinsStatusBtn;

    @FindBy(xpath = "//div[@id='jenkinsLink']/ul/a")
    WebElement jenkinsPageLink;

    @FindBy(xpath = "//div[@id='jenkinsPanel']/button")
    WebElement checkProgressBtn;

    @FindBy(xpath = "//div[@id='jenkinsPanel']/ul")
    WebElement totalJobs;

    @FindBy(xpath = "//div[@id='jenkinsPanel']/ul/li[1]")
    WebElement successfulJobs;

    @FindBy(xpath = "//div[@id='jenkinsPanel']/ul/li[2]")
    WebElement unstableJobs;

    @FindBy(xpath = "//div[@id='jenkinsPanel']/ul/li[3]")
    WebElement failingJobs;

    @FindBy(xpath = "//div[@id='jenkinsPanel']/ul/li[4]")
    WebElement disabledJobs;

    @FindBy(id = "jenkinsSlaveButton")
    WebElement manageJenkinsSlaveNodesBtn;

    /************************* List / Install / Remove software ****************************/

    @FindBy(id = "manageSingleSlaveButton")
    WebElement listInstallRemoveSoftwareBtn;

    @FindBy(id = "packageFilter_Single")
    WebElement searchPkgSingleTxtBox;

    @FindBy(xpath = "//div[@id='manageSingleSlavePanel']/div[1]/div[2]/span/div/button")
    WebElement buildServerBtn;

    @FindBy(xpath = "//div[@id='manageSingleSlavePanel']/div[1]/div[2]/a/button")
    WebElement listBtn;

    @FindBy(id = "singlePanelInstallBtn")
    WebElement singlePanelInstallBtn;

    @FindBy(id = "singlePanelRemoveBtn")
    WebElement singlePanelRemoveBtn;

    @FindBy(id = "singleServerPackageListTable")
    WebElement singleServerPackageListTable;

    @FindBy(xpath = "//div[@id='manageSingleSlavePanel']/div[3]//span[@class='page-list']/span/button")
    WebElement noOfRecordsBtn;

    @FindBy(xpath = "//div[@id='manageSingleSlavePanel']/div[3]/div[1]/div")
    WebElement notificationMsg;

    @FindBy(xpath = "//table[@id='singleServerPackageListTable']/tbody/tr/td[6]")
    List<WebElement> packageSummaryColumnRows;

    @FindBy(xpath = "//table[@id='singleServerPackageListTable']/tbody/tr/td[2]")
    WebElement packageColumnRows;

    /**************** List / Install / Remove software using managed runtime services ********/

    @FindBy(id = "manageMultipleSlaveButton")
    WebElement listInstallRemoveSoftwareUsingManagedServicesBtn;

    @FindBy(id = "packageFilter_Multiple")
    WebElement searchPkgMultipleTxtBox;
    // to be commented

    // added bu vaibhav on 8-02-2016 for changed functionality

    // for main button
    @FindBy(xpath = "//*[@id='manageMultipleSlavePanel']/div[1]/div[2]/span/div/button")
    WebElement buildServerdropdown;

    // LIST BUTTON
    @FindBy(id = "managedListBtn")
    WebElement ServerListBtn;

    @FindBy(xpath = "//div[@id='manageMultipleSlavePanel']/div[3]/div[2]/div")
    WebElement notificationMsgForSearchUsingManagedServices;

    @FindBy(xpath = "//div[@id='manageMultipleSlavePanel']/div[3]/div[2]/a/span/div/button")
    WebElement buildServerBtnForManagedServices;

    @FindBy(id = "syncManagedPackageButton")
    WebElement synchManagedPackagesBtn;

    @FindBy(id = "addToManagedList")
    WebElement addToManagedListBtn;

    @FindBy(id = "removeFromManagedList")
    WebElement removeFromManagedListBtn;

    @FindBy(id = "multiServerPackageListTable")
    WebElement multiServerPackageListTable;

    /************************** Upload Packages To Repository **************/

    @FindBy(xpath = "//div[@id='jenkinsStatus']/div[3]/div[1]")
    WebElement uploadPackagesToRepositoryBtn;

    @FindBy(id = "uploadPackageName")
    WebElement uploadPackageTextBox;

    @FindBy(xpath = "//div[@id='jenkinsStatus']/div[3]/div[2]/div[5]/div")
    WebElement uploadBtn;

    @FindBy(xpath = "//div[@id='jenkinsStatus']/div[3]/div[2]/div[not(@style) or @style='']/span/div/button")
    WebElement packageTypeBtn;

    /************************** Show/Clean build slave using managed runtime services **************/

    @FindBy(xpath = "//div[@id='managerebootServerButton'][1]")
    WebElement showCleanBuildSlavesBtn;

    @FindBy(xpath = "//table[@id='rebootServerListTable']/thead/tr/th[2]/div[1]")
    WebElement buildServerHeader;

    @FindBy(xpath = "//table[@id='rebootServerListTable']/thead/tr/th[3]/div[1]")
    WebElement hostNameHeader;

    @FindBy(xpath = "//table[@id='rebootServerListTable']/thead/tr/th[4]/div[1]")
    WebElement ipAddressHeader;

    @FindBy(xpath = "//table[@id='rebootServerListTable']/thead/tr/th[5]/div[1]")
    WebElement OSHeader;

    @FindBy(xpath = "//table[@id='rebootServerListTable']/thead/tr/th[6]/div[1]")
    WebElement statusHeader;

    @FindBy(xpath = "//table[@id='rebootServerListTable']/thead/tr/th[7]/div[1]")
    WebElement JenkinsSlaveLinkHeader;

    @FindBy(xpath = "//div[@id='rebootServerPanel']/div[1]")
    WebElement rebootSyncHelpTxt;

    // @FindBy(id="rebootSync")
    @FindBy(xpath = "//div[@id='rebootServerPanel']//a[2]/button[@id='rebootSync'][1]")
    WebElement rebootSyncBtn;

    @FindBy(xpath = "//div[@id='rebootServerPanel']/div[1]")
    WebElement rebootSyncHelpMsg;

    @FindBy(xpath = "//*[@id='rebootServerListTable']/tbody/tr")
    List<WebElement> numOfRowsInRebootSyncPanel;

    /****************************** Manage Jenkins Slave Nodes Functions *******************************/

    /* Function to open to Show Jenkins status section */
    public void openShowJenkinsStatusSection() {
        if (checkProgressBtn.isDisplayed()) {
            LogResult.pass("Show Jenkins status section is expanded.");
        } else {
            showJenkinsStatusBtn.click();

            if (checkProgressBtn.isDisplayed()) {
                LogResult.pass("Show Jenkins status section is expanded.");
            } else {
                LogResult.fail("Show Jenkins status section is not expanded.");
            }
        }
    }

    /* Function to close to Show Jenkins status section */
    public void closeShowJenkinsStatusSection() {
        if (checkProgressBtn.isDisplayed()) {
            showJenkinsStatusBtn.click();

            if (checkProgressBtn.isDisplayed()) {
                LogResult.fail("Show Jenkins status section is not closed.");
            } else {
                LogResult.pass("Show Jenkins status section is closed.");
            }
        } else {
            LogResult.pass("Show Jenkins status section is closed.");
        }
    }

    /* Function to verify the jenkins Page Url */
    public void verifyJenkinsPageUrl(String url) {
        String jenkinsPageUrl = jenkinsPageLink.getText();

        if (jenkinsPageUrl.equals(url)) {
            LogResult.pass("Jenkins page URL is correct.");
        } else {
            LogResult.fail("Jenkins page URL is not correct.");
        }
    }

    /* Function to verify that the jenkins status is displayed correctly */
    public void verifyJenkinsStatus() {
        String str = totalJobs.getText();
        String totaljobs = str.substring(0, str.indexOf('\n'));
        int noOftotalJobs = getNumber(totaljobs);
        int noOfSuccessJobs = getNumber(successfulJobs.getText());
        int noOfUnstableJobs = getNumber(unstableJobs.getText());
        int noOfFailingJobs = getNumber(failingJobs.getText());
        int noOfDisabledJobs = getNumber(disabledJobs.getText());

        int totalJobs = noOfSuccessJobs + noOfUnstableJobs + noOfFailingJobs
                + noOfDisabledJobs;

        if (noOftotalJobs == totalJobs) {
            LogResult.pass("Jenkins status is displayed correctly");
        } else {
            LogResult.fail("Jenkins status is not displayed correctly");
        }

    }

    /* Function to get only numbers from string */
    public int getNumber(String str) {

        String numberOnly = str.replaceAll("[^0-9]", "");

        return Integer.parseInt(numberOnly);
    }

    /* Function to verify the progress bar is displayed correctly */
    public void VerifyProgressBar() {
        String greenColor = "rgba(92, 184, 92, 1)";

        String bgColor = driver.findElement(
                By.xpath("//div[@id='progressBar']/div/div[1]")).getCssValue(
                "background-color");

        if (bgColor.equals(greenColor)) {
            LogResult.pass("Progress bar is displayed correctly");
        } else {
            LogResult.fail("Progress bar is not displayed correctly");
        }
    }

    /* Function to click Check Progress button */
    public void clickCheckProgressBtn() throws InterruptedException {
        checkProgressBtn.click();
        Thread.sleep(10000);
    }

    /* Function to open Manage Jenkins Slave Nodes section */
    public void clickManageJenkinsSlaveNodesBtnToOpen() {

        if (listInstallRemoveSoftwareBtn.isDisplayed()) {
            LogResult.pass("Manage Jenkins Slave Nodes section' is Opened.");
        } else {
            manageJenkinsSlaveNodesBtn.click();

            if (listInstallRemoveSoftwareBtn.isDisplayed()) {
                LogResult
                        .pass("Manage Jenkins Slave Nodes section' is Opened.");
            } else {

                LogResult
                        .fail("Manage Jenkins Slave Nodes section' is expanded.");
            }
        }
    }

    /********************** List / Install / Remove software *************************/

    /* Function to open List / Install / Remove software section */
    public void clickListInstallRemoveSoftwareBtnToOpen() {

        if (searchPkgSingleTxtBox.isDisplayed()) {
            LogResult
                    .pass("List / Install / Remove software on a given build server' section is expanded.");
        } else {
            listInstallRemoveSoftwareBtn.click();

            if (searchPkgSingleTxtBox.isDisplayed()) {

                LogResult
                        .pass("List / Install / Remove software on a given build server' section is expanded.");
            } else {
                LogResult
                        .fail("List / Install / Remove software on a given build server' section is expanded.");
            }
        }

    }

    /* Function to verify Placeholder text for Searchbox */
    public void verifyPlaceHolderTextForSearchBox() {
        String placeholderText = searchPkgSingleTxtBox
                .getAttribute("placeholder");

        if (placeholderText
                .contains("(e.g. firefox or leave blank to see which packages are installed"))
            LogResult.pass("placeholder text is correct for search box.");
        else
            LogResult.fail("placeholder text is not correct for search box.");
    }

    /* Function to enter packagename to search */
    public void enterPackageToSearch(String packageName)
            throws InterruptedException {

        searchPkgSingleTxtBox.clear();
        searchPkgSingleTxtBox.sendKeys(packageName);
        Thread.sleep(1000);

        if (searchPkgSingleTxtBox.getAttribute("value").contains(packageName)) {
            LogResult.pass("user is able to enter packagename in search box.");
        } else {
            LogResult
                    .fail("user is not able to enter packagename in search box.");
        }
    }

    /* Function to clear packagename from searchbox */
    public void clearPackageName() {

        searchPkgSingleTxtBox.clear();
    }

    /* Function to select Buildserver from dropdown */
    public void selectBuildServer(String buildServerName) {

        buildServerBtn.click();

        String xpath = "//div[@id='manageSingleSlavePanel']//ul/li/a/label[text()[contains(.,'"
                + buildServerName + "')]]/input";
        driver.findElement(By.xpath(xpath)).click();

        LogResult.pass(buildServerName + " Build Server is selected");
    }

    /* Function to select Buildserver from dropdown */
    public void selectFirstBuildServer() {

        buildServerBtn.click();

        String xpath = "//div[@id='manageSingleSlavePanel']//ul/li[1]/a/label/input";
        driver.findElement(By.xpath(xpath)).click();

        LogResult.pass("First Build Server is selected");
    }

    /* Function to list down packages by clicking list button */
    public void clickListBtn() {

        listBtn.click();

        wait.until(ExpectedConditions.visibilityOfElementLocated(By
                .xpath("//div[@id='manageSingleSlavePanel']/div[3]/div[1]/div")));

        if (singleServerPackageListTable.isDisplayed()) {
            LogResult
                    .pass("Packages with different available versions are displayed in table");
        } else {
            LogResult
                    .fail("Packages with different available versions are not displayed in table");
        }
    }

    /*
     * Function to verify the search results for the packagename entered in
     * search box
     */
    public void verifySearchResultsforPackage(String searchedPackage) {

        List<WebElement> packagenames = driver
                .findElements(By
                        .xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[2]"));
        int noOfpackages = 0;

        for (WebElement packagename : packagenames) {

            if (packagename.getText().contains(searchedPackage)) {
                noOfpackages++;
            } else {
                LogResult
                        .fail("Search Results are not correct for package searched.");
                break;
            }
        }

        if (noOfpackages == packagenames.size()) {
            LogResult.pass("Search Results are correct for package searched.");
        }
    }

    /* Function to select the package to install from the search result list */
    public String selectRandomPackageToInstall() {

        WebElement NApackagecheckbox = driver
                .findElement(By
                        .xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[3][text()[contains(.,'N/A')]]/preceding-sibling::td[2]/input"));

        WebElement packagename = driver
                .findElement(By
                        .xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[3][text()[contains(.,'N/A')]]/preceding-sibling::td[1]"));
        ;

        NApackagecheckbox.click();

        String packageSelected = packagename.getText();

        if (NApackagecheckbox.isSelected()) {
            LogResult.pass(packageSelected
                    + " Package is selected for installation");
        } else {
            LogResult.fail("Package is not selected for installation");
        }

        return packageSelected;
    }

    /* Function to select already installed package to install */
    public void selectAlreadyInstalledPackageToInstall() {

        WebElement alreadyInstalledPackage = driver
                .findElement(By
                        .xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[5][text()[contains(.,'No')]]/preceding-sibling::td[4]/input"));
        alreadyInstalledPackage.click();
    }

    /* Function to select the two versions of the package to install */
    public String selectTwoVersionsToInstall(String packagename) {

        List<WebElement> pkgCheckbox = driver
                .findElements(By
                        .xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[2][text()[contains(.,'"
                                + packagename
                                + "')]]//ancestor::tr[1]/td/input"));

        String firstVersion = driver
                .findElement(
                        By.xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[2][text()[contains(.,'"
                                + packagename + "')]]//ancestor::tr[1]/td[4]"))
                .getText();

        pkgCheckbox.get(0).click();

        pkgCheckbox.get(1).click();

        return firstVersion;
    }

    /* Function to select the installed package to update */
    public String selectPackageToUpdate() throws InterruptedException {

        String firstElement = driver
                .findElement(
                        By.xpath("//table[@id='singleServerPackageListTable']/tbody/tr[1]/td[5]"))
                .getText();

        if (firstElement.equals("No")) {
            driver.findElement(
                    By.xpath("//table[@id='singleServerPackageListTable']/thead/tr/th[5]/div[1]"))
                    .click();
            Thread.sleep(3000);
        }

        WebElement NApackagecheckbox = driver
                .findElement(By
                        .xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[5][text()[contains(.,'Yes')]]/preceding-sibling::td[4]/input"));

        WebElement packagename = driver
                .findElement(By
                        .xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[5][text()[contains(.,'Yes')]]/preceding-sibling::td[3]"));
        ;

        NApackagecheckbox.click();

        String packageSelected = packagename.getText();

        if (NApackagecheckbox.isSelected()) {
            LogResult.pass(packageSelected
                    + " Package is selected for installation");
        } else {
            LogResult.fail("Package is not selected for installation");
        }

        return packageSelected;
    }

    /* This functin selects package to uninstall */
    public void selectPackageToUninstall() {

        driver.findElement(
                By.xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[1]/input"))
                .click();

    }

    /*
     * Function to verify the If the Install/Remove button is enabled or
     * disabled
     */
    public void verifyInstallRemoveButtons(String buttonStatus) {

        if (buttonStatus.equalsIgnoreCase("enabled")) {
            if (singlePanelInstallBtn.isEnabled()
                    && singlePanelRemoveBtn.isEnabled())
                LogResult.pass("Install/Update and Remove buttons are enabled");
            else
                LogResult
                        .fail("Install/Update and Remove buttons are not enabled");
        }

        if (buttonStatus.equalsIgnoreCase("disabled")) {
            if (singlePanelInstallBtn.isEnabled()
                    || singlePanelRemoveBtn.isEnabled())
                LogResult
                        .fail("Install/Update and Remove buttons are not disabled");
            else
                LogResult
                        .pass("Install/Update and Remove buttons are disabled");
        }
    }

    /* Function to click on install update button */
    public void clickInstallUpdateBtn() {
        singlePanelInstallBtn.click();
    }

    /* Function to click on remove button tp uninstall the package */
    public void clickRemoveButtonToUninstall() {
        singlePanelRemoveBtn.click();
    }

    /*
     * Function to verify that the installation success pop up is displayed
     * correctly
     */
    public void verifyInstallationSuccessPopUp(String packagename) {

        wait.until(ExpectedConditions.visibilityOfElementLocated(By
                .xpath("//div[@id='errorAlert']//tbody/tr[2]")));

        String installedPackageName = driver.findElement(
                By.xpath("//div[@id='errorAlert']//tbody/tr[2]/td[1]"))
                .getText();

        String actionname = driver.findElement(
                By.xpath("//div[@id='errorAlert']//tbody/tr[2]/td[2]"))
                .getText();

        String status = driver.findElement(
                By.xpath("//div[@id='errorAlert']//tbody/tr[2]/td[3]"))
                .getText();

        if (installedPackageName.contains(packagename))
            LogResult
                    .pass("Package name is correct in installaton success message");
        else
            LogResult
                    .fail("Package name is not correct in installaton success message");

        if (actionname.contains("install/update"))
            LogResult
                    .pass("Action name is correct in installaton success message");
        else
            LogResult
                    .fail("Action name is not correct in installaton success message");

        if (status.contains("SUCCESS"))
            LogResult.pass("Status is correct in installaton success message");
        else
            LogResult
                    .fail("Status is not correct in installaton success message");

        driver.findElement(
                By.xpath("//div[@id='errorAlert']/div/div/div[3]/button"))
                .click();
    }

    /*
     * Function to verify that Installed version column is naot diaplayed as N/A
     * for installed package
     */
    public void verifyInstalledVersionIsNotNA(String packagename) {

        String version = driver
                .findElement(
                        By.xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[text() = '"
                                + packagename + "']/following-sibling::td[1]"))
                .getText();

        if (version.contains("N/A")) {
            LogResult
                    .fail("Installed version is displayed as N/A for installed package");
        } else {
            LogResult.pass("Installed version for package " + packagename
                    + " is " + version);
        }
    }

    /*
     * Function to verify that Installed version column is naot diaplayed as N/A
     * for installed package
     */
    public void verifyInstalledVersionIsNA(String packagename) {

        String version = driver
                .findElement(
                        By.xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[text() = '"
                                + packagename + "']/following-sibling::td[1]"))
                .getText();

        if (version.contains("N/A")) {
            LogResult
                    .pass("Installed version is displayed as N/A for installed package");
        } else {
            LogResult.fail("Installed version for package " + packagename
                    + " is " + version);
        }
    }

    /*
     * Function to verify that the package updation success pop up is displayed
     * correctly
     */
    public void verifyUpdationSuccessPopUp(String packagename) {

        wait.until(ExpectedConditions.visibilityOfElementLocated(By
                .xpath("//div[@id='errorAlert']//tbody/tr[2]")));

        String installedPackageName = driver.findElement(
                By.xpath("//div[@id='errorAlert']//tbody/tr[2]/td[1]"))
                .getText();

        String actionname = driver.findElement(
                By.xpath("//div[@id='errorAlert']//tbody/tr[2]/td[2]"))
                .getText();

        String status = driver.findElement(
                By.xpath("//div[@id='errorAlert']//tbody/tr[2]/td[3]"))
                .getText();

        if (installedPackageName.contains(packagename))
            LogResult
                    .pass("Package name is correct in updation success message");
        else
            LogResult
                    .fail("Package name is not correct in updation success message");

        if (actionname.contains("install/update"))
            LogResult
                    .pass("Action name is correct in updation success message");
        else
            LogResult
                    .fail("Action name is not correct in updation success message");

        if (status.contains("SUCCESS"))
            LogResult.pass("Status is correct in updation success message");
        else
            LogResult.fail("Status is not correct in updation success message");

        driver.findElement(
                By.xpath("//div[@id='errorAlert']/div/div/div[3]/button"))
                .click();
    }

    /*
     * Function to verify that the package is updated successfully and Installed
     * version and available versions are same
     */
    public void VerifyPackageUpdateIsSuccessfull(String packagename) {

        String installedversion = driver
                .findElement(
                        By.xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[text() = '"
                                + packagename + "']/following-sibling::td[1]"))
                .getText();

        String availableversion = driver
                .findElement(
                        By.xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[text() = '"
                                + packagename + "']/following-sibling::td[2]"))
                .getText();

        if (installedversion.equals(availableversion)) {
            LogResult
                    .pass("Installed version and availabble versions are same and package is updated.");
        } else {
            LogResult
                    .fail("Installed version and availabble versions are not same and package is not updated.");
        }
    }

    /*
     * Function to verify that the package uninstallation success pop up is
     * displayed correctly
     */
    public void verifyUninstallationSuccessPopUp(String packagename) {

        wait.until(ExpectedConditions.visibilityOfElementLocated(By
                .xpath("//div[@id='errorAlert']//tbody/tr[2]")));

        String installedPackageName = driver.findElement(
                By.xpath("//div[@id='errorAlert']//tbody/tr[2]/td[1]"))
                .getText();

        String actionname = driver.findElement(
                By.xpath("//div[@id='errorAlert']//tbody/tr[2]/td[2]"))
                .getText();

        String status = driver.findElement(
                By.xpath("//div[@id='errorAlert']//tbody/tr[2]/td[3]"))
                .getText();

        if (installedPackageName.contains(packagename))
            LogResult
                    .pass("Package name is correct in uninstallaton success message");
        else
            LogResult
                    .fail("Package name is not correct in uninstallaton success message");

        if (actionname.contains("remove/update"))
            LogResult
                    .pass("Action name is correct in uninstallaton success message");
        else
            LogResult
                    .fail("Action name is not correct in uninstallaton success message");

        if (status.contains("SUCCESS"))
            LogResult
                    .pass("Status is correct in uninstallaton success message");
        else
            LogResult
                    .fail("Status is not correct in uninstallaton success message");

        driver.findElement(
                By.xpath("//div[@id='errorAlert']/div/div/div[3]/button"))
                .click();
    }

    /*
     * Function to verify that the package is already installed and the correct
     * pop up message is displayed
     */
    public void verifyAlreadyInstalledMessage() {

        wait.until(ExpectedConditions.visibilityOfElementLocated(By
                .xpath("//div[@id='errorAlert']/div/div/div[1]")));
        String alreadyInstalledMsg = driver.findElement(
                By.xpath("//div[@id='errorAlert']/div/div/div[1]")).getText();

        if (alreadyInstalledMsg
                .contains("The selected package(s) is/are already installed"))
            LogResult
                    .pass("Package is already installed message is displayed correctly");
        else
            LogResult
                    .fail("Package is already installed message is not displayed correctly");

        driver.findElement(
                By.xpath("//div[@id='errorAlert']/div/div/div[3]/button"))
                .click();
    }

    /*
     * Function to verify that the package is not installed pop up message is
     * displayed when unstalling it
     */
    public void verifyPkgNotInstalledMessage() {

        wait.until(ExpectedConditions.visibilityOfElementLocated(By
                .xpath("//div[@id='errorAlert']/div/div/div[1]")));
        String alreadyInstalledMsg = driver.findElement(
                By.xpath("//div[@id='errorAlert']/div/div/div[1]")).getText();

        if (alreadyInstalledMsg
                .contains("The selected packages are not installed and therefore cannot be removed!"))
            LogResult
                    .pass("The selected packages are not installed and therefore cannot be removed message is displayed correctly");
        else
            LogResult
                    .fail("The selected packages are not installed and therefore cannot be removed message is not displayed correctly");

        driver.findElement(
                By.xpath("//div[@id='errorAlert']/div/div/div[3]/button"))
                .click();
    }

    /*
     * Function to verify that correct message is displayed when two versions of
     * same package are selected for installation
     */
    public void verifyTwoVersionMessage(String packagename, String version)
            throws InterruptedException {
        Thread.sleep(2000);
        Alert alert = driver.switchTo().alert();
        String alertmsg = alert.getText();

        if (alertmsg.contains(version) && alertmsg.contains(packagename))
            LogResult
                    .pass("Correct Pop up message is displayed stating that Only the first selected entry is marked for instalation");
        else
            LogResult
                    .fail("Correct Pop up message is not displayed stating that Only the first selected entry is marked for instalation");

        alert.accept();
    }

    /*
     * Function to verify that correct notification message is displayed above
     * search results table
     */
    public void verifyNotificationMessage(String message) {

        if (notificationMsg.getText().contains(message)) {

            LogResult.pass("Expected notification message is displayed.");
        } else {
            LogResult.fail("Expected notification message is not displayed.");
        }
    }

    /*
     * Function to verify that only installed packages are displayed in search
     * results
     */
    public void verifyOnlyInstalledPackagesareDisplayed()
            throws InterruptedException {

        selectMaximumRecordsToDisplay();

        List<WebElement> installedVersions = driver
                .findElements(By
                        .xpath("//table[@id='singleServerPackageListTable']/tbody/tr/td[3]"));

        int noOfpackages = 0;
        for (WebElement installedVersion : installedVersions) {

            noOfpackages++;
            if (installedVersion.getText() == "N/A") {
                LogResult.fail("Uninstalled packages are listed also.");
                break;
            }
        }

        if (noOfpackages == installedVersions.size()) {
            LogResult
                    .pass("Only installed packages are displayed in serch result");
        }
    }

    /* Function to select maximum records to display */
    public void selectMaximumRecordsToDisplay() throws InterruptedException {

        noOfRecordsBtn.click();
        Thread.sleep(1000);

        driver.findElement(
                By.xpath("//div[@id='manageSingleSlavePanel']/div[3]//span[@class='page-list']/span/ul/li[last()]/a"))
                .click();
        Thread.sleep(5000);
    }

    /***********************
     * List / Install / Remove software using managed runtime services Functions
     ***********************/

    /*
     * Function to open List / Install / Remove software using managed runtime
     * services section
     */
    public void clickListInstallRemoveSoftwareUsingManagedServicesBtnToOpen() {

        if (searchPkgMultipleTxtBox.isDisplayed()) {
            LogResult
                    .pass("List / Install / Remove software using managed runtime services' section is expanded.");
        } else {
            listInstallRemoveSoftwareUsingManagedServicesBtn.click();

            if (searchPkgMultipleTxtBox.isDisplayed()) {
                LogResult
                        .pass("List / Install / Remove software using managed runtime services' section is expanded.");
            } else {
                LogResult
                        .fail("List / Install / Remove software using managed runtime services' section is expanded.");
            }
        }
    }

    /* Function to enter packagename to search */
    public void enterPackageToSearchUsingManagedServices(String packageName)
            throws InterruptedException {

        searchPkgMultipleTxtBox.clear();
        searchPkgMultipleTxtBox.sendKeys(packageName);
        Thread.sleep(1000);

        if (searchPkgMultipleTxtBox.getAttribute("value").contains(packageName)) {
            LogResult.pass("user is able to enter packagename in search box.");
        } else {
            LogResult
                    .fail("user is not able to enter packagename in search box.");
        }
    }

    /* generic function for Selecting built server by vaibhav on 8-2-2016 */
    public void SelectBuiltServer(String buildServerName) {

        buildServerdropdown.click();
        // /input[@Value='CentOS']
        String xpathOfBuildserver = "//input[@Value='" + buildServerName + "']";
        // this xpath didnt work as it was giving remove software value which
        // was not visible
        // String xpathOfBuildserver = "//label[text()[contains(.,'" +
        // buildServerName +"')]]/input";
        WebElement BScheckbox = driver
                .findElement(By.xpath(xpathOfBuildserver));
        BScheckbox.click();
        ServerListBtn.click();
        wait.until(ExpectedConditions.visibilityOfElementLocated(By
                .id("multiServerPackageListTable")));

        if (multiServerPackageListTable.isDisplayed()) {
            LogResult.pass("Managed list of packages are displayed in table");
        } else {
            LogResult.fail("Managed list of packages are not displayed");
        }
    }

    /* Function to select maximum records to display */
    public void selectMaxRecordsToDisplayForManagedServices()
            throws InterruptedException {

        driver.findElement(
                By.xpath("//div[@id='manageRuntime']/div[1]//span[@class='page-list']/span/button"))
                .click();
        Thread.sleep(1000);

        driver.findElement(
                By.xpath("//div[@id='manageRuntime']/div[1]//span[@class='page-list']/span/ul/li[last()]/a"))
                .click();
        Thread.sleep(5000);
    }

    /*
     * Function to verify that correct notification message is displayed above
     * search results table for managed servics
     */
    public void verifyNotificationMessageForManagedServices(String message) {

        String notificationMsg = driver
                .findElement(
                        By.xpath("//div[@id='manageMultipleSlavePanel']/div[3]/div[2]/div"))
                .getText();
        if (notificationMsg.contains(message)) {

            LogResult.pass("Expected notification message is displayed.");
        } else {
            LogResult.fail("Expected notification message is not displayed.");
        }
    }

    /*
     * Function to verify that the build servers are populated as per list
     * button selected
     */
    public void verifyPopulatedBuildServers(String machineType) {

        List<WebElement> buildservers = driver
                .findElements(By
                        .xpath("//div[@id='manageMultipleSlavePanel']//label[@class='checkbox']/input"));

        switch (machineType) {
        case "CentOS"://RHEL
            for (WebElement buildserver : buildservers) {
                String strBS = buildserver.getAttribute("value");
                if (strBS.contains("CentOS")) {//RHEL
                    LogResult.pass(strBS
                            + " Build servers are displayed correctly");
                } else {
                    LogResult.fail(strBS
                            + " Build servers are not displayed correctly ");
                    break;
                }
            }
            break;
        case "Ubuntu":
            for (WebElement buildserver : buildservers) {
                String strBS = buildserver.getAttribute("value");
                if (strBS.contains("Ubuntu")) {
                    LogResult.pass(strBS + " Build server is displayed ");
                } else {
                    LogResult.fail(strBS + " Build server is displayed ");
                    break;
                }
            }
            break;
        case "All":
            for (WebElement buildserver : buildservers) {
                String strBS = buildserver.getAttribute("value");
                if (strBS.contains("Ubuntu") || strBS.contains("CentOS")) {//RHEL
                    LogResult.pass(strBS + " Build server is displayed ");
                } else {
                    LogResult.fail(strBS + " Build server is displayed ");
                    break;
                }
            }
            break;
        default:
            LogResult.fail(" Please send correct machine type");
            break;
        }

    }

    /*
     * Function to verify that the search results are correct for in multi
     * server package list table
     */
    public void verifySearchResultsForManagedServicesList(String machineType) {

        List<WebElement> oss = driver
                .findElements(By
                        .xpath("//table[@id='multiServerPackageListTable']/tbody/tr/td[7]"));

        List<WebElement> nodes = driver
                .findElements(By
                        .xpath("//table[@id='multiServerPackageListTable']/tbody/tr/td[8]"));

        switch (machineType) {
        case "CentOS": //RHEL
            for (WebElement os : oss) {
                String osname = os.getText();
                if (osname.contains("CentOS")) {//RHEL
                } else {
                    LogResult.fail(osname + " OS is not centos");//rhel
                    break;
                }
            }

            for (WebElement node : nodes) {
                String nodename = node.getText();
                if (nodename.contains("centos")) {//rhel
                } else {
                    LogResult.fail(nodename + " Node is not centos");//rhel
                    break;
                }
            }
            break;
        case "Ubuntu":
            for (WebElement os : oss) {
                String osname = os.getText();
                if (osname.contains("Ubuntu")) {
                } else {
                    LogResult.fail(osname + " OS is not Ubuntu");
                    break;
                }
            }

            for (WebElement node : nodes) {
                String nodename = node.getText();
                if (nodename.contains("ubuntu")) {
                } else {
                    LogResult.fail(nodename + " Node is not Ubuntu");
                    break;
                }
            }
            break;
        case "All":
            for (WebElement os : oss) {
                String osname = os.getText();
                if (osname.contains("Ubuntu") || osname.contains("CentOS")) {//RHEL
                } else {
                    LogResult.fail(osname + " OS is not Ubuntu");
                    break;
                }
            }

            for (WebElement node : nodes) {
                String nodename = node.getText();
                if (nodename.contains("ubuntu") || nodename.contains("centos")) {//rhel
                } else {
                    LogResult.fail(nodename + " Node is not Ubuntu");
                    break;
                }
            }
            break;
        default:
            LogResult.fail(" Please send correct machine type");
            break;
        }
    }

    /*
     * Function to verify that the checkboxes are not enabled for non removable
     * packages
     */
    public void verifyChkboxNotEnabledForNonRemovablePkgs() {

        List<WebElement> nonRemovablePkgsChkBox = driver
                .findElements(By
                        .xpath("//table[@id='multiServerPackageListTable']/tbody/tr/td[6][text()='No']/ancestor::tr[1]/td[1]"));

    }

    /*
     * Function to select the package to add to manages services
     * of list
     */
    public String selectPackageToAdd(String packagename) {

        WebElement packageChkBox = driver
                .findElement(By
                        .xpath("//table[@id='multiServerPackageListTable']/tbody/tr/td[2][text()[contains(.,'"
                                + packagename + "')]]/ancestor::tr/td[1]/input"));

        packageChkBox.click();

        String version = driver
                .findElement(
                        By.xpath("//table[@id='multiServerPackageListTable']/tbody/tr/td[2][text()[contains(.,'"
                                + packagename + "')]]/ancestor::tr/td[5]"))
                .getText();

        if (packageChkBox.isSelected()) {
            LogResult.pass(packagename + " is selected.");
        } else {
            LogResult.pass(packagename + " is not selected.");
        }
        return version;
    }

    /*
     * Function to select the package and remove from manages services
     * of list
     */
    public String selectPackageToRemove(String packagename) {

        WebElement packageChkBox = driver
                .findElement(By
                        .xpath("//table[@id='multiServerPackageListTable']/tbody/tr/td[3][text()[not(contains(.,'N/A'))]]/ancestor::tr/td[1]/input"));

        packageChkBox.click();

        String version = driver
                .findElement(
                        By.xpath("//table[@id='multiServerPackageListTable']/tbody/tr/td[2][text()[contains(.,'"
                                + packagename + "')]]/ancestor::tr/td[5]"))
                .getText();

        if (packageChkBox.isSelected()) {
            LogResult.pass(packagename + " is selected.");
        } else {
            LogResult.pass(packagename + " is not selected.");
        }
        return version;
    }


    /* Function to click Add Button */
    public void clickAddToManagedListBtn() {
        driver.findElement(By.id("addToManagedList")).click();
    }

    /* Function to click Remove Button */
    public void clickremoveFromManagedListBtn() {
        driver.findElement(By.id("removeFromManagedList")).click();
    }

    /*
     * Function to verify that the pop up message stating eligible packages to
     * add is displayed and accepted
     */
    public void verifyAndAcceptAddPopup(String packageName, String version)
            throws InterruptedException {
        Thread.sleep(2000);
        Alert alert = driver.switchTo().alert();
        String alertmsg = alert.getText();

        if (alertmsg.contains(version) && alertmsg.contains(packageName)
                && alertmsg.contains("The below packages are eligible for Add")) {
            LogResult
                    .pass("Correct Pop up message stating the eligible package and version to add is displayed.");
            alert.accept();
        } else {
            LogResult
                    .fail("Correct Pop up message stating the eligible package and version to add is displayed.");
            alert.accept();
        }

    }

    /*
     * Function to verify that the package is Added to managed list successfully
     * message is displayed correctly.
     */
    public void verifyPkgAddSuccessMessage() {

        wait.until(ExpectedConditions.visibilityOfElementLocated(By
                .xpath("//div[@id='errorAlert']/div/div/div[1]")));
        String alreadyInstalledMsg = driver.findElement(
                By.xpath("//div[@id='errorAlert']/div/div/div[1]")).getText();

        if (alreadyInstalledMsg.contains("Success!"))
            LogResult
                    .pass("Added Successfully ! message is displayed correctly");
        else
            LogResult
                    .fail("Added Successfully ! message is not displayed correctly");

        driver.findElement(
                By.xpath("//div[@id='errorAlert']/div/div/div[3]/button"))
                .click();
    }

    /*
     * Function to verify that the package is removed from managed list
     * successfully message is displayed correctly.
     */
    public void verifyPkgRemoveSuccessMessage() {

        wait.until(ExpectedConditions.visibilityOfElementLocated(By
                .xpath("//div[@id='errorAlert']/div/div/div[1]")));
        String alreadyInstalledMsg = driver.findElement(
                By.xpath("//div[@id='errorAlert']/div/div/div[1]")).getText();

        if (alreadyInstalledMsg.contains("Success!"))
            LogResult
                    .pass("Removed Successfully ! message is displayed correctly");
        else
            LogResult
                    .fail("Removed Successfully ! message is not displayed correctly");

        driver.findElement(
                By.xpath("//div[@id='errorAlert']/div/div/div[3]/button"))
                .click();
    }

    /* Function to click on synch button */
    public void clickSynchBtn() {
        synchManagedPackagesBtn.click();
    }

    /*
     * Function to verify the Please select build server message is displayed
     * correctly.
     */
    public void verifySelectBuildServerMsg() throws InterruptedException {
        wait.until(ExpectedConditions.visibilityOfElementLocated(By
                .xpath("//div[@id='errorAlert']/div/div/div[1]")));
        String selectBuildServermsg = driver.findElement(
                By.xpath("//div[@id='errorAlert']/div/div/div[1]")).getText();

        if (selectBuildServermsg.contains("Please select build server"))
            LogResult
                    .pass("Please select build server message is displayed correctly");
        else
            LogResult
                    .fail("Please select build server message is not displayed correctly");

        driver.findElement(
                By.xpath("//div[@id='errorAlert']/div/div/div[3]/button"))
                .click();

        Thread.sleep(2000);
    }

    /* Function to select the build server to sysch the managed packages. */
    public void selectBuildServerToSynch(String buildserver) {

        buildServerBtnForManagedServices.click();

        String xpathOfBuildserver = "//div[@id='manageMultipleSlavePanel']//label[@class='checkbox']/input[contains(@value,'"
                + buildserver + "')]";
        WebElement BScheckbox = driver
                .findElement(By.xpath(xpathOfBuildserver));
        BScheckbox.click();

        if (BScheckbox.isSelected()) {
            LogResult.pass("Build server is selected to synch");
        } else {
            LogResult.fail("Build server is not selected to synch");
        }
    }

    /*
     * Function to verify that Installation initiated in background pop message
     * is displayed corretly
     */
    public void verifyBackgroundInstallationPopup(String buildServer) {

        wait.until(ExpectedConditions.visibilityOfElementLocated(By
                .xpath("//div[@id='errorAlert']/div/div/div[1]")));
        String Msg = driver.findElement(
                By.xpath("//div[@id='errorAlert']/div/div/div[1]")).getText();

        String str1 = "installation job(s) initiated in the background";
        String str2 = "package(s) to be installed and";
        String str3 = "package(s) to be uninstalled on";
        String str4 = "Sync completed on";

        if (Msg.contains(str1) && Msg.contains(str2) && Msg.contains(str3)
                && Msg.contains(str4) && Msg.contains(buildServer))
            LogResult
                    .pass("Backgroud installation and uninstallation message is displayed correctly");
        else
            LogResult
                    .fail("Backgroud installation and uninstallation message is not displayed correctly");

        driver.findElement(
                By.xpath("//div[@id='errorAlert']/div/div/div[3]/button"))
                .click();
    }

    /* Function to verify Synch successful pop up */
    public void verifySychSuccessPopUp() {

    }

    /****************************** Upload Packages To Repository *******************************/

    /* Function to click on Upload package to Repository button */
    public void clickuploadPackagesToRepositoryBtnToOpen() {

        if (uploadPackageTextBox.isDisplayed()) {
            LogResult.pass("Upload package to repository section is expanded.");
        } else {
            uploadPackagesToRepositoryBtn.click();

            if (uploadPackageTextBox.isDisplayed()) {
                LogResult
                        .pass("Upload package to repositorysection is expanded.");
            } else {
                LogResult
                        .fail("Upload package to repository section is not expanded.");
            }
        }

    }

    /* Function to enter the package to upload */
    public void enterPackageToUpload(String packagename)
            throws InterruptedException {

        String uesrDir = System.getProperty("user.dir");

        String packagepath = uesrDir + "/packages/" + packagename;

        driver.findElement(By.id("packageFile")).sendKeys(packagepath);

        Thread.sleep(2000);
    }

    /* Function to select the package type while uploading the package */
    public void selectPackageType(String packageType)
            throws InterruptedException {

        packageTypeBtn.click();

        String packageTypeXpath1 = "//div[@id='jenkinsStatus']/div[3]/div[2]/div[not(@style) or @style='']/span/div/ul/li[1]/a/label/input";

        driver.findElement(By.xpath(packageTypeXpath1)).click();
    }

    /* Function to click on Upload button */
    public void clickUploadBtn() {

        uploadBtn.click();
    }

    /*
     * Function to verify that the package is uploaded successfully message is
     * displayed correctly.
     */
    public void verifyUploadedSuccessfullyMessage() {

        wait.until(ExpectedConditions.visibilityOfElementLocated(By
                .xpath("//div[@id='errorAlert']/div/div/div[1]")));
        String alreadyInstalledMsg = driver.findElement(
                By.xpath("//div[@id='errorAlert']/div/div/div[1]")).getText();

        if (alreadyInstalledMsg.contains("Uploaded Successfully !"))
            LogResult
                    .pass("Uploaded Successfully ! message is displayed correctly");
        else
            LogResult
                    .fail("Uploaded Successfully ! message is not displayed correctly");

        driver.findElement(
                By.xpath("//div[@id='errorAlert']/div/div/div[3]/button"))
                .click();
    }

    /* Function to open Show/Clean build slaves using managed runtime services */
    public void clickShowCleanBuildSlavesUsingManagedServicesBtnToOpen() {

        if (rebootSyncBtn.isDisplayed()) {
            LogResult
                    .pass("Show/Clean Build Slaves using managed runtime services section is expanded.");
        } else {
            showCleanBuildSlavesBtn.click();

            if (rebootSyncBtn.isDisplayed()) {

                LogResult
                        .pass("Show/Clean Build Slaves using managed runtime services section is expanded.");
            } else {
                LogResult
                        .fail("Show/Clean Build Slaves using managed runtime services section is expanded.");
            }
        }

    }

    public void verifyRebootSyncUI() {

        if (rebootSyncHelpTxt.isDisplayed()) {
            LogResult.pass("Reboot+Sync help text is displayed.");
        } else {
            LogResult.fail("Reboot+Sync help text is not displayed.");
        }

        if (rebootSyncBtn.isDisplayed()) {
            LogResult.pass("Reboot+Sync button is displayed.");
        } else {
            LogResult.fail("Reboot+Sync button is not displayed.");
        }

        if (buildServerHeader.isDisplayed()) {
            LogResult.pass("Build Server header is displayed.");
            if (buildServerHeader.getText().contentEquals("Build Server")) {
                LogResult.pass("Build Server header has text as: "
                        + buildServerHeader.getText());
            } else {
                LogResult.fail("Build Server header has text as: "
                        + buildServerHeader.getText());
            }
        } else {
            LogResult.fail("Build Server header is not displayed.");
        }

        if (hostNameHeader.isDisplayed()) {
            LogResult.pass("Host Name header is displayed.");
            if (hostNameHeader.getText().contentEquals("Hostname")) {
                LogResult.pass("Host Name header has text as: "
                        + hostNameHeader.getText());
            } else {
                LogResult.fail("Host Name header has text as: "
                        + hostNameHeader.getText());
            }
        } else {
            LogResult.fail("Host Name header is not displayed.");
        }

        if (ipAddressHeader.isDisplayed()) {
            LogResult.pass("IP Address header is displayed.");
            if (ipAddressHeader.getText().contentEquals("IP Address")) {
                LogResult.pass("IP Address header has text as: "
                        + ipAddressHeader.getText());
            } else {
                LogResult.fail("IP Address header has text as: "
                        + ipAddressHeader.getText());
            }
        } else {
            LogResult.fail("IP Address header is not displayed.");
        }

        if (OSHeader.isDisplayed()) {
            LogResult.pass("OS header is displayed.");
            if (OSHeader.getText().contentEquals("OS")) {
                LogResult.pass("OS header has text as: " + OSHeader.getText());
            } else {
                LogResult.fail("OS header has text as: " + OSHeader.getText());
            }
        } else {
            LogResult.fail("OS header is not displayed.");
        }

        if (statusHeader.isDisplayed()) {
            LogResult.pass("Status header is displayed.");
            if (statusHeader.getText().contentEquals("Status")) {
                LogResult.pass("Status header has text as: "
                        + statusHeader.getText());
            } else {
                LogResult.fail("Status header has text as: "
                        + statusHeader.getText());
            }
        } else {
            LogResult.fail("Status header is not displayed.");
        }

        if (JenkinsSlaveLinkHeader.isDisplayed()) {
            LogResult.pass("Jenkins Slave Link header is displayed.");
            if (JenkinsSlaveLinkHeader.getText().contentEquals(
                    "Jenkins slave link")) {
                LogResult.pass("Jenkins Slave Link header has text as: "
                        + JenkinsSlaveLinkHeader.getText());
            } else {
                LogResult.fail("Jenkins Slave Link header has text as: "
                        + JenkinsSlaveLinkHeader.getText());
            }
        } else {
            LogResult.fail("Jenkins Slave Link header is not displayed.");
        }

    }

    public void verifyHelpTextForRebootSyncBuildSlaves(String message) {

        String helpMsg = rebootSyncHelpTxt.getText();
        if (helpMsg.contains(message)) {

            LogResult.pass("Expected help text is displayed.");
        } else {
            LogResult.fail("Expected help text is not displayed.");
        }
    }

    public void verifyRebootSyncBtn(String buttonStatus) {

        if (buttonStatus.equalsIgnoreCase("enabled")) {
            if (rebootSyncBtn.isEnabled())
                LogResult.pass("Reboot+Sync button is enabled.");
            else
                LogResult.fail("Reboot+Sync button is disabled.");
        }

    }

    public void verifySelectBuildSlavePopupMsg() {

        clickOnRebootSyncBtn();

        String selectBuildSlaveMsg = driver.findElement(
                By.xpath("//div[@id='errorAlert']/div/div/div[1]")).getText();

        if (selectBuildSlaveMsg.equalsIgnoreCase("Please select build server!")) {

            LogResult.pass("Popup displayed with message: "
                    + selectBuildSlaveMsg);
        } else {

            LogResult.fail("Popup displayed with message: "
                    + selectBuildSlaveMsg);
        }

        driver.findElement(
                By.xpath("//div[@id='errorAlert']/div/div/div[3]/button"))
                .click();

    }

    public void selectBuildServerForSync() throws InterruptedException {

        Thread.sleep(2000);

        // check for number of rows before proceeding

        if (numOfRowsInRebootSyncPanel.size() > 0) {

            for (int i = 1; i < 2; i++) {

                driver.findElement(
                        By.xpath("//table[@id='rebootServerListTable']/tbody/tr[1]//input"))
                        .click();

                Thread.sleep(2000);

                String buildServer = driver
                        .findElement(
                                By.xpath("//table[@id='rebootServerListTable']/tbody/tr[1]/td[2]"))
                        .getText();

                LogResult.pass(buildServer + " Build Server is selected");

                clickOnRebootSyncBtn();

                String syncStatus = driver
                        .findElement(
                                By.xpath("//table[@id='rebootServerListTable']/tbody/tr[1]/td[6]/span[2]"))
                        .getText();

                LogResult.pass("Status is displayed as: "
                        + syncStatus);

                wait.until(ExpectedConditions.visibilityOfElementLocated(By
                        .xpath("//div[@id='errorAlert']//button")));

                String syncMsg = driver.findElement(
                        By.xpath("//div[@id='errorAlert']//span")).getText();

                LogResult.pass("Reboot and Sync completed with message: "
                        + syncMsg);

                driver.findElement(By.xpath("//div[@id='errorAlert']//button"))
                        .click();

                String syncConnectedStatus = driver
                        .findElement(
                                By.xpath("//table[@id='rebootServerListTable']/tbody/tr[1]/td[6]/span"))
                        .getText();

                LogResult.pass("Reboot and Sync completed with status: "
                        + syncConnectedStatus);

            }

        } else {

            LogResult.fail("No build servers are present.");

        }

    }

    public void clickOnRebootSyncBtn() {

        rebootSyncBtn.click();
    }

    public String getPageURL() {
        return driver.getCurrentUrl();
    }

    public void checkJenkinslinkForBuildServers(String jenkinsUrl)
            throws InterruptedException {

        // check for number of rows before proceeding
        if (numOfRowsInRebootSyncPanel.size() > 0) {

            for (int i = 1; i <= numOfRowsInRebootSyncPanel.size(); i++) {

                String currentWindow = driver.getWindowHandle();

                String buildServer = driver
                        .findElement(
                                By.xpath("//table[@id='rebootServerListTable']/tbody/tr["
                                        + i + "]/td[2]")).getText();

                driver.findElement(
                        By.xpath("//table[@id='rebootServerListTable']/tbody/tr["
                                + i + "]/td[7]/a")).click();

                Thread.sleep(2000);

                Set<String> windowHandles = driver.getWindowHandles();

                for (String window : windowHandles) {
                    // eliminate switching to current window
                    if (!window.equals(currentWindow)) {
                        // Now switchTo new Tab.
                        driver.switchTo().window(window);

                        wait.until(ExpectedConditions.urlContains(jenkinsUrl
                                + "/computer"));

                        if (getPageURL().contains(jenkinsUrl + "/computer")) {
                            LogResult.pass("Jenkins link is opened for "
                                    + buildServer);
                        } else {
                            LogResult.fail("Jenkins link is not opened for "
                                    + buildServer);
                        }

                        driver.close();

                    }
                }

                driver.switchTo().window(currentWindow);

            }

        } else {
            LogResult.fail("No jenkins link for build servers are present.");
        }

    }
}