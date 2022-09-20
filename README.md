# Problem statement
Design an ingestion pipeline to fetch Mutual Fund data from the [AMFI](https://www.amfiindia.com/nav-history-download) website, model, and store that data into a database for further processing.

# Submission Requirements
- The pipeline should be able to do a full load to begin with and then fetch the incremental data every day.
- Modelling the data and choice of database is left to you.
- The pipeline should be able to deal with failures and should be designed to fetch and store data in a performance-efficient manner.
- (Extra) Try to get the initial load(fetch+DB insertion) to complete in less than 3 hours.
- (Extra) Model the data and tune it such that read queries for a particular fund/multiple funds over a certain time period are performant.

## Data analysis

# Available AMFI data
The [AMFI NAV history](https://www.amfiindia.com/nav-history-download) page has two main sections:
- Latest NAV, providing latest NAV reports in different formats (and different APIs)
- NAV history, providing historical NAV data through a unified API

# Latest NAV
- Limiting my scope to [Complete NAV report](https://www.amfiindia.com/spages/NAVAll.txt)
- Available data
	- NAV data format: Scheme Code;ISIN Div Payout/ ISIN Growth;ISIN Div Reinvestment;Scheme Name;Net Asset Value;Date
	- Scheme type: Open ended scheme variations, close ended scheme variations
	- Mutual fund
- Each NAV row contains the latest available data for a given scheme
- NAV data is calculated and updated at the end of every market day
- API currently gives around 13000 records (excluding blank lines)
- (Optimization) Since data from inactive schemes will be processed during the historical load, the incremental loads can only focus on recent data
	- In scenarios where old NAV data is edited for any reason, the changes will not get reflected in this approach
	
# NAV history
- [API](https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx)
- The NAV history page has dropdowns to set the API parameters
	- For all funds and all scheme types, only date needs to be populated - https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt=01-Sep-2022
	- Choosing a fund allows for start and end dates - https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf=3&frmdt=01-Sep-2022&todt=03-Sep-2022
	- Start and end dates also work for all funds and all scheme types, when using the API directly - https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt=01-Sep-2022&todt=03-Sep-2022
	- Although the page only allows a time period of 90 days, the API itself does not seem to have that limitation
- Available data
	- NAV data format: Scheme Code;Scheme Name;ISIN Div Payout/ISIN Growth;ISIN Div Reinvestment;Net Asset Value;Repurchase Price;Sale Price;Date
	- Scheme type: Open ended scheme variations, close ended scheme variations
	- Mutual fund
- Based on the some of the data available, we can expect around 2 million records per year
- The scheme types don't seem to be consistent between Latest NAV and NAV history. For example, NAV history uses "Open Ended Schemes ( Money Market )" while Latest NAV uses "Open Ended Schemes(Money Market)".

# Query scenarios
Since data usage scenarios will influence the data should be modeled, I looked for some common queries using NAV data. 
(*The problem statement did not specify how the data might be used*)
- Filter NAV data based on scheme, category, start and end dates
- Compare NAV between dates
- Calculate and compare averages over month/year
- 52 week highest/lowest NAVs
Other observations
- NAV data usually cannot be compared across schemes. (*Potential for data partitioning*)
- Any operation/aggregation on NAV will ALWAYS require some level of filtering, at least on scheme
- Data loads happen rarely (daily at most), and loaded data will not be updated in this design

## [Data modelling](./modeling.md)
## Pipeline design and implementation

1. Fetch data from API (latest or historical)
2. Create temporary csv file to enable COPY
3. COPY data from csv to staging table
4. Move data from staging table to nav_data based on conditions
4. Use a scheduling tool (chron, Airflow etc) to schedule daily incremental loads
