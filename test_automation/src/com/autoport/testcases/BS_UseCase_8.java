package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BuildServersTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class BS_UseCase_8 {

    WebDriver driver;
    HomePage homePage;
    BuildServersTab buildServerTab;
    String centosBuildServerToSync;
    String ubuntuBuildServerToSync;
    String BSUbuntu;
    String BSCentOS;

    @BeforeTest
    public void beforeTest() throws Exception {
        // CommonFunctions.launchBrowser();
        driver = CommonFunctions.driver;
        homePage = CommonFunctions.homePage;
        buildServerTab = CommonFunctions.buildServerTab;
        centosBuildServerToSync = ReadTestData.readParameter("BS_UseCase_8",
                "centosBuildServerToSync");
        ubuntuBuildServerToSync = ReadTestData.readParameter("BS_UseCase_8",
                "ubuntuBuildServerToSync");
        BSUbuntu = ReadTestData.readParameter("BS_UseCase_6", "BSUbuntu");
        BSCentOS = ReadTestData.readParameter("BS_UseCase_6", "BSCentOS");
        CommonFunctions.goTo_ListInstallUsingManagedServicesSection();
    }

    @Test(priority = 0)
    public void BS_Synch_Packages_On_CentOS_Servers_029() throws Exception {
        buildServerTab.SelectBuiltServer(BSCentOS);

        buildServerTab.verifyPopulatedBuildServers(BSCentOS);

        buildServerTab.clickSynchBtn();

        buildServerTab.verifySelectBuildServerMsg();

        buildServerTab.selectBuildServerToSynch(centosBuildServerToSync);

        buildServerTab.clickSynchBtn();

        buildServerTab.verifyBackgroundInstallationPopup(centosBuildServerToSync);

        buildServerTab.verifySychSuccessPopUp();
    }

    @Test(priority = 1)
    public void BS_Synch_Packages_On_Ubuntu_Servers_030() throws Exception {
        buildServerTab.SelectBuiltServer(BSUbuntu);

        buildServerTab.verifyPopulatedBuildServers(BSUbuntu);

        buildServerTab.clickSynchBtn();

        buildServerTab.verifySelectBuildServerMsg();

        buildServerTab.selectBuildServerToSynch(ubuntuBuildServerToSync);

        buildServerTab.clickSynchBtn();

        buildServerTab
                .verifyBackgroundInstallationPopup(ubuntuBuildServerToSync);

        buildServerTab.verifySychSuccessPopUp();
    }
}
