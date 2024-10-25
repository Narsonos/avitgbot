# avitgbot
Simple Telegram Bot for Av\*to Tr\*cking.

# Tools used
- Python 3
- Aiogram as Telegram Bots Framework
- Requests + BS4 for parsing
- SQLite3 to store requests

# Installation
1. Clone
2. Install requested libraries (sorry, forgot about requirements.txt)
3. Rename "rename_to_config.py" to "config.py" and insert your Bot token, UserID, Database Filename (with extension)
4. Run

# How to use?
- /add - send request name and request link on separate lines. The bot will begin tracking this and other added requests with 3 min interval between passes and 15 secs between each request.
- /delete - to delete a request pick a request identeficator from the list of the given ids and request names.
- /status - shows your tracked requests

Note: To form a request link you need to just open av\*to website, request the desired content there, APPLY all the filters you need. It is HIGHLY RECOMMENDED to use sorting "by date" since it ensures that the latest offer is the first. After getting output from avito - copy the link and provide to the bot. 
