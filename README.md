# gTech Ads: bid2x Technical Implementation Guide

<table>
  <tr>
   <td><strong>Author(s)</strong>
   </td>
   <td colspan="2" >Mark Oliver - mdoliver@google.com
   </td>
  </tr>
  <tr>
   <td><strong>Stakeholder(s)</strong>
   </td>
   <td colspan="2" >Andrew Chan - andrewlfchan@google.com, Joey Thompson - joeythompson@google.com
   </td>
  </tr>
  <tr>
   <td><strong>Add’l Reader(s)</strong>
   </td>
   <td colspan="2" >Peer [ ], Manager [<strong> </strong>]
   </td>
  </tr>
  <tr>
   <td><strong>Status</strong>
   </td>
   <td colspan="2" >[ <strong>Draft</strong> | In review | Working Copy | Complete ]
   </td>
  </tr>
  <tr>
   <td><strong>Last Updated</strong>
   </td>
   <td colspan="2" ><strong>2025-04-24</strong>
   </td>
  </tr>
  <tr>
   <td><strong>Bug Assigned</strong>
   </td>
   <td colspan="2" >
   </td>
  </tr>
  <tr>
   <td><strong>Abstract</strong>
   </td>
   <td colspan="2" >This file gives a detailed description on preparing for a bid2x deployment, how to use the config file(s), and how to install it in a GCP environment.
   </td>
  </tr>
</table>

## Disclaimer
`  Copyright 2025 Google LLC`<br>
`  Licensed under the Apache License, Version 2.0 (the "License");`<br>
`  you may not use this file except in compliance with the License.`<br>
`  You may obtain a copy of the License at`<br>
`      https://www.apache.org/licenses/LICENSE-2.0`<br>
`  Unless required by applicable law or agreed to in writing, software`<br>
`  distributed under the License is distributed on an "AS IS" BASIS,`<br>
`  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.`<br>
`  See the License for the specific language governing permissions and`<br>
`  limitations under the License.`


## Introduction {#introduction}

Our customers own a great deal of 1st party data that, traditionally, our advertising systems have no access to.  Some of this data can be potentially useful as an input signal to allow Google advertising systems to bid more intelligently.

This system originated when an airline wanted to use their first party data that related to 'struggling routes' to affect change in bidding.  Simply put, they wanted our advertising systems to bid more aggressively for ad spots when a struggling route was in play.  Of course, the airline did not want to make the struggling routes public, so they created an 'index' to use with our provided code that allowed them to assign a bid multiplier when the index was in a certain range.  This was our <span style="text-decoration:underline;">bid2index</span> solution.

As time went on the question was asked, "if I have an auto customer with different campaigns for different car models, could I use up-to-date inventory information in the same way to tailor bidding according to the models that are actually available?"  There's no use bidding for space to advertise models they don't actually have … so why not?  This was based on the same code as the airline project and became our <span style="text-decoration:underline;">bid2inventory</span> solution.

Continuing this train of thought: Why not empty hotel rooms?  Why not number of candy bars shipped to stores in a given area?  Why not any other metrics combined with inventory like margin to optimize profit?  Indeed, why not any number of factors that the customer might have that could have a positive impact on the bidding?  And those factors, because they're not all known a priori became the 'x', the factor any given customer would provide in an attempt to optimize their bidding.  And that's how it became <span style="text-decoration:underline;">bid2x</span>.


## Getting Access {#getting-access}

At the time of writing this bid2x is available at this location: [https://professional-services.googlesource.com/solutions/bid2x/](https://professional-services.googlesource.com/solutions/bid2x/)

Depending on what group you are in within Google or if you don't have a @[google.com](google.com) email address you may need to be added to a group to obtain access.  Please contact the authors / stakeholders of bid2x to see about having your email added to the correct Google Group to obtain access.  Once you have access you can clone the code using 'git' commands.


## Solution Pieces {#solution-pieces}

What's in a bid2x solution?  Based on the information provided in the introduction your first guess would probably be 'first party data'.  But there's more, pieces are needed to coordinate passing this information to our advertising platforms in an intelligent way.  The sections below will break down the solution separately for each implementation type.


#### DV360 description {#dv360-description}

The bid2x solution for DV360 uses Custom Bidding scripts to translate the customer's first party data into the desired impact on Line Items within a set of Campaigns.  The bid2x solution supports multiple campaigns and <span style="text-decoration:underline;">many</span> line items per campaign.


#### SA360/GTM description {#sa360-gtm-description}

The bid2x solution for SA360 makes use of dynamic HTML tags in Google Tag Manager.   Like the DV360 solution the implementation for SA360 makes use of 1st party data, but instead of communicating this information directly with SA360, the solution makes use of Google Tag Manager to indirectly deliver the information.

At this point reviewing a few topology diagrams of the solution would be beneficial…


## Classic bid2x Topologies {#classic-bid2x-topologies}


#### Topology for DV360 deployment {#topology-for-dv360-deployment}

The pieces for a bid2x solution using DV360 are often arranged as follows:



![bid2x DV Topology](./img/bid2x_dv_topology.png)


The major components are:



1. The bid2x Python code that runs in Google Cloud Platform, usually deployed in Cloud Run / Cloud Functions.  This single code base is the same for DV360 and SA360/GTM implementations whether it is reads/writes to the Google Sheet or read/write API interactions with DV or GTM.
2. The bid2x control Google Sheet coordinates data between various data sources and prepares it for use in the bid2x system.  For DV360, the control sheet is a landing pad for campaign-specific data with various campaigns split between sheet tabs and individual tabs containing all the participating line items in that campaign.
3. GCP's BigQuery is primarily used as an input source for customer first party data.
4. For the DV360 implementation the customer's trafficking information (campaigns, line items, custom bidding scripts) are interacted with via the DV360 API.
5. As an alternative to BQ as a mechanism for getting customer first party data into the Google Sheet other mechanisms and data stores are supported through Google Sheet connectors.

The noted data flows within the diagram are:



1. The bid2x Python app interacts with DV360 to create custom bidding algorithms and scripts, to re-write custom bidding scripts, to read line items within a campaign, and to assign line items to uploaded custom bidding scripts.
2. The bid2x Python app communicates with the Google Sheet to write line item information to various tabs and to make a record of the latest action it has taken.  Additionally, the Python script reads the bidding information PER line item across tabs to create a separate bidding script per campaign to allow bidding prioritizing utilizing first party data.
3. The Google Sheet is updated with first party data from BigQuery.  Typically this data is scheduled to update daily.  The raw data from this update ends up in a 'raw' data tab and then is combined with line item and other data on the campaign tabs.
4. As an alternative to using BQ for first party data input any other connector mechanism that Sheets supports is a candidate to bring in data.


#### Topology for SA360/GTM deployment {#topology-for-sa360-gtm-deployment}

The topology for a deployment that targets SA360 involves the use of Google Tag Manager to influence SA360.  Here's a sample topology:




![bid2x DV Topology](./img/bid2x_gtm_topology.png)



1. The bid2x Python code that runs in Google Cloud Platform, usually Cloud Run / Cloud Functions.  This single code base is the same for DV360 and SA360/GTM implementations whether it is reads/writes to the Google Sheet or read/write API interactions with DV or GTM.
2. The bid2x control Google Sheet coordinates data between various data sources and prepares it for use in the bid2x system.  For SA360/GTM, the control sheet is a landing pad for campaign-specific data with individual tabs containing all the first party data for that campaign.
3. GCP's BigQuery is primarily used as an input source for customer first party data.
4. For the SA360/GTM implementation Google Tag Manager is interfaced with over API to update a tag being used to prioritize bidding.
5. As an alternative to BQ as a mechanism for getting customer first party data into the Google Sheet other mechanisms and data stores are supported through Google Sheet connectors.

The noted data flows within the diagram are:



1. First party data from BigQuery is brought into a separate tab in Google Sheets and then distributed amongst the correct campaign / zone tabs, as needed.
2. As an alternative to BQ, first party data can be brought into Google Sheets through any other mechanism that is supported.  However, is should be noted that the BQ connector supports timed updates and is convenient for at least that reason.
3. Data from the control Google Sheet is gathered by the cloud-based executable for bid2x and converted into a JavaScript routine that assigns a relative value to a variable based on the 1st party data and the current state of the environment when it is run.
4. The JavaScript routine is uploaded to Google Tag Manager to the correct variable.  As the end customer navigates the site, the JavaScript routine will run and evaluate to a value based on algorithm and other variables referenced in the data layer.  The resultant will be available to SA360 as a value to optimize on.


## Authentication {#authentication}

As can be seen from the topology section there are a number of data flows that require explicit access.  The bid2x Python app running with GCP runs with the identity of a service account that is specific to each deployment.  This account needs to be granted the following rights:



* Cloud Run Jobs Invoker
* Cloud Scheduler Admin
* BigQuery Query Runner (if 1st party data being sourced from BigQuery)

Enabled API & Service:



* Google Sheets API
* Display & Video 360 API (for DV deployments)
* Google Tag Manager API (for SA/GTM deployments)


## Configuration Files {#configuration-files}

Below is a sample configuration file.


```
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



* This is a bid2x configuration file for a DV360 deployment ("platform_type": "DV"),
* This 'control sheet' the CSE and end-user will use to see what's going on is ([https://docs.google.com/spreadsheets/d/abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGH/edit](https://docs.google.com/spreadsheets/d/abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGH/edit)) and is clearly fake as that's a made up URL with the letters a-z, the numbers 0-9, and then A-H making up the ID.  It is intended to be replaced with a real URI based upon a spreadsheet you clone from an existing template.
* During operation it uses a service account as defined here: ("service_account_email": "service_account@project_name[.iam.gserviceaccount.com](.iam.gserviceaccount.com)"), again just a placeholder intended to be replaced with a real value.
* The partner ID for the deployment is defined here ( "partner_id": 999999 ), again values the need to be replaced for your deployment.  The top-level values for advertiser ID and custom bidding algorithm ID ("advertiser_id": 8888888,"cb_algo_id": 777777) are not for use when using the 'zone' objects as those objects have their own definition of advertiser_id and algorithm_id.  They are used for some of the lesser used ACTIONS like 'action_list_scripts' and 'action_remove_algorithm' that operate without going into the zone_array.
* There are two "zones".  In Bid2x, at least for a DV360 deployment, a zone is synonymous with a 'campaign'.  You can tell there are 2 zones being used in two ways.  First, the value for 'zones_to_process' contains two values ("zones_to_process": "C1,C2") and in the defined 'zone_array' there is a list of 2 object, each with a .name corresponding to either "C1" or "C2".  Of course, you can DEFINE a zone in the zone_array but choose not to operate on that zone by omitting it from the "zones_to_process" variable.
* Looking more closely at the zone object "C2" it is defined to operate within a given advertiser and campaign, using a specific custom bidding algorithm id ( "campaign_id": 11111111 ,"advertiser_id": 2222222, "algorithm_id": 3333333).  Once again these number are placeholders that need to be updated with specifics from your implementation.
* The OAuth file downloaded from GCP is client-secret.json ("json_auth_file": "client-secret.json") that will be looked for LOCALLY (i.e. not in the GCP bucket).  That is, at the time of writing of this document the expectation is that this file is available in the local directory during installation as it will be zipped up and copied to the image made by Cloud Build during the deployment of the Cloud Run Jobs image.  There is *some* consideration being given to making this file available in the GCS bucket but we have found that it doesn't change much (if at all) during the project's lifetime so there is minor benefit to having it in a location like GCS where it can be changed easily.
* The generated Custom Bidding Algorithms made by this configuration will be actioned over the two floodlights defined in the variable floodlight_id_list that currently contains placeholders to floodlight ids: ("floodlight_id_list": [1111111,2222222])
* And last but not least, what will this config actually DO?  Look at the 'action' variables to determine that:
    * `"action_list_algos": false,`
    * `"action_list_scripts": false,`
    * `"action_create_algorithm": false,`
    * `"action_update_spreadsheet": false,`
    * `"action_remove_algorithm": false,`
    * `"action_update_scripts": false,`
    * `"action_test": true,`
* In this case the action is set to perform a 'test'.  A test in bid2x generates the script and outputs it to the spreadsheet.  For a DV installation the output goes to the tab 'CB_Scripts' in the spreadsheet.  For a GTM/SA360 installation the output goes to the 'JS_Scripts' tab in the spreadsheet.  However, in this case recall that the spreadsheet id and url were both just placeholders, and the values for the zones and advertiser and more were also just placeholders… so actually running this config code will probably just throw an error for connecting to an invalid advertisers or opening a spreadsheet that doesn't exist.
* However, the action_test verb in the config is a great method to test your configuration without making any write-backs to either DV or GTM.
* For a **DV** installation the <span style="text-decoration:underline;">weekly run</span> config should have its `action_update_scripts` set to true.
* For a **DV** installation the <span style="text-decoration:underline;">daily run</span> config should have its `action_update_spreadsheet` set to true.
* For a **SA360/GTM** installation the <span style="text-decoration:underline;">weekly run</span> config should have its `action_date_scripts` set to true.


### Top level configuration items: {#top-level-configuration-items}

The top level configuration for the JSON file are those items contained in the top level set of curly braces ({ }).  These values are typically system-wide settings.


<table>
  <tr>
   <td><strong>Fieldname</strong>
   </td>
   <td><strong>Datatype</strong>
   </td>
   <td><strong>Description</strong>
   </td>
   <td><strong>Example</strong>
   </td>
   <td><strong>Legal Values</strong>
   </td>
   <td><strong>Default Value</strong>
   </td>
  </tr>
  <tr>
   <td>scopes
   </td>
   <td>list of strings
   </td>
   <td>The top level list of scopes that are used by the Python app to communicate with external APIs.
   </td>
   <td>"scopes": [     "https://www.googleapis.com/auth/display-video", "https://www.googleapis.com/auth/spreadsheets"
<p>
]
   </td>
   <td>Any list of Google API service strings.  Commonly used strings in the context of bid2x are:
<p>
'https://www.googleapis.com/auth/display-video'
<p>
'https://www.googleapis.com/auth/tagmanager.edit.containerversions',
<p>
'https://www.googleapis.com/auth/tagmanager.edit.containers',
<p>
'https://www.googleapis.com/auth/tagmanager.publish',
<p>
'https://www.googleapis.com/auth/tagmanager.readonly',
<p>
'https://www.googleapis.com/auth/tagmanager.delete.containers',
<p>
'https://www.googleapis.com/auth/spreadsheets'
   </td>
   <td>[    'https://www.googleapis.com/auth/display-video',  'https://www.googleapis.com/auth/spreadsheets',
<p>
]
   </td>
  </tr>
  <tr>
   <td>api_name
   </td>
   <td>string
   </td>
   <td>The name of the API service to connect to.
   </td>
   <td>"api_name": "displayvideo"
   </td>
   <td>"displayvideo" or "tagmanager"
   </td>
   <td>"displayvideo"
   </td>
  </tr>
  <tr>
   <td>api_version
   </td>
   <td>string
   </td>
   <td>The version of the API service to connect to.
   </td>
   <td>"api_version": "v3"
   </td>
   <td>"v1", "v2", or "v3"
   </td>
   <td>"v3"
   </td>
  </tr>
  <tr>
   <td>platform_type
   </td>
   <td>string
   </td>
   <td>This short string tells the system now to interpret the objects held in the
   </td>
   <td>"platform_type": "DV"
   </td>
   <td>"DV" or "GTM"
   </td>
   <td>"DV"
   </td>
  </tr>
  <tr>
   <td>debug
   </td>
   <td>boolean
   </td>
   <td>Boolean true/false flag that enables debugging statements to be printed to stdout from the bid2x main executable when it runs.  Since the executable usually runs in something like GCP Cloud Functions or GCP Cloud Run these output items are found in the logs.
   </td>
   <td>"debug": true
   </td>
   <td>true or false
   </td>
   <td>true
   </td>
  </tr>
  <tr>
   <td>trace
   </td>
   <td>boolean
   </td>
   <td>This Boolean flag enables a level of debugging text to stdout beyond that which the standard 'debug' offers.  Warning, the output from this gives A LOT of output but is helpful in trying to understand cases where there are problems.
   </td>
   <td>"trace": false
<p>

   </td>
   <td>true or false
   </td>
   <td>false
   </td>
  </tr>
  <tr>
   <td>defer_pattern
   </td>
   <td>boolean
   </td>
   <td>
   </td>
   <td>"defer_pattern": true
<p>

   </td>
   <td>
   </td>
   <td>false
   </td>
  </tr>
  <tr>
   <td>alternate_algorithm
   </td>
   <td>boolean
   </td>
   <td>Boolean flag that selects the creation of an alternate algorithm syntax.  Each sub-module implements the alternate algorithm in its own manner but for DV360 a custom bidding script using max_aggregate() is created when alternate_algorithm = false and an algorithm using compound 'if' statements is used when alternate_algorithm = true.
   </td>
   <td>"alternate_algorithm": false
<p>

   </td>
   <td>true or false
   </td>
   <td>false
   </td>
  </tr>
  <tr>
   <td>new_algo_name
   </td>
   <td>string
   </td>
   <td>When new custom bidding algorithms are made in DV360 the algorithms have an internal name and a display name.  The string set here is used to set the new algorithm name.
   </td>
   <td>"new_algo_name": "bid2Inventory"
<p>

   </td>
   <td>Any string DV360 would accept for an algorithm name.
   </td>
   <td>"bid2Inventory"
   </td>
  </tr>
  <tr>
   <td>new_algo_display_name
   </td>
   <td>string
   </td>
   <td>Custom Bidding algorithms in DV360 also have a 'display name'.  This string is used as the display name.
   </td>
   <td>"new_algo_display_name": "bid2Inventory"
<p>

   </td>
   <td>
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>line_item_name_pattern
   </td>
   <td>string
   </td>
   <td>When bid2x is used to interrogate a DV360 advertiser and populate the control spreadsheet with line items related to the bid2x project the line items sub to the advertiser ID will be inspected by name and matched against this string.  Any line items with a name containing a SUBSTRING that matches this string will be assumed to be part of the bid2x solution and will have it's information copied to the controlling Google Sheet.
   </td>
   <td>"line_item_name_pattern": "bid-to-inventory"
<p>

   </td>
   <td>Anything that matches your use case for the line items.  Many use "bid-to-inventory" as in the DV360 it allows them to quickly identity which Line Items are being managed through bid2x.  However, other names more suited to your implementation are encouraged.
   </td>
   <td>"bid-to-inventory"
   </td>
  </tr>
  <tr>
   <td>json_auth_file
   </td>
   <td>string (filename)
   </td>
   <td>Contains the name and possibly the path to a file containing the authentication file needed to connect to the connected products like DV360, Tag Manager, Google Sheets.  This is typically a client-secrets.json file created in GCP from a service account's profile.
   </td>
   <td>"json_auth_file": "client-secret.json"
<p>

   </td>
   <td>Filenames on their own will be assumed to be in the local file system.  For Cloud Run and Cloud Functions this means the config file needs to be part of the deployment ZIP file.
   </td>
   <td>"client-secret.json"
   </td>
  </tr>
  <tr>
   <td>cb_tmp_file_prefix
   </td>
   <td>string (partial path)
   </td>
   <td>For the DV360 solution, the upload of custom bidding algorithm scripts is actually much easier from a file as opposed from code.  In light of that, once the new script is computed in the code it is written to a temp file before upload.  This variable allows the location and name of this temp file to be controlled.  The filename is written as:
<p>
<code>[cb_tmp_file_prefix]_[zone name].txt.</code>
   </td>
   <td>"cb_tmp_file_prefix": "/tmp/cb_script"
<p>

   </td>
   <td>Any legal path prefix string.
   </td>
   <td>"/tmp/cb_script"
   </td>
  </tr>
  <tr>
   <td>cb_last_update_file_prefix
   </td>
   <td>string (partial path)
   </td>
   <td>This is a string containing the path to a temp file where the previous custom bidding upload string was saved as <code>[cb_last_update_file_prefix]_[zone name].txt</code>.
<p>
(Now deprecated as the state of the previous upload is now determined by downloading the current custom bidding script directly before uploading the new one).
   </td>
   <td>"cb_last_update_file_prefix": "last_upload"
<p>

   </td>
   <td>Any legal path prefix string.
   </td>
   <td>"last_upload"
   </td>
  </tr>
  <tr>
   <td>partner_id
   </td>
   <td>integer
   </td>
   <td>The partner_id setting at the top level of the configuration file is for use SPECIFICALLY with <a href="#action-items">actions</a> that are not related to general operation.  General operation is considered to be the <code>actions action_update_spreadsheet</code> and <code>action_update_scripts</code>.  These are steady-state operations that occur on a scheduled basis - updating the spreadsheet and updating the scripts in either DV or GTM.
<p>
The advertiser_id, and cb_algo_id variables are used with the
<p>
<code>action_remove_algorithm</code> action method.
   </td>
   <td>"partner_id": 999999
<p>

   </td>
   <td>Any legal partner_id that you have access to.
   </td>
   <td>The default value is a placeholder and not usable.  The default value needs to be replaced.
   </td>
  </tr>
  <tr>
   <td>advertiser_id
   </td>
   <td>integer
   </td>
   <td>See description for partner_id.
   </td>
   <td>"advertiser_id": 8888888
   </td>
   <td>Any legal advertiser_id.
   </td>
   <td>The default value is a placeholder and not usable.  The default value needs to be replaced.
   </td>
  </tr>
  <tr>
   <td>cb_algo_id
   </td>
   <td>integer
   </td>
   <td>See description for partner_id.
   </td>
   <td>"cb_algo_id": 777777
   </td>
   <td>Any legal custom bidding algorithm id.
   </td>
   <td>The default value is a placeholder and not usable.  The default value needs to be replaced.
   </td>
  </tr>
  <tr>
   <td>service_account_email
   </td>
   <td>string (valid service account email address)
   </td>
   <td>The service account email to be used in conjunction with the service account in play for the deployment.  This is normally the same service account email address specified in the json_auth_file.
   </td>
   <td>"service_account_email": "service_account@project_name.iam.gserviceaccount.com"
   </td>
   <td>Any string conforming to general email address rules that has sufficient authorization to use the necessary APIs.
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>zones_to_process
   </td>
   <td>string (comma delimited list)
   </td>
   <td>A comma delimited list of zone names to process during the current 'run'.  The scope of 'processing' in this context means performing whichever 'action' items are set to 'true'.
   </td>
   <td>"zones_to_process": "C1,C2"
   </td>
   <td>When bid2x loads this configuration item it is parsed into a list of names that are used during the run.  The names should match those of the zone_array elements.  Providing non-matching names may produce unexpected results.
   </td>
   <td>"c1,c2,c3,c4,c5'.  The default value is a placeholder and not usable.  The default value needs to be replaced
   </td>
  </tr>
  <tr>
   <td>floodlight_id_list
   </td>
   <td>list of integers
   </td>
   <td>When creating a DV360 custom bidding script a separate statement line is needed for each supported floodlight.  This config item is ALWAYS a list, even if there is only a single floodlight (it would in that case be just a list of 1 item).
   </td>
   <td>"floodlight_id_list": [
<p>
   1111111,
<p>
   2222222
<p>
]
   </td>
   <td>A list of floodlight IDs to apply custom bidding changes to.  The floodlight IDs need to belong to the associated partner_id or advertiser_id.
   </td>
   <td>The default value is a placeholder and not usable.  The default value needs to be replaced
   </td>
  </tr>
  <tr>
   <td>attr_model_id
   </td>
   <td>integer
   </td>
   <td>For DV360 this is the attribution model ID.  If you don't know this it's probably zero (0). Usually this value is non-zero if the customer is employing a non-last-touch attribution model.
   </td>
   <td>"attr_model_id": 0
   </td>
   <td>A valid attribution model ID or just zero.
   </td>
   <td>0
   </td>
  </tr>
  <tr>
   <td>bidding_factor_high
   </td>
   <td>integer
   </td>
   <td>The high watermark for the bidding factor.  Regardless of what is read from the controlling spreadsheet the maximum bidding factor that will be applied will be this number.
   </td>
   <td>"bidding_factor_high": 1000
<p>

   </td>
   <td>A positive number.
   </td>
   <td>1000
   </td>
  </tr>
  <tr>
   <td>bidding_factor_low
   </td>
   <td>integer
   </td>
   <td>The low watermark for the bidding factor.  Regardless of what is read from the spreadsheet the minimum bidding factor will be this number.
   </td>
   <td>"bidding_factor_low": 0
   </td>
   <td>A positive number or zero less than bidding_factor_high.
   </td>
   <td>0
   </td>
  </tr>
</table>



### Action items: {#action-items}

Key to understanding the way bid2x operates is in knowing how the action items in the config work.  By default ALL action items are false so that bid2x would just start and stop without doing anything.  By setting one of the actions to true the user is setting how the rest of the file will be interpreted and used.


<table>
  <tr>
   <td><strong>Fieldname</strong>
   </td>
   <td><strong>Datatype</strong>
   </td>
   <td><strong>Description</strong>
   </td>
   <td><strong>Example</strong>
   </td>
   <td><strong>Legal Values</strong>
   </td>
   <td><strong>Default Value</strong>
   </td>
  </tr>
  <tr>
   <td>action_list_algos
   </td>
   <td>boolean
   </td>
   <td>This action lists all custom bidding algorithms for the supplied advertiser_id (fill in advertiser_id in JSON or pass <code>--advertiser</code> option on command line)
   </td>
   <td>"action_list_algos": false
   </td>
   <td>true or false
   </td>
   <td>false
   </td>
  </tr>
  <tr>
   <td>action_list_scripts
   </td>
   <td>boolean
   </td>
   <td>This action walks through all zones and lists the custom bidding scripts for each advertiser.
   </td>
   <td>"action_list_scripts": false
   </td>
   <td>true or false
   </td>
   <td>false
   </td>
  </tr>
  <tr>
   <td>action_create_algorithm
   </td>
   <td>boolean
   </td>
   <td>This action creates a new custom bidding algorithm for each supplied zone/campaign.  Supply a JSON config file with zones containing advertiser_id and name elements and this action will create new algorithms in each campaign using <code>new_algo_name</code> and <code>new_algo_display_name</code> settings for guidance.
   </td>
   <td>"action_create_algorithm": false
   </td>
   <td>true or false
   </td>
   <td>false
   </td>
  </tr>
  <tr>
   <td>action_update_spreadsheet
   </td>
   <td>boolean
   </td>
   <td>This action walks the passed zone list, connects to DV, and populates a Google Sheet tab for each campaign with the following items:
<ul>

<li>entityStatus</li>

<li>lineItemID</li>

<li>displayName</li>

<li>lineItemType</li>

<li>campaignID</li>

<li>advertiserID

<p>
for each line item that matches the <code>line_item_name_pattern</code> setting.</li>
</ul>
   </td>
   <td>"action_update_spreadsheet": false
   </td>
   <td>true or false
   </td>
   <td>false
   </td>
  </tr>
  <tr>
   <td>action_remove_algorithm
   </td>
   <td>boolean
   </td>
   <td>This action item removes the algorithm ID specified in the <code>cb_algo_id</code> setting.  When used from the command line this action is <code>-ar</code> or <code>--action_remove</code> and should be used with argument <code>-g</code> or <code>--algorithm</code> to specify the numeric value of the algorithm_id to be removed.
   </td>
   <td>"action_remove_algorithm": false
   </td>
   <td>true or false
   </td>
   <td>false
   </td>
  </tr>
  <tr>
   <td>action_update_scripts
   </td>
   <td>boolean
   </td>
   <td>This is the main action for the bid2x system whereby is uses the supplied zone info to walk through each zone, connect to the control Google Sheet, compose the updated script and upload the script to either DV or GTM.
   </td>
   <td>"action_update_scripts": false,
   </td>
   <td>true or false
   </td>
   <td>false
   </td>
  </tr>
  <tr>
   <td>action_test
   </td>
   <td>boolean
   </td>
   <td>The 'action_test' setting allows you to do a dry run of the system writing the script that would be uploaded to DV or GTM to a sheet within Google Sheets.  In Google Sheets the tab for this output for DV360 is, by default, named 'CB_Scripts' and the tab for GTM/SA360 output is named 'JS_Scripts'.
   </td>
   <td>"action_test": true
   </td>
   <td>true or false
   </td>
   <td>false
   </td>
  </tr>
</table>



### Sheet configuration items: {#sheet-configuration-items}

Whether you're running a DV360 or an GTM/SA360 configuration of bid2x, a Google Sheets spreadsheet is used for monitoring and control.  The setting of the configuration items under the 'sheet' scope is thus vital to ensure it's working effectively.


<table>
  <tr>
   <td><strong>Fieldname</strong>
   </td>
   <td><strong>Datatype</strong>
   </td>
   <td><strong>Description</strong>
   </td>
   <td><strong>Example</strong>
   </td>
   <td><strong>Legal Values</strong>
   </td>
   <td><strong>Default Value</strong>
   </td>
  </tr>
  <tr>
   <td>sheet_id
   </td>
   <td>string
   </td>
   <td>The ID of the bid2x control sheet for this implementation.
   </td>
   <td>"sheet_id": "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGH",
   </td>
   <td>32 byte UUID string
   </td>
   <td>The default value is a placeholder and not usable.  The default value needs to be replaced.
   </td>
  </tr>
  <tr>
   <td>sheet_url
   </td>
   <td>string
   </td>
   <td>The URL of the control sheet for this implementation.
   </td>
   <td>"sheet_url": "https://docs.google.com/spreadsheets/d/abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGH/edit",
   </td>
   <td>Valid path to a Google Sheet, as a string.
   </td>
   <td>The default value is a placeholder and not usable.  The default value needs to be replaced.
   </td>
  </tr>
  <tr>
   <td>json_auth_file
   </td>
   <td>string (filename)
   </td>
   <td>The path/filename of the auth file with an entity capable of accessing the Sheets API and had access to the sheet mentioned in sheet_id and sheet_url.
   </td>
   <td>"json_auth_file": "client-secret.json",
   </td>
   <td>A valid filename and/or path to a filename.
   </td>
   <td>This is typically the exact same JSON pointed to by the top level configuration section setting.
   </td>
  </tr>
  <tr>
   <td>column_status
   </td>
   <td>string
   </td>
   <td>The column in which the line item status will be written in the use of action_update_spreadsheet.  Recall that for a line item to show up in this list it must match the line_item_name_pattern setting.
   </td>
   <td>"column_status": "A",
   </td>
   <td>Any column A to ZZZ, as a string.
   </td>
   <td>"A"
   </td>
  </tr>
  <tr>
   <td>column_lineitem_id
   </td>
   <td>string
   </td>
   <td>The column in which the line item ID will be written in the use of action_update_spreadsheet.    Recall that for a line item to show up in this list it must match the line_item_name_pattern setting.
   </td>
   <td>"column_lineitem_id": "B",
<p>

   </td>
   <td>Any column A to ZZZ, as a string.
   </td>
   <td>"B"
   </td>
  </tr>
  <tr>
   <td>column_lineitem_name
   </td>
   <td>string
   </td>
   <td>The column in which the line item name will be written in the use of action_update_spreadsheet.    Recall that for a line item to show up in this list it must match the line_item_name_pattern setting.
   </td>
   <td>"column_lineitem_name": "C",
   </td>
   <td>Any column A to ZZZ, as a string.
   </td>
   <td>"C"
   </td>
  </tr>
  <tr>
   <td>column_lineitem_type
   </td>
   <td>string
   </td>
   <td>The column in which the line item type will be written in the use of action_update_spreadsheet.    Recall that for a line item to show up in this list it must match the line_item_name_pattern setting.
   </td>
   <td>"column_lineitem_type": "D",
   </td>
   <td>Any column A to ZZZ, as a string.
   </td>
   <td>"D"
   </td>
  </tr>
  <tr>
   <td>column_campaign_id
   </td>
   <td>string
   </td>
   <td>The column in which the campaign_id associated with the line item will be written in the use of action_update_spreadsheet.    Recall that for a line item to show up in this list it must match the line_item_name_pattern setting.
   </td>
   <td>"column_campaign_id": "E",
   </td>
   <td>Any column A to ZZZ, as a string.
   </td>
   <td>"E"
   </td>
  </tr>
  <tr>
   <td>column_advertiser_id
   </td>
   <td>string
   </td>
   <td>The column in which the advertiser_id associated with the line item will be written in the use of action_update_spreadsheet.    Recall that for a line item to show up in this list it must match the line_item_name_pattern setting.
   </td>
   <td>"column_advertiser_id": "F",
   </td>
   <td>Any column A to ZZZ, as a string.
   </td>
   <td>"F"
   </td>
  </tr>
  <tr>
   <td>column_custom_bidding
   </td>
   <td>string
   </td>
   <td>The column that will contain a Yes or No text (usually a button) to indicate whether this line item is participating in the script generation.
   </td>
   <td>"column_custom_bidding": "K"
   </td>
   <td>Any column A to ZZZ, as a string.
   </td>
   <td>"K"
   </td>
  </tr>
  <tr>
   <td>debug
   </td>
   <td>boolean
   </td>
   <td>A debug flag specifically for Google Sheet interactions.  Helps to debug Sheet connectivity issues.
   </td>
   <td>"debug": false
   </td>
   <td>true or false
   </td>
   <td>false
   </td>
  </tr>
  <tr>
   <td>trace
   </td>
   <td>boolean
   </td>
   <td>A trace flag that is specific to Google Sheet interactions.
   </td>
   <td>"trace": false
   </td>
   <td>true or false
   </td>
   <td>false
   </td>
  </tr>
</table>



### Zone_array configuration items {#zone_array-configuration-items}


#### For DV360 campaigns / zones {#for-dv360-campaigns-zones}

In DV360 deployments the zones in the configuration files are listed under the top level item 'zone_array' and represent campaigns.


<table>
  <tr>
   <td><strong>Fieldname</strong>
   </td>
   <td><strong>Datatype</strong>
   </td>
   <td><strong>Description</strong>
   </td>
   <td><strong>Example</strong>
   </td>
   <td><strong>Legal Values</strong>
   </td>
   <td><strong>Default Value</strong>
   </td>
  </tr>
  <tr>
   <td>name
   </td>
   <td>string
   </td>
   <td>The name of the campaign or zone.  Quite often this name is used for geographic separation between campaigns and that is the origin of the name 'zone' as the initial clients for bid2x had trafficking setups that wanted different treatment per 'zone.
<p>
This name will show up in the scripts and also in the Google Sheets tabs.
   </td>
   <td>"name": "C1"
   </td>
   <td>Strings, but probably under 10-12 characters as too long and Sheets tab names could be cumbersome.
   </td>
   <td>C1
   </td>
  </tr>
  <tr>
   <td>campaign_id
   </td>
   <td>integer
   </td>
   <td>This is the campaign ID that the custom bidding script applies to.  The campaign can often be a decent approximation of a zone.
   </td>
   <td>"campaign_id": 66666666
   </td>
   <td>Must be a legal campaign_id in DV360 that the service account has read/write access to.
   </td>
   <td>The default value is spurious and needs to be replaced with a valid value.
   </td>
  </tr>
  <tr>
   <td>advertiser_id
   </td>
   <td>integer
   </td>
   <td>The advertiser_id associated with the provided campaign_id.
   </td>
   <td>"advertiser_id": 2222222
   </td>
   <td>Must be a legal advertiser_id in the context of DV360.
   </td>
   <td>The default value is spurious and needs to be replaced with a valid value.
   </td>
  </tr>
  <tr>
   <td>algorithm_id
   </td>
   <td>integer
   </td>
   <td>The algorithm_id that will be used for the publishing of custom bidding scripts for this zone.
<p>
Note: algorithm_ids must be PRE-CREATED.  Custom Bidding Algorithms (which have the associated algorithm_id) can be created in the DV360 User Interface -or- can be created through the bid2x tool using the <code>-ac</code> / <code>--action_create</code> command line argument or by configuring a JSON file specifically for algorithm creation with <code>action_create_algorithm</code> set to true.
   </td>
   <td>"algorithm_id": 5555555
   </td>
   <td>Must be a legal algorithm_id in the context of DV360.
   </td>
   <td>The default value is spurious and needs to be replaced with a valid value.
   </td>
  </tr>
  <tr>
   <td>cb_algorithm
   </td>
   <td>string
   </td>
   <td>Currently unused.
   </td>
   <td>"cb_algorithm": ""
   </td>
   <td>Any string
   </td>
   <td>""
   </td>
  </tr>
  <tr>
   <td>debug
   </td>
   <td>boolean
   </td>
   <td>A debug flag designed for zone-specific actions.
   </td>
   <td>"debug": true
   </td>
   <td>true or false
   </td>
   <td>false
   </td>
  </tr>
  <tr>
   <td>update_row
   </td>
   <td>integer
   </td>
   <td>An integer specifying which cell ROW will be updated in the Google Sheets status tab (default name 'CB_Scripts') when a custom bidding script for this zone is updated using a call to <code>ACTION_UPDATE_SCRIPTS</code> or the command line arg <code>-au</code> / <code>--action_update</code>.
   </td>
   <td>"update_row": 3
   </td>
   <td>An integer row
   </td>
   <td>The JSON config file should be crafted such that the update rows and columns do not overlap and make sense on the CB_Scripts sheet.  No internal checking done on these values.
   </td>
  </tr>
  <tr>
   <td>update_col
   </td>
   <td>integer
   </td>
   <td>An integer specifying which cell COLUMN will be updated in the Google Sheets status tab (default name 'CB_Scripts') when a custom bidding script for this zone is updated using a call to <code>ACTION_UPDATE_SCRIPTS</code> or the command line arg <code>-au</code> / <code>--action_update</code>.
   </td>
   <td>"update_col": 2
   </td>
   <td>An integer column (not a letter). Column A = 1, column B = 2, etc.
   </td>
   <td>The JSON config file should be crafted such that the update rows and columns do not overlap and make sense on the CB_Scripts sheet.  No internal checking done on these values.
   </td>
  </tr>
  <tr>
   <td>test_row
   </td>
   <td>integer
   </td>
   <td>An integer specifying which cell ROW will be updated in the Google Sheets status tab (default name 'CB_Scripts') when a custom bidding script for this zone is generated using a call to <code>ACTION_TEST</code> or the command line arg <code>-at</code> / <code>--action_test</code>.
   </td>
   <td>"test_row": 3
   </td>
   <td>An integer row
   </td>
   <td>The JSON config file should be crafted such that the update rows and columns do not overlap and make sense on the CB_Scripts sheet.  No internal checking done on these values.
   </td>
  </tr>
  <tr>
   <td>test_col
   </td>
   <td>integer
   </td>
   <td>An integer specifying which cell COLUMN will be updated in the Google Sheets status tab (default name 'CB_Scripts') when a custom bidding script for this zone is generated using a call to <code>ACTION_TEST</code> or the command line arg <code>-at</code> or <code>--action_test</code>.
   </td>
   <td>"test_col": 4
   </td>
   <td>An integer column (not a letter). Column A = 1, column B = 2, etc.
   </td>
   <td>The JSON config file should be crafted such that the update rows and columns do not overlap and make sense on the CB_Scripts sheet.  No internal checking done on these values.
   </td>
  </tr>
</table>



#### For GTM/SA360 {#for-gtm-sa360}


<table>
  <tr>
   <td><strong>Fieldname</strong>
   </td>
   <td><strong>Datatype</strong>
   </td>
   <td><strong>Description</strong>
   </td>
   <td><strong>Example</strong>
   </td>
   <td><strong>Legal Values</strong>
   </td>
   <td><strong>Default Value</strong>
   </td>
  </tr>
  <tr>
   <td>name
   </td>
   <td>string
   </td>
   <td>The name of the 'zone' or area or campaign that this GTM dynamic tag will be applied to.
   </td>
   <td>"name": "C1"'
   </td>
   <td>Any string
   </td>
   <td>GTM_&lt;zone#>
   </td>
  </tr>
  <tr>
   <td>account_id
   </td>
   <td>integer
   </td>
   <td>The GTM account id.
   </td>
   <td>"account_id": 11111111
   </td>
   <td>Any legal GTM account ID that you have access to.
   </td>
   <td>The default value is spurious and needs to be replaced with a valid value.
   </td>
  </tr>
  <tr>
   <td>container_id
   </td>
   <td>integer
   </td>
   <td>The container_id within which the tag that will be modified exists.
   </td>
   <td>"container_id": 222222
   </td>
   <td>Any legal GTM container_id.
   </td>
   <td>The default value is spurious and needs to be replaced with a valid value.
   </td>
  </tr>
  <tr>
   <td>workspace_id
   </td>
   <td>integer
   </td>
   <td>The workspace_id that will be modified
   </td>
   <td>"workspace_id": 33333
   </td>
   <td>Any legal workspace ID.
   </td>
   <td>The default value is spurious and needs to be replaced with a valid value.
   </td>
  </tr>
  <tr>
   <td>variable_id
   </td>
   <td>integer
   </td>
   <td>The ID of the variable in GTM that will be modified with updated JavaScript based on the most recent customer data.
   </td>
   <td>"variable_id": 4444
   </td>
   <td>Any legal variable ID.
   </td>
   <td>The default value is spurious and needs to be replaced with a valid value.
   </td>
  </tr>
  <tr>
   <td>update_row
   </td>
   <td>integer
   </td>
   <td>An integer specifying which cell ROW will be updated in the Google Sheets status tab (default name 'VB_Scripts' for GTM/SA360) when the JAvaScript-based tag for this zone is updated using a call to <code>ACTION_UPDATE_SCRIPTS</code> or the command line arg <code>-au</code> / <code>--action_update</code>.
   </td>
   <td>"update_row": 2
   </td>
   <td>An integer row
   </td>
   <td>The default value is a placeholder and needs to be replaced with a valid value.
   </td>
  </tr>
  <tr>
   <td>update_col
   </td>
   <td>integer
   </td>
   <td>An integer specifying which cell COLUMN will be updated in the Google Sheets status tab (default name 'VB_Scripts' for GTM/SA360) when the JAvaScript-based tag for this zone is updated using a call to <code>ACTION_UPDATE_SCRIPTS</code> or the command line arg <code>-au</code> / <code>--action_update</code>.
   </td>
   <td>"update_col": 4
   </td>
   <td>An integer column (not a letter). Column A = 1, column B = 2, etc.
   </td>
   <td>The default value is a placeholder and needs to be replaced with a valid value.
   </td>
  </tr>
  <tr>
   <td>test_row
   </td>
   <td>integer
   </td>
   <td>An integer specifying which cell ROW will be updated in the Google Sheets status tab (default name 'VB_Scripts') when JavaScript for this zone is generated using a call to <code>ACTION_TEST</code> or the command line arg <code>-at</code> / <code>--action_test.</code>
   </td>
   <td>"test_row": 2
   </td>
   <td>An integer row
   </td>
   <td>The default value is a placeholder and needs to be replaced with a valid value.
   </td>
  </tr>
  <tr>
   <td>test_col
   </td>
   <td>integer
   </td>
   <td>An integer specifying which cell COLUMN will be updated in the Google Sheets status tab (default name 'VB_Scripts') when JavaScript for this zone is generated using a call to <code>ACTION_TEST</code> or the command line arg <code>-at</code> / <code>--action_test.</code>
   </td>
   <td>"test_col": 8
   </td>
   <td>An integer column (not a letter). Column A = 1, column B = 2, etc.
   </td>
   <td>The default value is a placeholder and needs to be replaced with a valid value.
   </td>
  </tr>
</table>



## Implementation notes {#implementation-notes}


### Sheets input / output {#sheets-input-output}

When connecting to 1st party company data BigQuery is recommended because it allows control over frequency of refresh.  Not all connectors provide the same flexibility so investigate whether the connector you're going to use is reliable, updates the sheet regardless of if it's open, and can transfer the quantity and variety of data you will need.

It has been found that importing raw data from your 1st party data source into a separate tab is a best practice.  From there, generate the formulae you will need to transform and select the data and get it into the various campaign / zone specific tabs.


### Campaigns {#campaigns}

For DV360-connected deployment a campaign is your gateway to select the Line Items you want to operate on and include in the custom bidding rule.  For this reason DV360 deployments utilize the zone/campaign named Sheets tab to organize the line items.

For the SA360 deployment the emphasis is on gathering up the information per SA campaign to write the JavaScript function for within the tag in GTM.  These deployments use their capaign-specific tab in Sheets for gathering up and aligning the 1st party data. (Update this)


### Supported Line Item Types in DV360 {#supported-line-item-types-in-dv360}

All types of line items in DV360 are supported with the exception of the following types:


```
    'LINE_ITEM_TYPE_YOUTUBE_AND_PARTNERS_NON_SKIPPABLE'
    'LINE_ITEM_TYPE_YOUTUBE_AND_PARTNERS_REACH'
    'LINE_ITEM_TYPE_YOUTUBE_AND_PARTNERS_ACTION'
```


These types of line items are NOT supported due to their inability to have bidding adjusted per line item, which is the point of bid2x.


### DV360 Line item Naming {#dv360-line-item-naming}

For bid2x to work in the smoothest manner it is important to adopt a naming convention for your line items that can work to your benefit.  The configuration files provides a setting called 'line_item_name_pattern' that should be set to a SUBSTRING of the name of line items you want to participate in this system.

For example, consider the following line item names:


```
    display_washington_en_bid-to-inventory_desktop_product1
    display_oregon_en_bid-to-inventory_mobile_product3
    display_california_sp_bid-to-inventory_desktop_product1
    display_california_sp_mobile_product2
```


With the default setting of line_item_name_pattern equal to "bid-to-inventory" the first 3 line items would match and would show up in the control Google Sheet but the last line item, that does not contain the substring 'bid-to-inventory', does not match and would not be included in the solution.


### Frequency of Script Updates {#frequency-of-script-updates}

For both DV and SA some time is needed for the uploaded scripts to work in an optimal manner.

For DV, once the new script is uploaded the underlying system will train on the new ruleset for a time before implementing.  Worst case scenario this could take 24 hours but it is often the case that a new script is running within 1-2 hours up being updated.  If this is the very first time a custom bidding script is being uploaded to this campaign then there will be no coverage until the script is marked as active in DV360.  However, if this is a subsequent update to an existing script the previous script will continue to be used until the new script is ready to be used, so you'll be covered.

For SA, once the script is updated and published in Google Tag Manager, new sessions on the web will start using the new dynamic variable script immediately.  However, SA needs some time to adjust to the new script as it learns about the changes to the underlying variables so it could be a day or two before changes from the newly updated script have a demonstrable effect on the bidding.

In either case this means that the time between script updates needs to be on the order of days.  We recommend a weekly change to allow the system to stabilize using the updates and show results.  Clearly there is a tradeoff between the stability of a script being active for many days and the staleness of the real-time data that helped write the script.  It is for this reason that bid2x is designed to work well for 'weekly realtime' data but not for scenarios where minute-by-minute or hourly changes are desired.


### Start-up and call from Google Cloud Scheduler {#start-up-and-call-from-google-cloud-scheduler}

Due to Cloud Functions becoming deprecated in favour of Cloud Run Jobs, bid2x has changed and moved the compute portion of the system.  What was previously executed in a Cloud Functions environment now operates through Cloud Run Jobs.  Additionally, the previous mechanism by which the Cloud Function was called via a PubSub message has been altered since Cloud Run Jobs are called directly from Cloud Scheduler as a type of API call.

Refer to the section detailing the installation script for the details.


## Installation script {#installation-script}

Core to deploying bid2x is the install script.  This is a BASH script that utilizes the gcloud command to perform a one-shot install in your client's environment.  Depending on how you obtained the bid2x code you may need to make the install script executable with a command similar to:


```
    chmod +x install.sh
```


The installation script is designed to work within the Cloud Shell environment of GCP.  It *may* work in other environments, but it also may not.


### Installer Prerequisites {#installer-prerequisites}

Get access to the deployment environment and ensure you have the right permissions to do the following:



* Activate APIs
    * gcloud services enable {api}.googleapis.com, where api is ALL of the following:
        * "artifactregistry"
        * "cloudbuild"
        * "cloudscheduler"
        * "displayvideo" (if installing for DV360)
        * "logging"
        * "run"
        * "sheets"
        * "storage-api"
        * "tagmanager" (if installing for GTM/SA360)
    * These APIs will be activated with the rights of the person running the script.
* Add IAM rights to service accounts:
    * The local user running the installer script will attempt to add
        * roles/cloudscheduler.serviceAgent
    * to the defined SERVICE_ACCOUNT
    * The local user running the installer script will attempt to add
        * roles/run.invoker
    * to the defined INVOKER_SERVICE_ACCOUNT
    * The local user running the installer script will attempt to add
        * roles/storage.objectViewer
    * to the defined INVOKER SERVICE ACCOUNT
* Delete old installations, specifically:
    * gcloud run jobs delete &lt;named-job>
    * gcloud scheduler jobs delete &lt;named-schedule>
* Deploy a new Cloud Run job, specifically:
    * gcloud run jobs deploy &lt;job name>
* Make a new Cloud Scheduler event:
    * gcloud scheduler jobs create http &lt;named job>


### Installer User-Definable Parameters {#installer-user-definable-parameters}

The top of the installation script file contains around 200 lines of code that are expected to be modified by the person doing the installation.  Here is the contents of those lines as of the writing of this document:


```
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

# The name given to the Cloud Run Job for the weekly run.  This is the name
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


#### Main Project Parameters {#main-project-parameters}


<table>
  <tr>
   <td>PROJECT
   </td>
   <td>Set this to the GCP project name (not the ID) that you are deploying into.
<p>
If you're not sure what the current project is use the command:
<p>
<code>gcloud config get-value project</code>
<p>
Default: bid2x-deploy-test
<p>
(don't use the default value)
   </td>
  </tr>
  <tr>
   <td>REGION
   </td>
   <td>Set this to the GCP region you are deploying in (NOT THE ZONE i.e. should not end with 'a' or 'b' or whatever designates a zone for your locale).
<p>
Default: us-central1
   </td>
  </tr>
  <tr>
   <td>TIMEZONE
   </td>
   <td>The timezone you want to use for the CRON jobs. Note that the default timezone of the GCP Cloud Shell is UTC (Universal Coordinated Time) so be aware that by default there are multiple time zones in play that need to be considered.
<p>
Default: America/Toronto
<p>
(because isn't that the centre of the universe? 🤪)
   </td>
  </tr>
  <tr>
   <td>LOG_FILE
   </td>
   <td>File that <span style="text-decoration:underline;">the most current</span> installation log will be written to.  See the section dedicated to the Installation Log file for more details.
<p>
Default: bid2x_installer.log
   </td>
  </tr>
  <tr>
   <td>BUCKET_NAME
   </td>
   <td>Cloud Storage config container unique name (do not include 'gs://'').  This is the bucket in your project where the installer will copy your configuration JSON file and where the Cloud Run Job that performs the weekly or daily bid2x action will, by default, look for it's config.
<p>
Default bucket name is auto-generated as: '&lt;project-name>-config'.
   </td>
  </tr>
  <tr>
   <td>DEPOLYMENT_TYPE
   </td>
   <td>Bid2x deployment type.
<p>
Can be 'DV' or 'SA'.
   </td>
  </tr>
  <tr>
   <td>QUIET
   </td>
   <td>Quite mode flag.  Use "--quiet" to force quiet mode on the gcloud command, otherwise use "" (empty string) and quite mode will NOT be used with gcloud commands.
<p>
Warning: running without --quiet can make some commands interactive and thus require the answering of (Y/N) questions during the install.
   </td>
  </tr>
</table>



#### Virtual Machine Environment Parameters {#virtual-machine-environment-parameters}


<table>
  <tr>
   <td>CPU
   </td>
   <td>Cloud Run Jobs deployment cpu default for bid2x.  A single CPU='1' is usually sufficient for bid2x.
<p>
Default: 1 (as a string)
   </td>
  </tr>
  <tr>
   <td>MEMORY
   </td>
   <td>Cloud Run Jobs deployment memory default for bid2x. This number CAN be increased when needed, for example ='1Gi' or ='2Gi'.
<p>
Some DV trafficking profiles can contain a LARGE number of Line Items in a campaign and a large download of Line Items can exhaust memory (watch the logs). Don't be afraid to increase this number as needed.
<p>
Default: '512Mi'
   </td>
  </tr>
</table>



#### Service Account Parameters {#service-account-parameters}


<table>
  <tr>
   <td>SERVICE_ACCOUNT
   </td>
   <td>Service account used for IAM calls and "cloud run jobs deploy" commands.
<p>
Default: "bid2x-service@&lt;PROJECT>.iam.gserviceaccount.com"
   </td>
  </tr>
  <tr>
   <td>INVOKER_SERVICE_ACCOUNT
   </td>
   <td>The SA that will RUN the Cloud Run command (i.e. with run.jobs.run permission).
<p>
Default: "bid2x-service@${PROJECT}.iam.gserviceaccount.com"
   </td>
  </tr>
</table>


*Note: having both service accounts as the same value <span style="text-decoration:underline;">is a viable configuration</span>.  However, there are some deployments where it is desired to have a service account that runs the jobs be a more 'locked down' service account, capable only of running existing jobs, not able to deploy new jobs or make IAM calls.  Hence, the discrimination between the two accounts.


#### Cloud Run Job Detail Parameters {#cloud-run-job-detail-parameters}


<table>
  <tr>
   <td>WEEKLY_CLOUD_RUN_JOB_NAME
   </td>
   <td>The name given to the Cloud Run Job for the weekly run.  This is the name of the Cloud Run job in the UI.
<p>
Default: bid2x-weekly
   </td>
  </tr>
  <tr>
   <td>WEEKLY_CRON_SCHEDULE
   </td>
   <td>A string containing a cron-style config for the schedule.
<p>
&lt;min 0-60,*> &lt;hour 0-23,*> &lt;day 1-31,*> &lt;month 1-12,*> &lt;day of week 1-7,*>.
<p>
The default of "0 20 * * 7" is a schedule for Sundays(7) at 8pm (20:00) in the timezone defined in the TIMEZONE variable earlier in the file.
   </td>
  </tr>
  <tr>
   <td>WEEKLY_CONFIG
   </td>
   <td>The bid2x configuration JSON file that contains the action to perform weekly.  This is usually action_update_scripts.
<p>
This file should already exist and be readable; as there is a test for the existence of this file in the pre-run checks.
<p>
Default: sample_config_dv.json
<p>
(make a new file as this is just a sample file)
<p>
Tip: uses gs://&lt;bucketname>/file.json to load from GCS bucket.
   </td>
  </tr>
  <tr>
   <td>WEEKLY_SCHEDULER_JOB_NAME
   </td>
   <td>The name shown in the Cloud Scheduler UI for this configuration item.
<p>
Default: "&lt;WEEKLY_CLOUD_RUN_JOB_NAME>-scheduled-update"
   </td>
  </tr>
  <tr>
   <td>WEEKLY_ARGS
   </td>
   <td>A comma-separated list of command-line args after "python main.py". See the help text on bid2x to see the full list & defaults. (python main.py --help).
<p>
Default: "-i,${WEEKLY_CONFIG}"
<p>
That is, the default tells the python code to load the config file using the -i argument.
<p>
Example:
<p>
<code>python main.py -i sample_config_dv.json</code>
<p>
or
<p>
<code>python main.py -i gs://my-project-config/dv_weekly.json</code>
   </td>
  </tr>
  <tr>
   <td>DAILY_CLOUD_RUN_JOB_NAME
   </td>
   <td>The name given to the Cloud Run Job for the daily run (DV only).  This is the name of the Cloud Run job in the UI.
<p>
Default: bid2x-daily
   </td>
  </tr>
  <tr>
   <td>DAILY_CRON_SCHEDULE
   </td>
   <td>A string containing a cron-style config for the schedule.
<p>
&lt;min 0-60,*> &lt;hour 0-23,*> &lt;day 1-31,*> &lt;month 1-12,*> &lt;day of week 1-7,*>.
<p>
The default of "0 4 * * *" is a schedule for every day at 4:00am" in the timezone defined in the TIMEZONE variable earlier in the file.
   </td>
  </tr>
  <tr>
   <td>DAILY_CONFIG
   </td>
   <td>The bid2x configuration JSON file that contains the action to perform daily.  This is usually action_update_spreadsheet.
<p>
This file should already exist and be readable; as there is a test for the existence of this file in the pre-run checks.
<p>
Default: sample_config_dv.json
<p>
(make a new file as this is just a sample file)
<p>
Tip: uses gs://&lt;bucketname>/file.json to load from GCS bucket.
   </td>
  </tr>
  <tr>
   <td>DAILY_SCHEDULER_JOB_NAME
   </td>
   <td>The name shown in the Cloud Scheduler UI for this configuration item.
<p>
Default: "&lt;DAILY_CLOUD_RUN_JOB_NAME>-scheduled-update"
   </td>
  </tr>
  <tr>
   <td>DAILY_ARGS
   </td>
   <td>The daily config file is usually a JSON with 'action_update_spreadsheet' set to true.
<p>
Default: "-i,${DAILY_CONFIG}"
<p>
Example:
<p>
<code>python main.py -i sample_config_dv.json</code>
<p>
or
<p>
<code>python main.py -i gs://my-project-config/dv_daily.json</code>
   </td>
  </tr>
</table>



#### Installation Control Flags {#installation-control-flags}

By default leave all control flags as 1 to run all parts of the installer. If you're having some installation issues (it happens) you can adjust the values to get only portions of the installation to run.


<table>
  <tr>
   <td>SET_UP_ENVIRONMENT
   </td>
   <td>Run set up environment section.  This consists of little more than a gcloud command to set the correct project but may be expanded later.
<p>
Default: 1 (i.e. perform this portion of the install)
   </td>
  </tr>
  <tr>
   <td>PRE_RUN_CHECKS
   </td>
   <td>Run the pre-run checks portion of the installer.  This section checks for the existence of the config files you are referring to in the installer configuration AND checks for the existence of the SERVICE_ACCOUNT.
<p>
Default: 1 (i.e. run it, use 0 to skip)
   </td>
  </tr>
  <tr>
   <td>ACTIVATE_APIS
   </td>
   <td>Run the portion of the installer that activates the various APIs that need to be enabled in order for bid2x to operate properly.
<p>
Default: 1 (i.e. run it, use 0 to skip)
   </td>
  </tr>
  <tr>
   <td>GRANT_PERMISSIONS
   </td>
   <td>Run the portion of the installer that grants permissions to the SERVICE_ACCOUNT and the INVOKER_SERVICE_ACCOUNT.  Sometimes you are given a service account already provisioned or are running in an environment where you have no IAM rights.  So, it's common that this section might be disabled.
<p>
Default: 1 (i.e. run it, use 0 to skip)
   </td>
  </tr>
  <tr>
   <td>DELETE_OLD_INSTALL
   </td>
   <td>Run the portion of the installer that deletes old installs.
<p>
Default: 1 (i.e. run it, use 0 to skip)
   </td>
  </tr>
  <tr>
   <td>GCS_OPERATIONS
   </td>
   <td>Run the portion of the installer that ensures the creation of a bucket and copies the config file(s) to that bucket for use by bid2x.
<p>
Default: 1 (i.e. run it, use 0 to skip)
   </td>
  </tr>
  <tr>
   <td>DEPLOY_JOBS
   </td>
   <td>Run the portion of the installer that creates the cloud run job deployment(s).  This section collects the code and configuration files, uses cloud build to generate a Docker environment, and deploys.
<p>
Default: 1 (i.e. run it, use 0 to skip)
   </td>
  </tr>
  <tr>
   <td>CREATE_SCHEDULER_JOBS
   </td>
   <td>Run the portion of the installer that creates Cloud Scheduler jobs that call the Cloud Run Job deployments at specific times/dates.
<p>
Default: 1 (i.e. run it, use 0 to skip)
   </td>
  </tr>
</table>



### Installation Log file {#installation-log-file}

Every time you run the install.sh script it generates a log file controlled by the name LOG_FILE within the top portion of the script itself.  By default this is bid2x_installer.log.  This file is always checked for upon running the installer and will be backed up to a new name with an extension using the time/date you created the old install log.  In this way, log files are NEVER overwritten and there is always a full traceable path of what you did during the installation complete with time and date stamped files indicating when those actions were completed.

During communications with the bid2x development team the installation logs are our mechanism to see what happened if anything goes wrong and are our best bet in helping you.  So don't forget the installation logs when looking for assistance.


#### Log File Format {#log-file-format}

The format of the installation log file breaks up the install into numbers sections separated by indented titleblocks highlighted by characters like '======' and '-------'.  The beginning and the end of the installation always prints the time and date as a reference.

Here's a sample output from the log:


```
***********************************************************************
bid2x installer - Starting - Fri Apr 18, 2025 - 08:01:36 PM UTC
***********************************************************************
=====================================================================================================================================================================================================================
1. Setting up environment
=====================================================================================================================================================================================================================
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    1.1. Setting Default Project
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Updated property [core/project].
Setting Default Project complete
=====================================================================================================================================================================================================================
2. Running pre-run checks
=====================================================================================================================================================================================================================
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    2.1. Checking for file: sample_config_dv.json...
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
File found: sample_config_dv.json
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    2.2. Checking for file: sample_config_dv.json...
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
File found: sample_config_dv.json
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    2.3. Checking for Service Account: bid2x-service@bid2x-deploy-test12.iam.gserviceaccount.com in
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Service Account found: bid2x-service@bid2x-deploy-test12.iam.gserviceaccount.com
Pre-run Checks Passed.
Proceeding with deployment...
=====================================================================================================================================================================================================================
3. Activate APIs
=====================================================================================================================================================================================================================
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
=====================================================================================================================================================================================================================
4. Grant GCP IAM Permissions
=====================================================================================================================================================================================================================
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    4.1. Add Cloud Scheduler Permissions to Service Account
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    4.2. Add Cloud Job Invoker Permissions to Invoker Service Account
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    4.3. Add Permissions for INVOKER to access GCS as Viewer
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
=====================================================================================================================================================================================================================
5. Delete old matching GCP install components.
=====================================================================================================================================================================================================================
** WARNING ** : This section of the bid2x install MAY show errors.
This happens if the script attempts to DELETE components that do
not exist. Therefore, if this is your first install or you are
attempting again after a partial or failed installation please be
aware that errors in this section can happen and do not NECESSARILY
mean you have an invalid installation.
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    5.1. Delete old install of weekly run
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Deleting [bid2x-weekly]...
failed.
ERROR: (gcloud.run.jobs.delete) Job [bid2x-weekly] could not be found.
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    5.2. Delete old install of weekly scheduler
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Deleted job [bid2x-weekly-scheduled-update].
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    5.3. Delete old install of daily run
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Deleting [bid2x-daily]...
failed.
ERROR: (gcloud.run.jobs.delete) Job [bid2x-daily] could not be found.
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    5.4. Delete old install of daily scheduler
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Deleted job [bid2x-daily-scheduled-update].
Existing GCP components deletion completed.
=====================================================================================================================================================================================================================
6. Create Cloud Storage Bucket
=====================================================================================================================================================================================================================
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
=====================================================================================================================================================================================================================
7. Deploy Cloud Run Job(s)
=====================================================================================================================================================================================================================
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    7.1. Deploy Cloud Run Job for Weekly update
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
This command is equivalent to running `gcloud builds submit --tag [IMAGE] .` and `gcloud run jobs deploy bid2x-weekly --image [IMAGE]`

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
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    7.2. Deploy Cloud Run Job for Daily update
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
This command is equivalent to running `gcloud builds submit --tag [IMAGE] .` and `gcloud run jobs deploy bid2x-daily --image [IMAGE]`

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
=====================================================================================================================================================================================================================
8. Create Cloud Scheduler Job(s)
=====================================================================================================================================================================================================================
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    8.1. Construct weekly invocation URI
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Weekly Invocation URI: https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/bid2x-deploy-test12/jobs/bid2x-weekly:run
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    8.2. Create weekly cloud scheduler job
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    8.3. Construct daily invocation URI
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Daily Invocation URI: https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/bid2x-deploy-test12/jobs/bid2x-daily:run
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    8.4. Create daily cloud scheduler job
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
timeZone: America/Toronto
userUpdateTime: '2025-04-18T20:07:25Z'
Completed creating cloud scheduler definitions.
***********************************************************************
bid2x installer - Finished - Fri Apr 18, 2025 - 08:07:25 PM UTC
***********************************************************************
