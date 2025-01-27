<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
"""BidToX - bid2x_platform application module.

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

  Description:
  ------------

  This module contains the Platform class which is the abstract class
  for the platform the script is being used.  It contains the necessary
  methods to run the script.
"""

import abc
=======
from abc import ABC, abstractmethod
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )
from typing import Any
from pandas import DataFrame

import pandas

DataFrame = pandas.DataFrame
abstractmethod = abc.abstractmethod
ABC = abc.ABC


class Platform(ABC):
  """Abstract class for the platform the script is being used.

      Attributes:
          None.

      Methods:
          process_script(self, service): Abstract method for running the
              script creation and uploading to the correct platform.
          print_dataframe(self, debug, input_df): Prints given dataframe.
  """

  @abstractmethod
  def __str__(self):
    pass

  @abstractmethod
  def process_script(self, service):
    pass

  @abstractmethod
  def top_level_copy(self, source: Any) -> None:
    pass

  def print_dataframe(self, debug: bool, input_df: DataFrame) -> None:
    """Converts a dataframe to a string and prints it to stdout.

    Args:
        debug: prints output if debug is true.
        input_df: any dataframe.

    Returns:
        None.
    """
    # make sure indexes pair with number of rows
    df = input_df.reset_index()

    if debug:
      print(df.to_string())
