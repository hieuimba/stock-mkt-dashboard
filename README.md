# Stock Market Dashboard
Data Engineering Project
https://stock-mkt-dashboard.streamlit.app/

## Description
This project aims to provide a daily summary of the US Stock Market in order to assist traders and investors make better trading decisions. Information is aggregated based on end-of-day index, ETF and stock prices in order to visualize:

-   Broad market performance and trend
-   One-day returns of major indexes and sectors
-   Sector correlations
-   Stock market heatmap
-   Stock distributions

## Architecture

The project’s architecture is an end to end data pipeline which extracts price information from the source APIs (Alpaca Market Data API and Finviz) and load it into a SQL warehouse for processing and transformation. The data is then visualized in Streamlit as an interactive dashboard.
![process_map](https://github.com/hieuimba/stock-mkt-dashboard/assets/89481020/76d271f9-c3df-4e7b-99ab-a21f74d87187)

## Technology Stack

The following technologies are used to build the project:

-   Azure Functions: for connecting to source data API
-   Azure Data Factory: for data connectors, scheduling, orchestration
-   SQL Database: for staging environment & data warehouse
-   Azure Blob Storage: for miscelaneous & config files
-   Azure Logic Apps: for front-end API (more efficient than Azure Functions)
-   Streamlit Cloud: for dashboard & visualizations

## Lessons Learned
Making this app was fun, here are a few key take-aways from my experience:

**Azure Functions:**
- Azure Functions provide a built-in HTTP endpoint trigger that can be integrated easily with DataFactory’s HTTP dataset connector. I’ve found this to be a very simple and effective method to connect to any custom source using Python.

**Data Factory:**
- When factoring in cost for repeated usage, DataFactory is probably best used as an ingestion and/or orchestration tool. Avoid dataflows as I found that I can do pretty much the same things in SQL much easier and especially cheaper.
- If possible, limit the number of activities since your execution time is billed for at least one minute per activity, rounded up to the next minute. This means that if your activity runs for only 5 seconds you are still charged for a full minute. These add up really quickly especially if you are running looped activities.
- Extra tip for copy activities: Change the maximum DIUs (Data Integration Unit) to 2 and increase as required. The default setting is Auto, which starts at 4 but scales automatically. By doing this you can save 50% of your cost! Of course, this affects performance but for smaller datasets it's definitely worth it.

![Untitled](https://github.com/hieuimba/stock-mkt-dashboard/assets/89481020/8182e21c-b228-4e28-8c1c-8deed4ec822e)

**Logic App:**
- Logic App is great for building an API but is more expensive than Azure Fuctions. I find it’s generally worth it if you want the flow control operators and/or the built-in connectors for Azure services.
- In this app, the pre-built Azure AD authentication provided by Logic App is perfect for connecting to SQL server, which saves me the hassle of manually setting up a connection otherwise.

 ![Untitled2](https://github.com/hieuimba/stock-mkt-dashboard/assets/89481020/b66190a2-8d61-4b87-816f-4d5d8bf7100e)
