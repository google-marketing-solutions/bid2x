"""BidToX - bid2x_platform application module.

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

  This module contains the Platform class which is the abstract class
  for the platform the script is being used.  It contains the necessary
  methods to run the script.
"""

import abc
from typing import Any

import pandas

DataFrame = pandas.DataFrame
abstractmethod = abc.abstractmethod
ABC = abc.ABC


class Platform(ABC):
  """Abstract base class for DV360 and GTM platform implementations."""

  @abstractmethod
  def __str__(self) -> str:
    pass

  @abstractmethod
  def process_script(self, service: Any, *args: Any, **kwargs: Any) -> Any:
    pass

  @abstractmethod
  def top_level_copy(self, source: Any) -> None:
    pass

  def print_dataframe(self, debug: bool, input_df: DataFrame) -> None:
    """Print a dataframe when debug output is enabled.

    Args:
        debug: When True, write the dataframe to stdout.
        input_df: Dataframe to display.

    Returns:
        None.
    """
    df = input_df.reset_index()

    if debug:
      print(df.to_string())
