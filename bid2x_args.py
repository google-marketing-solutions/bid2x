from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import bid2x_var

def process_command_line_args ()-> None:
  # Process arguments
  parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

  # on/off arguments
  parser.add_argument("-aa","--alt_algo",
                      default=bid2x_var.ALTERNATE_ALGORITHM,
                      action='store_true',
                      help="Use alternate algorithm (default false)")
  parser.add_argument("-d","--debug",
                      default=bid2x_var.DEBUG,
                      action='store_true',
                      help="Run script in debug mode " + \
                        "(increases verbosity of output)")
  parser.add_argument("-c","--clear_onoff",
                      default=bid2x_var.CLEAR_ONOFF,
                      action='store_true',
                      help="On update of sheet overwrite Yes/No custom" + \
                        " bidding button based on pattern.")
  parser.add_argument("-dp","--defer_pattern",
                      default=bid2x_var.DEFER_PATTERN,
                      action='store_true',
                      help="When set to true DO NOT use LI name pattern to" + \
                        " set rule on/off.  Default is False.")

  # default value numeric arguments
  parser.add_argument("-a","--advertiser",
                      default=bid2x_var.ADVERTISER_ID,
                      type=int,
                      help="Pass a new advertiser ID")
  parser.add_argument("-b","--attribute",
                      default=bid2x_var.ATTR_MODEL_ID,
                      type=int,
                      help="Pass a new Model Attribute ID")
  parser.add_argument("-bh","--bidding_high",
                      default=bid2x_var.BIDDING_FACTOR_HIGH,
                      type=int,
                      help="Bidding factor high limit")
  parser.add_argument("-bl","--bidding_low",
                      default=bid2x_var.BIDDING_FACTOR_LOW,
                      type=int,
                      help="Bidding factor high limit")
  parser.add_argument("-f","--floodlight",
                      default=bid2x_var.FLOODLIGHT_ID_LIST,
                      type=int,
                      help="Pass a new floodlight ID for the CB script")
  parser.add_argument("-g","--algorithm",
                      default=bid2x_var.CB_ALGO_ID,
                      type=int,
                      help="Change the custom bidding algorithm ID to update")
  parser.add_argument("-p","--partner",
                      default=bid2x_var.PARTNER_ID,
                      type=int,
                      help="DV360 Partner ID to use")

  # default value names / filenames
  parser.add_argument("-i","--input_file",
                      default=bid2x_var.INPUT_FILE,
                      help="JSON file to load config from")
  parser.add_argument("-j","--json_file",
                      default=bid2x_var.JSON_AUTH_FILE,
                      help="JSON auth filename to use")
  parser.add_argument("-l","--last_upload",
                      default=bid2x_var.CB_LAST_UPDATE_FILE_PREFIX,
                      help="File containing last successfully uploaded script")
  parser.add_argument("-lp","--li_pattern",
                      default=bid2x_var.LINE_ITEM_NAME_PATTERN,
                      help="Line item string pattern to match. " + \
                        " Default: *bid-to-x*")
  parser.add_argument("-na","--algo_name",
                      default=bid2x_var.NEW_ALGO_NAME,
                      help="New custom bidding algorithm DV internal name")
  parser.add_argument("-nd","--algo_display_name",
                      default=bid2x_var.NEW_ALGO_DISPLAY_NAME,
                      help="New custom bidding algorithm DV display name. " + \
                        "Use quotes to include spaces.")
  parser.add_argument("-s","--service_account",
                      default=bid2x_var.SERVICE_ACCOUNT_EMAIL,
                      help="Service account email (typically: " + \
                        "name@<gcp_project>.iam.gserviceaccount.com) to use")
  parser.add_argument("-t","--tmp",
                      default=bid2x_var.CB_TMP_FILE_PREFIX,
                      help="full path location of temp prefix")
  parser.add_argument("-z","--zones",
                      default=bid2x_var.ZONES_TO_PROCESS,
                      help="Sales zones to process")

  # action arguments
  parser.add_argument("-ac","--action_create",
                      default=bid2x_var.ACTION_CREATE_ALGORITHM,
                      action='store_true',
                      help='Action to run: Create a new custom ' + \
                        'bidding algorithm')
  parser.add_argument("-ah","--action_update_spreadsheet",
                      default=bid2x_var.ACTION_UPDATE_SPREADSHEET,
                      action='store_true',
                      help='Action to run: Update spreadsheet' + \
                        ' with values from DV360')
  parser.add_argument("-al","--action_list_algos",
                      default=bid2x_var.ACTION_LIST_ALGOS,
                      action='store_true',
                      help='Action to run: List custom bidding algorithms')
  parser.add_argument("-ar","--action_remove",
                      default=bid2x_var.ACTION_REMOVE_ALGORITHM,
                      action='store_true',
                      help='Action to run: Remove a custom bidding ' + \
                        'algorithm, use with -g option')
  parser.add_argument("-as","--action_list_scripts",
                      default=bid2x_var.ACTION_LIST_SCRIPTS,
                      action='store_true',
                      help='Action to run: List custom bidding scripts' + \
                        ' for selected algorithm')
  parser.add_argument("-at","--action_test",
                      default=bid2x_var.ACTION_TEST,
                      action='store_true',
                      help='Action to run: Test new functionality')
  parser.add_argument("-au","--action_update",
                      default=bid2x_var.ACTION_UPDATE_SCRIPTS,
                      action='store_true',
                      help='Action to run: Update custom bidding script')

  args = vars(parser.parse_args())

  # Set Actions from arguments
  bid2x_var.ACTION_LIST_ALGOS = args['action_list_algos']
  bid2x_var.ACTION_LIST_SCRIPTS = args['action_list_scripts']
  bid2x_var.ACTION_CREATE_ALGORITHM = args['action_create']
  bid2x_var.ACTION_UPDATE_SPREADSHEET = args['action_update_spreadsheet']
  bid2x_var.ACTION_REMOVE_ALGORITHM = args['action_remove']
  bid2x_var.ACTION_UPDATE_SCRIPTS = args['action_update']
  bid2x_var.ACTION_TEST = args['action_test']

  # Set debug flag from arguments
  bid2x_var.DEBUG = args["debug"]

  # Names
  bid2x_var.NEW_ALGO_NAME = args['algo_name']
  bid2x_var.NEW_ALGO_DISPLAY_NAME = args['algo_display_name']

  # Set files used in the solution from the arguments
  bid2x_var.JSON_AUTH_FILE = args["json_file"]
  bid2x_var.CB_TMP_FILE_PREFIX = args["tmp"]
  bid2x_var.CB_LAST_UPDATE_FILE_PREFIX = args["last_upload"]

  # Value-specific information (defaults)
  bid2x_var.PARTNER_ID = args["partner"]
  bid2x_var.ADVERTISER_ID = args["advertiser"]
  bid2x_var.CB_ALGO_ID = args["algorithm"]
  bid2x_var.SERVICE_ACCOUNT_EMAIL = args["service_account"]
  bid2x_var.ZONES_TO_PROCESS = args["zones"]

  # need to figure out how to handle lists
  bid2x_var.FLOODLIGHT_ID_LIST = [4851514,4854533]

  bid2x_var.ATTR_MODEL_ID = args["attribute"]
  bid2x_var.BIDDING_FACTOR_HIGH = args["bidding_high"]
  bid2x_var.BIDDING_FACTOR_LOW = args["bidding_low"]
  bid2x_var.CLEAR_ONOFF = args["clear_onoff"]
  bid2x_var.DEFER_PATTERN = args["defer_pattern"]
  bid2x_var.ALTERNATE_ALGORITHM = args["alt_algo"]
  bid2x_var.LINE_ITEM_NAME_PATTERN = args["li_pattern"]

  bid2x_var.JSON_AUTH_FILE = args["json_file"]
  bid2x_var.INPUT_FILE = args["input_file"]