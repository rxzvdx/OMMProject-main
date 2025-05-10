# SWE Team 6:
# Joseph, Tyler, Antonio, Ross, Kashan, Gavin
# File: database_connection.py
# Purpose: 
#   1.) This function, makeConnection(), establishes a connection to the MySQL Database
#       using credentials stored in the config class. 
#   2.) Retrieves the database username, password, host, and database name from the 
#       config and uses them to connect via mysql.connector.connect()
#   3.) It returns a connection object that allows interaction with the database.
# Last edited: 02/06/2025 

import mysql.connector
from config import config

def makeConnection():
    return mysql.connector.connect(user = config.database_username, 
                                   password = config.database_pass, 
                                   host = config.database_host, 
                                   database = config.database)
