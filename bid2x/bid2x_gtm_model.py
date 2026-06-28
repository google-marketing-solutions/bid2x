"""BidToX - bid2x_model application module.

  Copyright 2025 Google LLC

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  Description:
  ------------

  This module contains the Bid2xGTMModel class which is used to
  represent a GTM zone in the Bid2X system.
"""


class Error(Exception):
  """Base exception for Bid2xGTMModel."""


class InvalidArgumentError(Error):
  """Raised when an invalid argument is provided."""


class Bid2xGTMModel:
  """Model for a GTM zone and its spreadsheet status coordinates."""

  # Set properties of this class.
  name: str
  account_id: int
  container_id: int
  workspace_id: int
  variable_id: int

  debug: bool
  trace: bool

  update_row: int
  update_col: int
  test_row: int
  test_col: int
  cb_algorithm: str

  def __init__(
      self, name: str, account_id: int, container_id: int, workspace_id: int,
      variable_id: int, update_row: int, update_col: int, test_row: int,
      test_col: int
  ) -> None:

    self.name = name
    self.account_id = account_id
    self.container_id = container_id
    self.workspace_id = workspace_id
    self.variable_id = variable_id

    self.debug = False
    self.trace = False
    self.cb_algorithm = ''

    self.update_row = update_row
    self.update_col = update_col
    self.test_row = test_row
    self.test_col = test_col

  def __str__(self) -> str:
    """Override str method for this object to return a sensible string.

    Args:
       None
    Returns:
       A formatted string containing the main object properties.
    """
    zone_str = (
        f'Zone Name: {self.name}\n'
        f'\taccount_id: {self.account_id}\n'
        f'\tcontainer_id: {self.container_id}\n'
        f'\tworkspace_id: {self.workspace_id}\n'
        f'\tvariable_id: {self.variable_id}\n'
        f'\tupdate_row: {self.update_row}\n'
        f'\tupdate_col: {self.update_col}\n'
        f'\ttest_row: {self.test_row}\n'
        f'\ttest_col: {self.test_col}\n'
    )

    return zone_str

  def set_name(self, name: str) -> None:
    self.name = name

  def set_spreadsheet_row_col(
      self, update_row: int, update_col: int, test_row: int, test_col: int
  ) -> None:
    """Setter function for row and col variables.

    Args:
      update_row: The row number to use for an update string when the
                  custom bidding algorithm is changed (--au argument)
      update_col: The column number (not letter) to use for an update string
                  when the custom bidding algorithm is changed.
      test_row:   The row number to use for an update string when a
                  test is run (--at argument).
      test_col:   The column number (not letter) to use for an update string
                   when a test is run.
    Returns:
      None
    """
    self.update_row = update_row
    self.update_col = update_col
    self.test_row = test_row
    self.test_col = test_col

  def set_cb_algorithm(self, str_algor: str) -> None:
    self.cb_algorithm = str_algor