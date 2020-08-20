#!/usr/bin/python
import praw
import pdb
import re
import os
import time
import mysql.connector as SQLC
from mysql.connector import Error
import database as db
from configparser import ConfigParser
import logging

# Set up logging
logging.basicConfig(filename = 'riotresponses.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Read config.ini
config = ConfigParser()
config.read("config.ini")

# Create Reddit instance
reddit = praw.Reddit(username = config["REDDIT"]["username"],
					password = config["REDDIT"]["password"],
					client_id = config["REDDIT"]["client_id"],
					client_secret = config["REDDIT"]["client_secret"],
					user_agent = "RiotResponses Bot v0.3")

# Formats a comment with the author name, comment body, and permalink to the comment
def formatResponse(comment):
	body = comment.body
	# Replace new lines with a single space to preserve Reddit table formatting
	body = re.sub(r'\n+', ' ', body).strip()
	formatted = comment.author.name + " | [Link](https://www.reddit.com" + comment.permalink + ") | " + body
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
	body += "\n\nUsername | Link | Response\n" + "---|---|---\n" + formatResponse(comment)
	# Post to subreddit
	post = reddit.subreddit(config["REDDIT"]["target_subreddit"]).submit(title=post_title, selftext=body)

	# Add submission ids for original post and response post to previous_posts
	previous_posts[comment.submission.id] = post.id
	# Update database
	db.insert(comment.submission.id, post.id)

# Updates a previously created post to add a new response from the same submission
def updatePost(comment, post):
	body = post.selftext
	body += "\n" + formatResponse(comment)
	post.edit(body)

def parseComment(comment):
	# Check if comment is from a Riot employee
	if comment.author_flair_text == ":riot:":
	#print(comment.id)
		# Check if another comment from same thread was previously posted
		if comment.submission.id not in previous_posts:
			createPost(comment)
		else:
			updatePost(comment, reddit.submission(previous_posts[comment.submission.id]))

# Connect to database
dbcon = db.connect()
previous_posts = {}

# Check for table in database
if not db.checkTableExists(dbcon, "Posts"):
	db.createTable(dbcon)
# If table already exists in database, import rows into dictionary
else:
	dbcur = dbcon.cursor()
	dbcur.execute("SELECT * FROM Posts")
	dbposts = dbcur.fetchall()
	for (source, post) in dbposts:
		previous_posts[source] = post

# Close database connection after loading in data
db.disconnect(dbcon)

# Create subreddit instance
subreddit = reddit.subreddit('VALORANT')

# Setup subreddit stream
stream = subreddit.stream.comments()

while True:
	try:
		# Get comments from stream
		for comment in stream:
			parseComment(comment)
	except KeyboardInterrupt:
		# Write to log file
		logging.info("KeyboardInterrupt")
		exit()			# Exit on KeyboardInterrupt
	except Exception as err:
		# Write error to log file
		logging.exception("Exception raised!")
	time.sleep(5 * 60) # Try again after 5 minutes
