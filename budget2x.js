/**
 * =============================================================================
 * budget2x for Google Ads
 * =============================================================================
 *
 * Description:
 * This script updates campaign daily budgets based on data from a Google Sheet.
 * It uses a master control tab ("KeySheet") to determine which sets of campaigns
 * to update. This allows for managing budgets across multiple accounts or logical
 * groups from a single spreadsheet.
 *
 * This code is expected to be loaded into the Ads Script portion of Google Ads
 * for a manager or sub-manager account of multiple MCCs.  Look for the scripts
 * under Tools-->Bulk Actions-->Scripts.  Make a new script and cut and paste
 * this code into that location.
 *
 * This code uses an associated Google Sheet.
 * Instructions for the Google Sheet:
 * 1. Set the SPREADSHEET_URL variable below to the URL of your Google Sheet.
 * 2. Create a tab named "KeySheet" or ensure there is a "KeySheet" tab.
 * 3. In "KeySheet", create the following headers in the first row:
 * - Column A: Zone Name (e.g., "North America Campaigns")
 * - Column B: MCC (The account ID, for reference)
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
 * https://docs.google.com/spreadsheets/d/1PIxTrwMc3QBhv_1vbjt4B-cNaD7MucmHWk-gzQhhjRA/edit
 *
 * @author Mark D. Oliver @mdoliver
 * @version 1.1
 */

// TODO: Replace with your copy of the control sheet for budget2x.
const SPREADSHEET_URL =
    'https://docs.google.com/spreadsheets/d/your_sheet_id/edit';

// --- SCRIPT CONFIGURATION ---
// Name of the main control sheet.
const KEY_SHEET_NAME = 'KeySheet';
// Number of header rows in the KeySheet to skip.
const KEY_SHEET_HEADER_ROWS = 1;

// Column positions in KeySheet (0-indexed, e.g., A=0, B=1).
const COL_ZONE_NAME = 0;
const COL_MCC = 1;
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
    spreadsheet = SpreadsheetApp.openByUrl(SPREADSHEET_URL);
  } catch (e) {
    Logger.log('FATAL ERROR: Failed to open spreadsheet. ' +
      'Please check the SPREADSHEET_URL. Details: ' + e);
    return;
  }

  const keySheet = spreadsheet.getSheetByName(KEY_SHEET_NAME);

  if (!keySheet) {
    Logger.log('FATAL ERROR: The KeySheet named "' + KEY_SHEET_NAME +
      '" was not found. Terminating script.');
    throw new Error('KeySheet not found.');
  }

  // Get all data from the KeySheet to process.
  const keySheetData = keySheet.getDataRange().getValues();

  // Iterate over each configuration row in the KeySheet, skipping the header.
  for (let i = KEY_SHEET_HEADER_ROWS; i < keySheetData.length; i++) {
    const row = keySheetData[i];
    const status = row[COL_STATUS];
    const tabName = row[COL_TAB_NAME];
    const reference = row[COL_REFERENCE];
    const zoneName = row[COL_ZONE_NAME];

    // Stop if we hit an empty row.
    if (!zoneName && !tabName && !reference) {
      continue;
    }

    Logger.log('--------------------------------------------------');
    // Process the row only if its Status is explicitly 'On'.
    if (status && status.toString().trim().toLowerCase() === 'on') {
      Logger.log('Processing Zone: "' + zoneName + '" | Tab: "' +
        tabName + '"');
      applyBudgetsFromTab(spreadsheet, tabName, reference);
    } else {
      Logger.log('Skipping Zone: "' + zoneName + '" (Status is "' + status +
        '", not "On").');
    }
  }
  Logger.log('--------------------------------------------------');
  Logger.log('Script finished.');
}

/**
 * Fetches campaign and budget data from a specific tab and applies budgets.
 * @param {!GoogleAppsScript.Spreadsheet.Spreadsheet} spreadsheet Active sheet.
 * @param {string} tabName The name of the sheet containing budget data.
 * @param {string} startReference The starting cell of the data (e.g., "B5").
 */
function applyBudgetsFromTab(spreadsheet, tabName, startReference) {
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
  // over 3 columns (ID, Budget, Status).
  const numRows = lastRow - startRow + 1;
  const budgetDataRange = budgetSheet.getRange(startRow, startCol, numRows, 3);
  const budgetValues = budgetDataRange.getValues();

  Logger.log('  -> Found ' + budgetValues.length +
    ' potential campaign(s) to update.');

  // Iterate over each campaign/budget/status triplet.
  for (let i = 0; i < budgetValues.length; i++) {
    let campaignId = budgetValues[i][0];
    const newBudget = budgetValues[i][1];
    const campaignStatus = budgetValues[i][2];

    // Validate that the Campaign ID exists.
    if (!campaignId || campaignId.toString().trim() === '') {
      continue; // Skip rows with no Campaign ID.
    }

    // Check the individual campaign's status before proceeding.
    if (!campaignStatus ||
        campaignStatus.toString().trim().toLowerCase() !== 'on') {
      Logger.log('  -> SKIPPING Campaign ID ' + campaignId +
        ' because its status is "' + campaignStatus + '", not "On".');
      continue;
    }

    // Validate that the budget is a positive number.
    if (newBudget === '' || isNaN(parseFloat(newBudget)) ||
      parseFloat(newBudget) <= 0) {
      Logger.log('  -> SKIPPING Campaign ID ' + campaignId +
        ' due to invalid budget: "' + newBudget + '".');
      continue;
    }

    // Ensure Campaign ID is a string for the API call.
    campaignId = campaignId.toString().trim();

    // Set the budget for the individual campaign.
    setCampaignBudget(campaignId, parseFloat(newBudget));
  }
}

/**
 * Sets the daily budget for a single campaign using its ID.
 * @param {string} id The Campaign ID.
 * @param {number} newBudget The new daily budget amount.
 */
function setCampaignBudget(id, newBudget) {
  // Use AdWordsApp.campaigns() to find campaigns of any standard type.
  const campaignIterator = AdWordsApp.campaigns().withIds([id]).get();

  if (campaignIterator.totalNumEntities() === 0) {
    Logger.log('    -> ERROR: Campaign with ID "' + id +
      '" was not found in this account.');
    return;
  }

  while (campaignIterator.hasNext()) {
    const campaign = campaignIterator.next();
    const budget = campaign.getBudget();
    const oldBudget = budget.getAmount();

    Logger.log('    -> Processing Campaign: "' + campaign.getName() +
      '" (ID: ' + id + ')');

    if (oldBudget === newBudget) {
      Logger.log('       - SKIPPED: New budget ($' + newBudget +
        ') is the same as the current budget.');
      continue;
    }

    Logger.log('       - Old Budget: $' + oldBudget + ' -> New Budget: $' +
      newBudget);

    try {
      budget.setAmount(newBudget);
      Logger.log('       - SUCCESS: Budget updated.');
    } catch (err) {
      Logger.log('       - FAILED: Could not set budget. Error: ' + err);
    }
  }
}
