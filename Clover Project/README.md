[Author] Jonathan Carbonneau
[Last_Updated] 08/30/2022

## Description

- This Vivaspot service integrates with Clover and “mines”
- Clover data to better target customers as well as
- create predictive models on revenue.

## Structure

1. Based on input via the Merchant ID, Clover token or both, the service can access the merchant’s Clover data through the Clover Rest API.
2. On a recurring basis (every 24 hours) - customer information (emails, mobile phone numbers, opt-ins, etc.) is extracted and placed in data repository (e.g. Google Sheets).
3. Customers are “tagged” based on various Clover data points such as “Top Revenue Spender”, “One-Time Visitor”, “Multiple Visitor” and other tags that would make market targeting more efficient. These tags are also placed in the data repository.
4. Based on revenue and transaction data extracted, and using predictive modeling techniques, forecasts and other relevant analytics are presented to the merchant.
5. Based on transaction data and customer spend provide insight into the offerings that are generating profit, vs those that are not.

## Product Details

1. Users access the Vivaspot Insights dashboard through simple login via user id/password
2. Users can select the various models, insights and analytics that they want to run
3. Graphs and insights will display though the dashboard. These can be adjusted based on timeline.
4. Users can set to have reports sent to them via email on a weekly/monthly basis 5) Users can select to have data extracted and deposited into a Google Sheet. The Google sheet has 4 columns (email, mobile, opt-in, tags).

## IDEs

1. Install [Visual Studio Code](https://code.visualstudio.com/)
2. Install [SSMS](https://docs.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms?view=sql-server-ver16)
   - Useful to troubleshoot queries in SSMS as opposed to in VS Code

## Installing Libraries

- Run PowerShell as administrator and run the following commands (make sure you have pip installed)
  - pip install xml.dom.minidom
  - pip install smtplib
  - pip install werkzeug.exceptions
  - pip install flask
  - pip install json
  - pip install flask_table
