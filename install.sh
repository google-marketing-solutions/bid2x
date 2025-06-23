#!/bin/bash

# Copyright 2025 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# =============================================================================
# bid2x Installation Script
# =============================================================================

# Usage:
#   ./install.sh

# General Notes:
#   To be executed from the local directory containing the bid2x .py code.
#   There are a few references in the installer to '.' which is the current
#   directory so your location within the filesystem when running this is
#   critical. In general, it is anticipated that this script will be run from
#   within GCP's Cloud Shell. It might work from other shells _but_ it is has
#   only been primarily tested from within the GCP Cloud Shell.

# File prep:
#   The script requires the existence of a config file (.json) and an
#   authorization file (also .json).
#   There are a few sample config files in the bid2x directory:
#     sample_config_dv.json, &
#     sample_config_sa.json

#   Typically, the configuration .json file refers to the auth .json file by
#   name  (something like 'client-secret.json').  The auth file contains the
#   credentials needed to access the external services that bid2x utilizes and
#   is typically created using the GCP web UI.

#   It is recommended that both of these JSON files are kept in the same
#   location as the bid2x .py code as the installer will be looking for them
#   in the current directory and wraps them up into a zip file for Cloud Run
#   Jobs deployment.

# Authentication:
#   ALWAYS ensure you're logged into GCP BEFORE RUNNING THIS SCRIPT.  If the
#   GCP Cloud Shell has recently been opened then this auth should happen
#   automatically. If you are using a stale Cloud Shell you may need to refresh
#   or do a 'gcloud auth login' to ensure your auth is current.

# Service Account prep:
#   You must have a service account created and ready for use BEFORE running
#   this installation script because it is part of the core configuration (see
#   SERVICE_ACCOUNT and INVOKER_SERVICE_ACCOUNT variables below).

# Installation Time Expectations:
#   A full run of a 'DV' type installation with this script in the region
#   US-CENTRAL1 on a fresh project takes approximately 10-15 minutes.
#   A run of type 'SA' should be a shorter installation due to fewer components
#   being deployed; perhaps 7-10 minutes.

# Installation Logs:
#   Each installation creates a log file , by default 'bid2x_installer.log'.
#   The logic in this shell script will NOT allow an old log to be
#   overwritten.  Legacy logs will be renamed with an extension with the
#   original installation time/date.

# Ensure that the following are set according to your needs:

# ----------------------------------------------------------------------------
# Main project parameters
# ----------------------------------------------------------------------------

# Set this to the GCP project name (not the ID) that you are deploying into.
# If you're not sure what the current project is use the command
# 'gcloud config get-value project'.
PROJECT="bid2x-deployment-project"

# Set this to the GCP region you are deploying in (NOT THE ZONE i.e. should
# not end with 'a' or 'b' or whatever).
REGION="us-central1"

# The timezone you want to use for the CRON jobs.
# Note that the default timezone of the GCP Cloud Shell is UTC (Universal
# Coordinated Time) so be aware that by default there are multiple time zones
# in play that need to be considered.
TIMEZONE="America/Toronto"

# File that the most current installation log will be written to.
LOG_FILE="bid2x_installer.log"

# Cloud Storage config container unique name (do not include 'gs://'').
# By default auto-generate 'project-name-config'.
BUCKET_NAME="${PROJECT}-config"

# Time allotted for Cloud Run Jobs to complete.
TASK_TIMEOUT=60m

# Bid2x deployment type: can be 'DV' or 'SA'.
DEPOLYMENT_TYPE='DV'

# Verbosity mode - uncomment what you want.  Some gcloud commands seem to
# ignore --quiet and output whatever they want. YMMV.
# Warning: running without --quiet can make some commands interactive
# and thus require the answering of (Y/N) questions during the install.
QUIET='--quiet'
# QUIET=' '

# ----------------------------------------------------------------------------
# Virtual Machine Environment details for Cloud Run Job deployments.
# ----------------------------------------------------------------------------
# Cloud Run Jobs deployment cpu default for bid2x.  A single CPU='1' is
# usually sufficient for bid2x.
CPU='1'

# Cloud Run Jobs deployment memory default for bid2x. This number CAN be
# increased when needed, for example ='1Gi' or ='2Gi'.
# Some DV trafficking profiles can contain a LARGE number of Line Items in a
# campaign and a large download of Line Items can exhaust memory
# (watch the logs). Don't be afraid to increase this number as needed.
MEMORY='512Mi'
# MEMORY='1Gi'
# MEMORY='2Gi'

# ----------------------------------------------------------------------------
# Service account(s) for the deployment.
# ----------------------------------------------------------------------------
# Service account used for IAM calls and "cloud run jobs deploy" commands.
SERVICE_ACCOUNT="bid2x-service@${PROJECT}.iam.gserviceaccount.com"
#SERVICE_ACCOUNT="improvado-service-account@${PROJECT}.iam.gserviceaccount.com"

# The SA that will RUN the Cloud Run command (i.e. with
# run.jobs.run permission).
INVOKER_SERVICE_ACCOUNT="bid2x-service@${PROJECT}.iam.gserviceaccount.com"
# INVOKER_SERVICE_ACCOUNT="improvado-service-account@${PROJECT}.iam.gserviceaccount.com"

# The two service account variables above MAY be the same but can also be
# different; depending on your requirements.

# ----------------------------------------------------------------------------
# Cloud Run Job details for the weekly and daily runs.
# ----------------------------------------------------------------------------
# Fill in weekly items in for DV and SA type deployments.

# The name given to the Cloud Run Job for the weekly run.  This is the name
# of the Cloud Run job in the UI.
WEEKLY_CLOUD_RUN_JOB_NAME="bid2x-weekly"
# This is the name of the test deployment. The test deployment makes a
# Cloud Run Job instance that is NOT scheduled to run but can be used to
# manually test the deployment.
WEEKLY_CLOUD_RUN_JOB_TEST="bid2x-test-run"

# <min 0-60,*> <hour 0-23,*> <day 1-31,*> <month 1-12,*> <day of week 1-7,*>.
# The default of "0 20 * * 7" is a schedule for Sundays(7) at 8pm (20:00).
WEEKLY_CRON_SCHEDULE="0 20 * * 7"

# This file should already exist and be readable; there is a test for
# existence of this file in the pre-run checks.
# WEEKLY_CONFIG points to the configuration file (.JSON) for bid2x
# that runs weekly on a scheduled basis.
# WEEKLY_CONFIG_TEST points to a file that normally runs with the
# config of 'action_test = True'.  This is a convenience deployment
# that does not have an associated Cloud Scheduler event but can
# be run by the deployer manually to ensure expected behavior.
WEEKLY_CONFIG="sample_config_dv.json"
WEEKLY_CONFIG_TEST="testrun_dv.json"

# You want a different name for the scheduler job?  Oh, you fancy huh?!
WEEKLY_SCHEDULER_JOB_NAME="${WEEKLY_CLOUD_RUN_JOB_NAME}-scheduled-update"

# Comma-separated list of command-line args after "python main.py".
# See the help text on bid2x to see the full list & defaults
# (python main.py --help).
WEEKLY_ARGS="-i,${WEEKLY_CONFIG}"


# ONLY fill out these items for DV deployments (SA/GTM deployments do not
# have daily spreadsheet updates) and hence deploy fewer components

# The name given to the Cloud Run Job for the daily DV run.
DAILY_CLOUD_RUN_JOB_NAME="bid2x-daily"

# <min 0-60,*> <hour 0-23,*> <day 1-31,*> <month 1-12,*> <day of week 1-7,*>.
# The default of "0 4 * * *" is a schedule for every day at 4:00am".
DAILY_CRON_SCHEDULE="0 4 * * *"

# This file should already exist and be readable. Only checked if you're
# deploying a 'DV' type bid2x.
DAILY_CONFIG="sample_config_dv.json"

# Name of the Scheduler job for the daily job.
DAILY_SCHEDULER_JOB_NAME="${DAILY_CLOUD_RUN_JOB_NAME}-scheduled-update"

# The daily config file is usually a JSON with 'action_update_spreadsheet'
# set to true.
DAILY_ARGS="-i,${DAILY_CONFIG}"

# ----------------------------------------------------------------------------
# Control flags - set to determine which part of the install script runs.
# ----------------------------------------------------------------------------
# By default leave them all as 1 to run all parts of the installer.
# If you're having some installation issues (it happens) you can adjust the
# values below to get only portions of the installation to run.

# Flag, 1 == Run set up environment section, 0 == don't run this section.
SET_UP_ENVIRONMENT=1

# Flag, 1 == Run pre-run checks, 0 == don't run this section.
PRE_RUN_CHECKS=1

# Flag, 1 == Run activate APIs section, 0 == don't run this section.
ACTIVATE_APIS=1

# Flag, 1 == Make IAM calls, 0 == don't run this section.
GRANT_PERMISSIONS=1

# Flag, 1 == Attempt to delete old components, 0 == don't run this section.
DELETE_OLD_INSTALL=1

# Create bucket (when necessary) and copy config file(s) to bucket.
# Flag, 1 == Create bucket if necessary & copy files, 0 == don't run section.
GCS_OPERATIONS=1

# Flag, 1 == Deploy Cloud Run Jobs, 0 == don't run this section.
DEPLOY_JOBS=1

# Flag, 1 == create Cloud Scheduler Jobs, 0 == don't run this section.
CREATE_SCHEDULER_JOBS=1

# =============================================================================
# Most users should not have to edit below this line
# =============================================================================

# Keep some minimal state. Assume GCS portion not successful until it is.
GCS_SUCCESSFUL=0

# Define log_message() convenience function.

# --- Configuration ---
declare -ga LOG_SECTION_NUMBERS=()
# Tracks the highest index accessed in LOG_SECTION_NUMBERS.
# for resetting purposes
declare -gi LOG_MAX_LEVEL_REACHED=-1
# Characters for separator lines at indent levels (level 0, 1, 2,...).
declare -ga LOG_SEPARATOR_CHARS=('=' '-' '*' '+' '#' '%' '&' '.')
# Number of spaces per indentation level.
declare -gi LOG_SPACES_PER_INDENT=4

log_message() {
    # --- Parameters and Local Variables ---
    local level msg term_width indent_str \
          num_str sep_char separator_line i \
          effective_level # Calculated level for array access.

    level="$1"
    msg="$2"

    # --- Input Validation ---
    if ! [[ "$level" =~ ^[0-9]+$ ]]; then
        echo "ERROR (log_message): Indent level '$level' must" \
          " be a non-negative integer." >&2
        return 1 # Use return in functions, exit will stop the whole script.
    fi
     if [[ -z "$msg" ]]; then
        echo "ERROR (log_message): Message text cannot be empty." >&2
        return 1
    fi

    # Ensure level is treated as a number for comparisons and array indexing.
    effective_level=$((level))

    # --- Terminal Width Detection ---
    # Try tput first, then COLUMNS env var, default to 80.
    if command -v tput >/dev/null && tput Co >/dev/null 2>&1; then
        term_width=$(tput cols)
    else
        term_width=${COLUMNS:-80}
    fi
    # Sanity check term_width.
    [[ "$term_width" -lt 20 ]] && term_width=80

    # --- Numbering Logic ---
    # Expand array if needed (when accessing a deeper level than ever before).
    # This ensures parent levels exist in the array, initialized to 0 if new.
    while [[ $effective_level -gt $LOG_MAX_LEVEL_REACHED ]]; do
         LOG_MAX_LEVEL_REACHED=$((LOG_MAX_LEVEL_REACHED + 1))
         LOG_SECTION_NUMBERS[LOG_MAX_LEVEL_REACHED]=0
    done

    # Increment current level's number.
    LOG_SECTION_NUMBERS[effective_level]=$(( \
      LOG_SECTION_NUMBERS[effective_level] + 1 ))

    # Reset number counts for all deeper levels (e.g. calling level 0
    # resets level 1, 2...).
    for (( i = effective_level + 1; i <= LOG_MAX_LEVEL_REACHED; i++ )); do
         LOG_SECTION_NUMBERS[i]=0
    done

    # Format the hierarchical number string (e.g., 1 or 1.2 or 1.2.1).
    # Start with level 0 num (handles case where first call might be > level 0).
    # Default to 0 if level 0 hasn't been called.
    num_str="${LOG_SECTION_NUMBERS[0]:-0}"
    for (( i = 1; i <= effective_level; i++ )); do
        # Append .NUMBER, default to .0 if somehow unset/level skipped.
        num_str+=".${LOG_SECTION_NUMBERS[i]:-0}"
    done

    # --- Indentation ---
    indent_str=""
    if [[ $effective_level -gt 0 ]]; then
         # Create a string of spaces for indentation.
         indent_str=$(printf '%*s' \
          $((effective_level * LOG_SPACES_PER_INDENT)) "")
    fi

    # --- Separators ---
    # Choose separator char based on level, default to last char
    # in array if level is too high.
    if [[ $effective_level -ge ${#LOG_SEPARATOR_CHARS[@]} ]]; then
        # Use index -1 to get the last element reliably.
        sep_char="${LOG_SEPARATOR_CHARS[-1]}"
    else
        sep_char="${LOG_SEPARATOR_CHARS[$effective_level]}"
    fi

    # Create the separator line string matching the
    # available width after indentation.
    local content_width=$(( term_width - \
      (effective_level * LOG_SPACES_PER_INDENT) ))
    # Ensure minimum width of 1, prevent negative width on narrow terminals.
    [[ $content_width -lt 1 ]] && content_width=1
    # Generate the line using printf and tr for repeating character.
    separator_line=$(printf "%${content_width}s" "" | tr ' ' "$sep_char")

    # --- Output ---
    # Use printf for consistent output and handling of special characters.
    printf "%s%s\n" "${indent_str}" "${separator_line}"
    # Numbered message line.
    printf "%s%s. %s\n" "${indent_str}" "${num_str}" "${msg}"
    printf "%s%s\n" "${indent_str}" "${separator_line}"
}

# Ensure old log files persist - back them up.

# Check if logfile exists and is regular file (-f).
if [[ -f "$LOG_FILE" ]]; then
  echo "Existing log file found: '$LOG_FILE' ... backing up."

  # Get modification time as seconds since epoch.
  MOD_EPOCH=$(stat -c %Y "$LOG_FILE")
  # Format the epoch time.
  TIMESTAMP=$(date -d "@$MOD_EPOCH" +"%Y%m%d_%H%M%S")
  BACKUP_NAME="${LOG_FILE}.${TIMESTAMP}"
  echo "   -> Backup name: '$BACKUP_NAME'"

  # Attempt to move (rename) the existing log file.
  if mv -f "$LOG_FILE" "$BACKUP_NAME"; then
      echo "   -> Backup successful: Moved '$LOG_FILE' to '$BACKUP_NAME'"
  else
      # Handle potential errors during move (e.g., permissions).
      echo "   -> ERROR: Failed to move '$LOG_FILE' to '$BACKUP_NAME'. " \
        "Check permissions/manually remove existing log file: '$LOG_FILE'." >&2
      exit 1 # Exit the script if backup fails - harsh, I know.
  fi
else
  echo "No existing log file found at '$LOG_FILE'. A new one will be created."
fi

echo "Setting up logging to '$LOG_FILE'..."

# Log AND Display both stdout and stderr from this point in the script onwards.
echo "Applying redirection: Logging AND displaying" \
  " stdout & stderr to ${LOG_FILE}."
exec > >(tee -a "$LOG_FILE") 2> >(tee -a "$LOG_FILE" >&2)

echo "***********************************************************************"
echo "bid2x installer - Starting - $(date '+%a %b %d, %Y - %I:%M:%S %p %Z')"
echo "***********************************************************************"

# Set up the environment.
if [[ ${SET_UP_ENVIRONMENT} -eq 1 ]]; then

  log_message 0 "Setting up environment"
  log_message 1 "Setting Default Project"
  gcloud config set project "${PROJECT}"

  echo "Setting Default Project complete"
else
  echo "Skipping environment setup"
fi


if [[ ${PRE_RUN_CHECKS} -eq 1 ]]; then
  log_message 0 "Running pre-run checks"

  # Check 1a: Existence and readability of the config for the standard Cloud Run Job file.
  log_message 1 "Checking for file: ${WEEKLY_CONFIG}..."
  if [[ ! -r "${WEEKLY_CONFIG}" ]]; then
    # Print error message to standard error (>&2).
    echo "Error: Required file not found or not readable: ${WEEKLY_CONFIG}" >&2
    exit 2 # Exit the script with a non-zero status code.
  fi
  echo "File found: ${WEEKLY_CONFIG}"

  # Check 1b: Existence and readability of the config for the test Cloud Run Job file.
  log_message 1 "Checking for file: ${WEEKLY_CONFIG_TEST}..."
  if [[ ! -r "${WEEKLY_CONFIG_TEST}" ]]; then
    # Print error message to standard error (>&2).
    echo "Error: Required file not found or not readable: ${WEEKLY_CONFIG_TEST}" >&2
    exit 2 # Exit the script with a non-zero status code.
  fi
  echo "File found: ${WEEKLY_CONFIG_TEST}"


  # Check 2: Existence and readability of the second file.
  # If this a 'DV' type installation check for the second config file as well.
  if [[ ${DEPOLYMENT_TYPE} == 'DV' ]]; then
    log_message 1 "Checking for file: ${DAILY_CONFIG}..."
    if [[ ! -r "${DAILY_CONFIG}" ]]; then
      log_message 2 "Error: Required file not found " \
        "or not readable: ${DAILY_CONFIG}" >&2
      exit 3
    fi
    echo "File found: ${DAILY_CONFIG}"
  fi

  # Check 3: Existence of the GCP Service Account.
  # NOTE: The identity running this script needs
  # 'iam.serviceAccounts.get' permission.
  log_message 1 "Checking for Service Account: ${SERVICE_ACCOUNT} in " \
    "project ${PROJECT}..."

  # We run the gcloud command and check its exit status ($?).
  # We redirect stdout and stderr to /dev/null to suppress output,
  # as we only care about the exit code for this check.
  if ! gcloud iam service-accounts describe \
    "${SERVICE_ACCOUNT}" --project="${PROJECT}" > /dev/null 2>&1; then
    # If the command failed (exit code != 0), the SA likely
    # doesn't exist or permissions are missing.
    log_message 2 "Error: Service Account ${SERVICE_ACCOUNT} not found" \
      " in project ${PROJECT}, or insufficient permissions to check." >&2
    log_message 2 "This can also be caused by attempting an install in " \
      "a 'stale' Cloud Shell, close & re-open / re-authenticate and try again."
    exit 4
  fi
  echo "Service Account found: ${SERVICE_ACCOUNT}"
  echo "Pre-run Checks Passed."
  echo "Proceeding with deployment..."
else
  echo "Skipping pre-run checks"
fi


if [[ ${ACTIVATE_APIS} -eq 1 ]]; then
  log_message 0 "Activate APIs"
  # Check for active APIs.
  APIS_USED=(
    "artifactregistry"
    "cloudbuild"
    "cloudscheduler"
    "displayvideo"
    "logging"
    "run"
    "sheets"
    "storage-api"
    "tagmanager"
  )
  SERVICES=$(gcloud --project=${PROJECT} services list \
    | grep -v TITLE \
    | cut -f 2 -d' ')

  ACTIVE_SERVICES="$SERVICES"

  for api in "${APIS_USED[@]}"; do
    if [[ "${ACTIVE_SERVICES}" =~ ${api} ]]; then
      echo "${api} already active"
    else
      log_message 1 "Activating ${api}"
      gcloud services enable "${api}.googleapis.com" \
        --project="${PROJECT}" "${QUIET}"
    fi
  done
  echo "API Activation completed"
else
  echo "Skipping API activation"
fi


if [[ ${GRANT_PERMISSIONS} -eq 1 ]]; then
  log_message 0 "Grant GCP IAM Permissions"

  log_message 1 "Add Cloud Scheduler Permissions to Service Account"
  # Grant permissions for service account for creating Cloud Scheduler jobs.
  gcloud projects add-iam-policy-binding "${PROJECT}" \
      --member "serviceAccount:${SERVICE_ACCOUNT}"    \
      --role="roles/cloudscheduler.serviceAgent"      \
      --condition=None                                \
      "${QUIET}"

  log_message 1 "Add Cloud Job Invoker Permissions to Invoker Service Account"
  # Grant permissions to service account to run the Cloud Run Job(s).
  gcloud projects add-iam-policy-binding ${PROJECT}         \
      --member "serviceAccount:${INVOKER_SERVICE_ACCOUNT}"  \
      --role "roles/run.invoker"                            \
      --condition=None                                      \
      "${QUIET}"

  log_message 1 "Add Permissions for INVOKER to access GCS as Viewer"
  # Grant permissions to service account to run the Cloud Run Job(s).
  gcloud projects add-iam-policy-binding ${PROJECT}         \
      --member "serviceAccount:${INVOKER_SERVICE_ACCOUNT}"  \
      --role "roles/storage.objectViewer"                   \
      --condition=None                                      \
      "${QUIET}"

  echo "IAM permissioning completed."
else
  echo "Skipping IAM permissions."
fi


if [[ ${DELETE_OLD_INSTALL} -eq 1 ]]; then
  log_message 0 "Delete old matching GCP install components."

  echo "** WARNING ** : This section of the bid2x install MAY show errors."
  echo "This happens if the script attempts to DELETE components that do"
  echo "not exist. Therefore, if this is your first install or you are"
  echo "attempting again after a partial or failed installation please be"
  echo "aware that errors in this section can happen and do not NECESSARILY"
  echo "mean you have an invalid installation."

  # Delete old install of weekly run.
  log_message 1 "Delete old install of weekly run"
  gcloud run jobs delete ${WEEKLY_CLOUD_RUN_JOB_NAME} \
    --project="${PROJECT}"                            \
    --region="${REGION}"                              \
    "${QUIET}"

  log_message 1 "Delete old install of test run"
  gcloud run jobs delete ${WEEKLY_CLOUD_RUN_JOB_TEST} \
    --project="${PROJECT}"                            \
    --region="${REGION}"                              \
    "${QUIET}"

  # Delete old install of weekly scheduler.
  log_message 1 "Delete old install of weekly scheduler"
  gcloud scheduler jobs delete ${WEEKLY_SCHEDULER_JOB_NAME}  \
    --project="${PROJECT}"                                   \
    --location="${REGION}"                                   \
    "${QUIET}"

  if [[ ${DEPOLYMENT_TYPE} == 'DV' ]]; then
    # Delete old install of daily run.
    log_message 1 "Delete old install of daily run"
    gcloud run jobs delete "${DAILY_CLOUD_RUN_JOB_NAME}"  \
      --project="${PROJECT}"                              \
      --region="${REGION}"                                \
      "${QUIET}"

    # Delete old install of daily scheduler.
    log_message 1 "Delete old install of daily scheduler"
    gcloud scheduler jobs delete "${DAILY_SCHEDULER_JOB_NAME}" \
      --project="${PROJECT}"                                   \
      --location="${REGION}"                                   \
      "${QUIET}"
  fi

  echo "Existing GCP components deletion completed."
else
  echo "Skipping deletion of old installations"
fi



if [[ ${GCS_OPERATIONS} -eq 1 ]]; then
  log_message 0 "Create Cloud Storage Bucket"

  echo "Checking if bucket gs://${BUCKET_NAME} exists..."
  # Attempt to list the bucket.
  # 'gcloud storage ls' exits with 0 if the bucket exists, non-zero otherwise.
  # Redirect stdout and stderr to /dev/null to keep the script output clean.
  if gcloud storage ls --project="${PROJECT}" \
    "gs://${BUCKET_NAME}" >/dev/null 2>&1; then
    echo "Bucket gs://${BUCKET_NAME} already exists. "
    echo "No creation action needed."
  else
    echo "Bucket gs://${BUCKET_NAME} does not exist. Attempting to create..."
    # Bucket does not exist, so create it.
    # || exit ensures the script exits if the creation fails for any other
    #   reason (permissions, etc.).
    gcloud storage buckets create "gs://${BUCKET_NAME}" \
      --project="${PROJECT}" \
      --location="${REGION}" || exit 1
    # Exit script if creation fails unexpectedly.

    # Check if creation was successful.
    if gcloud storage ls --project="${PROJECT}" \
      "gs://${BUCKET_NAME}" >/dev/null 2>&1; then
      echo "Bucket gs://${BUCKET_NAME} created successfully."
    else
      echo "ERROR: Failed to create bucket gs://${BUCKET_NAME}"
      echo "or it's not accessible yet."
      exit 1 # Exit with an error status.
    fi
  fi

  GCS_DESTINATION_URI="gs://${BUCKET_NAME}/"

  # Copy config file(s) to the bucket.
  # --- Weekly Config File Copy to Bucket ---
  if [[ -n "$WEEKLY_CONFIG" ]]; then
    echo "Attempting to copy local file "
    echo "'${WEEKLY_CONFIG}' to '${GCS_DESTINATION_URI}'..."
    gcloud storage cp "${WEEKLY_CONFIG}" "${GCS_DESTINATION_URI}" \
      --project="${PROJECT}" \
      || { echo "ERROR: Failed to copy ${WEEKLY_CONFIG}"; exit 1; }
    echo "Successfully copied '${WEEKLY_CONFIG}'."

    # Copy test run config file to the bucket.
    gcloud storage cp "${WEEKLY_CONFIG_TEST}" "${GCS_DESTINATION_URI}" \
      --project="${PROJECT}" \
      || { echo "ERROR: Failed to copy ${WEEKLY_CONFIG}"; exit 1; }
    echo "Successfully copied '${WEEKLY_CONFIG_TEST}'."

  else
    echo "WEEKLY_CONFIG variable not defined. Skipping copy."
  fi

  if [[ ${DEPOLYMENT_TYPE} == 'DV' ]]; then
    # --- Daily Config File Copy to Bucket ---
    if [[ -n "$DAILY_CONFIG" ]]; then
      echo "Attempting to copy local file "
      echo "'${DAILY_CONFIG}' to '${GCS_DESTINATION_URI}'..."
      gcloud storage cp "${DAILY_CONFIG}" "${GCS_DESTINATION_URI}" \
        --project="${PROJECT}" \
        || { echo "ERROR: Failed to copy ${DAILY_CONFIG}"; exit 1; }
      echo "Successfully copied '${DAILY_CONFIG}'."
    else
      echo "DAILY_CONFIG variable not defined. Skipping copy."
    fi

  fi

  # The GCS portion of the install ran successfully, set the
  # flag so following sections are aware GCS is available.
  GCS_SUCCESSFUL=1
else
  GCS_SUCCESSFUL=0
fi

if [[ ${DEPLOY_JOBS} -eq 1 ]]; then
  log_message 0 "Deploy Cloud Run Job(s)"

  # Modify the passed args if we're using GCS to store them.
  if [[ ${GCS_SUCCESSFUL} -eq 1 ]]; then
    # If the GCS portion of the installer ran and was successful then
    # modify the start-up args to tell the Cloud Run Job executable
    # to load the config file(s) from the GCS bucket.
    # If the GCS portion of the installer was NOT run then the
    # original startup args will be used which loads the config file(s)
    # from the local filesystem.
    # When creating the container to run bid2x all files in the local
    # directory are zip'd up and included so the config JSON files
    # should be present to use.
    WEEKLY_ARGS="-i,gs://${BUCKET_NAME}/${WEEKLY_CONFIG}"
    WEEKLY_ARGS_TEST="-i,gs://${BUCKET_NAME}/${WEEKLY_CONFIG_TEST}"
    DAILY_ARGS="-i,gs://${BUCKET_NAME}/${DAILY_CONFIG}"
  fi

  # Deploy Cloud Run Job for Weekly update.
  log_message 1 "Deploy Cloud Run Job for Weekly update"
  gcloud run jobs deploy "${WEEKLY_CLOUD_RUN_JOB_NAME}" \
    --source .                                          \
    --tasks 1                                           \
    --max-retries 1                                     \
    --args="${WEEKLY_ARGS}"                             \
    --region "${REGION}"                                \
    --service-account="${INVOKER_SERVICE_ACCOUNT}"      \
    --project="${PROJECT}"                              \
    --task-timeout="${TASK_TIMEOUT}"                    \
    --cpu="${CPU}"                                      \
    --memory="${MEMORY}"                                \
    "${QUIET}"

  # Deploy Cloud Run Job for manual test runs.
  gcloud run jobs deploy "${WEEKLY_CLOUD_RUN_JOB_TEST}" \
    --source .                                          \
    --tasks 1                                           \
    --max-retries 1                                     \
    --args="${WEEKLY_ARGS_TEST}"                        \
    --region "${REGION}"                                \
    --service-account="${INVOKER_SERVICE_ACCOUNT}"      \
    --project="${PROJECT}"                              \
    --task-timeout="${TASK_TIMEOUT}"                    \
    --cpu="${CPU}"                                      \
    --memory="${MEMORY}"                                \
    "${QUIET}"


  if [[ ${DEPOLYMENT_TYPE} == 'DV' ]]; then
    # Deploy Cloud Run Job for Daily update for DV type installations.
    log_message 1 "Deploy Cloud Run Job for Daily update"
    gcloud run jobs deploy "${DAILY_CLOUD_RUN_JOB_NAME}" \
      --source .                                         \
      --tasks 1                                          \
      --max-retries 1                                    \
      --args="${DAILY_ARGS}"                             \
      --region "${REGION}"                               \
      --service-account="${INVOKER_SERVICE_ACCOUNT}"     \
      --project="${PROJECT}"                             \
      --task-timeout="${TASK_TIMEOUT}"                   \
      --cpu="${CPU}"                                     \
      --memory="${MEMORY}"                               \
      "${QUIET}"
  fi

  echo "Cloud Run Jobs deployment completed."
else
  echo "Skipping Cloud Run Jobs deployment"
fi


if [[ ${CREATE_SCHEDULER_JOBS} -eq 1 ]]; then
  # Construct the invocation URI for weekly scheduled job.
  log_message 0 "Create Cloud Scheduler Job(s)"

  log_message 1 "Construct weekly invocation URI"
  BASE_URL="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1"
  INVOC_PATH="/namespaces/${PROJECT}/jobs/${WEEKLY_CLOUD_RUN_JOB_NAME}:run"
  WEEKLY_INVOCATION_URI="${BASE_URL}${INVOC_PATH}"

  echo "Weekly Invocation URI: ${WEEKLY_INVOCATION_URI}"
  log_message 1 "Create weekly cloud scheduler job"

  # Create the Weekly Cloud Scheduler job.
  gcloud scheduler jobs create http "${WEEKLY_SCHEDULER_JOB_NAME}" \
    --schedule="${WEEKLY_CRON_SCHEDULE}"                           \
    --uri="${WEEKLY_INVOCATION_URI}"                               \
    --http-method=POST                                             \
    --oidc-service-account-email="${SERVICE_ACCOUNT}"              \
    --location="${REGION}"                                         \
    --time-zone="${TIMEZONE}"                                      \
    --project="${PROJECT}"                                         \
    --description="Weekly Scheduled Run of bid2x"                  \
    "${QUIET}"

  if [[ ${DEPOLYMENT_TYPE} == 'DV' ]]; then
    log_message 1 "Construct daily invocation URI"
    # Construct the invocation URI for the daily scheduled job if DV.
    BASE_URL="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1"
    INVOC_PATH="/namespaces/${PROJECT}/jobs/${DAILY_CLOUD_RUN_JOB_NAME}:run"
    DAILY_INVOCATION_URI="${BASE_URL}${INVOC_PATH}"

    echo "Daily Invocation URI: ${DAILY_INVOCATION_URI}"
    log_message 1 "Create daily cloud scheduler job"

    # Create the Daily Cloud Scheduler job.
    gcloud scheduler jobs create http "${DAILY_SCHEDULER_JOB_NAME}" \
      --schedule="${DAILY_CRON_SCHEDULE}"                           \
      --uri="${DAILY_INVOCATION_URI}"                               \
      --http-method=POST                                            \
      --oidc-service-account-email="${SERVICE_ACCOUNT}"             \
      --location="${REGION}"                                        \
      --time-zone="${TIMEZONE}"                                     \
      --project="${PROJECT}"                                        \
      --description="Daily Scheduled Run of bid2x"                  \
      "${QUIET}"

  fi

  echo "Completed creating cloud scheduler definitions."
else
  echo "Skipping Cloud Scheduler Jobs creation"
fi

echo "***********************************************************************"
echo "bid2x installer - Finished - $(date '+%a %b %d, %Y - %I:%M:%S %p %Z')"
echo "***********************************************************************"

exit 0