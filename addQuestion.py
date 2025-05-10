# SWE Team 6:
# Joseph, Tyler, Antonio, Ross, Kashan, Gavin
# File: addQuestion.py
# Purpose:  
#   1.) Handles adding questions to the database in a Flask web application. 
#   2.) Processes form submissions from a webpage, extracts question details and associated tags
#   3.) Validates user inputs, and interacts with the database to store questions
#   4.) Manages error handling for tag mismatches and input length constraints
#   5.) Uploads images related to the question and redirects users to a succes page upon successful submission
# Last edited: 02/06/2025 

from flask import flash, redirect, render_template, request, session, url_for
from connection import makeConnection
import os
from werkzeug.utils import secure_filename
from database import get_question, create_question


def addQuestionToDB(UPLOAD_FOLDER):
    if request.method == 'POST':

        question_text = request.form['questionInput']     
        example_text = request.form['explanationInput']
        selected_tags = request.form.getlist('subjectDropdown')

        # Get users id (faculty who created the question)
        user_id = session.get('users_id')

        try:
            create_question.create_question(question_text, example_text, user_id, selected_tags)

        except TypeError: #Type error for tag mistmatch
            msg = "Error has occured:\n Tag Mismatch (let developer know what tags you were trying to add)"
            return render_template("404.html", msg = msg, user_state = session.get('user_state'))

        except OverflowError: #Overflow for an answer being too long (The database is set up so that an answer can be 150 characters long)
            msg = "Error has occured:\n Answers couldn't be uploaded into the database, (let developer know there is an issue with inputting answers)"
            return render_template("404.html", msg = msg, user_state = session.get('user_state'))


        session['edited_question_id'] = create_question.get_latest_question_ID()
        question_id = create_question.get_latest_question_ID()

        create_question.inputImages(UPLOAD_FOLDER, question_id) #Uploads images from page to the file structure

        question = get_question.getquestionfromdatabase(question_id, UPLOAD_FOLDER)

        
        return redirect(url_for('success_page', question= question, user_state = session.get('user_state')))
    return render_template('addQuestion.html', user_state = session.get('user_state'), msg = "")
