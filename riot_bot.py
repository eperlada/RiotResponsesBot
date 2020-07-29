#!/usr/bin/python
import praw
import pdb
import re
import os
import time

def parse_comment(comment):
	#if comment.author_flair_text == ":Omen:":
	print(comment.id)
		#if comment.link_id not in previous_posts:

# Create Reddit instance
reddit = praw.Reddit('bot2')

# Create empty list if first time running code
if not os.path.isfile("previous_posts.txt"):
	previous_posts = []

# If we have run the code before, load the list of posts we have replied to
else:
    # Read the file into a list and filter out empty values
    with open("previous_posts.txt", "r") as f:
        previous_posts = f.read()
        previous_posts = previous_posts.split("\n")
        previous_posts = list(filter(None, previous_posts))

# Create subreddit instance
subreddit = reddit.subreddit('VALORANT')

# Setup subreddit stream
stream = subreddit.stream.comments()

while True: 
	try:
		# Get comments from stream
		for comment in stream:
			parse_comment(comment)
	except KeyboardInterrupt:
		# Write to log file
		with open("log.txt", "a") as f:
			f.write("KeyboardInterrupt: %s\n" % time.ctime())
		# Write list back to file after keyboard interrupt
		with open("previous_posts.txt", "w") as f:
			for post_id in previous_posts:
				f.write(post_id + "\n") 
		exit()
	except Exception as err:
		# Write error to log file
		with open("log.txt", "a") as f:
			f.write("%s: %s\n" % string(err), time.ctime())
		# Write list back to file in case of error
		with open("previous_posts.txt", "w") as f:
			for post_id in previous_posts:
				f.write(post_id + "\n") 
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
