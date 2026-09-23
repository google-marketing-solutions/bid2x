const test = require('node:test');
const assert = require('node:assert/strict');

const {
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
} = require('../budget2x_helpers.js');

test('cleanAccountId removes hyphens', () => {
  assert.equal(cleanAccountId('123-456-7890'), '1234567890');
  assert.equal(cleanAccountId(1234567890), '1234567890');
});

test('isStatusOn treats On case-insensitively', () => {
  assert.equal(isStatusOn('On'), true);
  assert.equal(isStatusOn(' on '), true);
  assert.equal(isStatusOn('Off'), false);
  assert.equal(isStatusOn(''), false);
});

test('isKeySheetRowEmpty detects blank KeySheet rows', () => {
  assert.equal(isKeySheetRowEmpty('', '', ''), true);
  assert.equal(isKeySheetRowEmpty('Zone', '', ''), false);
});

test('isValidBudgetValue accepts positive numbers only', () => {
  assert.equal(isValidBudgetValue(25), true);
  assert.equal(isValidBudgetValue('12.5'), true);
  assert.equal(isValidBudgetValue(''), false);
  assert.equal(isValidBudgetValue(0), false);
  assert.equal(isValidBudgetValue('abc'), false);
});

test('matchesCampaignNameFilter supports regex and invalid patterns', () => {
  assert.equal(matchesCampaignNameFilter('Brand_US', '^Brand.*'), true);
  assert.equal(matchesCampaignNameFilter('Generic_US', '^Brand.*'), false);
  assert.equal(matchesCampaignNameFilter('Any', ''), true);
  assert.equal(matchesCampaignNameFilter('Any', '['), false);
});

test('parseKeySheetRow maps column indexes', () => {
  const row = [];
  row[COL_ZONE_NAME] = 'North America';
  row[COL_MCC] = '123-456-7890';
  row[COL_TAB_NAME] = 'NA Tab';
  row[COL_STATUS] = 'On';
  row[COL_REFERENCE] = 'B5';

  assert.deepEqual(parseKeySheetRow(row), {
    zoneName: 'North America',
    mccId: '123-456-7890',
    tabName: 'NA Tab',
    status: 'On',
    reference: 'B5',
  });
});
