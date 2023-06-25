My Data Engineering Project

https://stock-mkt-dashboard.streamlit.app/

Azure Functions:

- Azure Functions provide a built-in HTTP endpoint trigger that can be integrated easily with DataFactory’s HTTP dataset connector. I’ve found this to be a very simple and effective method to connect to any custom source using Python.

Data Factory:

- When factoring in cost for repeated usage, DataFactory is probably best used as an ingestion and/or orchestration tool. Avoid dataflows as I found that I can do pretty much the same things in SQL much easier and especially cheaper.
- If possible, limit the number of activities since your execution time is billed for at least one minute per activity, rounded up to the next minute. This means that if your activity runs for only 5 seconds you are still charged for a full minute. These add up really quickly especially if you are running looped activities.
- Extra tip for copy activities: Change the maximum DIUs (Data Integration Unit) to 2 and increase as required. The default setting is Auto, which starts at 4 but scales automatically. By doing this you can save 50% of your cost! Of course, this affects performance but for smaller datasets it is defnitely worth it.

![Untitled](https://github.com/hieuimba/stock-mkt-dashboard/assets/89481020/8182e21c-b228-4e28-8c1c-8deed4ec822e)


Logic App:

- Logic App is great for building an API but is more expensive than Azure Fuctions. I find it’s generally worth it if you want the flow control operators and/or the built-in connectors for Azure services.
- In this app, the pre-built Azure AD authentication provided by the Logic App is perfect for connecting to SQL server, which eliminates the hassle of manually setting up a connection otherwise.
- 
 ![Untitled2](https://github.com/hieuimba/stock-mkt-dashboard/assets/89481020/b66190a2-8d61-4b87-816f-4d5d8bf7100e)
