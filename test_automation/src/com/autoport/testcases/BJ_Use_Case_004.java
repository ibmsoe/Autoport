package com.autoport.testcases;

import org.openqa.selenium.WebDriver;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import com.autoport.pageobjects.BatchJobsTab;
import com.autoport.pageobjects.HomePage;
import com.autoport.pageobjects.SearchTab;
import com.autoport.utilities.CommonFunctions;
import com.autoport.utilities.ReadTestData;

public class BJ_Use_Case_004 {

    WebDriver driver;

    HomePage homePage;
    SearchTab searchTab;
    BatchJobsTab batchJobsTab;

    String topRepositoryName;
    String topRepositoryValue;

    @BeforeTest
    public void beforeTest() throws Exception {

         //CommonFunctions.launchBrowser();
        driver = CommonFunctions.driver;

        homePage = CommonFunctions.homePage;
        searchTab = CommonFunctions.searchTab;
        batchJobsTab = CommonFunctions.batchJobsTab;

        topRepositoryName = ReadTestData.readParameter("batchJobsTabData", "topRepositoryName");
        topRepositoryValue = ReadTestData.readParameter("searchTabData", "topRepositoryValue");

        homePage.clickBatchJobsTab();

    }

    @Test(priority = 0)
    public void BJ_Batch_file_detail_UI_009() throws InterruptedException {

        batchJobsTab.clickListSelectBtn();

        batchJobsTab.clickOnListLocalBtn();

        // batchJobsTab.clickOnDateModifiedHeader();

        batchJobsTab.selectFirstRow();

        batchJobsTab.clickOnDetailsBtn();

        batchJobsTab.verifyBatchFileDetailsUI(topRepositoryName + "-" + topRepositoryValue);

        batchJobsTab.verifyBatchConfigTableHeaders();

        batchJobsTab.verifyBatchConfigActionsColumn();

        batchJobsTab.verifyBatchRepoHeaders();

        batchJobsTab.verifyBatchRepoActionsColumn();

        batchJobsTab.clickOnListLocalBtn();

        batchJobsTab.selectFirstRow();

        batchJobsTab.clickOnArchiveBtn();

        batchJobsTab.clickOnAlertCloseBtn();

        batchJobsTab.clearBatchFileSearchTbx();

        batchJobsTab.enterBatchSearchTerm(topRepositoryName+"-"+topRepositoryValue);

        batchJobsTab.clickOnListArchivedBtn();

        batchJobsTab.selectFirstRow();

        batchJobsTab.clickOnDetailsBtn();

        batchJobsTab.verifyBatchFileDetailsUI(topRepositoryName + "-" + topRepositoryValue);

        batchJobsTab.verifyBatchConfigTableHeaders();

        batchJobsTab.verifyBatchConfigActionsColumn();

        batchJobsTab.verifyBatchRepoHeaders();

        batchJobsTab.verifyBatchRepoActionsColumn();

        batchJobsTab.clearBatchFileSearchTbx();

        batchJobsTab.enterBatchSearchTerm(topRepositoryName+"-"+topRepositoryValue);

        batchJobsTab.clickOnListAllBtn();

        batchJobsTab.selectFirstRow();

        batchJobsTab.clickOnDetailsBtn();

        batchJobsTab.verifyBatchFileDetailsUI(topRepositoryName + "-" + topRepositoryValue);

        batchJobsTab.verifyBatchConfigTableHeaders();

        batchJobsTab.verifyBatchConfigActionsColumn();

        batchJobsTab.verifyBatchRepoHeaders();

        batchJobsTab.verifyBatchRepoActionsColumn();
    }

    @Test(priority = 1)
    public void BJ_Save_batch_file_detailed_view_010() throws InterruptedException {

        batchJobsTab.clickOnListLocalBtn();

        batchJobsTab.selectFirstRow();

        batchJobsTab.clickOnDetailsBtn();

        batchJobsTab.saveBatchFileAs(topRepositoryName + "-0" + topRepositoryValue);// spring-framework-03

        batchJobsTab.clickOnSaveBatchDetailsBtn();

        batchJobsTab.clickOnAlertCloseBtn();

        batchJobsTab.clearBatchFileSearchTbx();

        batchJobsTab.clickOnListLocalBtn();

        // batchJobsTab.verifyBatchFileNameChangeInListing(topRepositoryName +
        // "-0" + topRepositoryValue);

        batchJobsTab.newBatchFileCreationConfirmation(topRepositoryName + "-0" + topRepositoryValue);// spring-framework-03

        batchJobsTab.clearBatchFileSearchTbx();

        batchJobsTab.enterBatchSearchTerm(topRepositoryName+"-"+topRepositoryValue);

        batchJobsTab.clickOnListArchivedBtn();

        batchJobsTab.selectFirstRow();

        batchJobsTab.clickOnDetailsBtn();

        batchJobsTab.saveBatchFileAs(topRepositoryName + "-1" + topRepositoryValue);// spring-framework-13

        batchJobsTab.clickOnSaveBatchDetailsBtn();

        batchJobsTab.clickOnAlertCloseBtn();

        batchJobsTab.clearBatchFileSearchTbx();

        batchJobsTab.enterBatchSearchTerm(topRepositoryName);

        batchJobsTab.clickOnListLocalBtn();

        // batchJobsTab.verifyBatchFileNameChangeInListing(topRepositoryName +
        // "-1" + topRepositoryValue);// spring-framework-13

        batchJobsTab.newBatchFileCreationConfirmation(topRepositoryName + "-1" + topRepositoryValue);// spring-framework-13
    }

    @Test(priority = 2)
    public void BJ_Back_detailed_view_011() throws InterruptedException {

        batchJobsTab.selectFirstRow();

        batchJobsTab.clickOnDetailsBtn();

        batchJobsTab.clickOnDetailsBackBtn();

        batchJobsTab.clickOnListArchivedBtn();

        batchJobsTab.selectFirstRow();

        batchJobsTab.clickOnDetailsBtn();

        batchJobsTab.clickOnDetailsBackBtn();

        batchJobsTab.clickOnListAllBtn();

        batchJobsTab.selectFirstRow();

        batchJobsTab.clickOnDetailsBtn();

        batchJobsTab.clickOnDetailsBackBtn();

    }

    @Test(priority = 3)
    public void BJ_Batch_file_settings_012() throws InterruptedException {

        batchJobsTab.clickOnListLocalBtn();

        batchJobsTab.selectFirstRow();

        batchJobsTab.clickOnDetailsBtn();

        batchJobsTab.clickOnSettingsBtn();

        batchJobsTab.verifyBatchConfigSettingsUI();

    }

    @Test(priority = 4)
    public void BJ_Continue_Reset_Show_Modify_Commands_batch_file_settings_013() throws InterruptedException {

        batchJobsTab.clickOnBatchConfigSettingsContinueBtn();

        batchJobsTab.clickOnSettingsBtn();

        batchJobsTab.clickOnBatchConfigSettingsResetBtn();

        batchJobsTab.clickOnSettingsBtn();

        batchJobsTab.clickOnBatchConfigSettingsShowModifyCommandsBtn();

    }

    @Test(priority = 5)
    public void BJ_Show_Modify_Commands_UI_013a() {

        batchJobsTab.verifyBatchConfigSettingsShowModifyCommandsUI();
    }

    @Test(priority = 6)
    public void BJ_Continue_Reset_Back_Show_Modify_Commands_batch_file_settings_013b() throws InterruptedException {

        batchJobsTab.clickOnShowModifyCommandsBackBtn();

        batchJobsTab.clickOnBatchConfigSettingsShowModifyCommandsBtn();

        batchJobsTab.clickOnShowModifyCommandsResetBtn();

        batchJobsTab.clickOnShowModifyCommandsContinueBtn();
    }

    @Test(priority = 7)
    public void BJ_Move_delete_repository_batch_file_014() throws InterruptedException {

        batchJobsTab.verifyRepoUpMove();

        batchJobsTab.verifyRepoDownMove();

        batchJobsTab.verifyRepoDelete();

    }

    @Test(priority = 8)
    public void BJ_Archive_local_batch_file_015() throws InterruptedException {


        batchJobsTab.clickOnListLocalBtn();

        batchJobsTab.selectFirstRow();

        batchJobsTab.clickOnArchiveBtn();

        batchJobsTab.clickOnAlertCloseBtn();

        batchJobsTab.clearBatchFileSearchTbx();

        batchJobsTab.enterBatchSearchTerm(topRepositoryName + "-1" + topRepositoryValue);

        batchJobsTab.clickOnListArchivedBtn();

        batchJobsTab.verifyArchivedBatchFile(topRepositoryName + "-1" + topRepositoryValue);

//        batchJobsTab.clearBatchFileSearchTbx();

    }

    @Test(priority = 9)
    public void BJ_Remove_batch_file_016() throws InterruptedException {

        batchJobsTab.clearBatchFileSearchTbx();

        batchJobsTab.enterBatchSearchTerm(topRepositoryName);//+"-"+topRepositoryValue

        batchJobsTab.clickOnListLocalBtn();

        batchJobsTab.selectFirstRow();

        batchJobsTab.clickOnRemoveBtn();

        batchJobsTab.clickOnListArchivedBtn();

        batchJobsTab.selectFirstRow();

        batchJobsTab.clickOnRemoveBtn();

        batchJobsTab.clickOnListAllBtn();

        batchJobsTab.selectFirstRow();

        batchJobsTab.clickOnRemoveBtn();

    }


}
