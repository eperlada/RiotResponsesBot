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
            host=config["DATABASE"]["host"],
            user=config["DATABASE"]["user"],
            passwd=config["DATABASE"]["passwd"],
            database=config["DATABASE"]["database"],
            auth_plugin='mysql_native_password'
        )
        print("Connected to MySQL database")
        return dbcon
    except Error as e:
        print("Error connecting to MySQL database", e)


def disconnect(dbcon):
    if dbcon is not None and dbcon.is_connected():
        dbcon.close()
        print("MySQL connection closed")


def insertPost(sourceid, postid, author, title):
    dbcon = connect()
    try:
        dbcur = dbcon.cursor()
        dbcur.execute("INSERT INTO Posts VALUES (%s, %s, %s, %s, NOW())",
                      (sourceid, postid, author, title))
        dbcon.commit()
        print("Successfully inserted into Posts")
    except Error as e:
        print("Error inserting into Posts table", e)
    finally:
        dbcur.close()
        disconnect(dbcon)


def insertComment(commentid, sourceid, author, content):
    dbcon = connect()
    try:
        dbcur = dbcon.cursor()
        dbcur.execute("INSERT INTO Comments VALUES (%s, %s, %s, %s, NOW())",
                      (commentid, sourceid, author, content))
        dbcon.commit()
        print("Successfully inserted into Comments")
    except Error as e:
        print("Error inserting into Comments table", e)
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


def createPostsTable(dbcon):
    try:
        dbcur = dbcon.cursor()
        dbcur.execute("""
			CREATE TABLE Posts (
				sourceid VARCHAR(8),
        postid VARCHAR(8),
				author VARCHAR(20),
        title VARCHAR(300),
				time DATETIME,
        PRIMARY KEY (sourceid)
			)""")
        print("Successfully created Posts table in database")
    except Error as e:
        print("Error creating Posts table in database", e)
    finally:
        dbcur.close()


def createCommentsTable(dbcon):
    try:
        dbcur = dbcon.cursor()
        dbcur.execute("""
			CREATE TABLE Comments (
				commentid VARCHAR(8),
				sourceid VARCHAR(8),
        author VARCHAR(20),
        content TEXT,
				time DATETIME,
        PRIMARY KEY (commentid),
        FOREIGN KEY (sourceid) REFERENCES Posts(sourceid)
			)""")
        print("Successfully created Comments table in database")
    except Error as e:
        print("Error creating Comments table in database", e)
    finally:
        dbcur.close()
