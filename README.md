Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This is not an officially supported Google product. This project is not
eligible for the [Google Open Source Software Vulnerability Rewards
Program](https://bughunters.google.com/open-source-security).

# gTech Ads: bid2x Technical Implementation Guide

## Table of Contents

[Table of Contents](#table-of-contents)

[Introduction](#introduction)

- [Getting Access](#getting-access)
- [Solution Pieces](#solution-pieces)
- [DV360 description](#dv360-description)
- [SA360/GTM description](#sa360/gtm-description)
- [budget2x for Google Ads description](#budget2x-for-google-ads-description)

[Classic bid2x Topologies](#classic-bid2x-topologies)

- [Topology for DV360 deployment](#topology-for-dv360-deployment)
- [Topology for SA360/GTM deployment](#topology-for-sa360/gtm-deployment)
- [Topology for Google Ads (budget2x) deployment](#topology-for-google-ads-budget2x)

[Authentication](#authentication)

[Command Line Arguments](#command-line-arguments)

- [General Usage](#general-usage)
- [On/Off Toggle Arguments](#onoff-toggle-arguments)
- [Numeric Value Arguments](#numeric-value-arguments)
- [Name and File Path Arguments](#name-and-file-path-arguments)
- [Action Arguments](#action-arguments)
- [Command Line Argument Examples](#command-line-argument-examples)

    - [Example 1: Load configuration from my_config.json](#example-1-load-configuration-from-my_configjson)
    - [Example 2: Create a new custom bidding algorithm manually](#example-2-create-a-new-custom-bidding-algorithm-manually)
    - [Example 3: List custom bidding algos under a given advertiser id](#example-3-list-custom-bidding-algos-under-a-given-advertiser-id)

[Configuration File Examples](#configuration-file-examples)

- [DV360 Configuration Sample and Discussion](#dv360-configuration-sample-and-discussion)
- [SA360 and GTM Configuration Sample and Discussion](#sa360-and-gtm-configuration-sample-and-discussion)
- [SA360 Sample Configuration for lengthy output](#sa360-sample-configuration-for-lengthy-output)
- [SA360 Sample Lengthy JavaScript Output](#sa360-sample-lengthy-javascript-output)
- [SA360 Sample Configuration for compact output](#sa360-sample-configuration-for-compact-output)
- [SA360 Sample Compact JavaScript Output](#sa360-sample-compact-javascript-output)
- [budget2x Configuration](#budget2x-configuration)

[Configuration File Reference for DV360 and SA/GTM](#config-file-ref)

- [Top level configuration items](#top-level-configuration-items)
- [gtm_floodlight_list items](#gtm_floodlight_list-items)
- [Action items](#action-items)
- [Sheet configuration items](#sheet-configuration-items)
- [Zone_array configuration items](#zone_array-configuration-items)
    - [For DV360 campaigns and zones](#for-dv360-campaigns-and-zones)
    - [For GTM and SA360](#for-gtm-and-sa360)

[Implementation notes](#implementation-notes)

- [Sheets input / output](#sheets-input--output)
- [Campaigns](#campaigns)
- [Supported Line Item Types in DV360](#supported-line-item-types-in-dv360)
- [DV360 Line item Naming](#dv360-line-item-naming)
- [Frequency of Script Updates](#frequency-of-script-updates)
    - [Frequency for DV360 and SA/GTM deployments](#frequency-for-dv360-and-sagtm-deployments)
    - [budget2x on Google Ads](#budget2x-on-google-ads)

- [Start-up and call from Google Cloud Scheduler](#start-up-and-call-from-google-cloud-scheduler)
    - [Start-up for DV360 and SA/GTM deployments](#start-up-for-dv360-and-sagtm-deployments)
    - [budget2x on Google Ads](#budget2x-on-google-ads-1)

[Installation script](#installation-script)

- [Installation for DV360 and SA/GTM deployments](#installation-for-dv360-and-sagtm-deployments)
- [Installer Prerequisites](#installer-prerequisites)
- [Installer User-Definable Parameters](#installer-user-definable-parameters)
- [Main Project Parameters](#main-project-parameters)
- [Virtual Machine Environment Parameters](#virtual-machine-environment-parameters)
- [Service Account Parameters](#service-account-parameters)
- [Cloud Run Job Detail Parameters](#cloud-run-job-detail-parameters)
- [Installation Control Flags](#installation-control-flags)
- [Installation Log file](#installation-log-file)

[Log File Format](#log-file-format)

## Introduction

Our customers own a great deal of 1st party data that, traditionally, our
advertising systems have no access to. Some of this data can be potentially
useful as an input signal to allow Google advertising systems to bid more
intelligently.

This system originated when an airline wanted to use their first party data
that related to 'struggling routes' to affect change in bidding. Simply put,
they wanted our advertising systems to bid more aggressively for ad spots when
a struggling route was in play. Of course, the airline did not want to make
the struggling routes public, so they created an 'index' to use with our
provided code that allowed them to assign a bid multiplier when the index was
in a certain range. This was our "bid2index" solution.

As time went on the question was asked, "if I have an auto customer with
different campaigns for different car models, could I use up-to-date inventory
information in the same way to tailor bidding according to the models that are
actually available?" There's no use bidding for space to advertise models they
don't actually have … so why not? This was based on the same code as the
airline project and became our "bid2inventory" solution.

Continuing this train of thought: Why not empty hotel rooms? Why not number of
candy bars shipped to stores in a given area? Why not any other metrics
combined with inventory like margin to optimize profit? Indeed, why not any
number of factors that the customer might have that could have a positive
impact on the bidding? And those factors, because they're not all known
*a priori* became the 'x', the factor any given customer would provide in
an attempt to optimize their bidding. And that's how it became bid2x.
 
## Getting Access

At the time of writing this bid2x is available at this location:
[https://professional-services.googlesource.com/solutions/bid2x/]
(https://professional-services.googlesource.com/solutions/bid2x/)
Depending on what group you are in within Google or if you don't have an
@[google.com](http://google.com) email address you may need to be added to
a group to obtain access. Please contact the authors/stakeholders of bid2x to
see about having your email added to the correct Google Group to obtain access.
Once you have access you can clone the code using 'git' commands.
 
## Solution Pieces

What's in a bid2x solution? Based on the information provided in the
introduction your first guess would probably be 'first party data'. But there's
more, pieces are needed to coordinate passing this information to our
advertising platforms in an intelligent way. The sections below will break down
the solution separately for each implementation type.
 
#### DV360 description

The bid2x solution for DV360 uses Custom Bidding scripts to translate the
customer's first party data into the desired impact on Line Items within a set
of Campaigns. The bid2x solution supports multiple campaigns and many line
items per campaign.
 
#### SA360/GTM description

The bid2x solution for SA360 makes use of dynamic HTML tags in Google Tag
Manager. Like the DV360 solution the implementation for SA360 makes use of 1st
party data, but instead of communicating this information directly with SA360,
the solution makes use of Google Tag Manager to indirectly deliver the
information.
 
#### budget2x for Google Ads description

The bid2x solution for Google Ads, called
'budget2x'
is a different approach.
The budget2x solution uses the Google Ads 'Ads Script' functionality to join
1st party data to the budgets applied to a set of campaigns. Bidding, per se,
in Google Ads is controlled at a macro level by selecting a bidding strategy
and there currently aren't API-based controls for bidding like in DV360 or
SA360. The PMAX campaign bidding strategy has been proving itself to be robust
and aggressive in spending, therefore, in order to direct Google Ads based
campaigns with 1st party data the decision has to be made to adjust budgets.
Typically the budget2x script is implemented to feed off of updating 1st party
data and affect changes to the budgets of campaigns under it's control on a
daily basis.
The budget2x solution utilizes typescript (a.k.a Ads Script) code that is added
to an account in Google Ads and then activated. The script is linked to a
Google Sheet where daily budgets are calculated. Usually the Sheet is linked
to a database table or other source of information to keep the budgets current
and relevant. A sample budget2x spreadsheet to copy is [available here]
(https://docs.google.com/spreadsheets/d/1PIxTrwMc3QBhv_1vbjt4B-cNaD7MucmHWk-gzQhhjRA/edit).

At this point reviewing a few topology diagrams of the solution would be
beneficial…

## Classic bid2x Topologies

#### Topology for DV360 deployment

The pieces for a bid2x solution using DV360 are often arranged as follows:
![bid2x DV Topology](./img/bid2x_dv_topology.png)

The major components are:

1. The bid2x Python code that runs in Google Cloud Platform, usually deployed
in Cloud Run / Cloud Functions. This single codebase is the same for DV360
and SA360/GTM implementations whether it is reads/writes to the Google Sheet or
read/write API interactions with DV or GTM.
2. The bid2x control Google Sheet coordinates data between various data sources
and prepares it for use in the bid2x system. For DV360, the control sheet is a
landing pad for campaign-specific data with various campaigns split between
sheet tabs and individual tabs containing all the participating line items in
that campaign.
3. GCP's BigQuery is primarily used as an input source for customer first
party data.
4. For the DV360 implementation the customer's trafficking information
(campaigns, line items, custom bidding scripts) are interacted with via the
DV360 API.
5. As an alternative to BQ as a mechanism for getting customer first party data
into the Google Sheet other mechanisms and data stores are supported through
Google Sheet connectors.

The noted data flows within the diagram are:

1. The bid2x Python app interacts with DV360 to create custom bidding algorithms
and scripts, to re-write custom bidding scripts, to read line items within a
campaign, and to assign line items to uploaded custom bidding scripts.
2. The bid2x Python app communicates with the Google Sheet to write line item
information to various tabs and to make a record of the latest action it has
taken. Additionally, the Python script reads the bidding information PER line
item across tabs to create a separate bidding script per campaign to allow
bidding prioritizing utilizing first party data.
3. The Google Sheet is updated with first party data from BigQuery. Typically
this data is scheduled to update daily. The raw data from this update ends up
in a 'raw' data tab and then is combined with line item and other data on the
campaign tabs.
4. As an alternative to using BQ for first party data input any other connector
mechanism that Sheets supports is a candidate to bring in data.

#### Topology for SA360/GTM deployment

The topology for a deployment that targets SA360 involves the use of Google Tag
Manager to influence SA360. Here's a sample topology:
![bid2x DV Topology](./img/bid2x_gtm_topology.png)

1. The bid2x Python code that runs in Google Cloud Platform, usually Cloud Run/
Cloud Functions. This single codebase is the same for DV360 and SA360/GTM
implementations whether it is reads/writes to the Google Sheet or read/write
API interactions with DV or GTM.
2. The bid2x control Google Sheet coordinates data between various data sources
and prepares it for use in the bid2x system. For SA360/GTM, the control sheet
is a landing pad for campaign-specific data with individual tabs containing all
the first party data for that campaign.
3. GCP's BigQuery is primarily used as an input source for customer first party
data.
4. For the SA360/GTM implementation Google Tag Manager is interfaced with over
API to update a tag being used to prioritize bidding.
5. As an alternative to BQ as a mechanism for getting customer first party data
into the Google Sheet other mechanisms and data stores are supported through
Google Sheet connectors.

The noted data flows within the diagram are:

1. First party data from BigQuery is brought into a separate tab in Google
Sheets and then distributed amongst the correct campaign / zone tabs, as needed.
2. As an alternative to BQ, first party data can be brought into Google Sheets
through any other mechanism that is supported. However, is should be noted
that the BQ connector supports timed updates and is convenient for at least that
reason.
3. Data from the control Google Sheet is gathered by the cloud-based executable
for bid2x and converted into a JavaScript routine that assigns a relative value
to a variable based on the 1st party data and the current state of the
environment when it is run.
4. The JavaScript routine is uploaded to Google Tag Manager to the correct
variable. As the end customer navigates the site, the JavaScript routine will
run and evaluate to a value based on algorithm and other variables referenced
in the data layer. The resultant will be available to SA360 as a value to
optimize on.

#### Topology for Google Ads (budget2x) deployment

The topology of the pieces in a budget2x solution using Google Ads is shown
in this diagram:
![budget2x Google Ads Topology](./img/budget2x_topo.png)
Typically, 'real-time' or up-to-date data is provided to BigQuery (A) and then
shows up in Google Sheets (B) through use of a Data Connector. From there the
Sheet uses an 'Extract' of the data in order to perform manipulations of the
values (normalization, scaling, etc.) and it made available on one or more
specific sheets within the spreadsheet (C).
When the timer kicks within Google Ads the budget2x code runs, connects to the
Google Sheet (D) and uses the data to set budgets. The sample budget2x
spreadsheet walks through how to connect multiple child MCCs through a KeySheet
by deploying the code at a parent or manager MCC level giving the script access
to multiple child MCCs, each with their own set of campaigns.

## Authentication
 
As can be seen from the topology section there are a number of data flows that
require explicit access. The bid2x Python app running with GCP runs with the
identity of a service account that is specific to each deployment. This
account needs to be granted the following rights:

* Cloud Run Jobs Invoker: ROLE: roles/run.invoker
* Cloud Scheduler Service Agent: ROLE: roles/cloudscheduler.serviceAgent
* Cloud Storage Object Viewer: ROLE: roles/storage.objectViewer

Enabled API & Service:

* Google Sheets API
* Display & Video 360 API (for DV deployments)
* Google Tag Manager API (for SA/GTM deployments)

Budget2x has a leaner set of requirements, since all the processing is done
within Google Ads the only authentication of note is to ensure that the person
that activates the script has the rights to view the Google Sheet being used
to coordinate the first-party data.

## Command Line Arguments

This section provides a guide to the command-line arguments used by the Bid2X
script for DV360 and SA360/GTM. There are no command-line arguments for
budget2x.

The arguments allow you to customize the script's behavior, specify
input/output files, define IDs, and control various actions related to managing
custom bidding algorithms in DV360.

The script uses argparse with ArgumentDefaultsHelpFormatter, meaning that if
you run the script with the \-h or \--help flag, you will see these
descriptions along with their default values.

### **General Usage**

To use these arguments, you would typically run the script from your command
line like so:

```Bash
python main.py [options]
```
For example, to run in debug mode and specify a particular advertiser ID:

```Bash
python main.py --debug --advertiser 12345
```

However, most choose to drive the functionality of bid2x from associated
JSON files containing all the selected options. In this case invoke bid2x
like this:

```Bash
python main.py -i <option_filename.json>
```

Should you choose to employ the command like arguments they are documented
below, grouped by their function.h

### **On/Off Toggle Arguments**

These arguments are boolean flags. Including the flag sets the option to True.
If the flag is omitted, it defaults to False (unless the default is explicitly
stated otherwise by the bid2x\_var module's initial settings, though
action='store\_true' typically implies a default of False for the argument
itself being present).

* **\-aa, \--alt\_algo**
  * **Description**: Use alternate algorithm.
  * **Default**: False (as implied by action='store\_true' and typical
  initial state in bid2x\_var.ALTERNATE\_ALGORITHM).
* **\-d, \--debug**
  * **Description**: Run script in debug mode. This enables the first
  level of verbosity for output.
  * **Default**: False (as implied by action='store\_true' and typical
  initial state in bid2x\_var.DEBUG).
* **\-c, \--clear\_onoff**
  * **Description**: On update of the sheet, overwrite the Yes/No custom
  bidding button based on a pattern.
  * **Default**: False (as implied by action='store\_true' and typical initial
  state in bid2x\_var.CLEAR\_ONOFF).
* **\-dp, \--defer\_pattern**
  * **Description**: When set to true, the script will NOT use the Line Item
  (LI) name pattern to set the rule on/off.
  * **Default**: False (as implied by action='store\_true' and typical initial
  state in bid2x\_var.DEFER\_PATTERN).
* **\-vv, \--verbose**
  * **Description**: Run script in trace mode. This enables the top level of
  verbosity for output (more detailed than debug).
  * **Default**: False (as implied by action='store\_true' and typical
  initial state in bid2x\_var.TRACE).

### **Numeric Value Arguments**

These arguments require a numerical value. If not provided, they will use a
predefined default from the bid2x\_var module.

* **\-a ADVERTISER, \--advertiser ADVERTISER**
  * **Description**: Pass a new advertiser ID to be used by the script.
  * **Type**: Integer
  * **Default**: Value from bid2x\_var.ADVERTISER\_ID. (100000)
* **\-b ATTRIBUTE, \--attribute ATTRIBUTE**
  * **Description**: Pass a new Model Attribute ID.
  * **Type**: Integer
  * **Default**: Value from bid2x\_var.ATTR\_MODEL\_ID. (0)
* **\-bh BIDDING\_HIGH, \--bidding\_high BIDDING\_HIGH**
  * **Description**: Set the bidding factor high limit.
  * **Type**: Integer
  * **Default**: Value from bid2x\_var.BIDDING\_FACTOR\_HIGH. (1000.0)
* **\-bl BIDDING\_LOW, \--bidding\_low BIDDING\_LOW**
  * **Description**: Set the bidding factor low limit. (Note: The original
  help text mentions "high limit", which might be a typo. It likely refers
  to the low limit.)
  * **Type**: Integer
  * **Default**: Value from bid2x\_var.BIDDING\_FACTOR\_LOW. (0.5)
* **\-g ALGORITHM, \--algorithm ALGORITHM**
  * **Description**: Specify the custom bidding algorithm ID that you want
  to update or interact with.
  * **Type**: Integer
  * **Default**: Value from bid2x\_var.CB\_ALGO\_ID. (1000000)
* **\-p PARTNER, \--partner PARTNER**
  * **Description**: Specify the DV360 Partner ID to use.
  * **Type**: Integer
  * **Default**: Value from bid2x\_var.PARTNER\_ID. (100000)

### **Name and File Path Arguments**

These arguments expect string values, typically for names, file paths, or
identifiers. Default values are sourced from the bid2x\_var module.

* **\-f FLOODLIGHT, \--floodlight FLOODLIGHT**
  * **Description**: Pass a new floodlight ID list for the Custom Bidding (CB)
  script. The list should be provided as a comma-separated string of integers
  (e.g., "123,456,789").
  * **Default**: Value from bid2x\_var.FLOODLIGHT\_ID\_LIST.
  ('1000001,1000002')
* **\-i INPUT\_FILE, \--input\_file INPUT\_FILE**
  * **Description**: Specify the JSON file from which to load the configuration.
  * **Default**: Value from bid2x\_var.INPUT\_FILE. (None)
* **\-j JSON\_FILE, \--json\_file JSON\_FILE**
  * **Description**: Specify the JSON authentication filename to use for
  API access.
  * **Default**: Value from bid2x\_var.JSON\_AUTH\_FILE. (client-secret.json)
* **\-l LAST\_UPLOAD, \--last\_upload LAST\_UPLOAD**
  * **Description**: Specify the file that contains information about the last
  successfully uploaded script. This is typically a prefix, and the script
  might append other identifiers to it. ('last\_upload')
  * **Default**: Value from bid2x\_var.CB\_LAST\_UPDATE\_FILE\_PREFIX.
* **\-lp LI\_PATTERN, \--li\_pattern LI\_PATTERN**
  * **Description**: Define the line item string pattern to match.
  * **Default**: \*bid-to-x\* (as specified by
  bid2x\_var.LINE\_ITEM\_NAME\_PATTERN). (bid-to-x)
* **\-na ALGO\_NAME, \--algo\_name ALGO\_NAME**
  * **Description**: Set the new custom bidding algorithm's internal name
  in DV360.
  * **Default**: Value from bid2x\_var.NEW\_ALGO\_NAME. (bid2x)
* **\-nd ALGO\_DISPLAY\_NAME, \--algo\_display\_name ALGO\_DISPLAY\_NAME**
  * **Description**: Set the new custom bidding algorithm's display name in
  DV360. If the name includes spaces, enclose it in quotes
  (e.g., "My New Algorithm").
  * **Default**: Value from bid2x\_var.NEW\_ALGO\_DISPLAY\_NAME. (bid2x)
* **\-s SERVICE\_ACCOUNT, \--service\_account SERVICE\_ACCOUNT**
  * **Description**: Specify the service account email to use for
  authentication. This typically follows the format:
  name@\<gcp\_project\>.iam.gserviceaccount.com.
  * **Default**: Value from bid2x\_var.SERVICE\_ACCOUNT\_EMAIL.
  (bid-to-x@client-gcp.iam.gserviceaccount.com)
* **\-t TMP, \--tmp TMP**
  * **Description**: Specify the full path location for a temporary file
  prefix. The script will use this prefix for creating temporary files.
  * **Default**: Value from bid2x\_var.CB\_TMP\_FILE\_PREFIX. (/tmp/cb\_script)
* **\-z ZONES, \--zones ZONES**
  * **Description**: Specify the sales zones to process. This might be a
  comma-separated list or a specific format expected by the script.
  * **Default**: Value from bid2x\_var.ZONES\_TO\_PROCESS. (c1,c2,c3,c4,c5)

### **Action Arguments**

These arguments are boolean flags that instruct the script to perform a
specific action. Only one action should typically be specified per script
execution.

* **\-ac, \--action\_create**
  * **Description**: Action to run: Create a new custom bidding algorithm.
  * **Default**: False (as implied by action='store\_true' and typical initial
  state in bid2x\_var.ACTION\_CREATE\_ALGORITHM).
* **\-ah, \--action\_update\_spreadsheet**
  * **Description**: Action to run: Update the spreadsheet with values
  retrieved from DV360.
  * **Default**: False (as implied by action='store\_true' and typical initial
  state in bid2x\_var.ACTION\_UPDATE\_SPREADSHEET).
* **\-al, \--action\_list\_algos**
  * **Description**: Action to run: List all available custom bidding
  algorithms.
  * **Default**: False (as implied by action='store\_true' and typical initial
  state in bid2x\_var.ACTION\_LIST\_ALGOS).
* **\-ar, \--action\_remove**
  * **Description**: Action to run: Remove a custom bidding algorithm. This
  action should be used in conjunction with the \-g (or \--algorithm) option to
  specify which algorithm to remove.
  * **Default**: False (as implied by action='store\_true' and typical initial
  state in bid2x\_var.ACTION\_REMOVE\_ALGORITHM).
* **\-as, \--action\_list\_scripts**
  * **Description**: Action to run: List the custom bidding scripts associated
  with the selected algorithm (use with \-g or \--algorithm).
  * **Default**: False (as implied by action='store\_true' and typical initial
  state in bid2x\_var.ACTION\_LIST\_SCRIPTS).
* **\-at, \--action\_test**
  * **Description**: Action to run: Execute a test of new or specific
  functionality within the script.
  * **Default**: False (as implied by action='store\_true' and typical initial
  state in bid2x\_var.ACTION\_TEST).
* **\-au, \--action\_update**
  * **Description**: Action to run: Update an existing custom bidding script.
  * **Default**: False (as implied by action='store\_true' and typical initial
  state in bid2x\_var.ACTION\_UPDATE\_SCRIPTS).

This comprehensive list should help in utilizing the BidToX script effectively
by providing control over its various parameters and actions directly from the
command line.
 
## Command Line Argument Examples

This section gives some examples of calling the bid2x python script with
different arguments.
 
### Example 1: Load configuration from my_config.json

#### Command example:
```bash
python main.py -i my_config.json
```
#### Discussion:
Notice that in this command THE ONLY argument is \-i to load the named config
file. This is the typical use case putting ALL the other settings for the
project in the config file. It is not recommended to combine command line
arguments and configuration file settings as, at this time, precedence between
the two has yet to be verified in ALL calling cases.

Configuration files can also be loaded from a GCS bucket using the
gs://\<bucket\>/filename.json syntax when passing the filename to the
\-i / \--input\_file argument.
 
### Example 2: Create a new custom bidding algorithm manually

#### Command example:
```bash
python main.py -p 1234 -a 5678 -na my_algorithm -nd my_algorithm --action_create
```
#### Discussion:
For partner '1234' and advertiser '5678' this command will create a new custom
bidding algorithm with internal and external name 'my\_algorithm'.

### Example 3: List custom bidding algos under a given advertiser id

#### Command example:
```bash
python main.py -p 1234 -a 5678 -al
```

#### Discussion:
This action command (\-al) is equivalent to \--action\_list\_algos and lists
all the custom bidding algorithms under advertiser id 5678 for partner id
1234\. This command is a nice passive manner in which to double check
connectivity to DV360 from the command line.
 
## Configuration File Examples
 
### DV360 Configuration Sample and Discussion

Below is a sample configuration file for a DV360 deployment.

```JSON
{
    "scopes": [
      "https://www.googleapis.com/auth/display-video",
      "https://www.googleapis.com/auth/spreadsheets"
    ],
    "api_name": "displayvideo",
    "api_version": "v3",
    "platform_type": "DV",
    "sheet": {
      "sheet_id": "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGH",
      "sheet_url": "https://docs.google.com/spreadsheets/d/abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGH/edit",
      "json_auth_file": "client-secret.json",
      "column_status": "A",
      "column_lineitem_id": "B",
      "column_lineitem_name": "C",
      "column_lineitem_type": "D",
      "column_campaign_id": "E",
      "column_advertiser_id": "F",
      "column_custom_bidding": "K",
      "debug": false,
      "trace": false,
      "clear_onoff": false
    },
    "zone_array": [
      {
        "name": "C1",
        "campaign_id": 66666666,
        "advertiser_id": 2222222,
        "algorithm_id": 5555555,
        "cb_algorithm": "",
        "debug": true,
        "trace": false,
        "update_row": 3,
        "update_col": 2,
        "test_row": 3,
        "test_col": 4
      },
      {
        "name": "C2",
        "campaign_id": 11111111,
        "advertiser_id": 2222222,
        "algorithm_id": 3333333,
        "cb_algorithm": "",
        "debug": true,
        "trace": false,
        "update_row": 4,
        "update_col": 2,
        "test_row": 4,
        "test_col": 4
      }
    ],
    "action_list_algos": false,
    "action_list_scripts": false,
    "action_create_algorithm": false,
    "action_update_spreadsheet": false,
    "action_remove_algorithm": false,
    "action_update_scripts": false,
    "action_test": true,
    "debug": true,
    "trace": false,
    "clear_onoff": false,
    "defer_pattern": true,
    "alternate_algorithm": false,
    "new_algo_name": "bid2Inventory",
    "new_algo_display_name": "bid2Inventory",
    "line_item_name_pattern": "bid-to-inventory",
    "json_auth_file": "client-secret.json",
    "cb_tmp_file_prefix": "/tmp/cb_script",
    "cb_last_update_file_prefix": "last_upload",
    "partner_id": 999999,
    "advertiser_id": 8888888,
    "cb_algo_id": 777777,
    "service_account_email": "service_account@project_name.iam.gserviceaccount.com",
    "zones_to_process": "C1,C2",
    "floodlight_id_list": [
      1111111,
      2222222
    ],
    "attr_model_id": 0,
    "bidding_factor_high": 1000,
    "bidding_factor_low": 0
}
```
Let's break down this configuration file through a number of bullet points:

* This is a bid2x configuration file for a DV360 deployment ("platform\_type":
"DV"),
* This 'control sheet' the CSE and end-user will use to see what's going on is
([https://docs.google.com/spreadsheets/d/abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGH/edit]
(https://docs.google.com/spreadsheets/d/abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGH/edit))
and is clearly fake as that's a made up URL with the letters a-z, the numbers
0-9, and then A-H making up the ID. It is intended to be replaced with a real
URI based upon a spreadsheet you clone from an existing template.
* During operation it uses a service account as defined here:
("service\_account\_email":
"service\_account@project\_name[.iam.gserviceaccount.com], again just a
placeholder intended to be replaced with a real value.
* The partner ID for the deployment is defined here ( "partner\_id": 999999 ),
again values the need to be replaced for your deployment. The top-level values
for advertiser ID and custom bidding algorithm ID ("advertiser\_id": 8888888,
"cb\_algo\_id": 777777\) are not for use when using the 'zone' objects as
those objects have their own definition of advertiser\_id and algorithm\_id.
They are used for some of the lesser used ACTIONS like 'action\_list\_scripts'
and 'action\_remove\_algorithm' that operate without going into the zone\_array.
* There are two "zones". In Bid2x, at least for a DV360 deployment, a zone is
synonymous with a 'campaign'. You can tell there are 2 zones being used in
two ways. First, the value for 'zones\_to\_process' contains two values
("zones\_to\_process": "C1,C2") and in the defined 'zone\_array' there is a
list of 2 object, each with a .name corresponding to either "C1" or "C2". Of
course, you can DEFINE a zone in the zone\_array but choose not to operate on
that zone by omitting it from the "zones\_to\_process" variable.
* Looking more closely at the zone object "C2" it is defined to operate within
a given advertiser and campaign, using a specific custom bidding algorithm id
( "campaign\_id": 11111111 ,"advertiser\_id": 2222222, "algorithm\_id":
3333333). Once again these number are placeholders that need to be updated
with specifics from your implementation.
* The OAuth file downloaded from GCP is client-secret.json ("json\_auth\_file":
"client-secret.json") that will be looked for LOCALLY (i.e. not in the GCP
bucket). That is, at the time of writing of this document the expectation is
that this file is available in the local directory during installation as it
will be zipped up and copied to the image made by Cloud Build during the
deployment of the Cloud Run Jobs image. There is \*some\* consideration being
given to making this file available in the GCS bucket but we have found that
it doesn't change much (if at all) during the project's lifetime so there is
minor benefit to having it in a location like GCS where it can be changed
easily.
* The generated Custom Bidding Algorithms made by this configuration will be
actioned over the two floodlights defined in the variable floodlight\_id\_list
that currently contains placeholders to floodlight ids:
("floodlight\_id\_list": \[1111111,2222222\])
* And last but not least, what will this config actually DO? Look at the
'action' variables to determine that:
  * "action\_list\_algos": false,
  * "action\_list\_scripts": false,
  * "action\_create\_algorithm": false,
  * "action\_update\_spreadsheet": false,
  * "action\_remove\_algorithm": false,
  * "action\_update\_scripts": false,
  * "action\_test": true,
* In this case the action is set to perform a 'test'. A test in bid2x
generates the script and outputs it to the spreadsheet. For a DV installation
the output goes to the tab 'CB\_Scripts' in the spreadsheet. For a GTM/SA360
installation the output goes to the 'JS\_Scripts' tab in the spreadsheet.
However, in this case recall that the spreadsheet id and url were both just
placeholders, and the values for the zones and advertiser and more were also
just placeholders… so actually running this config code will probably just
throw an error for connecting to an invalid advertisers or opening a
spreadsheet that doesn't exist.
* However, the action\_test verb in the config is a great method to test
your configuration without making any write-backs to either DV or GTM.
* For a **DV** installation the weekly run config should have its
action\_update\_scripts set to true.
* For a **DV** installation the daily run config should have its
action\_update\_spreadsheet set to true.

### SA360 and GTM Configuration Sample and Discussion
 
#### SA360 Sample Configuration for lengthy output

Below is a sample configuration file for an SA360/GTM deployment.

```json
{
    "scopes": [
        "https://www.googleapis.com/auth/tagmanager.edit.containerversions",
        "https://www.googleapis.com/auth/tagmanager.edit.containers",
        "https://www.googleapis.com/auth/tagmanager.publish",
        "https://www.googleapis.com/auth/tagmanager.readonly",
        "https://www.googleapis.com/auth/tagmanager.delete.containers",
        "https://www.googleapis.com/auth/spreadsheets"
    ],
    "api_name": "tagmanager",
    "api_version": "v2",
    "platform_type": "GTM",
    "sheet": {
      "sheet_id": "1FqujqXpWSU7tbIjKIRTYKhgguScy4kPBbGjQ2IkoyIw",
      "sheet_url": "https://docs.google.com/spreadsheets/d/1FqujqXpWSU7tbIjKIRTYKhgguScy4kPBbGjQ2IkoyIw/edit",
      "json_auth_file": "gtm_auth_file.json",
      "debug": true
    },
    "zone_array": [
      {
        "name": "GTM_T1",
        "account_id": 1234567890,
        "container_id": 987654321,
        "workspace_id": 987,
        "variable_id": 123,
        "debug": true,
        "update_row": 3,
        "update_col": 2,
        "test_row": 3,
        "test_col": 4
      }
    ],
    "debug": true,
    "trace": false,
    "json_auth_file": "gtm_auth_file.json",
    "service_account_email": "service_account@project_name.iam.gserviceaccount.com",
    "gtm_account_id": 999999,
    "gtm_container_id": 8888888,
    "gtm_workspace_id": 1,
    "gtm_variable_id": 1,
    "gtm_preprocessing_script": "var customPageName = {{Custom - pageName}};",
    "gtm_postprocessing\_script": "",
    "gtm_floodlight_list": [
      {
        "floodlight_name": "Floodlight_1",
        "floodlight_condition": "{{Event}} == 'Floodlight - BidtoX|Type1'",
        "per_row_condition": "{{getLocation}} == '#getLocation#' && {{getVehicleModel}} == '#getVehicleModel#'",
        "total_var": "conversion_var_default_value_1"
      },
      {
        "floodlight_name": "Floodlight_2",
        "floodlight_condition": "{{Event}} == 'Floodlight - BidtoX|Type2'",
        "per_row_condition": "{{getLocation}} == '#getLocation#' && {{sales}} == '#localSalesperson#'",
        "total_var": "conversion_var_default_value_2"
      }
  ],
    "value_adjustment_column_name": "Index",
    "index_low_column_name": "INDEX_LOW",
    "index_high_column_name": "INDEX_HIGH",
    "zones_to_process": "GTM_T1",
    "action_update_scripts": true,
    "action_test": false
  }
```
Breaking down this configuration:

* there is a single zone that points to a specific variable within a
workspace, within a container, owned by an account. (There are a lot of IDs
and often it is helpful to look at the GTM web UI URI in order to get some
of them).
* Specifically, for this contrived example, account 123467890 will have
container 12345678 and workspace 123\. Within this there is a variable
whose ID is 1234 that is expected to be a "Custom JavaScript" type variable
that already exists.
* This variable will receive JavaScript code dynamically generated by bid2x
that corresponds to 1st party data that is held within the associated
spreadsheet.
* The gtm\_floodlight\_list is an array of objects with the following string
properties:
  * "floodlight_name", Required. The name of the floodlight.,
  * "floodlight_condition", Optional. The EXACT clause that will be used in
  the generated JavaScript code to determine if this floodlight is happening.
  If no string is provided the system will assume that the string
  "{{Event}} == <'floodlight_name'>" is sufficient to detect this condition.
  Upon entering the created 'if-clause' the system will automatically generate
  a statement to set the default conversion value based on the 'total\_var'
  setting for this floodlight.
  * "per_row_condition": Once a floodlight has been determined a set of
  inner-conditionals needs to be generated
  * The general form of the per\_row\_condition is
  "{{getVariable1_DL}} == '#getVar1#' && {{getVariable2_DL}} == '#getVar2#'".
  Items contained in double curly brackets are the GTM standard way of access
  data layer variables. Items contained in \#'s are replaced in the output
  with content from the data source (Google Sheets) referred to in the variable
  sheet: sheet\_id and sheet\_url and whose tab name is the name of the zone.
  In GTM implementations there is often a single zone defined and multiple
  floodlights defined under gtm\_floodlight\_list.
  * "total_var": "conversion_var_default_value_1"
* The name of the Sheets tab containing the 1st party data to be read in needs
to match the name of the zone, in this case "GTM_T1". The columns in this
spreadsheet needs to have headers according to data that needs to be filled in
between \#'s. So in this example there needs to be a column with header
'getLocation' and 'getVehicleModel'. There also needs to be a column header
matching the "value_adjustment_column_name", in this case 'Index'.
* More specifically, a column labelled 'getLocation' is expected to hold
values to be used when generating the per_row_condition for this specific
floodlight.
* This is repeated with continuing 'else if' statements under the rows are
complete. This is all within a single floodlight. If there are multiple
floodlights defined then this is repeated for each floodlight event.
* For example, let's take the above configuration and a spreadsheet with a
"GTM_T1" tab containing the following data:

| getLocation | getVehicleModel | localSalesperson | numberCoffees | Index |
| :---- | :---- | :---- | :---- | :---- |
| Oklahoma | Sedan | Biff | 9 | 1.2 |
| Oklahoma | Sports | Dan | 2 | 1.1 |
| Oklahoma | SUV | Jan | 3 | 0.9 |
| Texas | Sedan | Phil | 4 | 0.6 |
| Texas | Sports | Alice | 5 | 1.0 |
| Texas | SUV | Bob | 7 | 1.4 |
| New York | Sedan | Rodigo | 1 | 1.1 |
| New York | Sports | Allison | 3 | 1.05 |
| New York | SUV | Robin | 8 | 1.0 |

#### SA360 Sample Lengthy JavaScript Output
* The spreadsheet would be read and would create the following JavaScript code
to update the GTM variable:

```javascript
function () {
    if ( {{Event}} == 'Floodlight - BidtoX|Type1' ) {

        var adjusted_value = {{conversion_var_default_value_1}};

        if ({{getLocation}} == 'Oklahoma' && {{getVehicleModel}} == 'Sedan') {
            adjusted_value *= 1.2; }
        else if ({{getLocation}} == 'Oklahoma' && {{getVehicleModel}} == 'Sports') {
            adjusted_value *= 1.1; }
        else if ({{getLocation}} == 'Oklahoma' && {{getVehicleModel}} == 'SUV') {
            adjusted_value *= 0.9; }
        else if ({{getLocation}} == 'Texas' && {{getVehicleModel}} == 'Sedan') {
            adjusted_value *= 0.6; }
        else if ({{getLocation}} == 'Texas' && {{getVehicleModel}} == 'Sports') {
            adjusted_value *= 1.0; }
        else if ({{getLocation}} == 'Texas' && {{getVehicleModel}} == 'SUV') {
            adjusted_value *= 1.4; }
        else if ({{getLocation}} == 'New York' && {{getVehicleModel}} == 'Sedan') {
            adjusted_value *= 1.1; }
        else if ({{getLocation}} == 'New York' && {{getVehicleModel}} == 'Sports') {
            adjusted_value *= 1.05; }
        else if ({{getLocation}} == 'New York' && {{getVehicleModel}} == 'SUV') {
            adjusted_value *= 1.0; }
    }
    else if ( {{Event}} == 'Floodlight - BidtoX|Type2' ) {

        var adjusted_value = {{conversion_var_default_value_2}};

        if ({{getLocation}} == 'Oklahoma' && {{sales}} == 'Biff') {
            adjusted_value *= 1.2; }
        else if ({{getLocation}} == 'Oklahoma' && {{sales}} == 'Dan') {
            adjusted_value *= 1.1; }
        else if ({{getLocation}} == 'Oklahoma' && {{sales}} == 'Jan') {
            adjusted_value *= 0.9; }
        else if ({{getLocation}} == 'Texas' && {{sales}} == 'Phil') {
            adjusted_value *= 0.6; }
        else if ({{getLocation}} == 'Texas' && {{sales}} == 'Alice') {
            adjusted_value *= 1.0; }
        else if ({{getLocation}} == 'Texas' && {{sales}} == 'Bob') {
            adjusted_value *= 1.4; }
        else if ({{getLocation}} == 'New York' && {{sales}} == 'Rodrigo') {
            adjusted_value *= 1.1; }
        else if ({{getLocation}} == 'New York' && {{sales}} == 'Allison') {
            adjusted_value *= 1.05; }
        else if ({{getLocation}} == 'New York' && {{sales}} == 'Robin') {
            adjusted_value *= 1.0; }
    }

    return adjusted_value;
}
```

* Notice that the external structure is a conditional walking the different
floodlight names while the internal sets the 'adjusted\_value' to the original
'revenue' for this floodlight and then walks another conditional structure to
potentially make changes to that value. Also notice that the internal if/else
if structure is EXACTLY THE SAME within each different floodlight, just the
revenue source changes.
* In general the format following this format:

```javascript
              if ({{Event}} == {{Floodlight_Item_n}}) {

              adjusted_value = {{Revenue_Item_n}}
              if ({{var1}} = var1_value && {{var2}} == var2_value) then {
              adjusted_value *= index_from_row }
              … (repeat for each row in spreadsheet)

              }... (repeat for each configured floodlight)
```

* Notice that the spreadsheet contained an additional (superfluous) column.
In the example this was labelled 'numberCoffees'. The bid2x code just grabs
all the data from the sheet as a Pandas dataFrame and then asks for content by
the name of the field. The fields that are important are put into the
configuration file in the per\_row\_condition and
value\_adjustment\_column\_name items. So it doesn't matter if there are extra
columns as long as the needed ones exist. And this is important because often
the index is a calculated number based on inventory, margin, time of year,
etc. etc. etc. So the emphasis is to get the first party data into Sheets and
then do whatever transformation necessary to get it into a finalized column
for use with bid2x.
* Finally, the action\_update\_scripts is set to true, so when this
configuration file is executed by the Cloud Scheduler (typically using the
'weekly run' config) it will generate the function as above and update the
GTM variable.
 
#### SA360 Sample Configuration for compact output

Another way to generate a more compact JavaScript function is to use the
keyword 'lookup' in the 'per\_row\_condition' section of the
gtm\_floodlight\_list. Here's an example configuration:

```json
{
    "scopes": [
      "https://www.googleapis.com/auth/tagmanager.edit.containerversions",
      "https://www.googleapis.com/auth/tagmanager.edit.containers",
      "https://www.googleapis.com/auth/tagmanager.publish",
      "https://www.googleapis.com/auth/tagmanager.readonly",
      "https://www.googleapis.com/auth/tagmanager.delete.containers",
      "https://www.googleapis.com/auth/spreadsheets"
    ],
    "api_name": "tagmanager",
    "api_version": "v2",
    "platform_type": "GTM",
    "sheet": {
      "sheet_id": "1FqujqXpWSU7tbIjKIRTYKhgguScy4kPBbGjQ2IkoyIw",
      "sheet_url": "https://docs.google.com/spreadsheets/d/1FqujqXpWSU7tbIjKIRTYKhgguScy4kPBbGjQ2IkoyIw/edit",
      "json_auth_file": "gtm_auth_file.json",
      "debug": true
    },
    "zone_array": [
      {
        "name": "GTM_T1",
        "account_id": 1234567890,
        "container_id": 12345678,
        "workspace_id": 987,
        "variable_id": 123,
        "debug": true,
        "update_row": 3,
        "update_col": 2,
        "test_row": 3,
        "test_col": 4
      }
    ],
    "debug": true,
    "trace": false,
    "json_auth_file": "gtm_auth_file.json",
    "service_account_email": "service_account@project_name.iam.gserviceaccount.com",
    "gtm_account_id": 1234567890,
    "gtm_container_id": 12345678,
    "gtm_workspace_id": 987,
    "gtm_variable_id": 123,
    "gtm_preprocessing_script": "var customPageName = {{Custom - pageName}}; \n var event = {{Event}}; \n var region = {{getRegion}}",
    "gtm_postprocessing_script": "",
    "gtm_floodlight_list": [
      {
        "floodlight_name": "Build and Price",
        "floodlight_condition": " event === 'Configurator Lead' && customPageName.includes('summary') ",
        "per_row_condition": "lookup#region#model",
        "total_var": "Build and Price Lead Value"
      },
      {
        "floodlight_name": "Floodlight - Build Start",
        "floodlight_condition": " ['toolPageChange', 'page_view', 'gtm.js'].includes(event) && /^shopping-tools\\\\|configurator.\*(exterior|mainstage)$/.test(customPageName) ",
        "per_row_condition": "lookup#region#model",
        "total_var": "Build Start Lead Value"
      }
  \],
    "value_adjustment_column_name": "Index",
    "index_low_column_name": "INDEX_LOW",
    "index_high_column_name": "INDEX_HIGH",
    "zones_to_process": "GTM_T1",
    "action_update_scripts": false,
    "action_test": true
  }
```

#### SA360 Sample Compact JavaScript Output

* By using the 'lookup' keyword separated from column names using '\#'
characters you can automatically create a lookup table and an embedded
function within the generated JavaScript code in order to reduce the amount
of code repetition. Lookup tables have been tested and known to work for
2 and 3 concurrent variables.
* Pay particular attention to the changes in the 'per\_row\_condition'
elements of the floodlights… starting with 'lookup' and then listing the
variables to use to build the lookup table, a more concise output is
possible; sometimes needed in GTM where there is a finite memory size
available.
* Using the exact same input table with location data showing Oklahoma,
Texas, and New York output of this JSON configuration becomes the following
JavaScript code using a 'multipliers' lookup table:

```javascript
  function() {
    var customPageName = {{Custom - pageName}};
    var event = {{Event}};
    var region = {{getRegion}}
    var model = {{getVehicleModel}}

    var multipliers = {
      "Oklahoma": {
          "Sedan": 1.2,
          "Sports": 1.1,
          "SUV": 0.9
      },
      "Texas": {
          "Sedan": 0.6,
          "Sports": 1.0,
          "SUV": 1.4
      },
      "New York": {
          "Sedan": 1.1,
          "Sports": 1.05,
          "SUV": 1.0
      }
  };

    function getMultiplier(var1, var2) {
        return ((multipliers && multipliers[var1]) && (multipliers && multipliers[var1])[var2]) || 1.0;
    }

    if (  event === 'Configurator Lead' && customPageName.includes('summary')  ) {
      conversion_value = parseFloat({{Build and Price Lead Value}});
    }
    else if (  ['toolPageChange', 'page_view', 'gtm.js'].includes(event) && /^shopping-tools\|configurator.*(exterior|mainstage)$/.test(customPageName)  ) {
      conversion_value = parseFloat({{Build Start Lead Value}});
    }

    conversion_value *= getMultiplier(region, model);

    return conversion_value;
  }
``` 
### budget2x Configuration

The configuration for budget2x mainly happens in the Google Sheet being used.
The only real configuration for the budget2x script is to modify the value of
SPREADSHEET\_URL near the top of the file to match the URL of the Google Sheet
you are using BEFORE you deploy the script.
    
## Configuration File Reference for DV360 and SA/GTM {#config-file-ref}
 
### Top level configuration items

The top level configuration for the JSON file are those items contained in the
top level set of curly braces ({ }). These values are typically system-wide
settings.

| Fieldname | Datatype | Description | Example | Legal Values | Default Value |
| :---- | :---- | :---- | :---- | :---- | :---- |
| scopes | list of strings | The top level list of scopes that are used by the Python app to communicate with external APIs. | "scopes": \[     "https://www.googleapis.com/auth/display-video", "https://www.googleapis.com/auth/spreadsheets" \] | Any list of Google API service strings. Commonly used strings in the context of bid2x are: 'https://www.googleapis.com/auth/display-video' 'https://www.googleapis.com/auth/tagmanager.edit.containerversions', 'https://www.googleapis.com/auth/tagmanager.edit.containers', 'https://www.googleapis.com/auth/tagmanager.publish', 'https://www.googleapis.com/auth/tagmanager.readonly', 'https://www.googleapis.com/auth/tagmanager.delete.containers', 'https://www.googleapis.com/auth/spreadsheets'  | \[    'https://www.googleapis.com/auth/display-video',  'https://www.googleapis.com/auth/spreadsheets', \] |
| api\_name | string | The name of the API service to connect to. | "api\_name": "displayvideo" | "displayvideo" or "tagmanager" | "displayvideo" |
| api\_version | string | The version of the API service to connect to. | "api\_version": "v3" | "v1", "v2", or "v3" | "v3" |
| platform\_type | string | This short string tells the system now to interpret the objects held in the  | "platform\_type": "DV" | "DV" or "GTM" | "DV" |
| debug | boolean | Boolean true/false flag that enables debugging statements to be printed to stdout from the bid2x main executable when it runs. Since the executable usually runs in something like GCP Cloud Functions or GCP Cloud Run these output items are found in the logs. | "debug": true | true or false | true |
| trace | boolean | This Boolean flag enables a level of debugging text to stdout beyond that which the standard 'debug' offers. Warning, the output from this gives A LOT of output but is helpful in trying to understand cases where there are problems. | "trace": false     | true or false | false |
| defer\_pattern | boolean |  | "defer\_pattern": true      |  | false |
| alternate\_algorithm | boolean | Boolean flag that selects the creation of an alternate algorithm syntax. Each sub-module implements the alternate algorithm in its own manner but for DV360 a custom bidding script using max\_aggregate() is created when alternate\_algorithm \= false and an algorithm using compound 'if' statements is used when alternate\_algorithm \= true. | "alternate\_algorithm": false      | true or false | false |
| new\_algo\_name | string | When new custom bidding algorithms are made in DV360 the algorithms have an internal name and a display name. The string set here is used to set the new algorithm name. | "new\_algo\_name": "bid2Inventory"      | Any string DV360 would accept for an algorithm name. | "bid2Inventory" |
| new\_algo\_display\_name | string | Custom Bidding algorithms in DV360 also have a 'display name'. This string is used as the display name. | "new\_algo\_display\_name": "bid2Inventory"     |  |  |
| line\_item\_name\_pattern | string | When bid2x is used to interrogate a DV360 advertiser and populate the control spreadsheet with line items related to the bid2x project the line items sub to the advertiser ID will be inspected by name and matched against this string. Any line items with a name containing a SUBSTRING that matches this string will be assumed to be part of the bid2x solution and will have it's information copied to the controlling Google Sheet. | "line\_item\_name\_pattern": "bid-to-inventory"      | Anything that matches your use case for the line items. Many use "bid-to-inventory" as in the DV360 it allows them to quickly identity which Line Items are being managed through bid2x. However, other names more suited to your implementation are encouraged. | "bid-to-inventory" |
| json\_auth\_file | string (filename) | Contains the name and possibly the path to a file containing the authentication file needed to connect to the connected products like DV360, Tag Manager, Google Sheets. This is typically a client-secrets.json file created in GCP from a service account's profile. | "json\_auth\_file": "client-secret.json"      | Filenames on their own will be assumed to be in the local file system. For Cloud Run and Cloud Functions this means the config file needs to be part of the deployment ZIP file. | "client-secret.json" |
| cb\_tmp\_file\_prefix | string (partial path) | For the DV360 solution, the upload of custom bidding algorithm scripts is actually much easier from a file as opposed from code. In light of that, once the new script is computed in the code it is written to a temp file before upload. This variable allows the location and name of this temp file to be controlled. The filename is written as: \[cb\_tmp\_file\_prefix\]\_\[zone name\].txt. | "cb\_tmp\_file\_prefix": "/tmp/cb\_script"      | Any legal path prefix string. | "/tmp/cb\_script" |
| cb\_last\_update\_file\_prefix | string (partial path) | This is a string containing the path to a temp file where the previous custom bidding upload string was saved as \[cb\_last\_update\_file\_prefix\]\_\[zone name\].txt. (Now deprecated as the state of the previous upload is now determined by downloading the current custom bidding script directly before uploading the new one). | "cb\_last\_update\_file\_prefix": "last\_upload"      | Any legal path prefix string. | "last\_upload" |
| partner\_id | integer | The partner\_id setting at the top level of the configuration file is for use SPECIFICALLY with [actions](#action-items:) that are not related to general operation. General operation is considered to be the actions action\_update\_spreadsheet and action\_update\_scripts. These are steady-state operations that occur on a scheduled basis \- updating the spreadsheet and updating the scripts in either DV or GTM. The advertiser\_id, and cb\_algo\_id variables are used with the action\_remove\_algorithm action method. | "partner\_id": 999999      | Any legal partner\_id that you have access to. | The default value is a placeholder and not usable. The default value needs to be replaced. |
| advertiser\_id | integer | See description for partner\_id. | "advertiser\_id": 8888888 | Any legal advertiser\_id. | The default value is a placeholder and not usable. The default value needs to be replaced. |
| cb\_algo\_id | integer | See description for partner\_id. | "cb\_algo\_id": 777777     | Any legal custom bidding algorithm id. | The default value is a placeholder and not usable. The default value needs to be replaced. |
| service\_account\_email | string (valid service account email address) | The service account email to be used in conjunction with the service account in play for the deployment. This is normally the same service account email address specified in the json\_auth\_file. | "service\_account\_email": "service\_account@project\_name.iam.gserviceaccount.com"     | Any string conforming to general email address rules that has sufficient authorization to use the necessary APIs. |  |
| zones\_to\_process | string (comma delimited list) | A comma delimited list of zone names to process during the current 'run'. The scope of 'processing' in this context means performing whichever 'action' items are set to 'true'. | "zones\_to\_process": "C1,C2"     | When bid2x loads this configuration item it is parsed into a list of names that are used during the run. The names should match those of the zone\_array elements. Providing non-matching names may produce unexpected results. | "c1,c2,c3,c4,c5'. The default value is a placeholder and not usable. The default value needs to be replaced |
| attr\_model\_id | integer | For DV360 this is the attribution model ID. If you don't know this it's probably zero (0). Usually this value is non-zero if the customer is employing a non-last-touch attribution model. | "attr\_model\_id": 0     | A valid attribution model ID or just zero. | 0 |
| bidding\_factor\_high | integer | The high watermark for the bidding factor. Regardless of what is read from the controlling spreadsheet the maximum bidding factor that will be applied will be this number. | "bidding\_factor\_high": 1000     | A positive number. | 1000 |
| bidding\_factor\_low | integer | The low watermark for the bidding factor. Regardless of what is read from the spreadsheet the minimum bidding factor will be this number. | "bidding\_factor\_low": 0 | A positive number or zero less than bidding\_factor\_high. | 0 |
| floodlight_id_list | list of integers | For DV deployments this is the list of floodlights to consider when deploying the created script | "floodlight_id_list": [ 1111111, 2222222 ] | Must be a list of integers. | No default value, if using with a single floodlight value this is must still be a list. |
| gtm\_preprocessing\_script | string | A string containing JavaScript code to be placed as-is inside the generated function just after the function starts. It usually contains convenience assignments so that other parts of the code can use them. | "gtm\_preprocessing\_script": "var customPageName \= {{Custom \- pageName}};\\nvar event \= {{Event}};\\nvar region \= {{getRegion}}", | Any string that evaluates to legal JavaScript code. Probably not a good idea to put your own 'return' statement in here. 🤔 Carriage return characters "\\n" can be used to produce better looking output. | "" (empty string) |
| gtm\_postprocessing\_script | string | A string containing code to be inserted just before the generated function return statement; just in case something needs to be adjusted right before return. | "gtm\_postprocessing\_script": "\\nconversion\_value \*= 10;\\n", | Any string that evaluates to legal JavaScript code. | "" (empty string) |

### gtm_floodlight_list items:

When using bid2x for interaction with Search Ads 360 through the use of Google
Tag Manager, it is imperative to get the configuration of the floodlight
list accurate. This list, configured in JSON, is loaded into a list of
floodlight objects that are the core parts of encapsulating the functionality
needed.

| Fieldname | Datatype | Description | Example | Legal Values | Default Value |
| :---- | :---- | :---- | :---- | :---- | :---- |
| floodlight\_name | string | The name of the floodlight in this configuration. For clarity this value is typically set the EXACT name of the floodlight tag within GTM that you're operating with. | "floodlight\_name": "Google Inventory Bid \- Floodlight \- BidtoX|Build and Price Lead|IM"  | Any string name. | There is no default, this items is required. |
| floodlight\_condition | string | When JavaScript code is generated by the bid2x system, this string is used to detect that the floodlight for this configuration item is occurring. The entire string is placed within a conditional statement like this but otherwise unmodified: \[else\] if ( \<content of floodlight\_condition\> ) { … } | "floodlight\_condition": " {{Event}} \=== 'Configurator Lead'  " | Any code that would run within the parentheses of an if or else if statement in JavaScript INCLUDING functions, {{ }} delimeters, operators, and calls to methods of known objects. More complexity can be gained by pre-defining variables in the gtm\_preprocessing\_script string. | If no floodlight\_condition is defined the system will default to the conditional as being:"{{Event}} \== \<floodlight\_name\>" |
| per\_row\_condition | string | (Use case 1 \- be sure to see use case 2 below) Once inside the if clause for this floodlight item,, the per\_row\_condition gives the ability to create a separate if-then conditional comparing items available in the GTM environment to data provided through the linked spreadsheet. Again, a freeform string is used to capture the needed logic from the use of functions, operators, etc. with the addition of column names from the spreadsheet being supported through hash '\#' delimeters. | "per\_row\_condition": "{{getVariable1\_DL}} \== '\#getVar1\_Sheet\#' && {{getVariable2\_DL}} \== '\#getVar2\_Sheet\#'" In this example, an if-else if clause within the floodlight if-else if clause is generated using EVERY ROW in the linked spreadsheet from the columns 'getVar1\_Sheet' and 'getVar2\_Sheet'  | Any legal JavaScript code that can go inside an if ( ) statement plus the addition of hash delimeted variables from the spreadsheet. | There is no default, this item is required. |
| per\_row\_condition | string | (Use case 2 \- be sure to reference use case 1 above). If the per\_row\_condition starts with the string "lookup\#" then it is assumed the user wants to generate a lookup table and the remainder of the string is used to list variable names to use to build a 2 or 3 dimensional lookup table called 'multipliers'. The linked spreadsheet is used to look up the provided column names and build a table using up-to-date data. A smaller if/else if structure is generated for determining the current floodlight and assigning a default value, then a single call to an embedded helper function is used to look up the correct multiplier. In cases where there are large sets of data in the linked spreadsheet, this results in a much more concise JavaScript function. | "per\_row\_condition": "lookup\#getLocation\#getVehicleModel", | For this use case the string MUST start with "lookup\#" and then have a hash delimited list of variables to build the lookup table with. | There is no default, this item is required. |
| total\_var | string | This variable is the name of the GTM variable that carries the DEFAULT VALUE for this floodlight. This variable will be evaluated using the double curlies {{var name}} and then converted into a floating point number for use with the generated script. It needs to be a number (not a string) because the premise of this entire setup is that first party data will inform us about a multiplier to use with this default value to change its value given the other variables in play (for example, make, model, location, etc.). With a higher or lower value, Search Ads 360 will automatically adjust its bidding to maximize revenue and prioritize those floodlight conditions with higher multipliers. | "total\_var": "Build and Price Lead Revenue" | Any string that matches the name of a variable in GTM that carries the default value of the floodlight. | There is no default, this item is required. |

### Action items:

Key to understanding the way bid2x operates is in knowing how the action items
in the config work. By default ALL action items are false so that bid2x would
just start and stop without doing anything. By setting one of the actions to
true the user is setting how the rest of the file will be interpreted and used.

| Fieldname | Datatype | Description | Example | Legal Values | Default Value |
| :---- | :---- | :---- | :---- | :---- | :---- |
| action\_list\_algos | boolean | This action lists all custom bidding algorithms for the supplied advertiser\_id (fill in advertiser\_id in JSON or pass \--advertiser option on command line) | "action\_list\_algos": false  | true or false | false |
| action\_list\_scripts | boolean | This action walks through all zones and lists the custom bidding scripts for each advertiser. | "action\_list\_scripts": false | true or false | false |
| action\_create\_algorithm | boolean | This action creates a new custom bidding algorithm for each supplied zone/campaign. Supply a JSON config file with zones containing advertiser\_id and name elements and this action will create new algorithms in each campaign using new\_algo\_name and new\_algo\_display\_name settings for guidance. | "action\_create\_algorithm": false | true or false | false |
| action\_update\_spreadsheet | boolean | This action walks the passed zone list, connects to DV, and populates a Google Sheet tab for each campaign with the following items: entityStatus lineItemID displayName lineItemType campaignID advertiserID for each line item that matches the line\_item\_name\_pattern setting. | "action\_update\_spreadsheet": false | true or false | false |
| action\_remove\_algorithm | boolean | This action item removes the algorithm ID specified in the cb\_algo\_id setting. When used from the command line this action is \-ar or \--action\_remove and should be used with argument \-g or \--algorithm to specify the numeric value of the algorithm\_id to be removed. | "action\_remove\_algorithm": false | true or false | false |
| action\_update\_scripts | boolean | This is the main action for the bid2x system whereby is uses the supplied zone info to walk through each zone, connect to the control Google Sheet, compose the updated script and upload the script to either DV or GTM. | "action\_update\_scripts": false, | true or false | false |
| action\_test | boolean | The 'action\_test' setting allows you to do a dry run of the system writing the script that would be uploaded to DV or GTM to a sheet within Google Sheets. In Google Sheets the tab for this output for DV360 is, by default, named 'CB\_Scripts' and the tab for GTM/SA360 output is named 'JS\_Scripts'. | "action\_test": true | true or false | false |

### Sheet configuration items:

Whether you're running a DV360 or a GTM/SA360 configuration of bid2x, a
Google Sheets spreadsheet is used for monitoring and control. The setting of
the configuration items under the 'sheet' scope is thus vital to ensure it's
working effectively.

| Fieldname | Datatype | Description | Example | Legal Values | Default Value |
| :---- | :---- | :---- | :---- | :---- | :---- |
| sheet\_id | string | The ID of the bid2x control sheet for this implementation. | "sheet\_id": "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGH", | 32 byte UUID string | The default value is a placeholder and not usable. The default value needs to be replaced. |
| sheet\_url | string | The URL of the control sheet for this implementation. | "sheet\_url": "https://docs.google.com/spreadsheets/d/abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGH/edit",  | Valid path to a Google Sheet, as a string. | The default value is a placeholder and not usable. The default value needs to be replaced. |
| json\_auth\_file | string (filename) | The path/filename of the auth file with an entity capable of accessing the Sheets API and had access to the sheet mentioned in sheet\_id and sheet\_url. | "json\_auth\_file": "client-secret.json",  | A valid filename and/or path to a filename. | This is typically the exact same JSON pointed to by the top level configuration section setting. |
| column\_status | string | The column in which the line item status will be written in the use of action\_update\_spreadsheet. Recall that for a line item to show up in this list it must match the line\_item\_name\_pattern setting. | "column\_status": "A",  | Any column A to ZZZ, as a string. | "A" |
| column\_lineitem\_id | string | The column in which the line item ID will be written in the use of action\_update\_spreadsheet. Recall that for a line item to show up in this list it must match the line\_item\_name\_pattern setting. | "column\_lineitem\_id": "B",       | Any column A to ZZZ, as a string. | "B" |
| column\_lineitem\_name | string | The column in which the line item name will be written in the use of action\_update\_spreadsheet. Recall that for a line item to show up in this list it must match the line\_item\_name\_pattern setting. | "column\_lineitem\_name": "C",  | Any column A to ZZZ, as a string. | "C" |
| column\_lineitem\_type | string | The column in which the line item type will be written in the use of action\_update\_spreadsheet. Recall that for a line item to show up in this list it must match the line\_item\_name\_pattern setting. | "column\_lineitem\_type": "D",  | Any column A to ZZZ, as a string. | "D" |
| column\_campaign\_id | string | The column in which the campaign\_id associated with the line item will be written in the use of action\_update\_spreadsheet. Recall that for a line item to show up in this list it must match the line\_item\_name\_pattern setting. | "column\_campaign\_id": "E",  | Any column A to ZZZ, as a string. | "E" |
| column\_advertiser\_id | string | The column in which the advertiser\_id associated with the line item will be written in the use of action\_update\_spreadsheet. Recall that for a line item to show up in this list it must match the line\_item\_name\_pattern setting. | "column\_advertiser\_id": "F", | Any column A to ZZZ, as a string. | "F" |
| column\_custom\_bidding | string | The column that will contain a Yes or No text (usually a button) to indicate whether this line item is participating in the script generation. | "column\_custom\_bidding": "K" | Any column A to ZZZ, as a string. | "K" |
| debug | boolean | A debug flag specifically for Google Sheet interactions. Helps to debug Sheet connectivity issues. | "debug": false | true or false | false |
| trace | boolean | A trace flag that is specific to Google Sheet interactions. | "trace": false | true or false | false |

### Zone_array configuration items

#### For DV360 campaigns and zones

In DV360 deployments the zones in the configuration files are listed under the
top level item 'zone\_array' and represent campaigns.

| Fieldname | Datatype | Description | Example | Legal Values | Default Value |
| :---- | :---- | :---- | :---- | :---- | :---- |
| name | string | The name of the campaign or zone. Quite often this name is used for geographic separation between campaigns and that is the origin of the name 'zone' as the initial clients for bid2x had trafficking setups that wanted different treatment per 'zone. This name will show up in the scripts and also in the Google Sheets tabs. | "name": "C1" | Strings, but probably under 10-12 characters as too long and Sheets tab names could be cumbersome. | C1 |
| campaign\_id | integer | This is the campaign ID that the custom bidding script applies to. The campaign can often be a decent approximation of a zone. | "campaign\_id": 66666666 | Must be a legal campaign\_id in DV360 that the service account has read/write access to. | The default value is spurious and needs to be replaced with a valid value. |
| advertiser\_id | integer | The advertiser\_id associated with the provided campaign\_id. | "advertiser\_id": 2222222 | Must be a legal advertiser\_id in the context of DV360. | The default value is spurious and needs to be replaced with a valid value. |
| algorithm\_id | integer | The algorithm\_id that will be used for the publishing of custom bidding scripts for this zone. Note: algorithm\_ids must be PRE-CREATED. Custom Bidding Algorithms (which have the associated algorithm\_id) can be created in the DV360 User Interface \-or- can be created through the bid2x tool using the \-ac / \--action\_create command line argument or by configuring a JSON file specifically for algorithm creation with action\_create\_algorithm set to true. | "algorithm\_id": 5555555 | Must be a legal algorithm\_id in the context of DV360. | The default value is spurious and needs to be replaced with a valid value. |
| cb\_algorithm | string | Currently unused. | "cb\_algorithm": "" | Any string | "" |
| debug | boolean | A debug flag designed for zone-specific actions. | "debug": true | true or false | false |
| update\_row | integer | An integer specifying which cell ROW will be updated in the Google Sheets status tab (default name 'CB\_Scripts') when a custom bidding script for this zone is updated using a call to ACTION\_UPDATE\_SCRIPTS or the command line arg \-au / \--action\_update. | "update\_row": 3 | An integer row | The JSON config file should be crafted such that the update rows and columns do not overlap and make sense on the CB\_Scripts sheet. No internal checking done on these values. |
| update\_col | integer | An integer specifying which cell COLUMN will be updated in the Google Sheets status tab (default name 'CB\_Scripts') when a custom bidding script for this zone is updated using a call to ACTION\_UPDATE\_SCRIPTS or the command line arg \-au / \--action\_update. | "update\_col": 2 | An integer column (not a letter). Column A \= 1, column B \= 2, etc. | The JSON config file should be crafted such that the update rows and columns do not overlap and make sense on the CB\_Scripts sheet. No internal checking done on these values. |
| test\_row | integer | An integer specifying which cell ROW will be updated in the Google Sheets status tab (default name 'CB\_Scripts') when a custom bidding script for this zone is generated using a call to ACTION\_TEST or the command line arg \-at / \--action\_test. | "test\_row": 3 | An integer row | The JSON config file should be crafted such that the update rows and columns do not overlap and make sense on the CB\_Scripts sheet. No internal checking done on these values. |
| test\_col | integer | An integer specifying which cell COLUMN will be updated in the Google Sheets status tab (default name 'CB\_Scripts') when a custom bidding script for this zone is generated using a call to ACTION\_TEST or the command line arg \-at or \--action\_test. | "test\_col": 4 | An integer column (not a letter). Column A \= 1, column B \= 2, etc. | The JSON config file should be crafted such that the update rows and columns do not overlap and make sense on the CB\_Scripts sheet. No internal checking done on these values. |

#### For GTM and SA360

| Fieldname | Datatype | Description | Example | Legal Values | Default Value |
| :---- | :---- | :---- | :---- | :---- | :---- |
| name | string | The name of the 'zone' or area or campaign that this GTM dynamic tag will be applied to. | "name": "C1"' | Any string | GTM\_\<zone\#\> |
| account\_id | integer | The GTM account id. | "account\_id": 11111111 | Any legal GTM account ID that you have access to. | The default value is spurious and needs to be replaced with a valid value. |
| container\_id | integer | The container\_id within which the tag that will be modified exists. | "container\_id": 222222 | Any legal GTM container\_id. | The default value is spurious and needs to be replaced with a valid value. |
| workspace\_id | integer | The workspace\_id that will be modified | "workspace\_id": 33333 | Any legal workspace ID. | The default value is spurious and needs to be replaced with a valid value. |
| variable\_id | integer | The ID of the variable in GTM that will be modified with updated JavaScript based on the most recent customer data. | "variable\_id": 4444 | Any legal variable ID. | The default value is spurious and needs to be replaced with a valid value. |
| update\_row | integer | An integer specifying which cell ROW will be updated in the Google Sheets status tab (default name 'VB\_Scripts' for GTM/SA360) when the JAvaScript-based tag for this zone is updated using a call to ACTION\_UPDATE\_SCRIPTS or the command line arg \-au / \--action\_update. | "update\_row": 2 | An integer row | The default value is a placeholder and needs to be replaced with a valid value. |
| update\_col | integer | An integer specifying which cell COLUMN will be updated in the Google Sheets status tab (default name 'VB\_Scripts' for GTM/SA360) when the JAvaScript-based tag for this zone is updated using a call to ACTION\_UPDATE\_SCRIPTS or the command line arg \-au / \--action\_update. | "update\_col": 4 | An integer column (not a letter). Column A \= 1, column B \= 2, etc. | The default value is a placeholder and needs to be replaced with a valid value. |
| test\_row | integer | An integer specifying which cell ROW will be updated in the Google Sheets status tab (default name 'VB\_Scripts') when JavaScript for this zone is generated using a call to ACTION\_TEST or the command line arg \-at / \--action\_test. | "test\_row": 2 | An integer row | The default value is a placeholder and needs to be replaced with a valid value. |
| test\_col | integer | An integer specifying which cell COLUMN will be updated in the Google Sheets status tab (default name 'VB\_Scripts') when JavaScript for this zone is generated using a call to ACTION\_TEST or the command line arg \-at / \--action\_test. | "test\_col": 8 | An integer column (not a letter). Column A \= 1, column B \= 2, etc. | The default value is a placeholder and needs to be replaced with a valid value. |

## Implementation notes

### Sheets input / output

When connecting to 1st party company data BigQuery is recommended because it
allows control over frequency of refresh. Not all connectors provide the same
flexibility so investigate whether the connector you're going to use is
reliable, updates the sheet regardless of if it's open, and can transfer
the quantity and variety of data you will need.

It has been found that importing raw data from your 1st party data source
into a separate tab is a best practice. From there, generate the formulae
you will need to transform and select the data and get it into the various
campaign / zone specific tabs.

### Campaigns

For DV360-connected deployment a campaign is your gateway to select the Line
Items you want to operate on and include in the custom bidding rule. For
this reason DV360 deployments utilize the zone/campaign named Sheets tab to
organize the line items.

For the SA360 deployment the emphasis is on gathering up the information per
SA campaign to write the JavaScript function for within the tag in GTM.
These deployments use their capaign-specific tab in Sheets for gathering up
and aligning the 1st party data. (Update this)

### Supported Line Item Types in DV360

All types of line items in DV360 are supported with the exception of the
following types:

'LINE\_ITEM\_TYPE\_YOUTUBE\_AND\_PARTNERS\_NON\_SKIPPABLE'
'LINE\_ITEM\_TYPE\_YOUTUBE\_AND\_PARTNERS\_REACH'
'LINE\_ITEM\_TYPE\_YOUTUBE\_AND\_PARTNERS\_ACTION'

These types of line items are NOT supported due to their inability to have
bidding adjusted per line item, which is the point of bid2x.

### DV360 Line item Naming

For bid2x to work in the smoothest manner it is important to adopt a naming
convention for your line items that can work to your benefit. The
configuration files provides a setting called 'line\_item\_name\_pattern'
that should be set to a SUBSTRING of the name of line items you want to
participate in this system.
For example, consider the following line item names:

* display\_washington\_en\_bid-to-inventory\_desktop\_product1
* display\_oregon\_en\_bid-to-inventory\_mobile\_product3
* display\_california\_sp\_bid-to-inventory\_desktop\_product1
* display\_california\_sp\_mobile\_product2

With the default setting of line\_item\_name\_pattern equal to
"bid-to-inventory" the first 3 line items would match and would show up in the
control Google Sheet but the last line item, that does not contain the
substring 'bid-to-inventory', does not match and would not be included
in the solution.

### Frequency of Script Updates
#### Frequency for DV360 and SA/GTM deployments
For both DV and SA some time is needed for the uploaded scripts to work in
an optimal manner.

For DV, once the new script is uploaded the underlying system will train on the
new ruleset for a time before implementing. Worst case scenario this could
take 24 hours but it is often the case that a new script is running within
1-2 hours up being updated. If this is the very first time a custom bidding
script is being uploaded to this campaign then there will be no coverage until
the script is marked as active in DV360. However, if this is a subsequent
update to an existing script the previous script will continue to be used
until the new script is ready to be used, so you'll be covered.

For SA, once the script is updated and published in Google Tag Manager, new
sessions on the web will start using the new dynamic variable script
immediately. However, SA needs some time to adjust to the new script as
it learns about the changes to the underlying variables so it could be a
day or two before changes from the newly updated script have a demonstrable
effect on the bidding.

In either case this means that the time between script updates needs to be on
the order of days. We recommend a weekly change to allow the system to
stabilize using the updates and show results. Clearly there is a tradeoff
between the stability of a script being active for many days and the staleness
of the real-time data that helped write the script. It is for this reason
that bid2x is designed to work well for 'weekly realtime' data but not for
scenarios where minute-by-minute or hourly changes are desired.

#### budget2x on Google Ads

The design of budget2x is such that daily budgets are impacted and there is
no learning period like in the DV or SA/GTM models. Therefore, it is
acceptable to run the script daily or even more frequently as long as your
1st party data is being updated frequently too and the use-case demands this
approach.
 
### Start-up and call from Google Cloud Scheduler

#### Start-up for DV360 and SA/GTM deployments

Due to Cloud Functions becoming deprecated in favour of Cloud Run Jobs, bid2x
has changed and moved the compute portion of the system. What was previously
executed in a Cloud Functions environment now operates through Cloud Run Jobs.
Additionally, the previous mechanism by which the Cloud Function was called
via a PubSub message has been altered since Cloud Run Jobs are called directly
from Cloud Scheduler as a type of API call.

Refer to the section detailing the installation script for the details.

#### budget2x on Google Ads

The deployment of the script within Google Ads is via cut and paste of the
script which is currently less than 300 lines, including all comments. Once
pasted into place within the scripts section of Google Ads the deployer is
free to use the 'Preview' function to see the action of the script without
making any changes.
 
## Installation script

#### Installation for DV360 and SA/GTM deployments

Core to deploying bid2x is the install script. This is a BASH script that
utilizes the gcloud command to perform a one-shot install in your client's
environment. Depending on how you obtained the bid2x code you may need to
make the install script executable with a command similar to:

```shell
chmod +x install.sh
```

The installation script is designed to work within the Cloud Shell
environment of GCP. It \*may\* work in other environments, but it also
may not.

### Installer Prerequisites

Get access to the deployment environment and ensure you have the right
permissions to do the following:

* Activate APIs
  * gcloud services enable {api}.googleapis.com, where api is ALL of
  the following:
    * "artifactregistry"
    * "cloudbuild"
    * "cloudscheduler"
    * "displayvideo" (if installing for DV360)
    * "logging"
    * "run"
    * "sheets"
    * "storage-api"
    * "tagmanager" (if installing for GTM/SA360)
  * These APIs will be activated with the rights of the person running
  the script.
* Add IAM rights to service accounts:
  * The local user running the installer script will attempt to add
    * roles/cloudscheduler.serviceAgent
  * to the defined SERVICE\_ACCOUNT
  * The local user running the installer script will attempt to add
    * roles/run.invoker
  * to the defined INVOKER\_SERVICE\_ACCOUNT
  * The local user running the installer script will attempt to add
    * roles/storage.objectViewer
  * to the defined INVOKER SERVICE ACCOUNT
  * The local installer needs the right to turn on services:
    * serviceusage.services.enable
  * as this allows the installer to enable the APIs that will be used by
  the installed code.
* Delete old installations, specifically:
  * gcloud run jobs delete \<named-job\>
  * gcloud scheduler jobs delete \<named-schedule\>
* Deploy a new Cloud Run job, specifically:
  * gcloud run jobs deploy \<job name\>
* Make a new Cloud Scheduler event:
  * gcloud scheduler jobs create http \<named job\>

### Installer User-Definable Parameters

The top of the installation script file contains around 200 lines of code
that are expected to be modified by the person doing the installation.
Here is the contents of those lines as of the writing of this document:

```shell
# ----------------------------------------------------------------------------
# Main project parameters
# ----------------------------------------------------------------------------

# Set this to the GCP project name (not the ID) that you are deploying into.
# If you're not sure what the current project is use the command
# 'gcloud config get-value project'.
PROJECT="bid2x-deploy-test12"

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

# Verbosity mode - uncomment what you want. Some gcloud commands seem to
# ignore --quiet and output whatever they want. YMMV.
# Warning: running without --quiet can make some commands interactive
# and thus require the answering of (Y/N) questions during the install.
QUIET='--quiet'
# QUIET=' '

# ----------------------------------------------------------------------------
# Virtual Machine Environment details for Cloud Run Job deployments.
# ----------------------------------------------------------------------------
# Cloud Run Jobs deployment cpu default for bid2x. A single CPU='1' is
# usually sufficient for bid2x.
CPU='1'

# Cloud Run Jobs deployment memory default for bid2x. This number CAN be
# increased when needed, for example ='1Gi' or ='2Gi'.
# Some DV trafficking profiles can contain a LARGE number of Line Items in a
# campaign and a large download of Line Items can exhaust memory
# (watch the logs). Don't be afraid to increase this number as needed.
MEMORY='512Mi'

# ----------------------------------------------------------------------------
# Service account(s) for the deployment.
# ----------------------------------------------------------------------------
# Service account used for IAM calls and "cloud run jobs deploy" commands.
SERVICE_ACCOUNT="bid2x-service@${PROJECT}.iam.gserviceaccount.com"

# The SA that will RUN the Cloud Run command (i.e. with
# run.jobs.run permission).
INVOKER_SERVICE_ACCOUNT="bid2x-service@${PROJECT}.iam.gserviceaccount.com"

# The two service account variables above MAY be the same but can also be
# different; depending on your requirements.

# ----------------------------------------------------------------------------
# Cloud Run Job details for the weekly and daily runs.
# ----------------------------------------------------------------------------
# Fill in weekly items in for DV and SA type deployments.

# The name given to the Cloud Run Job for the weekly run. This is the name
# of the Cloud Run job in the UI.
WEEKLY_CLOUD_RUN_JOB_NAME="bid2x-weekly"

# <min 0-60,*> <hour 0-23,*> <day 1-31,*> <month 1-12,*> <day of week 1-7,*>.
# The default of "0 20 * * 7" is a schedule for Sundays(7) at 8pm (20:00).
WEEKLY_CRON_SCHEDULE="0 20 * * 7"

# This file should already exist and be readable; there is a test for
# existence of this file in the pre-run checks.
WEEKLY_CONFIG="sample_config_dv.json"

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
```

A detailed description of each parameter and its use follows:

#### Main Project Parameters

| PROJECT | Set this to the GCP project name (not the ID) that you are deploying into. If you're not sure what the current project is use the command: gcloud config get-value project  Default: bid2x-deploy-test (don't use the default value) |
| :---- | :---- |
| REGION | Set this to the GCP region you are deploying in (NOT THE ZONE i.e. should not end with 'a' or 'b' or whatever designates a zone for your locale). Default: us-central1 |
| TIMEZONE | The timezone you want to use for the CRON jobs. Note that the default timezone of the GCP Cloud Shell is UTC (Universal Coordinated Time) so be aware that by default there are multiple time zones in play that need to be considered. Default: America/Toronto (because isn't that the centre of the universe? 🤪) |
| LOG\_FILE | File that the most current installation log will be written to. See the section dedicated to the Installation Log file for more details. Default: bid2x\_installer.log |
| BUCKET\_NAME | Cloud Storage config container unique name (do not include 'gs://''). This is the bucket in your project where the installer will copy your configuration JSON file and where the Cloud Run Job that performs the weekly or daily bid2x action will, by default, look for it's config. Default bucket name is auto-generated as: '\<project-name\>-config'. |
| DEPOLYMENT\_TYPE | Bid2x deployment type. Can be 'DV' or 'SA'. |
| QUIET  | Quite mode flag. Use "--quiet" to force quiet mode on the gcloud command, otherwise use "" (empty string) and quite mode will NOT be used with gcloud commands. Warning: running without \--quiet can make some commands interactive and thus require the answering of (Y/N) questions during the install. |

#### Virtual Machine Environment Parameters

| CPU | Cloud Run Jobs deployment cpu default for bid2x. A single CPU='1' is usually sufficient for bid2x. Default: 1 (as a string) |
| :---- | :---- |
| MEMORY | Cloud Run Jobs deployment memory default for bid2x. This number CAN be increased when needed, for example \='1Gi' or \='2Gi'. Some DV trafficking profiles can contain a LARGE number of Line Items in a campaign and a large download of Line Items can exhaust memory (watch the logs). Don't be afraid to increase this number as needed. Default: '512Mi' |

#### Service Account Parameters

| SERVICE\_ACCOUNT | Service account used for IAM calls and "cloud run jobs deploy" commands. Default: "bid2x-service@\<PROJECT\>.iam.gserviceaccount.com" |
| :---- | :---- |
| INVOKER\_SERVICE\_ACCOUNT | The SA that will RUN the Cloud Run command (i.e. with run.jobs.run permission). Default: "bid2x-service@${PROJECT}.iam.gserviceaccount.com" |

\*Note: having both service accounts as the same value is a viable
configuration. However, there are some deployments where it is desired to
have a service account that runs the jobs be a more 'locked down' service
account, capable only of running existing jobs, not able to deploy new jobs
or make IAM calls. Hence, the discrimination between the two accounts.
 
#### Cloud Run Job Detail Parameters

| WEEKLY\_CLOUD\_RUN\_JOB\_NAME | The name given to the Cloud Run Job for the weekly run. This is the name of the Cloud Run job in the UI. Default: bid2x-weekly |
| :---- | :---- |
| WEEKLY\_CRON\_SCHEDULE | A string containing a cron-style config for the schedule. \<min 0-60,\*\> \<hour 0-23,\*\> \<day 1-31,\*\> \<month 1-12,\*\> \<day of week 1-7,\*\>. The default of "0 20 \* \* 7" is a schedule for Sundays(7) at 8pm (20:00) in the timezone defined in the TIMEZONE variable earlier in the file. |
| WEEKLY\_CONFIG | The bid2x configuration JSON file that contains the action to perform weekly. This is usually action\_update\_scripts. This file should already exist and be readable; as there is a test for the existence of this file in the pre-run checks. Default: sample\_config\_dv.json (make a new file as this is just a sample file) Tip: uses gs://\<bucketname\>/file.json to load from GCS bucket. |
| WEEKLY\_SCHEDULER\_JOB\_NAME | The name shown in the Cloud Scheduler UI for this configuration item. Default: "\<WEEKLY\_CLOUD\_RUN\_JOB\_NAME\>-scheduled-update" |
| WEEKLY\_ARGS | A comma-separated list of command-line args after "python main.py". See the help text on bid2x to see the full list & defaults. (python main.py \--help). Default: "-i,${WEEKLY\_CONFIG}" That is, the default tells the python code to load the config file using the \-i argument. Example: python main.py \-i sample\_config\_dv.json or python main.py \-i gs://my-project-config/dv\_weekly.json |
| DAILY\_CLOUD\_RUN\_JOB\_NAME | The name given to the Cloud Run Job for the daily run (DV only). This is the name of the Cloud Run job in the UI. Default: bid2x-daily |
| DAILY\_CRON\_SCHEDULE | A string containing a cron-style config for the schedule. \<min 0-60,\*\> \<hour 0-23,\*\> \<day 1-31,\*\> \<month 1-12,\*\> \<day of week 1-7,\*\>. The default of "0 4 \* \* \*" is a schedule for every day at 4:00am" in the timezone defined in the TIMEZONE variable earlier in the file. |
| DAILY\_CONFIG | The bid2x configuration JSON file that contains the action to perform daily. This is usually action\_update\_spreadsheet. This file should already exist and be readable; as there is a test for the existence of this file in the pre-run checks. Default: sample\_config\_dv.json (make a new file as this is just a sample file) Tip: uses gs://\<bucketname\>/file.json to load from GCS bucket. |
| DAILY\_SCHEDULER\_JOB\_NAME | The name shown in the Cloud Scheduler UI for this configuration item. Default: "\<DAILY\_CLOUD\_RUN\_JOB\_NAME\>-scheduled-update" |
| DAILY\_ARGS | The daily config file is usually a JSON with 'action\_update\_spreadsheet' set to true. Default: "-i,${DAILY\_CONFIG}" Example: python main.py \-i sample\_config\_dv.json or python main.py \-i gs://my-project-config/dv\_daily.json |

#### Installation Control Flags

By default leave all control flags as 1 to run all parts of the installer.
If you're having some installation issues (it happens) you can adjust the
values to get only portions of the installation to run.

| SET\_UP\_ENVIRONMENT | Run set up environment section. This consists of little more than a gcloud command to set the correct project but may be expanded later. Default: 1 (i.e. perform this portion of the install) |
| :---- | :---- |
| PRE\_RUN\_CHECKS | Run the pre-run checks portion of the installer. This section checks for the existence of the config files you are referring to in the installer configuration AND checks for the existence of the SERVICE\_ACCOUNT. Default: 1 (i.e. run it, use 0 to skip) |
| ACTIVATE\_APIS | Run the portion of the installer that activates the various APIs that need to be enabled in order for bid2x to operate properly. Default: 1 (i.e. run it, use 0 to skip) |
| GRANT\_PERMISSIONS | Run the portion of the installer that grants permissions to the SERVICE\_ACCOUNT and the INVOKER\_SERVICE\_ACCOUNT. Sometimes you are given a service account already provisioned or are running in an environment where you have no IAM rights. So, it's common that this section might be disabled. Default: 1 (i.e. run it, use 0 to skip) |
| DELETE\_OLD\_INSTALL | Run the portion of the installer that deletes old installs. Default: 1 (i.e. run it, use 0 to skip) |
| GCS\_OPERATIONS | Run the portion of the installer that ensures the creation of a bucket and copies the config file(s) to that bucket for use by bid2x. Default: 1 (i.e. run it, use 0 to skip) |
| DEPLOY\_JOBS | Run the portion of the installer that creates the cloud run job deployment(s). This section collects the code and configuration files, uses cloud build to generate a Docker environment, and deploys. Default: 1 (i.e. run it, use 0 to skip) |
| CREATE\_SCHEDULER\_JOBS | Run the portion of the installer that creates Cloud Scheduler jobs that call the Cloud Run Job deployments at specific times/dates. Default: 1 (i.e. run it, use 0 to skip) |

### Installation Log file

Every time you run the install.sh script it generates a log file controlled by
the name LOG\_FILE within the top portion of the script itself. By default
this is bid2x\_installer.log. This file is always checked for upon running
the installer and will be backed up to a new name with an extension using the
time/date you created the old install log. In this way, log files are NEVER
overwritten and there is always a full traceable path of what you did during
the installation complete with time and date stamped files indicating when
those actions were completed.

During communications with the bid2x development team the installation logs
are our mechanism to see what happened if anything goes wrong and are our best
bet in helping you. So don't forget the installation logs when looking for
assistance.
 
#### Log File Format

The format of the installation log file breaks up the install into numbers
sections separated by indented titleblocks highlighted by characters like
'======' and '-------'. The beginning and the end of the installation
always prints the time and date as a reference.

Starting below is some sample output from the log:

```shell
***********************************************************************
bid2x installer - Starting - Fri Apr 18, 2025 - 08:01:36 PM UTC
***********************************************************************
===========================================================================================================================================================================
1. Setting up environment
===========================================================================================================================================================================
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    1.1. Setting Default Project
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Updated property [core/project].
Setting Default Project complete
===========================================================================================================================================================================
2. Running pre-run checks
===========================================================================================================================================================================
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    2.1. Checking for file: sample_config_dv.json...
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
File found: sample_config_dv.json
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    2.2. Checking for file: sample_config_dv.json...
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
File found: sample_config_dv.json
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    2.3. Checking for Service Account: bid2x-service@bid2x-deploy-test12.iam.gserviceaccount.com in
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Service Account found: bid2x-service@bid2x-deploy-test12.iam.gserviceaccount.com
Pre-run Checks Passed.
Proceeding with deployment...
===========================================================================================================================================================================
3. Activate APIs
===========================================================================================================================================================================
artifactregistry already active
cloudbuild already active
cloudscheduler already active
displayvideo already active
logging already active
run already active
sheets already active
storage-api already active
tagmanager already active
API Activation completed
===========================================================================================================================================================================
4. Grant GCP IAM Permissions
===========================================================================================================================================================================
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    4.1. Add Cloud Scheduler Permissions to Service Account
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Updated IAM policy for project [bid2x-deploy-test12].
bindings:
- members:
  - serviceAccount:service-465788751599@gcp-sa-artifactregistry.iam.gserviceaccount.com
  role: roles/artifactregistry.serviceAgent
- members:
  - serviceAccount:465788751599@cloudbuild.gserviceaccount.com
  role: roles/cloudbuild.builds.builder
- members:
  - serviceAccount:service-465788751599@gcp-sa-cloudbuild.iam.gserviceaccount.com
  role: roles/cloudbuild.serviceAgent
- members:
  - serviceAccount:bid2x-service@bid2x-deploy-test12.iam.gserviceaccount.com
  - serviceAccount:service-465788751599@gcp-sa-cloudscheduler.iam.gserviceaccount.com
  role: roles/cloudscheduler.serviceAgent
- members:
  - serviceAccount:service-465788751599@containerregistry.iam.gserviceaccount.com
  role: roles/containerregistry.ServiceAgent
- members:
  - serviceAccount:465788751599-compute@developer.gserviceaccount.com
  - serviceAccount:465788751599@cloudservices.gserviceaccount.com
  role: roles/editor
- members:
  - user:mdoliver@google.com
  role: roles/owner
- members:
  - serviceAccount:service-465788751599@gcp-sa-pubsub.iam.gserviceaccount.com
  role: roles/pubsub.serviceAgent
- members:
  - serviceAccount:bid2x-service@bid2x-deploy-test12.iam.gserviceaccount.com
  role: roles/run.invoker
- members:
  - serviceAccount:service-465788751599@serverless-robot-prod.iam.gserviceaccount.com
  role: roles/run.serviceAgent
- members:
  - serviceAccount:bid2x-service@bid2x-deploy-test12.iam.gserviceaccount.com
  role: roles/storage.objectViewer
etag: BwYzEvzEhnQ=
version: 1
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    4.2. Add Cloud Job Invoker Permissions to Invoker Service Account
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Updated IAM policy for project [bid2x-deploy-test12].
bindings:
- members:
  - serviceAccount:service-465788751599@gcp-sa-artifactregistry.iam.gserviceaccount.com
  role: roles/artifactregistry.serviceAgent
- members:
  - serviceAccount:465788751599@cloudbuild.gserviceaccount.com
  role: roles/cloudbuild.builds.builder
- members:
  - serviceAccount:service-465788751599@gcp-sa-cloudbuild.iam.gserviceaccount.com
  role: roles/cloudbuild.serviceAgent
- members:
  - serviceAccount:bid2x-service@bid2x-deploy-test12.iam.gserviceaccount.com
  - serviceAccount:service-465788751599@gcp-sa-cloudscheduler.iam.gserviceaccount.com
  role: roles/cloudscheduler.serviceAgent
- members:
  - serviceAccount:service-465788751599@containerregistry.iam.gserviceaccount.com
  role: roles/containerregistry.ServiceAgent
- members:
  - serviceAccount:465788751599-compute@developer.gserviceaccount.com
  - serviceAccount:465788751599@cloudservices.gserviceaccount.com
  role: roles/editor
- members:
  - user:mdoliver@google.com
  role: roles/owner
- members:
  - serviceAccount:service-465788751599@gcp-sa-pubsub.iam.gserviceaccount.com
  role: roles/pubsub.serviceAgent
- members:
  - serviceAccount:bid2x-service@bid2x-deploy-test12.iam.gserviceaccount.com
  role: roles/run.invoker
- members:
  - serviceAccount:service-465788751599@serverless-robot-prod.iam.gserviceaccount.com
  role: roles/run.serviceAgent
- members:
  - serviceAccount:bid2x-service@bid2x-deploy-test12.iam.gserviceaccount.com
  role: roles/storage.objectViewer
etag: BwYzEvzoCVY=
version: 1
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    4.3. Add Permissions for INVOKER to access GCS as Viewer
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Updated IAM policy for project [bid2x-deploy-test12].
bindings:
- members:
  - serviceAccount:service-465788751599@gcp-sa-artifactregistry.iam.gserviceaccount.com
  role: roles/artifactregistry.serviceAgent
- members:
  - serviceAccount:465788751599@cloudbuild.gserviceaccount.com
  role: roles/cloudbuild.builds.builder
- members:
  - serviceAccount:service-465788751599@gcp-sa-cloudbuild.iam.gserviceaccount.com
  role: roles/cloudbuild.serviceAgent
- members:
  - serviceAccount:bid2x-service@bid2x-deploy-test12.iam.gserviceaccount.com
  - serviceAccount:service-465788751599@gcp-sa-cloudscheduler.iam.gserviceaccount.com
  role: roles/cloudscheduler.serviceAgent
- members:
  - serviceAccount:service-465788751599@containerregistry.iam.gserviceaccount.com
  role: roles/containerregistry.ServiceAgent
- members:
  - serviceAccount:465788751599-compute@developer.gserviceaccount.com
  - serviceAccount:465788751599@cloudservices.gserviceaccount.com
  role: roles/editor
- members:
  - user:mdoliver@google.com
  role: roles/owner
- members:
  - serviceAccount:service-465788751599@gcp-sa-pubsub.iam.gserviceaccount.com
  role: roles/pubsub.serviceAgent
- members:
  - serviceAccount:bid2x-service@bid2x-deploy-test12.iam.gserviceaccount.com
  role: roles/run.invoker
- members:
  - serviceAccount:service-465788751599@serverless-robot-prod.iam.gserviceaccount.com
  role: roles/run.serviceAgent
- members:
  - serviceAccount:bid2x-service@bid2x-deploy-test12.iam.gserviceaccount.com
  role: roles/storage.objectViewer
etag: BwYzEv0KKko=
version: 1
IAM permissioning completed.
===========================================================================================================================================================================
5. Delete old matching GCP install components.
===========================================================================================================================================================================
** WARNING ** : This section of the bid2x install MAY show errors.
This happens if the script attempts to DELETE components that do
not exist. Therefore, if this is your first install or you are
attempting again after a partial or failed installation please be
aware that errors in this section can happen and do not NECESSARILY
mean you have an invalid installation.
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    5.1. Delete old install of weekly run
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Deleting [bid2x-weekly]...
failed.
ERROR: (gcloud.run.jobs.delete) Job [bid2x-weekly] could not be found.
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    5.2. Delete old install of weekly scheduler
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Deleted job [bid2x-weekly-scheduled-update].
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    5.3. Delete old install of daily run
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Deleting [bid2x-daily]...
failed.
ERROR: (gcloud.run.jobs.delete) Job [bid2x-daily] could not be found.
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    5.4. Delete old install of daily scheduler
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Deleted job [bid2x-daily-scheduled-update].
Existing GCP components deletion completed.
===========================================================================================================================================================================
6. Create Cloud Storage Bucket
===========================================================================================================================================================================
Checking if bucket gs://bid2x-deploy-test12-config exists...
Bucket gs://bid2x-deploy-test12-config already exists.
No creation action needed.
Attempting to copy local file
'sample_config_dv.json' to 'gs://bid2x-deploy-test12-config/'...
Copying file://sample_config_dv.json to gs://bid2x-deploy-test12-config/sample_config_dv.json


Successfully copied 'sample_config_dv.json'.
Attempting to copy local file
'sample_config_dv.json' to 'gs://bid2x-deploy-test12-config/'...
Copying file://sample_config_dv.json to gs://bid2x-deploy-test12-config/sample_config_dv.json


Successfully copied 'sample_config_dv.json'.
===========================================================================================================================================================================
7. Deploy Cloud Run Job(s)
===========================================================================================================================================================================
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    7.1. Deploy Cloud Run Job for Weekly update
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
This command is equivalent to running `gcloud builds submit --tag [IMAGE] .` and `gcloud run jobs deploy bid2x-weekly --image [IMAGE]

Building using Dockerfile and deploying container to Cloud Run job [[1mbid2x-weekly[m] in project [[1mbid2x-deploy-test12[m] region [[1mus-central1[m]
Building and creating job...
Uploading sources.........Creating temporary archive of 23 file(s) totalling 286.8 KiB before compression.
Some files were not included in the source upload.

Check the gcloud log [/tmp/tmp.ED5VICq33e/logs/2025.04.18/20.02.11.784646.log] to see which files and the contents of the
default gcloudignore file used (see `$ gcloud topic gcloudignore` to learn
more).

Uploading zipfile of [.] to [gs://run-sources-bid2x-deploy-test12-us-central1/jobs/bid2x-weekly/1745006534.41433-be8f5bfcb6074d10a21620742f4b4600.zip]
..done
Building Container............................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................done
Done.
Job [[1mbid2x-weekly[m] has successfully been deployed.

To execute this job, use:
gcloud run jobs execute bid2x-weekly
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    7.2. Deploy Cloud Run Job for Daily update
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 This command is equivalent to running `gcloud builds submit --tag [IMAGE] .` and `gcloud run jobs deploy bid2x-daily --image [IMAGE]

Building using Dockerfile and deploying container to Cloud Run job [[1mbid2x-daily[m] in project [[1mbid2x-deploy-test12[m] region [[1mus-central1[m]
Building and creating job...
Uploading sources......Creating temporary archive of 23 file(s) totalling 286.8 KiB before compression.
.Some files were not included in the source upload.

Check the gcloud log [/tmp/tmp.ED5VICq33e/logs/2025.04.18/20.04.45.187327.log] to see which files and the contents of the
default gcloudignore file used (see `$ gcloud topic gcloudignore` to learn
more).

Uploading zipfile of [.] to [gs://run-sources-bid2x-deploy-test12-us-central1/jobs/bid2x-daily/1745006687.495779-618a73a4d3284052883917b0b3c615b4.zip]
...done
Building Container...........................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................done
Done.
Job [[1mbid2x-daily[m] has successfully been deployed.

To execute this job, use:
gcloud run jobs execute bid2x-daily
Cloud Run Jobs deployment completed.
===========================================================================================================================================================================
8. Create Cloud Scheduler Job(s)
===========================================================================================================================================================================
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    8.1. Construct weekly invocation URI
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Weekly Invocation URI: https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/bid2x-deploy-test12/jobs/bid2x-weekly:run
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    8.2. Create weekly cloud scheduler job
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
attemptDeadline: 180s
description: Weekly Scheduled Run of bid2x
httpTarget:
  headers:
    User-Agent: Google-Cloud-Scheduler
  httpMethod: POST
  oidcToken:
    audience: https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/bid2x-deploy-test12/jobs/bid2x-weekly:run
    serviceAccountEmail: bid2x-service@bid2x-deploy-test12.iam.gserviceaccount.com
  uri: https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/bid2x-deploy-test12/jobs/bid2x-weekly:run
name: projects/bid2x-deploy-test12/locations/us-central1/jobs/bid2x-weekly-scheduled-update
retryConfig:
  maxBackoffDuration: 3600s
  maxDoublings: 16
  maxRetryDuration: 0s
  minBackoffDuration: 5s
schedule: 0 20 * * 7
state: ENABLED
timeZone: America/Toronto
userUpdateTime: '2025-04-18T20:07:20Z'
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    8.3. Construct daily invocation URI
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Daily Invocation URI: https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/bid2x-deploy-test12/jobs/bid2x-daily:run
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    8.4. Create daily cloud scheduler job
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
attemptDeadline: 180s
description: Daily Scheduled Run of bid2x
httpTarget:
  headers:
    User-Agent: Google-Cloud-Scheduler
  httpMethod: POST
  oidcToken:
    audience: https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/bid2x-deploy-test12/jobs/bid2x-daily:run
    serviceAccountEmail: bid2x-service@bid2x-deploy-test12.iam.gserviceaccount.com
  uri: https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/bid2x-deploy-test12/jobs/bid2x-daily:run
name: projects/bid2x-deploy-test12/locations/us-central1/jobs/bid2x-daily-scheduled-update
retryConfig:
  maxBackoffDuration: 3600s
  maxDoublings: 16
  maxRetryDuration: 0s
  minBackoffDuration: 5s
schedule: 0 4 * * *
state: ENABLED
imeZone: America/Toronto
userUpdateTime: '2025-04-18T20:07:25Z'
Completed creating cloud scheduler definitions.
***********************************************************************
bid2x installer - Finished - Fri Apr 18, 2025 - 08:07:25 PM UTC
***********************************************************************
```
