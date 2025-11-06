/**
  Copyright 2025 Google Inc.

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

 * =============================================================================
 * budget2x for Google Ads
 * =============================================================================
 *
 * Description:
 * This script updates campaign daily budgets based on data from a Google Sheet.
 * It uses a master control tab ("KeySheet") to determine which sets of campaigns
 * to update. This allows for managing budgets across multiple accounts or logical
 * groups from a single spreadsheet, specifically handling campaigns located
 * within different sub-MCC accounts accessible from a parent MCC.
 *
 * This code is expected to be loaded into the Ads Script portion of Google Ads
 * for a manager or sub-manager account of multiple MCCs. Look for the scripts
 * under Tools-->Bulk Actions-->Scripts. Make a new script and cut and paste
 * this code into that location.
 *
 * This code uses an associated Google Sheet.
 * Instructions for the Google Sheet:
 * 1. Set the SPREADSHEET_URL variable below to the URL of your Google Sheet.
 * 2. Create a tab named "KeySheet" or ensure there is a "KeySheet" tab.
 * 3. In "KeySheet", create the following headers in the first row:
 * - Column A: Zone Name (e.g., "North America Campaigns")
 * - Column B: MCC (The account ID of the sub-MCC where campaigns reside)
 * - Column C: Tab Name (The exact name of the tab with budget data)
 * - Column D: Status (Set to "On" to process this entire tab/zone)
 * - Column E: Reference (The starting cell of the data, e.g., "B5")
 * 4. For each data tab specified in "KeySheet":
 * - Ensure the campaign IDs are in the column specified by the "Reference".
 * - Ensure the corresponding daily budgets are in the column immediately
 * to the right of the campaign IDs.
 * - Ensure a status column is immediately to the right of the budget column.
 * Set this status to "On" to update the budget for that specific campaign row.
 * 5. Ensure that the Google Sheet is shared as 'Viewer' with the person /
 * entity that activates the script within Google Ads to ensure that the
 * script has the rights to read the spreadsheet.
 *
 * There is a sample budget2x Google Sheet here:
 * https://docs.google.com/spreadsheets/d/1PIxTrwMc3QBhv_1vbjt4B-cNaD7MucmHWk-gzQhhjRA/edit?
 *
 * @author Mark D. Oliver @mdoliver
 * @version 1.9 (Robust budget setting)
 * Latest changes include:
  * - MODIFIED: `setCampaignBudget` now robustly searches for campaigns across all
  *  major types (PMax, Shopping, Video, Search, Display) to ensure the
  *  correct campaign is found regardless of its type.
  * - FIXED: Removed a buggy section from `getAllCampaignsInAccount` that
  * incorrectly handled YouTube video entities as campaigns.
 * - Campaign Type retrieval logic refactored to manually label campaigns based 
 *   on the iterator used to retrieve them.
 * - Support for all major campaign types (PMAX, Search, Display, Video, Shopping)
 *   when updating the spreadsheet report and setting budgets.
 * - Writing to spreadsheet with all campaign types, status, current budget,
 *   and campaign IDs _before_ starting to read (optionally).
 * - Budget history is now logged to a configurable sheet.
 * - Removed automatic header writing in UpdateTab (must be set manually).
 * - Corrected campaign status retrieval (using isEnabled()).
 * - Fixed column clearing in UpdateTab to only affect written columns.
 * - Added campaign Type column to UpdateTab output.
 * - Implemented a Regex filter for campaign names, configurable at the top.
 */

// --- SCRIPT CONFIGURATION START ---

// TODO: Replace with your copy of the control sheet for budget2x.
const SPREADSHEET_URL =
    'https://docs.google.com/sheets/d/<unique-id-here>/edit';

// Name of the main control sheet tab.
const KEY_SHEET_NAME = 'KeySheet';
// Number of header rows in the KeySheet to skip.
const KEY_SHEET_HEADER_ROWS = 1;
// Column positions in KeySheet (0-indexed, e.g., A=0, B=1).
const COL_ZONE_NAME = 0; // Name of the 'zone / MCC'.
const COL_MCC = 1; // MCC ID used for switching accounts.
const COL_TAB_NAME = 2; // Sheet tab associated with this MCC ID.
const COL_STATUS = 3; // Whether to process this MCC.
const COL_REFERENCE = 4; // Upper left corner of <Campaign ID, Budget, On/Off>
//                          range

// Set to true to enable writing campaign details to the budget tabs.
// When set to true the script will overwrite the list of campaigns from this
// MCC on EVERY run. The campaigns are asked for in alphabetical order by
// name and by re-writing to the sheet a re-calculate is forced to recalculate
// the budgets and everything else.
// When set to false this step will be skipped and the list of campaigns will
// NOT be updated on every run.
// If all campaigns within an MCC are participating in the budget2x algorithm
// then refreshing the campaigns gives an opportunity to refresh status and new
// campaigns.
// If a subset of campaigns within an MCC are participating then setting this
// feature to false makes sense.
const ENABLE_UPDATE_TAB_REPORTING = true;

// Where to write campaign data - will start at the row specified in the
// KeySheet.
// NOTE: Headers for these columns are NOT written by the script and must be
// set manually.
const REPORT_OUTPUT_COL_NAME = 1; // Column A
const REPORT_OUTPUT_COL_TYPE = 2; // Column B (Campaign Type)
const REPORT_OUTPUT_COL_STATUS = 3; // Column C
const REPORT_OUTPUT_COL_BUDGET = 4; // Column D
const REPORT_OUTPUT_COL_ID = 5; // Column E

// Budget change history logging.
// Set to true to enable keeping a history for all changes.
const ENABLE_BUDGET_HISTORY_REPORTING = true;
// Name of the sheet to log budget changes to.
const BUDGET_HISTORY_SHEET_NAME = 'BudgetHistory';

// REGEX FILTER FOR CAMPAIGN NAMES
// Set this to a regular expression string to filter which campaigns are
// included in the UpdateTab report and are eligible for budget changes.
// Examples:
// - '.*' (Default): Matches all campaign names.
// - '^Brand.*': Matches names starting with 'Brand'.
// - '.*US_Only$': Matches names ending with 'US_Only'.
// - '^(?!.*Test).*': Matches names that DO NOT contain 'Test'.
// - '(Brand|Generic)_Campaign': Matches names containing 'Brand_Campaign'
//    OR 'Generic_Campaign'.
const CAMPAIGN_NAME_REGEX_FILTER = '.*';

// Set DEBUG = 1 for additional output in the logs.
const DEBUG = 1;

// --- SCRIPT CONFIGURATION END---

/**
 * The main function that orchestrates the budget update process.
 * It reads the KeySheet to determine which tabs to process.
 */
function main() {
    Logger.log('Starting budget update script...');
    let spreadsheet;
    try {
        // Attempt to open the Google Sheet by its URL.
        spreadsheet = SpreadsheetApp.openByUrl(SPREADSHEET_URL);
    } catch (e) {
        // Log a fatal error if the spreadsheet cannot be opened.
        Logger.log('FATAL ERROR: Failed to open spreadsheet. ' +
            'Please check the SPREADSHEET_URL. Details: ' + e);
        return; // Terminate script execution.
    }

    // Get the KeySheet by name.
    const keySheet = spreadsheet.getSheetByName(KEY_SHEET_NAME);
    if (!keySheet) {
        // Log a fatal error if the KeySheet is not found.
        Logger.log('FATAL ERROR: The KeySheet named "' + KEY_SHEET_NAME +
            '" was not found. Terminating script.');
        throw new Error('KeySheet not found.'); // Throw err to halt execution.
    }

    // Get all data from the KeySheet to process configurations.
    const keySheetData = keySheet.getDataRange().getValues();

    // Iterate over each config row in the KeySheet, skipping the header row.
    for (let i = KEY_SHEET_HEADER_ROWS; i < keySheetData.length; i++) {
        const row = keySheetData[i];
        const zoneName = row[COL_ZONE_NAME];
        const mccId = row[COL_MCC]; // Retrieve the MCC ID for the current row.
        const tabName = row[COL_TAB_NAME];
        const status = row[COL_STATUS];
        const reference = row[COL_REFERENCE];

        // If the row is entirely empty, skip to the next row.
        if (!zoneName && !tabName && !reference) {
            continue;
        }

        Logger.log('--------------------------------------------------');

        // Process the row only if its Status is explicitly 'On'.
        if (status && status.toString().trim().toLowerCase() === 'on') {
            // Validate that an MCC ID is provided for 'On' status rows.
            if (!mccId || mccId.toString().trim() === '') {
                Logger.log('Skipping Zone: "' + zoneName + '" | Tab: "' +
                    tabName + '" due to missing MCC ID in KeySheet. ' +
                    'Please ensure Column B (MCC) is populated ' +
                    'for active zones.');
                continue;
            }

            // Log details of the zone being processed, including the MCC ID.
            Logger.log('Processing Zone: "' + zoneName + '" | MCC: "' + mccId +
                '" | Tab: "' + tabName + '"');

            // Update the spreadsheet with current campaign data if enabled ---
            if (ENABLE_UPDATE_TAB_REPORTING) {
                UpdateTab(spreadsheet, tabName, mccId.toString().trim(),
                            reference);
            }

            // Call applyBudgetsFromTab, passing the spreadsheet, tab name,
            // reference, and MCC ID.
            applyBudgetsFromTab(spreadsheet, tabName, reference,
                mccId.toString().trim());
        } else {
            // Log that the zone is being skipped if its status is not 'On'.
            Logger.log('Skipping Zone: "' + zoneName + '" (Status is "' +
                status + '", not "On").');
        }
    }
    Logger.log('--------------------------------------------------');
    Logger.log('Script finished.');
}

/**
 * Helper function to retrieve all campaigns of various types in the currently
 * selected account and manually assign a type label.
 * @return {!Array<!Object>} An array of objects, each with a 'campaign' object
 * and a 'type' string (e.g., { campaign: AdsApp.Campaign, type: 'Search' }).
 */
function getAllCampaignsInAccount() {
    const combinedCampaignsMap = new Map(); // Map to store {id -> {campaign:
                                        // obj, type: string}} for uniqueness

    // --- Process Generic Campaigns ---
    const genericCampaignIterator =
        AdsApp.campaigns().orderBy("campaign.name").get();
    while (genericCampaignIterator.hasNext()) {
        const campaign = genericCampaignIterator.next();
        combinedCampaignsMap.set(campaign.getId(), { campaign: campaign,
                                    type: 'Generic Campaign' });
    }

    // --- Process Shopping Campaigns ---
    const shoppingCampaignIterator =
        AdsApp.shoppingCampaigns().orderBy("campaign.name").get();
    while (shoppingCampaignIterator.hasNext()) {
        const campaign = shoppingCampaignIterator.next();
        combinedCampaignsMap.set(campaign.getId(), { campaign: campaign,
                                                        type: 'Shopping' });
    }

    // --- Process Video Campaigns ---
    const videoCampaignIterator =
        AdsApp.videoCampaigns().orderBy("campaign.name").get();
    while (videoCampaignIterator.hasNext()) {
        const campaign = videoCampaignIterator.next();
        combinedCampaignsMap.set(campaign.getId(), { campaign: campaign,
                                                        type: 'Video' });
    }

    // --- Process Performance Max Campaigns ---
    const pmaxCampaignIterator =
        AdsApp.performanceMaxCampaigns().orderBy("campaign.name").get();
    while (pmaxCampaignIterator.hasNext()) {
        const campaign = pmaxCampaignIterator.next();
        combinedCampaignsMap.set(campaign.getId(), { campaign: campaign,
                                                    type: 'Performance Max' });
    }

    // Convert map values back to an array
    const combinedCampaigns = Array.from(combinedCampaignsMap.values());
  
    // Sort the combined list by name for consistent reporting
    return combinedCampaigns.sort((a, b) =>
        a.campaign.getName().localeCompare(b.campaign.getName()));
}

/**
 * Updates a specific tab in the spreadsheet with current campaign details
 * (name, type, status, current daily budget, and ID) for the selected MCC
 * account.
 * This function lists *all* campaign types found in the account, filtered by
 * regex.
 * The output start row is derived from the provided startReference.
 * @param {!GoogleAppsScript.Spreadsheet.Spreadsheet} spreadsheet The Google Sheet object.
 * @param {string} tabName The name of the sheet to write data to.
 * @param {string} accountIdToSelect The Customer ID of the account to fetch data from.
 * @param {string} startReference The starting cell reference from KeySheet (e.g., "B5").
 */
function UpdateTab(spreadsheet, tabName, accountIdToSelect, startReference) {
    Logger.log(`  -> Starting UpdateTab for account ${accountIdToSelect} on tab "${tabName}"`);
    const budgetSheet = spreadsheet.getSheetByName(tabName);
    if (!budgetSheet) {
        Logger.log('    -> ERROR: Sheet "' + tabName +
            '" not found for UpdateTab. Skipping this update.');
        return;
    }

    const originalAccount = AdsApp.currentAccount();
    const cleanedAccountId = accountIdToSelect.replace(/-/g, '');

    const accountIterator =
        AdsManagerApp.accounts().withIds([cleanedAccountId]).get();
    if (!accountIterator.hasNext()) {
        Logger.log(`    -> ERROR: Could not find account with ID ${accountIdToSelect}. Skipping UpdateTab.`);
        return;
    }

    const selectedAccount = accountIterator.next();
    AdsManagerApp.select(selectedAccount);
    Logger.log(`    -> Successfully switched to account: ${selectedAccount.getName()} (${selectedAccount.getCustomerId()}) for UpdateTab.`);

    const campaignsData = [];

    // Dynamically determine the report output start row from the 'startReference'
    let reportStartRow;
    try {
        reportStartRow = budgetSheet.getRange(startReference).getRow();
    } catch (e) {
        Logger.log('    -> ERROR: Invalid start reference "' + startReference +
            '" for UpdateTab. Defaulting report start row to 2. Error: ' + e);
        reportStartRow = 2; // Fallback if reference parsing fails
    }

    // Clear previous output data area in ONLY the columns we are writing to.
    const lastExistingRow = budgetSheet.getLastRow();
    const rangeToClearStartRow = reportStartRow; // Start clearing from the
                                                 // data start row
    const numRowsToClear = lastExistingRow - rangeToClearStartRow + 1;
    // Calculate the number of columns to clear based on the new
    // REPORT_OUTPUT_COL_ID
    const numColsToClear = (REPORT_OUTPUT_COL_ID - REPORT_OUTPUT_COL_NAME + 1);

    if (DEBUG) {
        Logger.log('rangeToClearStartRow: ' + rangeToClearStartRow);
        Logger.log('REPORT_OUTPUT_COL_NAME: ' + REPORT_OUTPUT_COL_NAME);
        Logger.log('numRowsToClear: ' + numRowsToClear);
        Logger.log('numColsToClear: ' + numColsToClear);
    }
 
    if (numRowsToClear > 0 && numColsToClear > 0) {
        budgetSheet.getRange(
            rangeToClearStartRow,
            REPORT_OUTPUT_COL_NAME,
            numRowsToClear,
            numColsToClear
        ).clearContent();
    }

    // Fetch all campaigns in the account using the helper function
    const allCampaignsInAccount = getAllCampaignsInAccount();
    const regex = new RegExp(CAMPAIGN_NAME_REGEX_FILTER);

    for (const campaignEntry of allCampaignsInAccount) {
        const campaign = campaignEntry.campaign; // Get the campaign object
        const campaignType = campaignEntry.type; // Get assigned type string

        try {
            const campaignName = campaign.getName();
            // Apply campaign name regex filter here for reporting
            if (CAMPAIGN_NAME_REGEX_FILTER && !campaignName.match(regex)) {
                continue; // Skip if name doesn't match the filter
            }

            // Correct status retrieval
            const campaignStatus = campaign.isEnabled() ? 'ENABLED' : 'PAUSED';
            const currentBudget = campaign.getBudget().getAmount();
            const campaignId = campaign.getId();

            if (DEBUG) {
              Logger.log('campaignName: ' + campaignName + ' campaignType: ' +
                campaignType + ' campaignStatus: ' + campaignStatus +
                ' campaignBudget: ' + currentBudget + ' campaignId: ' +
                campaignId);
            }
            // Push data in the new order: Name, Type, Status, Budget, ID
            campaignsData.push(
                    [campaignName,
                    campaignType,
                    campaignStatus,
                    currentBudget,
                    campaignId]);
        } catch (e) {
            Logger.log(`    -> WARNING: Could not retrieve data for campaign with ID ${campaign.getId()} (Name: ${campaign.getName()}). Error: ${e}`);
            // This can happen if a campaign object or its budget is not
            // accessible or malformed.
        }
    }

    if (campaignsData.length > 0) {
        // Write the collected campaign data to the sheet.
        const outputRange = budgetSheet.getRange(
            reportStartRow,
            REPORT_OUTPUT_COL_NAME,
            campaignsData.length,
            (REPORT_OUTPUT_COL_ID - REPORT_OUTPUT_COL_NAME + 1) // # of columns
        );
        outputRange.setValues(campaignsData);
        Logger.log(`    -> Successfully wrote ${campaignsData.length} campaign details to tab "${tabName}" starting at row ${reportStartRow}.`);
    } else {
        Logger.log(`    -> No campaigns found matching filter in account ${selectedAccount.getCustomerId()} to write to tab "${tabName}".`);
    }

    // Revert to the original account (parent MCC)
    AdsManagerApp.select(originalAccount);
    Logger.log(`  -> Reverted to original parent account: ${originalAccount.getCustomerId()}`);
}

/**
 * Fetches campaign and budget data from a specific tab and applies budgets.
 * This function now handles selecting the correct MCC account before processing
 * the campaigns for that account. It also ensures the script reverts to the
 * original parent account after processing.
 * @param {!GoogleAppsScript.Spreadsheet.Spreadsheet} spreadsheet The sheet.
 * @param {string} tabName The name of the sheet containing campaign budget data.
 * @param {string} startReference The starting cell of the data (e.g., "B5").
 * @param {string} accountIdToSelect The Customer ID of the account (client or
                                     sub-MCC) to select.
 */
function applyBudgetsFromTab(spreadsheet, tabName, startReference, accountIdToSelect) {
    const budgetSheet = spreadsheet.getSheetByName(tabName);
    if (!budgetSheet) {
        Logger.log('  -> ERROR: Sheet "' + tabName +
            '" not found. Skipping this zone.');
        return;
    }

    // Validate the starting cell reference.
    let startCell;
    try {
        startCell = budgetSheet.getRange(startReference);
    } catch (e) {
        Logger.log('  -> ERROR: Invalid start reference "' + startReference +
            '" for tab "' + tabName + '". Skipping.');
        return;
    }

    const startRow = startCell.getRow();
    const startCol = startCell.getColumn();
    const lastRow = budgetSheet.getLastRow();
  
    // If the sheet has no data or no data after our start row, exit.
    if (lastRow < startRow) {
        Logger.log('  -> INFO: No data found on sheet "' + tabName +
            '" starting from row ' + startRow + '.');
        return;
    }

    // Define the range to fetch: from the start cell to the last row,
    // over 3 columns (Campaign ID, New Budget, Campaign Status).
    const numRows = lastRow - startRow + 1;
    const budgetDataRange = budgetSheet.getRange(startRow, startCol,
        numRows, 3);
    const budgetValues = budgetDataRange.getValues();

    Logger.log('  -> Found ' + budgetValues.length +
        ' potential campaign(s) to update on tab "' + tabName + '".');

    // Store a ref. to the original account (the parent MCC running the script)
    // so we can revert to it after processing the child MCC.
    const originalAccount = AdsApp.currentAccount();
    Logger.log('  -> Script is currently running from parent account: '
        + originalAccount.getCustomerId());

    // Clean the account ID by removing hyphens, just to be sure.
    const cleanedAccountId = accountIdToSelect.replace(/-/g, '');

    const accountIterator =
        AdsManagerApp.accounts().withIds([cleanedAccountId]).get();
    if (!accountIterator.hasNext()) {
        Logger.log('  -> ERROR: Could not find or access account with ID ' + cleanedAccountId + '. Skipping this zone.');
        return;
    }

    const selectedAccount = accountIterator.next();
    AdsManagerApp.select(selectedAccount);
    Logger.log("  -> Successfully switched to account: " + selectedAccount.getName() + ' (' + selectedAccount.getCustomerId() + ')');

    // Iterate over each campaign/budget/status triplet within the selected account.
    for (let i = 0; i < budgetValues.length; i++) {
        let campaignId = budgetValues[i][0];
        const newBudget = budgetValues[i][1];
        const campaignStatus = budgetValues[i][2]; // 'On' or 'Off'

        // Validate that the Campaign ID exists in the row.
        if (!campaignId || campaignId.toString().trim() === '') {
            if (DEBUG) {
                Logger.log('     -> SKIPPING row ' + (startRow + i) +
                ' due to missing Campaign ID.');
            }
            continue; // Skip rows with no Campaign ID.
        }

        // Check the individual campaign's status from the
        // spreadsheet before proceeding.
        if (!campaignStatus ||
            campaignStatus.toString().trim().toLowerCase() !== 'on') {
            Logger.log('     -> SKIPPING Campaign ID ' + campaignId +
                ' because its individual status is "' + campaignStatus +
                '", not "On".');
            continue;
        }

        // Validate that the new budget is a valid, positive number.
        if (newBudget === '' || isNaN(parseFloat(newBudget)) ||
            parseFloat(newBudget) <= 0) {
            Logger.log('     -> SKIPPING Campaign ID ' + campaignId +
                ' due to invalid budget value: "' + newBudget + '".');
            continue;
        }

        // Ensure Campaign ID is a string for the API call
        campaignId = campaignId.toString().trim();

        // Set the budget for the individual campaign within the currently
        // selected account.
        setCampaignBudget(spreadsheet, campaignId, parseFloat(newBudget));
    }

    // IMPORTANT: Always revert to the original account after processing
    // a child account.
    AdsManagerApp.select(originalAccount);
    Logger.log(`  -> Reverted to original parent account after budget updates: ${originalAccount.getCustomerId()}`);
}

/**
 * MODIFIED: Sets the daily budget for a single campaign using its ID.
 * This function now robustly searches through all major campaign type selectors
 * (Performance Max, Shopping, Video, etc.) to find the campaign, ensuring it
 * works regardless of campaign type.
 * @param {!GoogleAppsScript.Spreadsheet.Spreadsheet} spreadsheet The Google Sheet object for logging.
 * @param {string} id The Campaign ID for which to set the budget.
 * @param {number} newBudget The new daily budget amount to set.
 */
function setCampaignBudget(spreadsheet, id, newBudget) {
    let campaign = null;
    let campaignIterator;

    // Create a list of selector functions for all major campaign types.
    // The script will iterate through them to find the campaign with the matching ID.
    const campaignSelectors = [
        () => AdsApp.performanceMaxCampaigns(),
        () => AdsApp.shoppingCampaigns(),
        () => AdsApp.videoCampaigns(),
        () => AdsApp.campaigns() // Catches Search, Display, and other generic types
    ];

    // Loop through each selector to find the campaign by its ID.
    for (const selector of campaignSelectors) {
        campaignIterator = selector().withIds([id]).get();
        if (campaignIterator.hasNext()) {
            campaign = campaignIterator.next();
            break; // Exit the loop as soon as the campaign is found.
        }
    }

    if (!campaign) {
        // Log an error if the campaign is not found in the selected account, regardless of type.
        Logger.log('    -> ERROR: Campaign with ID "' + id +
            '" was not found in the currently selected account (' +
            AdsApp.currentAccount().getCustomerId() + '). ' +
            'Skipping budget update for this campaign.');
        return;
    }

    const campaignName = campaign.getName();
    const regex = new RegExp(CAMPAIGN_NAME_REGEX_FILTER);

    // Apply campaign name regex filter here before setting budget
    if (CAMPAIGN_NAME_REGEX_FILTER && !campaignName.match(regex)) {
        Logger.log(`    -> SKIPPING Campaign ID ${id} (${campaignName}) due to name not matching regex filter: "${CAMPAIGN_NAME_REGEX_FILTER}".`);
        return;
    }

    const budget = campaign.getBudget();
    const oldBudget = budget.getAmount();

    // Log the campaign details, including the account it's found in.
    Logger.log('    -> Processing Campaign: "' + campaignName +
        '" (ID: ' + id + ') in account: ' +
        AdsApp.currentAccount().getCustomerId());

    if (oldBudget === newBudget) {
        // Skip update if the new budget is the same as the current one.
        Logger.log('      - SKIPPED: New budget ($' + newBudget +
            ') is the same as the current budget. No change needed.');
        return;
    }

    Logger.log('      - Old Budget: $' + oldBudget + ' -> New Budget: $' +
        newBudget);
    try {
        // Attempt to set the new budget.
        budget.setAmount(newBudget);
        Logger.log('      - SUCCESS: Budget updated for Campaign ID ' +
            id + '.');

        if (ENABLE_BUDGET_HISTORY_REPORTING) {
            // Log the successful budget change to the history sheet
            const now = new Date();
            const dateString =
                Utilities.formatDate(
                    now,
                    AdsApp.currentAccount().getTimeZone(),
                    'yyyy-MM-dd'
                );
            const timeString =
                Utilities.formatDate(
                    now,
                    AdsApp.currentAccount().getTimeZone(),
                    'HH:mm:ss'
                );
            const currentMccName = AdsApp.currentAccount().getName();
            const currentMccId = AdsApp.currentAccount().getCustomerId();

            logBudgetChange(
                spreadsheet,
                dateString,
                timeString,
                currentMccName,
                currentMccId,
                campaignName,
                campaign.getId(),
                newBudget
            );
        }

    } catch (err) {
        // Log any errors encountered while setting the budget.
        Logger.log('      - FAILED: Could not set budget for Campaign ID '
            + id + '. Error: ' + err);
    }
}

/**
 * Logs a budget change to a dedicated history sheet in the spreadsheet.
 * Creates the sheet and headers if they don't exist.
 * @param {!GoogleAppsScript.Spreadsheet.Spreadsheet} spreadsheet Sheet object.
 * @param {string} date The date of the change (e.g., 'YYYY-MM-DD').
 * @param {string} time The time of the change (e.g., 'HH:MM:SS').
 * @param {string} mccName The name of the MCC account.
 * @param {string} mccId The ID of the MCC account.
 * @param {string} campaignName The name of the campaign.
 * @param {string} campaignId The ID of the campaign.
 * @param {number} budgetValue The new budget value set.
 */
function logBudgetChange(spreadsheet, date, time, mccName, mccId, campaignName, campaignId, budgetValue) {
    let historySheet = spreadsheet.getSheetByName(BUDGET_HISTORY_SHEET_NAME);
    if (!historySheet) {
        historySheet = spreadsheet.insertSheet(BUDGET_HISTORY_SHEET_NAME);
        const historyHeaders = ['Date', 'Time', 'MCC Name', 'MCC ID', 'Campaign Name', 'Campaign ID', 'Budget Value Set'];
        historySheet.getRange(1, 1, 1, historyHeaders.length)
            .setValues([historyHeaders])
            .setFontWeight('bold')
            .setHorizontalAlignment('center'); // Center headers for better readability
    }

    historySheet.appendRow([date, time, mccName, mccId, campaignName, campaignId, budgetValue]);
    Logger.log(`      - LOGGED: Budget change for Campaign ID ${campaignId} (${campaignName}) logged to "${BUDGET_HISTORY_SHEET_NAME}".`);
}
