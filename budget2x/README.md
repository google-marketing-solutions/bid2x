# budget2x for Google Ads

## Description

This script automates the process of updating daily budgets for Google Ads campaigns, particularly Performance Max campaigns, based on data provided in a Google Sheet. It's designed to be run from a Google Ads Manager Account (MCC) and can update budgets for campaigns residing in various sub-MCC accounts linked to the main MCC. The script uses a central "KeySheet" within the Google Sheet to manage which sets of campaigns and their corresponding budgets to process.

## Prerequisites

1.  **Google Ads Manager Account (MCC):** You must have access to an MCC account that is a parent or super-MCC of the accounts containing the campaigns you wish to manage.
2.  **Permissions:** You need adequate permissions within the Google Ads MCC to create, edit, and run Ads Scripts.
3.  **Google Sheet:** A Google Sheet must be prepared to control the script's operations.

## Google Sheet Setup

1.  **Create or Copy the Sheet:** You can create a new Google Sheet or make a copy of the template available here: [Sample budget2x Google Sheet](https://docs.google.com/spreadsheets/d/1tGyQK0kZQlrgdyD9MWwpr3EqarAL29LD222fzMK9_Gk/edit)
2.  **Update Script Variable:** Once you have your Google Sheet, copy its URL. Open the script code and replace the placeholder URL in the `SPREADSHEET_URL` constant with the URL of *your* sheet:
    ```javascript
    const SPREADSHEET_URL = 'YOUR_GOOGLE_SHEET_URL_HERE';
    ```
3.  **Share the Sheet:** Share the Google Sheet with the email address of the user who will be authorizing and running the Ads Script. 'Viewer' access is sufficient as the script only needs to read data.
4.  **"KeySheet" Tab:**
    *   Ensure there is a tab named exactly `KeySheet`.
    *   Set up the first row with the following headers:
        *   **Column A:** `Zone Name` (A descriptive name, e.g., "North America Campaigns")
        *   **Column B:** `MCC` (The Customer ID of the sub-MCC account containing the campaigns for this zone, e.g., 123-456-7890)
        *   **Column C:** `Tab Name` (The exact name of the tab within this spreadsheet that contains the campaign/budget data)
        *   **Column D:** `Status` (Set to `On` to process this zone/tab. Any other value will cause it to be skipped.)
        *   **Column E:** `Reference` (The starting cell for the data in the data tab, e.g., `B5`)

5.  **Data Tabs:**
    *   For each tab name listed in `KeySheet` (Column C), create a corresponding tab.
    *   In each data tab, structure the data starting from the cell specified in `KeySheet`'s `Reference` column (Column E):
        *   **Reference Column:** Campaign IDs.
        *   **Column to the right of Reference:** New Daily Budget amounts.
        *   **Column to the right of Budget:** Campaign Status (Set to `On` to update this specific campaign's budget. Any other value or empty will skip the row).
    *   Example Data Tab Structure (if Reference is `B5`):
        *   `B5`: Campaign ID
        *   `C5`: New Budget
        *   `D5`: Status (`On`/`Off`)
        *   `B6`: Campaign ID
        *   `C6`: New Budget
        *   `D6`: Status (`On`/`Off`)
        *   ... and so on.

## Script Installation

1.  **Navigate to Scripts:** In your Google Ads MCC, go to "Tools & Settings" (the wrench icon) -> "Bulk Actions" -> "Scripts".
2.  **Create New Script:** Click the blue "+" button to create a new script.
3.  **Name the Script:** Give the script a descriptive name, e.g., "MCC Budget Updater from Sheet".
4.  **Paste Code:** Delete any existing code in the editor and paste the entire provided script code.
5.  **Update Spreadsheet URL:** Ensure you have updated the `SPREADSHEET_URL` variable in the code to point to your Google Sheet.
6.  **Authorize:** The first time you try to run or preview, you'll be prompted to authorize the script to access your Google Ads data and Google Sheets on your behalf. Follow the prompts.
7.  **Save:** Click "Save".

## Running the Script

*   **Manual Run:**
    *   Click "Preview" to test the script without making actual changes. Check the logs for any errors or unexpected actions.
    *   Click "Run" to execute the script and apply budget changes.
*   **Scheduling:**
    *   In the script editor, click on "Frequency" next to the save button.
    *   Set up a schedule (e.g., Daily, Weekly) as needed. The script will run automatically based on this schedule.

## Important Notes

*   **MCC Level:** This script MUST be installed and run from an MCC account.
*   **Sub-MCC Targeting:** The script switches context to the specific sub-MCC account ID listed in Column B of the `KeySheet` for each active zone.
*   **Campaign Type:** The current version of the `setCampaignBudget` function specifically looks for *Performance Max* campaigns using `AdsApp.performanceMaxCampaigns()`. Budgets for other campaign types will not be updated by this version.
*   **Error Handling:** The script includes logging for common errors such as inability to open the spreadsheet, missing sheets, or invalid cell references. Check the execution logs in the Ads Scripts interface after running.
*   **Idempotency:** If the new budget in the sheet is the same as the campaign's current budget, the script will skip the update for that campaign to save time and API operations.

## License and Contributing

This script is licensed under the Apache License, Version 2.0. Please see the `LICENSE` file in the root of this repository for the full license text.

Contributions are welcome! Please see the `CONTRIBUTING.md` file in the root of this repository for guidelines.

## Disclaimer

This is not an officially supported Google product.
