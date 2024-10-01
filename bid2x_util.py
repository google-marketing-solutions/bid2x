from googleapiclient.errors import HttpError
from google.api_core.exceptions import GoogleAPICallError
from http import HTTPStatus
from typing import Any
import time
import bid2x_var
import jsonpickle
import gspread

def google_dv_call(request: Any, context: str) -> dict:

  """Make an API call to DV360 with detailed exception handling.

  Args:
    request: A preformatted request to the DV API.
    context: text string used in the exception reporting.

  Returns:
    The response from the API call.
  """

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

# TODO: insert generic spreadsheet call routine here


def is_recoverable_http_error(err: HTTPStatus) -> bool:
  if err in [HTTPStatus.FORBIDDEN,
             HTTPStatus.INTERNAL_SERVER_ERROR,
             HTTPStatus.SERVICE_UNAVAILABLE]:
    return True
  else:
    return False


def is_number(s) -> bool:
  """is the passed variable a number?
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

def save_config(obj,filename_to_save: str)->bool:
  frozen = jsonpickle.encode(obj,indent=2,unpicklable=False)

  # Save the JSON string to a file
  with open(filename_to_save, 'w') as f:
      f.write(frozen)

  return True

def read_config(filename_to_load) -> Any:
  # Load the JSON string from the file
  with open(filename_to_load, 'r') as f:
      frozen = f.read()

  # Deserialize the object from the JSON string
  loaded = jsonpickle.decode(frozen)


  return loaded