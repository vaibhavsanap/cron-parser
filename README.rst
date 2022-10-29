# Description
This cron expression parser provides the parser to convert cron expression into simplified table of content when command should be executed.

# Project strcuture
cron_parser.py : file contains the logic to parse the cron expression. Also this file has the entrypoint main method to execute the logic for teting purpose
README.md  : readme file

# How to run ?
Setup python3 on server where you want to execute the script
Follow document to setup python
https://realpython.com/installing-python/

Install texttable lib. Used to print output in table format
pip install texttable

Run script
python cron_parser.py "expression"

e.g
python cron_parser.py "23 10-20 20-31 * * command"


