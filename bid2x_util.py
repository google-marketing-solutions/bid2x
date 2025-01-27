<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
"""BidToX - bid2x_util application module.

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

  This module contains utility functions used by the Bid2X application.
"""

import http
import time
=======
from googleapiclient.errors import HttpError
from google.api_core.exceptions import GoogleAPICallError
from http import HTTPStatus
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )
from typing import Any
import time
import bid2x_var
import jsonpickle
import gspread

import bid2x_var
from google.api_core import exceptions
from googleapiclient import errors
import jsonpickle


HttpError = errors.HttpError
GoogleAPICallError = exceptions.GoogleAPICallError
HTTPStatus = http.HTTPStatus


def google_dv_call(request: Any, context: str) -> dict[Any]:

  """Make an API call to DV360 with detailed exception handling.

  Args:
    request: A preformatted request to the DV API.
    context: text string used in the exception reporting.

  Returns:
    The response from the API call.
  """

  response = None

  try:
    response = request.execute()
  except HttpError as err:
    # If the error is a rate limit or connection error, wait and try again.
    if err.resp.status in [HTTPStatus.FORBIDDEN,
                           HTTPStatus.INTERNAL_SERVER_ERROR,
                           HTTPStatus.SERVICE_UNAVAILABLE]:
      time.sleep(bid2x_var.HTTP_RETRY_TIMEOUT)

      # We have slept an amount, retry the call
      response = request.execute()
    else:
      print(f'Error with DV360 in {context} call :{err}')
      raise
  except GoogleAPICallError as err:
    # Handle more specific Google API errors
    print(f'Error with DV360 in {context} call :{err}')

  return response

# Insert generic spreadsheet call routine here when we remove gspread.


def is_recoverable_http_error(err: HTTPStatus) -> bool:
  if err in [HTTPStatus.FORBIDDEN,
             HTTPStatus.INTERNAL_SERVER_ERROR,
             HTTPStatus.SERVICE_UNAVAILABLE]:
    return True
  else:
    return False


def is_number(s: Any) -> bool:
  """Is the passed variable a number?

  Args:
    s: any variable
  Returns:
    True if the passed variable evaluates to a number or a string containing
    a number
  """
  try:
    float(s)
    return True
  except ValueError:
    return False


def save_config(obj: Any, filename_to_save: str) -> bool:
  """Use jsonpickle to save a python object to a file.

  Args:
    obj: the object to save
    filename_to_save: the name of the file to save to
  Returns:
    True if the save is successful, False otherwise.
  """

  frozen = jsonpickle.encode(obj, indent=2, unpicklable=False)

  # Save the JSON string to a file
  with open(filename_to_save, 'w') as f:
    f.write(frozen)

  return True


def read_config(filename_to_load: str) -> Any:
  """Use jsonpickle to load a python object from a file.

  Args:
    filename_to_load: the name of the file to load from
  Returns:
    The object loaded from the file.
  """

  # Load the JSON string from the file
  with open(filename_to_load, 'r') as f:
    frozen = f.read()

  # Deserialize the object from the JSON string
  loaded = jsonpickle.decode(frozen)

  return loaded
