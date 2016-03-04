package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class BS_UseCase_6 {

    WebDriver driver;
    HomePage homePage;
    BuildServersTab buildServerTab;
    String BSUbuntu;
    String BSCentOS;
    String BSAll;

    @BeforeTest
    public void beforeTest() throws Exception {
        // CommonFunctions.launchBrowser();
        driver = CommonFunctions.driver;
        homePage = CommonFunctions.homePage;
        buildServerTab = CommonFunctions.buildServerTab;
        CommonFunctions.goTo_ListInstallUsingManagedServicesSection();
        BSUbuntu = ReadTestData.readParameter("BS_UseCase_6", "BSUbuntu");
        BSCentOS = ReadTestData.readParameter("BS_UseCase_6", "BSCentOS");
        BSAll = ReadTestData.readParameter("BS_UseCase_6", "BSAll");
    }

    @Test(priority = 0)
    public void BS_List_Managed_Packages_CentOS_022() throws Exception {

        buildServerTab.SelectBuiltServer(BSCentOS);

        String notificationMesssage = "This tool defines a minimum set of packages and package versions that cannot be removed. You can search for new packages and Add them to the Managed List. You can Remove any package that you added, but you cannot remove packages from the minimum set as they are required for proper function. These packages cannot be selected --- gray selection box. Once the Managed List is correct, select a Build server and press Sync and install procedures will commence.";

        buildServerTab
                .verifyNotificationMessageForManagedServices(notificationMesssage);

        buildServerTab.verifyPopulatedBuildServers(BSCentOS);

        buildServerTab.verifySearchResultsForManagedServicesList(BSCentOS);

    }

    @Test(priority = 1)
    public void BS_List_Managed_Packages_Ubuntu_023() throws Exception {

        buildServerTab.SelectBuiltServer(BSUbuntu);

        String notificationMesssage = "This tool defines a minimum set of packages and package versions that cannot be removed. You can search for new packages and Add them to the Managed List. You can Remove any package that you added, but you cannot remove packages from the minimum set as they are required for proper function. These packages cannot be selected --- gray selection box. Once the Managed List is correct, select a Build server and press Sync and install procedures will commence.";

        buildServerTab
                .verifyNotificationMessageForManagedServices(notificationMesssage);

        buildServerTab.verifyPopulatedBuildServers(BSUbuntu);

        buildServerTab.verifySearchResultsForManagedServicesList(BSUbuntu);
    }

    @Test(priority = 2)
    public void BS_List_Managed_Packages_All_024() throws Exception {

        buildServerTab.SelectBuiltServer(BSAll);

        String notificationMesssage = "This tool defines a minimum set of packages and package versions that cannot be removed. You can search for new packages and Add them to the Managed List. You can Remove any package that you added, but you cannot remove packages from the minimum set as they are required for proper function. These packages cannot be selected --- gray selection box. Once the Managed List is correct, select a Build server and press Sync and install procedures will commence.";

        buildServerTab
                .verifyNotificationMessageForManagedServices(notificationMesssage);

        buildServerTab.verifyPopulatedBuildServers(BSAll);

        buildServerTab.verifySearchResultsForManagedServicesList(BSAll);
    }
}
// *[@id='manageMultipleSlavePanel']/div[1]/div[2]/span/div/ul/li[1]/a/label
// *[@id='manageMultipleSlavePanel']/div[1]/div[2]/span/div/ul/li[3]/a/label