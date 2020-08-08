#!/usr/bin/python
import praw
import pdb
import re
import os
import time

# Create Reddit instance
reddit = praw.Reddit('bot1')

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
	# Add link to original post
	body = "##[Original Post](" + comment.submission.permalink + ")"
	# Create table with response
	body += "\n\nUsername | Link | Response\n" + "---|---|---\n" + formatResponse(comment)
	post = reddit.subreddit('RiotResponses').submit(title=post_title, selftext=body)
	# Add submission ids for original post and response post to previous_posts
	previous_posts[comment.submission.id] = post.id

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
			
# If first time running code, create empty dictionary
if not os.path.isfile("previous_posts.txt"):
	previous_posts = {}

# If we have run the code before, load the dictionary of link_ids where a Riot employee response was previously detected
else:
    # Read the file into a dictionary
	with open("previous_posts.txt", "r") as f:
		previous_posts = {source: link for line in f for (source, link) in (line.strip().split(None, 1),)}

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
		with open("log.txt", "a") as f:
			f.write("KeyboardInterrupt: %s\n" % time.ctime())
		# Write dictionary back to file after keyboard interrupt
		with open("previous_posts.txt", "w") as f:
			for source, link in previous_posts.items():
				f.write("%s %s\n" % (source, link))
		exit()			# Exit on KeyboardInterrupt
	except Exception as err:
		# Write error to log file
		with open("log.txt", "a") as f:
			f.write("%s: %s\n" % str(err), time.ctime())
		# Write dictionary back to file in case of error
		with open("previous_posts.txt", "w") as f:
			for source, link in previous_posts.items():
				f.write("%s %s\n" % (source, link))
	time.sleep(5 * 60) # Try again after 5 minutes