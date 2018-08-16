# YrlaLogParser
Parser for the driving log of Yrla, the car belonging to Y-sektionen. Can be used by the treasurer for billing.

Requires Python 3 and pip. To run, simply download the project and run (double-click) the file run.bat. The first time you run the program Chrome (or another web browser) will request you to authenticate yourself to Google. You might also need to have the spreadsheet "Yrla Liggare (Svar)" actually shared with the account being used (not tested without). When complete, all drives from 2018-01-01 and onwards will be shown in a browser tab.

To filter on dates you currently need to run the program another way. Open a command-line interface (cmd) and move to the YrlaLogParser directory. Run the program by typing "python main.py *from_date* *until_date*", where the dates can be on the form YYYY-MM-DD or YYMMDD. Example: "python main.py 2018-02-15 2018-04-30". This will give you all drives between those two dates (including the dates).
