# SWE Team 6:
# Joseph, Tyler, Antonio, Ross, Kashan, Gavin
# File: config.py
# Purpose: 
#   1.) Stores essential configuration settings for the application
#   2.) Defines the database username, password, host, and name
#   3.) Specifies the upload folder where question related images are stored, this ensures that media files are properly managed within the application
# Last edited: 02/06/2025 


class config():
    database_username = 'ubuntu'
    database_pass = 'ubuntu'
    database_host = "localhost"
    database = 'omm'
    upload_folder = 'static/question_images'
