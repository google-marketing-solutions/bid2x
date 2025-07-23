/**
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
 * https://docs.google.com/sheets/d/1PIxTrwMc3QBhv_1vbjt4B-cNaD7MucmHWk-gzQhhjRA/edit
 *
 * @author Mark D. Oliver @mdoliver
 * @version 1.3 (MCC support fixed + PMAX campaigns)
 */
// TODO: Replace with your copy of the control sheet for budget2x.
const SPREADSHEET_URL =
    'https://docs.google.com/sheets/d/1PIxTrwMc3QBhv_1vbjt4B-cNaD7MucmHWk-gzQhhjRA/edit';
// --- SCRIPT CONFIGURATION ---
// Name of the main control sheet.
const KEY_SHEET_NAME = 'KeySheet';
// Number of header rows in the KeySheet to skip.
const KEY_SHEET_HEADER_ROWS = 1;
// Column positions in KeySheet (0-indexed, e.g., A=0, B=1).
const COL_ZONE_NAME = 0;
const COL_MCC = 1; // Added MCC to retrieve the MCC ID for switching accounts.
const COL_TAB_NAME = 2;
const COL_STATUS = 3;
const COL_REFERENCE = 4;
// --- END CONFIGURATION ---
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
 * Fetches campaign and budget data from a specific tab and applies budgets.
 * This function now handles selecting the correct MCC account before processing
 * the campaigns for that account. It also ensures the script reverts to the
 * original parent account after processing.
 * @param {!GoogleAppsScript.Spreadsheet.Spreadsheet} spreadsheet The sheet.
 * @param {string} tabName The name of the sheet containing campaign budget data.
 * @param {string} startReference The starting cell of the data (e.g., "B5").
 * @param {string} accountIdToSelect The Customer ID of the account (client
 *                 or sub-MCC) to select.
 */
function applyBudgetsFromTab(spreadsheet, tabName, startReference,
                             accountIdToSelect) {
    const budgetSheet = spreadsheet.getSheetByName(tabName);
    if (!budgetSheet) {
        Logger.log('  -> ERROR: Sheet "' + tabName +
            '" not found. Skipping this zone.');
        return;
    }
    // Validate the starting cell reference.
    let startCell;
    try {
        startCell = budgetSheet.getRange(startReference);
    } catch (e) {
        Logger.log('  -> ERROR: Invalid start reference "' + startReference +
            '" for tab "' + tabName + '". Skipping.');
        return;
    }
    const startRow = startCell.getRow();
    const startCol = startCell.getColumn();
    const lastRow = budgetSheet.getLastRow();
    // If the sheet has no data or no data after our start row, exit.
    if (lastRow < startRow) {
        Logger.log('  -> INFO: No data found on sheet "' + tabName +
            '" starting from row ' + startRow + '.');
        return;
    }
    // Define the range to fetch: from the start cell to the last row,
    // over 3 columns (Campaign ID, New Budget, Campaign Status).
    const numRows = lastRow - startRow + 1;
    const budgetDataRange = budgetSheet.getRange(startRow, startCol,
        numRows, 3);
    const budgetValues = budgetDataRange.getValues();
    Logger.log('  -> Found ' + budgetValues.length +
        ' potential campaign(s) to update on tab "' + tabName + '".');
    // Store a ref. to the original account (the parent MCC running the script)
    // so we can revert to it after processing the child MCC.
    const originalAccount = AdsApp.currentAccount();
    Logger.log('  -> Script is currently running from parent account: '
        + originalAccount.getCustomerId());

    // Clean the account ID by removing hyphens, just to be sure.
    const cleanedAccountId = accountIdToSelect.replace(/-/g, '');

    const accountIterator =
        AdsManagerApp.accounts().withIds([cleanedAccountId]).get();
    while (accountIterator.hasNext()) {
      const selectedAccount = accountIterator.next();
      AdsManagerApp.select(selectedAccount);
      Logger.log("Successfully got to " + selectedAccount.getName());

      // Iterate over each campaign/budget/status triplet within
      // the selected account.
      for (let i = 0; i < budgetValues.length; i++) {
          let campaignId = budgetValues[i][0];
          const newBudget = budgetValues[i][1];
          const campaignStatus = budgetValues[i][2];
          // Validate that the Campaign ID exists in the row.
          if (!campaignId || campaignId.toString().trim() === '') {
              Logger.log('  -> SKIPPING row ' + (startRow + i) +
                  ' due to missing Campaign ID.');
              continue; // Skip rows with no Campaign ID.
          }
          // Check the individual campaign's status before proceeding.
          if (!campaignStatus ||
              campaignStatus.toString().trim().toLowerCase() !== 'on') {
              Logger.log('  -> SKIPPING Campaign ID ' + campaignId +
                  ' because its individual status is "' + campaignStatus +
                  '", not "On".');
              continue;
          }
          // Validate that the new budget is a valid, positive number.
          if (newBudget === '' || isNaN(parseFloat(newBudget)) ||
              parseFloat(newBudget) <= 0) {
              Logger.log('  -> SKIPPING Campaign ID ' + campaignId +
                  ' due to invalid budget value: "' + newBudget + '".');
              continue;
          }
          // Ensure Campaign ID is a string for the API call
          campaignId = campaignId.toString().trim();
          // Set the budget for the individual campaign within the currently
          // selected account. setCampaignBudget now operates on the context
          // set by selectedAccount.select().
          setCampaignBudget(campaignId, parseFloat(newBudget));
        }
    }
}
/**
 * Sets the daily budget for a single campaign using its ID.
 * This function now operates on the currently selected account,
 * which is managed by the calling `applyBudgetsFromTab` function.
 * @param {string} id The Campaign ID for which to set the budget.
 * @param {number} newBudget The new daily budget amount to set.
 */
function setCampaignBudget(id, newBudget) {
    // Use AdsApp.campaigns() to find campaigns of any standard type within
    // the currently selected account. The account context has already been
    // set by applyBudgetsFromTab via selectedAccount.select().

    const campaignIterator =
        AdsApp.performanceMaxCampaigns().withIds([id]).get();

    if (campaignIterator.totalNumEntities() === 0) {
        // Log an error if the campaign is not found in the selected account.
        Logger.log('    -> ERROR: Campaign with ID "' + id +
            '" was not found as a PMAX campaign in the currently ' +
            'selected account (' +
            AdsApp.currentAccount().getCustomerId() + '). ' +
            'giving up');
        return;
    }

    while (campaignIterator.hasNext()) {
        const campaign = campaignIterator.next();
        const budget = campaign.getBudget();
        const oldBudget = budget.getAmount();
        // Log the campaign details, including the account it's found in.
        Logger.log('    -> Processing Campaign: "' + campaign.getName() +
            '" (ID: ' + id + ') in account: ' +
            AdsApp.currentAccount().getCustomerId());
        if (oldBudget === newBudget) {
            // Skip update if the new budget is the same as the current one.
            Logger.log('      - SKIPPED: New budget ($' + newBudget +
                ') is the same as the current budget. No change needed.');
            continue;
        }
        Logger.log('      - Old Budget: $' + oldBudget + ' -> New Budget: $' +
            newBudget);
        try {
            // Attempt to set the new budget.
            budget.setAmount(newBudget);
            Logger.log('      - SUCCESS: Budget updated for Campaign ID ' +
                id + '.');
        } catch (err) {
            // Log any errors encountered while setting the budget.
            Logger.log('      - FAILED: Could not set budget for Campaign ID '
                + id + '. Error: ' + err);
        }
    }
}
