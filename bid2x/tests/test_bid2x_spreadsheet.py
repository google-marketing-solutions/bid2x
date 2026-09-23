"""Tests for bid2x_spreadsheet helpers."""

from unittest.mock import patch

from bid2x_spreadsheet import (
    Bid2xSpreadsheet,
    build_line_item_sheet_rows,
    build_sheet_clear_range,
    column_number_to_letter,
    extract_enabled_line_item_ids,
    should_include_line_item,
)


def test_column_number_to_letter() -> None:
  assert column_number_to_letter(1) == 'A'
  assert column_number_to_letter(2) == 'B'


def test_build_sheet_clear_range() -> None:
  assert build_sheet_clear_range('A', 'F', 2, 1000) == 'A2:F1000'


def test_should_include_line_item_filters_youtube_types() -> None:
  line_item = {
      'lineItemType': 'LINE_ITEM_TYPE_YOUTUBE_AND_PARTNERS_REACH',
      'displayName': 'bid-to-x campaign',
  }
  assert should_include_line_item(line_item, 'bid-to-x') is False


def test_build_line_item_sheet_rows_includes_matching_items() -> None:
  line_items = [
      {
          'entityStatus': 'ACTIVE',
          'lineItemId': 101,
          'displayName': 'bid-to-x display',
          'lineItemType': 'LINE_ITEM_TYPE_DISPLAY_DEFAULT',
          'campaignId': 500,
          'advertiserId': 900,
      },
      {
          'entityStatus': 'ACTIVE',
          'lineItemId': 102,
          'displayName': 'other display',
          'lineItemType': 'LINE_ITEM_TYPE_DISPLAY_DEFAULT',
          'campaignId': 500,
          'advertiserId': 900,
      },
  ]

  rows, auto_ons = build_line_item_sheet_rows(line_items, 'bid-to-x')

  assert len(rows) == 1
  assert rows[0][1] == 101
  assert auto_ons == [['Yes']]


def test_extract_enabled_line_item_ids_deduplicates() -> None:
  rows = [
      {'Generate Custom Bidding': 'Yes', 'Line Item ID': 101},
      {'Generate Custom Bidding': 'yes', 'Line Item ID': 101},
      {'Generate Custom Bidding': 'No', 'Line Item ID': 202},
  ]

  assert extract_enabled_line_item_ids(rows) == [101]


def test_init_defaults_clear_onoff_false() -> None:
  with patch('bid2x_spreadsheet.gspread.service_account'):
    sheet = Bid2xSpreadsheet('sheet-id', 'secrets.json')

  assert sheet.clear_onoff is False
  assert sheet.sheet_url.endswith('/sheet-id/edit')
