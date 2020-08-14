#!/usr/bin/python
import praw
import pdb
import re
import os
import time
import mysql.connector as SQLC
from mysql.connector import Error

def connect():
	try:			
		# Connect to database
		dbcon = SQLC.connect(
				host = "localhost",
				user = "Ethan",
				passwd = "Tvv0Xn8m#17O",
				database = "RedditBot"
			)
		print("Connected to MySQL database")
		return dbcon
	except Error as e:
		print("Error reading data from MySQL table ", e)

def disconnect(dbcon):		
	if dbcon is not None and dbcon.is_connected():
		dbcon.close()
		print("MySQL connection closed")
		
def insert(source, post):
	dbcon = connect()
	try:
		dbcur = dbcon.cursor()
			dbcur.execute("INSERT INTO Posts VALUES (%s, %s)", (source, post))
		dbcon.commit()
		print("Successfully inserted into Posts")
	except Error as e:
		print("Error inserting into MySQL table ", e)
	finally:	
		dbcur.close()
		disconnect(dbcon)

def checkTableExists(dbcon, tablename):
	dbcur = dbcon.cursor()
	dbcur.execute("""
		SELECT COUNT(*)
		FROM information_schema.tables
		WHERE table_name = '{0}'
		""".format(tablename.replace('\'', '\'\'')))
	if dbcur.fetchone()[0] == 1:
		dbcur.close()
		return True
	dbcur.close()
	return False
	
def createTable(dbcon):
	dbcur = dbcon.cursor()
	dbcur.execute("""
		CREATE TABLE Posts (
			Source VARCHAR(6),
			Post VARCHAR(6)
		)""")
	print("Posts Table created in database")
	dbcur.close()
	
