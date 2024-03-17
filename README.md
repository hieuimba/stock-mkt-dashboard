# Stock Market Dashboard
Data Engineering Project with Azure stack

https://stock-mkt-dashboard.streamlit.app/

## Description
This project provides a daily summary of the US Stock Market to assist traders and investors make better trading decisions. Information is aggregated based on end-of-day index, ETF, and stock prices to visualize:

-   Broad market performance and trend
-   One-day returns of major indexes and sectors
-   Sector correlations
-   Stock market heatmap
-   Stock performance distributions
  
![stock-mkt-dashboard](https://github.com/hieuimba/stock-mkt-dashboard/assets/89481020/7a930a4f-18ed-4292-acd0-e33214f6ad17)

## Architecture

The project’s architecture is an end-to-end data pipeline that extracts price information from source APIs (Alpaca, Finviz, and Yahoo Finance) and loads it into a SQL warehouse for processing and transformation. The data is then visualized in Streamlit as an interactive dashboard.

![data_process](https://github.com/hieuimba/stock-mkt-dashboard/assets/89481020/e7f7e636-c719-46e1-8088-3c23a89d2f42)

## Data Model

![data_model](https://github.com/hieuimba/stock-mkt-dashboard/assets/89481020/1f9deff5-487e-4587-9d0e-bc56ff954972)

## Technology Stack

The following technologies are used to build the project:

-   Azure Functions: for connecting to source data API
-   Azure Data Factory: for data connectors, scheduling, orchestration
-   SQL Database: for staging environment & data warehouse
-   Azure Blob Storage: for miscellaneous & config files
-   Azure Logic Apps: for web API & authentication
-   Streamlit Cloud: for dashboard & visualizations

## Lessons Learned
Making this app was my first time using Azure for a personal project, here are a few key takeaways from this experience:

**Azure Functions:**
- Azure Functions provide a built-in HTTP endpoint trigger that can be integrated easily with DataFactory’s HTTP dataset connector. I’ve found this to be a very simple and effective method to connect to any custom source using Python.

**Data Factory:**
- When factoring in the cost of computing activities, DataFactory is probably best used as an ingestion and/or orchestration tool. Avoid dataflows as they are not very cost-effective and you can pretty much do the same things in SQL for a fraction of the price.
- If possible, limit the number of activities since your execution time is billed for at least one minute per activity, rounded up to the next minute. This means that if your activity runs for only 5 seconds you are still charged for a full minute. These add up really quickly especially if you are running looped activities.
- Extra tip for copy activities: Change the maximum DIUs (Data Integration Unit) to 2 and increase as required. The default setting is Auto, which starts at 4 but scales automatically. By doing this you can save 50% of your cost! Of course, this affects performance but for smaller datasets it's definitely worth it.

![Untitled](https://github.com/hieuimba/stock-mkt-dashboard/assets/89481020/8182e21c-b228-4e28-8c1c-8deed4ec822e)

**Logic App:**
- Logic App is great as a simple API but is more expensive than Azure Functions. I find it’s worth it if you want the flow control operators and/or the built-in connectors for other Azure services.
- In this app, I used the pre-built Azure AD authentication connector to connect to the SQL warehouse, which eliminates the hassle of manually setting up a connection otherwise.
  
 ![Untitled2](https://github.com/hieuimba/stock-mkt-dashboard/assets/89481020/b66190a2-8d61-4b87-816f-4d5d8bf7100e)

**Data Warehouse**
- If the final data model is complex, it is useful to break down the transformation processes into manageable steps or layers. The first layer is the raw layer. Subsequent layers perform specific transformations that bring the data closer to its desired output. These layers help in organizing and simplifying the entire process. As an added benefit, this reduces the query time on the front end by shifting the heavy lifting to the database side, typically done only once per day rather than with every query.
