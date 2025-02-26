# SWE Team 6:
# Joseph, Tyler, Antonio, Ross, Kashan, Gavin
# File: create_question.py
# Purpose: The program is a Flask-based backend script that handles the creation of questions for the OMM assessment system. It inserts questions into a database, associates them with tags, stores possible answers, marks correct answers, and manages image uploads for questions and explanations.
# Last edited: 02/06/2025

from flask import flash, redirect, render_template, request, session, url_for

# Custom function to establish a database connection
from database.connection import makeConnection

import os

# Utility function for secure filenames
from werkzeug.utils import secure_filename

# Function for string sanitization
from database import prepare_string

def create_question(question_text, example_text, user_id, selected_tags):
    # Start connection
    cnx = makeConnection()
    cursor = cnx.cursor()

    # Insert question text, example text, is_active (Default 1), users_id (Work in Progress)
    insert_question = ("INSERT INTO question(question_text, example_text, is_active, users_ID) VALUES(%s, %s, %s, %s)")
    values = (question_text, example_text, 1, user_id)
    cursor.execute(insert_question, values)

    #Get the ID of the question created
    question_ID = get_latest_question_ID_in_with_cursor(cursor)

    # Attach selected tags to the question
    attach_tag(selected_tags, question_ID, cursor)

# Try to create answers, handling potential errors
    try:
        create_answers(question_ID, cursor)
    except OverflowError:
        raise OverflowError # Raising errors without additional handling could cause crashes
    except TypeError:
        raise TypeError

    # Commit changes and close the database connection 
    cnx.commit()
    cnx.close()

    return True # Indicate successful question creation

#Get the question ID of the last question added into the database USING the same cursor given
def get_latest_question_ID_in_with_cursor(cursor):
    # Retrieves the latest inserted question ID using the provided cursor
    cursor.execute("SELECT max(question_ID) FROM question")
    question_ID = cursor.fetchone()[0]

    return question_ID

# Get the question ID of the last question added into the database not using a given cursor
def get_latest_question_ID():
    # Retrieves the latest inserted question ID by opening a new database connection
    cnx = makeConnection()
    cursor = cnx.cursor()

    # Get the question ID of the last question added into the database
    cursor.execute("SELECT max(question_ID) FROM question")
    question_ID = cursor.fetchone()[0]

    cursor.close()
    cnx.close()

    return question_ID

def attach_tag(selected_tags, question_ID, cursor):
    # Associates tags with a given question
    try:
        for tag in selected_tags:
            # Get tag ID from the database
            query_tag = (f"SELECT tag_ID FROM tag WHERE tag_name = \"{tag}\"")
            cursor.execute(query_tag)
            tag_id = cursor.fetchone()

            if tag_id:
                tag_id = tag_id[0] # Extract tag ID
                insert_tag_question = (f"INSERT INTO tag_question(tag_ID, question_ID) VALUES(%s, %s)")
                values = (tag_id, question_ID)
                cursor.execute(insert_tag_question, values)
    except:
        raise ValueError("Tag mismatch")
    
#Take in a list of tags ["", "", ""], if ALL tags are blank, return False, else return True
def check_tags(select_tags):
    for tag in select_tags:
        if tag != "":
            return True
    
    return False

#Check to make sure that the user selects a non-blank answer to be the correct answer
def check_answer(answer, correct_answer):
    return True


def create_answers(question_ID, cursor):
    try:
        for i in range(1, 7):
            answer_text = request.form.get(f'answer{i}')
            correct_answer = int(request.form.get('correctAnswer'))

            #Check to make sure that the answer is not blank
            if answer_text != "":
                if i is correct_answer:
                    is_correct = 1
                else:
                    is_correct = 0
            
                #Inserting the answer into the database
                #Check duplicate answer, if duplicate exists we'll get the ID of it, else we get False and create a new answer entity
                answer_id = no_duplicate_answer(answer_text, cursor)

                if not answer_id: #If there is no duplicate answer, we need to create an answer.
                    cursor.execute(f"INSERT INTO answer(answer_text) VALUES (\"{answer_text}\")") #create answer entity

                    # Get answer_ID from the created answer
                    cursor.execute("SELECT max(answer_ID) FROM answer")
                    answer_id = cursor.fetchone()[0]

                # Insert answer id into question_answer bridging table
                insert_question_answer = ("INSERT INTO question_answer(question_ID, answer_ID, is_correct) VALUES(%s, %s, %s)")
                values = (question_ID, answer_id, is_correct)
                cursor.execute(insert_question_answer, values)
    except:
        raise OverflowError("Answer too long")


#Checks to see if an answer already exists in the database, if it does, returns the ID of the answer, else returns FALSE
def no_duplicate_answer(answer_text, cursor):
    cursor.execute(f"SELECT answer_ID FROM answer WHERE answer_text = \"{answer_text}\"")
    answer_id = cursor.fetchone()

    if answer_text != "" and answer_id:
            return answer_id[0] 
    
    return False


def inputImages(UPLOAD_FOLDER, question_id):
    # Check if upload folder exists if not, create folder
        if os.path.isdir(UPLOAD_FOLDER) == False:
            os.mkdir(UPLOAD_FOLDER)

        # Checking to see if an image was given for the question
        if "image" not in request.files:
            flash('No Image')
        else:
            flash('Yes Image')
            image = request.files["image"]

            if (image.filename != ''):
                # if allowed_file(image.filename):
                    image.filename = 'question_' + str(question_id) + '.jpeg'
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(UPLOAD_FOLDER, filename))
                # else:
                #     flash('Invalid file. Please only choose a jpeg.')
            else:
                print("No question image added")

        # Checking to see if an explanation image was given
        if "explanationImage" not in request.files:
            flash('No Image')
        else:
            flash('Yes Image')
            explanationImage = request.files["explanationImage"]

            if (explanationImage.filename != ''):
                if allowed_file(explanationImage.filename):
                    print('name before')
                    print(explanationImage.filename)
                    explanationImage.filename = 'question_' + str(question_id) + '_explanation.jpeg'
                    filename = secure_filename(explanationImage.filename)
                    print('name after')
                    print(filename)
                    explanationImage.save(os.path.join(UPLOAD_FOLDER, filename))
                else:
                    flash('Invalid file. Please only choose a jpeg.')
            else:
                print("No file selected for explanation image")


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png', 'bmp'} 

    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
