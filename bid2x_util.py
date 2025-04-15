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
import logging
import time
from typing import Any

import bid2x_var
from google.api_core import exceptions
from google.cloud import storage
from googleapiclient import errors
import jsonpickle
import urlparse

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
    if err.resp.status in [
        HTTPStatus.FORBIDDEN, HTTPStatus.INTERNAL_SERVER_ERROR,
        HTTPStatus.SERVICE_UNAVAILABLE
    ]:
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
  if err in [
      HTTPStatus.FORBIDDEN, HTTPStatus.INTERNAL_SERVER_ERROR,
      HTTPStatus.SERVICE_UNAVAILABLE
  ]:
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
  """Load a python object from a file or CGS with gs:// prefix.

  Args:
      filename_to_load: The path or GCS URI of the file to load.

  Returns:
      The object loaded and decoded from the file content.

  Raises:
      ValueError: If the path format is invalid.
      google.cloud.exceptions.NotFound: If the GCS object doesn't exist.
      FileNotFoundError: If the local file doesn't exist.
      Exception: For other potential errors during file reading or JSON
      decoding.
  """

  # --- Google Cloud Storage Handling ---
  if filename_to_load.startswith('gs://'):
    source_description = f'GCS path: {filename_to_load}'
    logging.info('Attempting to load config from %s', source_description)
    try:
      parsed_uri = urlparse(filename_to_load)
      bucket_name = parsed_uri.netloc
      object_name = parsed_uri.path.lstrip('/')

      if not bucket_name or not object_name:
        raise ValueError(f'Invalid GCS path format: {filename_to_load}')

      storage_client = storage.Client()
      bucket = storage_client.bucket(bucket_name)
      blob = bucket.blob(object_name)
      frozen = blob.download_as_text()
      logging.info('Successfully downloaded from %s', source_description)

    except Exception as e:
      logging.error('Failed to load from %s: %s', source_description, e)
      raise
  # --- Local File Handling (Default) ---
  else:
    source_description = f'local path: {filename_to_load}'
    logging.info('Attempting to load config from %s', source_description)
    try:
      with open(filename_to_load, 'r') as f:
        frozen = f.read()
      logging.info('Successfully read from %s', source_description)
    except FileNotFoundError:
      logging.error('Local file not found: %s', filename_to_load)
      raise
    except Exception as e:
      logging.error('Failed to read %s: %s', source_description, e)
      raise

  # --- Decoding Step ---
  # This now happens *after* the 'frozen' string is populated, before returning.
  if not frozen:
    # This case should ideally be caught by earlier errors, but safety check.
    raise ValueError(
        f'No content loaded from "{filename_to_load}". Cannot decode.'
    )

  try:
    logging.info('Attempting to decode JSON from %s', source_description)
    # Decode the loaded JSON string using jsonpickle
    loaded_object = jsonpickle.decode(frozen)
    logging.info(
        'Successfully decoded configuration from %s', source_description
    )
    return loaded_object  # Return the decoded Python object
  except Exception as e:
    # Catch potential errors during jsonpickle decoding
    logging.error(
        'Failed to decode JSON content from %s: %s', source_description, e
    )
    # Log the first few characters of the problematic string for debugging:
    logging.error('Content snippet (up to 100 chars): %s', frozen[:100])
    raise  # Re-raise the decoding error


def copy_iff_exists(src: Any, key_as_str: str, dst: Any):
  """If key exists in src copy to dst.

  Args:
    src: the source object.
    key_as_str: the string name of the key.
    dst: location to copy key value to.
  Returns:
    None
  """

  if key_as_str in src:
    dst[key_as_str] = src[key_as_str]
