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

# Replace the following as needed.
SERVICE_ACCOUNT="REPLACE-SERVICE-ACCOUNT@REPLACE-PROJECT-NAME.iam.gserviceaccount.com"
PROJECT="REPLACE-PROJECT-NAME"
FUNCTION_NAME="bid2x"
REGION="northamerica-northeast1"
TRIGGER="bid2x"
SCHEDULE='0 7 * * 7'
CONFIG="config_gtm.json"
TIMEZONE="America/Toronto"
ENTRYPOINT="hello_pubsub"
ACTIVATE_APIS=1

gcloud config set project ${PROJECT}

if [ ${ACTIVATE_APIS} -eq 1 ]; then
  # Check for active APIs
  APIS_USED=(
    "artifactregistry"
    "cloudbuild"
    "cloudfunctions"
    "cloudscheduler"
    "displayvideo"
    "drive"
    "eventarc"
    "logging"
    "pubsub"
    "run"
    "sheets"
    "storage-api"
    "tagmanager"
  )
  ACTIVE_SERVICES="$(gcloud --project=${PROJECT} services list | grep -v TITLE | cut -f 2 -d' ')"
  # echo ${ACTIVE_SERVICES[@]}

  for api in ${APIS_USED[@]}; do
    if [[ "${ACTIVE_SERVICES}" =~ ${api} ]]; then
      echo "${api} already active"
    else
      echo "Activating ${api}"
      gcloud --project=${PROJECT} services enable ${api}.googleapis.com
    fi
  done
fi

# Grant permissions for the service account
gcloud projects add-iam-policy-binding ${PROJECT} \
    --member serviceAccount:${SERVICE_ACCOUNT}    \
    --role="roles/pubsub.publisher"

gcloud projects add-iam-policy-binding ${PROJECT} \
    --member serviceAccount:${SERVICE_ACCOUNT}    \
    --role="roles/pubsub.subscriber"

gcloud projects add-iam-policy-binding ${PROJECT} \
    --member serviceAccount:${SERVICE_ACCOUNT}    \
    --role="roles/cloudscheduler.serviceAgent"

gcloud projects add-iam-policy-binding ${PROJECT} \
    --member serviceAccount:${SERVICE_ACCOUNT}    \
    --role="roles/eventarc.serviceAgent"

gcloud projects add-iam-policy-binding ${PROJECT} \
    --member serviceAccount:${SERVICE_ACCOUNT}    \
    --role "roles/run.invoker"

gcloud projects add-iam-policy-binding ${PROJECT} \
    --member serviceAccount:${SERVICE_ACCOUNT}    \
    --role "roles/storage.objectViewer"

# Delete any previous setups
gcloud beta scheduler jobs delete \
  --project=${PROJECT}            \
  --quiet                         \
  --location=${REGION}            \
  ${FUNCTION_NAME}

gcloud pubsub topics delete \
  --project=${PROJECT}      \
  --quiet                   \
  ${TRIGGER}

gcloud eventarc triggers delete ${TRIGGER}  \
  --location=${REGION}                      \
  --project=${PROJECT}                      \
  --quiet

gcloud run services delete ${FUNCTION_NAME} \
  --project=${PROJECT}                      \
  --region=${REGION}                        \
  --quiet

# Create topic
gcloud pubsub topics create                           \
  --project=${PROJECT}                                \
  --quiet                                             \
  --message-storage-policy-allowed-regions=${REGION}  \
  ${TRIGGER}


if [ ! -z ${ENTRYPOINT} ]; then
  # Create and deploy the code
  # Check for the code bucket
  gsutil ls -p ${PROJECT} gs://${PROJECT}-bid2x > /dev/null 2>&1
  RETVAL=$?
  if (( ${RETVAL} != "0" )); then
    echo Destination bucket missing. Creating.
    gsutil mb -p ${PROJECT} gs://${PROJECT}-bid2x
  fi

  [ -e bid2x.zip ] && rm -f bid2x.zip >/dev/null 2>&1

  # Create the zip
  zip bid2x.zip                   \
      README.md                   \
      install.sh requirements.txt \
      bid2x_*.py                  \
      main.py auth/*.py           \
      *.json

  # Copy it up
  gsutil cp bid2x.zip gs://${PROJECT}-bid2x > /dev/null 2>&1

  RETVAL=$?
  if (( ${RETVAL} != "0" )); then
    echo Error deploying zip file!
    exit
  fi

  SOURCE="gs://${PROJECT}-bid2x/bid2x.zip"

  gcloud run deploy ${FUNCTION_NAME}      \
    --source ${SOURCE}                    \
    --function=${ENTRYPOINT}              \
    --base-image python311                \
    --service-account=${SERVICE_ACCOUNT}  \
    --region=${REGION}                    \
    --no-allow-unauthenticated

  gcloud eventarc triggers create ${TRIGGER}                              \
    --location=${REGION}                                                  \
    --destination-run-service=${FUNCTION_NAME}                            \
    --destination-run-region=${REGION}                                    \
    --event-filters="type=google.cloud.pubsub.topic.v1.messagePublished"  \
    --transport-topic=projects/${PROJECT}/topics/${TRIGGER}               \
    --service-account=${SERVICE_ACCOUNT}

  # Create scheduled jobs
  gcloud beta scheduler jobs create pubsub              \
    ${FUNCTION_NAME}                                    \
    --schedule="${SCHEDULE}"                            \
    --topic="projects/${PROJECT}/topics/${TRIGGER}"     \
    --time-zone=${TIMEZONE}                             \
    --location=${REGION}                                \
    --message-body=${CONFIG}                            \
    --project=${PROJECT}
fi
