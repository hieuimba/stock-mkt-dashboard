My Data Engineering Project

https://stock-mkt-dashboard.streamlit.app/

Azure Functions:

- Azure Functions provide a built-in HTTP endpoint trigger that can be integrated easily with DataFactory’s HTTP dataset connector. I’ve found this to be a very simple and effective method to connect to any custom source using Python.

Data Factory:

- When factoring in cost for repeated usage, DataFactory is probably best used as an ingestion and/or orchestration tool. Avoid dataflows as I found that I can do pretty much the same things in SQL much easier and especially cheaper.
- If possible, limit the number of activities since your execution time is billed for at least one minute per activity, rounded up to the next minute. This means that if your activity runs for only 5 seconds you are still charged for a full minute. These add up really quickly especially if you are running looped activities.
- Extra tip for copy activities: Change the maximum DIUs (Data Integration Unit) to 2 and increase as required. The default setting is Auto, which starts at 4 but scales automatically. By doing this you can save 50% of your cost! Of course, this affects performance but for smaller datasets it is defnitely worth it.

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/572fc0e6-1bad-4429-93e9-c5daa9deae89/Untitled.png)

Logic App:

- Logic App is great for building an API but is more expensive than Azure Fuctions. I find it’s generally worth it if you want the flow control operators and/or the built-in connectors for Azure services.
- In this app, the pre-built Azure AD authentication provided by the Logic App is perfect for connecting to SQL server, which eliminates the hassle of manually setting up a connection otherwise.

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/a17c074d-14c2-4eb6-8676-68a61336ad57/Untitled.png)
