#!/usr/bin/python
import praw
import pdb
import re
import os
import time

def parse_comment(comment):
	# Check if comment is from a Riot employee
	#if comment.author_flair_text == ":riot:":
	print(comment.id)
		# Check if 
		#if comment.link_id not in previous_posts:

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
		exit()
	except Exception as err:
		# Write error to log file
		with open("log.txt", "a") as f:
			f.write("%s: %s\n" % string(err), time.ctime())
		# Write dictionary back to file in case of error
		with open("previous_posts.txt", "w") as f:
			for source, link in previous_posts.items():
				f.write("%s %s\n" % source, link)  
	time.sleep(5 * 60) # Try again after 5 minutes

"""for submission in subreddit.new(limit=10):
    #print(submission.title)

    # If we haven't replied to this post before
    if submission.id not in previous_posts:

        # Do a case insensitive search
        if re.search("i love python", submission.title, re.IGNORECASE):
            # Reply to the post
            submission.reply("testing 123")
            print("Bot replying to : ", submission.title)

            # Store the current id into our list
            previous_posts.append(submission.id)"""
