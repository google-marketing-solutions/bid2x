/**
 * Pure helpers for budget2x. Kept in sync with the copies in budget2x.js for
 * Google Ads Script deployment.
 */

const COL_ZONE_NAME = 0;
const COL_MCC = 1;
const COL_TAB_NAME = 2;
const COL_STATUS = 3;
const COL_REFERENCE = 4;

function cleanAccountId(accountId) {
  return accountId.toString().replace(/-/g, '');
}

function isStatusOn(status) {
  return Boolean(
      status && status.toString().trim().toLowerCase() === 'on');
}

function isKeySheetRowEmpty(zoneName, tabName, reference) {
  return !zoneName && !tabName && !reference;
}

function isValidBudgetValue(newBudget) {
  return newBudget !== '' &&
      !isNaN(parseFloat(newBudget)) &&
      parseFloat(newBudget) > 0;
}

function matchesCampaignNameFilter(campaignName, regexFilter) {
  if (!regexFilter) {
    return true;
  }
  try {
    return new RegExp(regexFilter).test(campaignName);
  } catch (e) {
    return false;
  }
}

function parseKeySheetRow(row) {
  return {
    zoneName: row[COL_ZONE_NAME],
    mccId: row[COL_MCC],
    tabName: row[COL_TAB_NAME],
    status: row[COL_STATUS],
    reference: row[COL_REFERENCE],
  };
}

module.exports = {
  cleanAccountId,
  isStatusOn,
  isKeySheetRowEmpty,
  isValidBudgetValue,
  matchesCampaignNameFilter,
  parseKeySheetRow,
  COL_ZONE_NAME,
  COL_MCC,
  COL_TAB_NAME,
  COL_STATUS,
  COL_REFERENCE,
};
