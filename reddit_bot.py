#!/usr/bin/python
import pdb
import re
import os
import time

import praw
from praw.exceptions import APIException
from prawcore.exceptions import ResponseException
from prawcore import ServerError

from configparser import ConfigParser
import logging

import mysql.connector as SQLC
from mysql.connector import Error

import database as db

# Set up logging
logging.basicConfig(filename='riotresponses.log',
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Read config.ini
config = ConfigParser()
config.read("config.ini")

# Create Reddit instance
reddit = praw.Reddit(username=config["REDDIT"]["username"],
                     password=config["REDDIT"]["password"],
                     client_id=config["REDDIT"]["client_id"],
                     client_secret=config["REDDIT"]["client_secret"],
                     user_agent="RiotResponses Bot v0.4")
reddit.validate_on_submit = True

# Formats a comment with the author name, comment body, and permalink to the comment
def formatResponse(comment):
    body = comment.body
    # Replace new lines with a single space to preserve Reddit table formatting
    body = re.sub(r'\n+', ' ', body).strip()
    formatted = '[' + comment.author.name + ']' + '(https://www.reddit.com/u/' + \
        comment.author.name + ')' + \
        " | [Link](https://www.reddit.com" + comment.permalink + ") | " + body
    return formatted

# Creates post with initial response
def createPost(comment):
    # Post title format: [Original Poster] Submission Title
    if comment.submission.author == None:
        op = "deleted"
    else:
        op = comment.submission.author.name
    post_title = "[" + op + "] " + comment.submission.title
    body = "##[Original Post](" + comment.submission.permalink + ")"
    body += "\n\nRiot Employee | Link | Response\n" + \
        "---|---|---\n" + formatResponse(comment)
    # Post to subreddit
    post = reddit.subreddit(config["REDDIT"]["target_subreddit"]).submit(
        title=post_title, selftext=body)

    # Add submission ids for original post and response post to previous_posts
    previous_posts[comment.submission.id] = post.id
    # Update database
    db.insertPost(comment.submission.id, post.id, op, comment.submission.title)
    db.insertComment(comment.id, comment.submission.id, comment.author.name, comment.body_html)

# Updates a previously created post to add a new response from the same submission
def updatePost(comment, post):
    body = post.selftext
    body += "\n" + formatResponse(comment)
    post.edit(body)
    # Update database
    db.insertComment(comment.id, comment.submission.id, comment.author.name, comment.body_html)


# Parse a comment from the subreddit stream
def parseComment(comment):
    # Check if comment is from a Riot employee
    if comment.author_flair_text == ":riot:":
        # Check if another comment from same thread was previously posted
        if comment.submission.id not in previous_posts:
            createPost(comment)
        else:
            updatePost(comment, reddit.submission(
                previous_posts[comment.submission.id]))


# Connect to database
dbcon = db.connect()
previous_posts = {}

# Check for tables in database
if not db.checkTableExists(dbcon, "Posts"):
    db.createPostsTable(dbcon)
if not db.checkTableExists(dbcon, "Comments"):
    db.createCommentsTable(dbcon)
# If table already exists in database, load stored rows into memory
else:
    dbcur = dbcon.cursor()
    dbcur.execute("SELECT sourceid, postid FROM Posts")
    dbposts = dbcur.fetchall()
    for (sourceid, postid) in dbposts:
        previous_posts[sourceid] = postid

# Close database connection after loading in data
db.disconnect(dbcon)

# Create subreddit instance
subreddit = reddit.subreddit('VALORANT')

while True:
    # Setup subreddit stream in loop to restart when exception is thrown
    stream = subreddit.stream.comments()
    try:
        # Get comments from stream
        for comment in stream:
            if comment is not None:
                parseComment(comment)
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt")
        exit()				# Exit on KeyboardInterrupt
    except ServerError as err:
        logging.exception("Reddit server down!")
        time.sleep(2 * 60)  # Try again after 2 minutes
    except APIException as err:
        logging.exception("API Exception occurred!")
        time.sleep(60)		# Try again after 1 minute
    except ResponseException as err:
        logging.exception("Response Exception occurred!")
        time.sleep(60)		# Try again after 1 minute

