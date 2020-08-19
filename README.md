# RiotResponses - reddit bot

Reddit bot created with Python 3.6 and MySQL 8.0

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)

## General info
This Reddit bot scans the VALORANT subreddit for comments from Riot Games employees. These comments are organized in tables and posted in submissions on the RiotResponses subreddit.
Additional Riot comments from the same VALORANT submission are added to the same RiotResponses submission.

## Technologies
Project is created with:
* Python 3.6
* MySQL 8.0
* PRAW 7.1.0

## Setup
A MySQL database is required to run this bot.

PRAW and mysql-connector are required to run this bot. Install them using:

```
$ pip install praw
$ pip install mysql-connector
```

To run this project, place all files (reddit_bot.py, database.py, config.ini) into one directory.
Update config.ini with your Reddit and MySQL database credentials, in addition to the target subreddit that the bot will post to.
Start the bot by running reddit_bot.py. 
The bot can be stopped at any time by closing the console or raising a KeyboardInterrupt (CTRL + C).


