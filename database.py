#!/usr/bin/python
import praw
import pdb
import re
import os
import time
import mysql.connector as SQLC
from mysql.connector import Error
from configparser import ConfigParser

# Read config.ini
config = ConfigParser()
config.read("config.ini")

def connect():
	try:			
		# Connect to database
		dbcon = SQLC.connect(
				host = config["DATABASE"]["host"],
				user = config["DATABASE"]["user"],
				passwd = config["DATABASE"]["passwd"],
				database = config["DATABASE"]["database"]
			)
		print("Connected to MySQL database")
		return dbcon
	except Error as e:
		print("Error connecting to MySQL database", e)

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
		print("Error inserting into MySQL table", e)
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
	try:
		dbcur = dbcon.cursor()
		dbcur.execute("""
			CREATE TABLE Posts (
				Source VARCHAR(6),
				Post VARCHAR(6)
			)""")
		print("Successfully created Posts table in database")
	except Error as e:
		print("Error creating Posts table in database", e)
	finally:
		dbcur.close()
	
