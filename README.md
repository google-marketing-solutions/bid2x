# bid2x/budget2x: First-Party Data for Google Ad Optimization

The bid2x / budget2x solution is a system designed to enable Google advertising platforms to leverage customer first-party data for more intelligent bidding and budget allocation. It evolved from earlier tools like "bid2index" (for struggling airline routes) and "bid2inventory" (for fluctuating auto inventory) to "bid2x," which encompasses any customer-provided factor that can positively impact bidding, such as service availability or profit margin.

Be sure to refer to the bid2x / budget2x YouTube channel for videos related to this solution:
[https://www.youtube.com/@bid2x](https://www.youtube.com/@bid2x)

The solution is deployed in different ways across key advertising platforms:

* bid2x for Display & Video 360 (DV360):

    - utilizes Custom Bidding scripts to translate first-party data into desired impacts on Line Items within DV360 Campaigns.

    - The bid2x Python code, running in Google Cloud Platform (GCP) (specifically Cloud Run), interacts with the DV360 API to create, rewrite, and assign these scripts.

    - A Google Sheet serves as a control hub, coordinating data from sources like GCP BigQuery (the recommended input for scheduled daily updates) and preparing it for the bid2x system.

    - Line items should follow a naming convention (e.g., "bid-to-inventory") to be managed by the system.

    - Weekly script updates are recommended to allow for DV360's learning period, which can take up to 24 hours to stabilize, though scripts are often active within 1-2 hours. Most DV360 line item types are supported, except those that don't allow per-line-item bidding adjustments.

    - [Jump to bid2x README](bid2x/README.md)

* bid2x for Search Ads 360 (SA360) via Google Tag Manager (GTM):

    - This implementation uses dynamic HTML tags within GTM to indirectly deliver first-party data to SA360, influencing bidding.

    - The bid2x Python application converts data from the Google Sheet (fed by BigQuery or other connectors) into a JavaScript routine. This routine assigns relative values based on the first-party data and the web environment where it runs.

    - This JavaScript routine is then uploaded to a Custom JavaScript variable in GTM via API.

    - Weekly updates are also recommended for SA360/GTM. While new GTM scripts are used immediately for new web sessions, SA360 requires a day or two to learn and adjust before changes demonstrate a clear effect on bidding.

    - [Jump to bid2x README](bid2x/README.md)

* budget2x for Google Ads:

    - This solution takes a different approach by directly adjusting campaign budgets rather than bidding strategies. This is due to Google Ads' macro-level bidding controls (e.g., PMAX campaigns) and the absence of API-based bidding controls similar to DV360 or SA360.

    - Implemented using Google Ads' 'Ads Script' functionality (written in TypeScript), which links to a Google Sheet where daily budgets are calculated based on first-party data.

    - Data flows from BigQuery to Google Sheets, where it is processed and normalized, then used by the Google Ads script to set daily campaign budgets.

    - Daily or even more frequent execution is acceptable, as there is no learning period for budget adjustments.

    - [Jump to budget2x README](budget2x/README.md)


The tool's owners and contacts include Mark Oliver, Andrew Chan, and Joey Thompson.