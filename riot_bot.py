#!/usr/bin/python
import praw
import pdb
import re
import os
import time

# Creates post
def create_post(comment):
	# Post title format: [Original Poster] Submission Title
	post_title = "[" + comment.submission.author.name + "] " + comment.submission.title
	# Format response with Riot staff username then response body
	response = comment.author.name + ": [" + comment.body + "](https://www.reddit.com" + comment.permalink + ")"
	# Add link to original post in body of response post
	post_body = "[Original Post](" + comment.submission.permalink + ")\n\n" + response
	post = reddit.subreddit('RiotResponses').submit(title=post_title, selftext=post_body)
	# Add submission ids for original post and response post to previous_posts
	previous_posts[comment.submission.id] = post.id

#def update_post(comment):

def parse_comment(comment):
	# Check if comment is from a Riot employee
	#if comment.author_flair_text == ":riot:":
	print(comment.id)
		# Check if another comment from same thread was previously posted
		#if comment.link_id not in previous_posts:
			#create_post(comment)
		#else:
			#update_post(comment)

# Create Reddit instance
reddit = praw.Reddit('bot2')

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

# Infinite loop to keep trying in case of exceptions
while True:
	try:
		# Get comments from stream
		for comment in stream:
			parse_comment(comment)
	except KeyboardInterrupt:
		# Write to log file
		with open("log.txt", "a") as f:
			f.write("KeyboardInterrupt: %s\n" % time.ctime())
		# Write dictionary back to file after keyboard interrupt
		with open("previous_posts.txt", "w") as f:
			for source, link in previous_posts.items():
				f.write("%s %s\n" % source, link)
		exit()			# Exit on KeyboardInterrupt
	except Exception as err:
		# Write error to log file
		with open("log.txt", "a") as f:
			f.write("%s: %s\n" % string(err), time.ctime())
		# Write dictionary back to file in case of error
		with open("previous_posts.txt", "w") as f:
			for source, link in previous_posts.items():
				f.write("%s %s\n" % source, link)
	time.sleep(5 * 60) # Try again after 5 minutes
