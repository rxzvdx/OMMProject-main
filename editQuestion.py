# SWE Team 6:
# Joseph, Tyler, Antonio, Ross, Kashan, Gavin
# File: editQuestion.py
# Purpose:  
#   1.) Allows users to edit questions in the database. It handles updating 
#   question text, explanations, tags, and associated images.
#   2.) When editing, it deactivates the old question, creates a new one, and transfers old images if necessary.
#   3.) It includes error handling for invalid input and ensures images are properly saved. 
# Last edited: 02/06/2025 

import os
from database import get_question, create_question
from flask import flash, redirect, render_template, request, session, url_for
from connection import makeConnection
from werkzeug.utils import secure_filename
from models import Question

def editQuestionByID(id, UPLOAD_FOLDER):
    oldQuestion = get_question.getquestionfromdatabase(id, UPLOAD_FOLDER)

    if request.method == 'POST':
        if request.form['button'] == "editQuestion":
            question_text = request.form['questionInput']     
            example_text = request.form['explanationInput']
            selected_tags = request.form.getlist('subjectDropdown')

            # Get user's ID (faculty who created the question)
            user_id = session.get('users_id')

            try:
                create_question.create_question(question_text, example_text, user_id, selected_tags)
            except TypeError:
                msg = "Error has occurred:\n Tag Mismatch (let developer know what tags you were trying to add)"
                return render_template("404.html", msg=msg, user_state=session.get('user_state'))
            except OverflowError:
                msg = "Error has occurred:\n Answers couldn't be uploaded into the database, (let developer know there is an issue with inputting answers)"
                return render_template("404.html", msg=msg, user_state=session.get('user_state'))

            deleteQuestion(oldQuestion.getID())  # Deactivates the old question in the database

            id = create_question.get_latest_question_ID()  # Grab new ID after editing
            session['edited_question_id'] = id

            # Image flags for removal
            removeImageFlag = request.form.get("removeImage") == "true"
            removeExplanationImageFlag = request.form.get("removeExplanationImage") == "true"

            # Remove old images if requested
            oldImagePath = f"{UPLOAD_FOLDER}/question_{oldQuestion.getID()}.jpeg"
            oldExplanationPath = f"{UPLOAD_FOLDER}/question_{oldQuestion.getID()}_explanation.jpeg"

            if removeImageFlag and os.path.exists(oldImagePath):
                os.remove(oldImagePath)
                flash("Old image removed.")

            if removeExplanationImageFlag and os.path.exists(oldExplanationPath):
                os.remove(oldExplanationPath)
                flash("Old explanation image removed.")

            # Handle new image uploads
            image = request.files.get("image")
            explanationImage = request.files.get("explanationImage")
            newImageUploaded = image and image.filename != "" and allowed_file(image.filename)
            newExplanationImageUploaded = explanationImage and explanationImage.filename != "" and allowed_file(explanationImage.filename)

            if newImageUploaded:
                filename = f"question_{id}.jpeg"
                image.save(os.path.join(UPLOAD_FOLDER, filename))
                flash("New image saved.")

            if newExplanationImageUploaded:
                filename = f"question_{id}_explanation.jpeg"
                explanationImage.save(os.path.join(UPLOAD_FOLDER, filename))
                flash("New explanation image saved.")

            # **Only transfer old images if no new image was uploaded and the old image was not removed**
            if not newImageUploaded and not removeImageFlag and oldQuestion.getImage():
                transferImages(UPLOAD_FOLDER, id, oldQuestion)

            if not newExplanationImageUploaded and not removeExplanationImageFlag and oldQuestion.getExplanationImage():
                transferImages(UPLOAD_FOLDER, id, oldQuestion)

            question = get_question.getquestionfromdatabase(id, UPLOAD_FOLDER)
            return redirect(url_for('success_page', question=question))

        if request.form['button'] == "deleteQuestion":
            deleteQuestion(id)  # Deactivates the question in the database
            deleteImages(id, UPLOAD_FOLDER)
            return render_template('404.html', msg="Successfully deleted question", user_state=session.get('user_state'))

    return render_template('editQuestion.html', question=oldQuestion, user_state=session.get('user_state'), msg="")


# UNUSED edit_question
# Given the old Question object, insert a new question 
def edit_question(oldQuestion, UPLOAD_FOLDER): 

    # Get question_text and example_text
    question_text = request.form['questionInput']     
    example_text = request.form['explanationInput']   

    # Get users id (faculty who created the question)
    user_id = session.get('users_id')

    # Start connection
    cnx = makeConnection()
    cursor = cnx.cursor()

    # Disable old question 
    remove_old_question = (f"""UPDATE question
                           SET is_active = 0
                           WHERE question_ID = {oldQuestion.getID()}""")
    cursor.execute(remove_old_question)
    cnx.commit()

    # Insert question text, example text, is_active (Default 1), users_id (Work in Progress)
    insert_question = ("INSERT INTO question(question_text, example_text, is_active, users_ID) VALUES(%s, %s, %s, %s)")
    values = (question_text, example_text, 1, user_id)
    cursor.execute(insert_question, values)
    cnx.commit()

    # Get question id for question we just added
    query_question = (f"SELECT question_ID FROM question WHERE question_text = \"{question_text}\" AND is_active = 1")
    cursor.execute(query_question)
    question_id = cursor.fetchall()[0][0]

     # Checking to see if an image was given for the question
    if "image" not in request.files:
        flash('No Image')
    else:
        flash('Yes Image')
        image = request.files["image"]

        if image.filename != '' and allowed_file(image.filename):
            image.filename = 'question_' + str(question_id) + '.jpeg'
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))
        else:
            flash('Invalid file. Please only choose a jpeg.')

    # # Checking to see if an explanation image was given
    if "explanationImage" not in request.files:
        flash('No Image')
    else:
        flash('Yes Image')
        explanationImage = request.files["explanationImage"]

        if explanationImage.filename != '' and allowed_file(explanationImage.filename):
            explanationImage.filename = 'question_' + str(question_id) + '_explanation.jpeg'
            filename = secure_filename(explanationImage.filename)
            explanationImage.save(os.path.join(UPLOAD_FOLDER, filename))
        else:
            flash('Invalid file. Please only choose a jpeg.')

    

    selected_tags = request.form.getlist('subjectDropdown')
    
    # For tags, loop through all the tags and see which one are checked
    # Then query for the tag id and insert into tag_question before moving on to
    # The next tag
    for tag in selected_tags:
        query_tag = (f"SELECT tag_ID FROM tag WHERE tag_name = \"{tag}\"")
        cursor.execute(query_tag)
        tag_id = cursor.fetchone()

        if tag_id:
            tag_id = tag_id[0] #Gets the tag_id item
            insert_tag_question = (f"INSERT INTO tag_question(tag_ID, question_ID) VALUES(%s, %s)")
            values = (tag_id, question_id)
            cursor.execute(insert_tag_question, values)
            cnx.commit()

    # Old answers from previous question
    answers = oldQuestion.getAnswers()

    answer_texts = [] # THIS IS FOR SPRINT MEETING TO SHOWCASE
    for i in range(1, 6):
        insert_answer = "INSERT INTO answer(answer_text) VALUES (%s)"
        answer_text = request.form.get(f'answer{i}')
        correctAnswer = int(request.form.get('correctAnswer'))

        if answer_text != "":
            if i is correctAnswer:
                is_correct = 1
            else:
                is_correct = 0

            # is_correct = 1 if request.form.get(f'correctAnswer{i}') else 0 #Can probably get rid of this line
            
            query_answer = (f"SELECT answer_ID FROM answer WHERE answer_text = \"{answer_text}\"")
            cursor.execute(query_answer)
            answer_id = cursor.fetchone()

            #There is a duplicate answer, we don't need to create another answer in the database, just link it to the new question
            if answer_text != "" and not answer_id:
                    values = (answer_text,)
                    cursor.execute(insert_answer, values)
                    cnx.commit()
                    answer_texts.append(answer_text)

            # Get answer id for answer1 
            query_answer = (f"SELECT answer_ID FROM answer WHERE answer_text = \"{answer_text}\"")
            cursor.execute(query_answer)
            answer_id = cursor.fetchall()[0][0]

            # Insert answer id into question_answer bridging table
            insert_question_answer = ("INSERT INTO question_answer(question_ID, answer_ID, is_correct) VALUES(%s, %s, %s)")
            values = (question_id, answer_id, is_correct)
            cursor.execute(insert_question_answer, values)
            cnx.commit()
        else:
            print(f"Answer {i} is None.")

    #Close connection
    cnx.close()
    cursor.close()

    return question_id

# If there are images attached to the old question, move them to the new question
def transferImages(UPLOAD_FOLDER, newID, oldQuestion: Question):
    image = request.files.get("image")  # Use .get() to avoid KeyError
    explanationImage = request.files.get("explanationImage")

    # Handling main question image
    if image and image.filename != "" and allowed_file(image.filename):  # Save new image
        flash('Yes, new image found.')
        image.filename = f"question_{newID}.jpeg"
        filename = secure_filename(image.filename)
        image.save(os.path.join(UPLOAD_FOLDER, filename))
        flash('New image saved.')
    
    elif oldQuestion.getImage():  # Only rename if it exists
        oldFileName = f"{UPLOAD_FOLDER}\\question_{str(oldQuestion.getID())}.jpeg"
        newFileName = f"{UPLOAD_FOLDER}\\question_{newID}.jpeg"
        
        if os.path.exists(oldFileName):  # Prevent renaming a non-existent file
            os.rename(oldFileName, newFileName)
            flash('Image attached from older question.')
        else:
            flash('No image found to transfer.')

    else:
        flash('No image from user or old question.')

    # Handling explanation image
    if explanationImage and explanationImage.filename != "" and allowed_file(explanationImage.filename):  # Save new explanation image
        flash('Yes, new explanation image found.')
        explanationImage.filename = f"question_{newID}_explanation.jpeg"
        filename = secure_filename(explanationImage.filename)
        explanationImage.save(os.path.join(UPLOAD_FOLDER, filename))
        flash('New explanation image saved.')
    
    elif oldQuestion.getExplanationImage():  # Only rename if it exists
        oldFileName = f"{UPLOAD_FOLDER}\\question_{str(oldQuestion.getID())}_explanation.jpeg"
        newFileName = f"{UPLOAD_FOLDER}\\question_{newID}_explanation.jpeg"
        
        if os.path.exists(oldFileName):  # Prevent renaming a non-existent file
            os.rename(oldFileName, newFileName)
            flash('Explanation image attached from older question.')
        else:
            flash('No explanation image found to transfer.')

    else:
        flash('No explanation image from user or old question.')


# Deactivate a question depending on the ID of the question
def deleteQuestion(id):
    cnx = makeConnection()
    cursor = cnx.cursor()

    #Deactivates a question depending on it's ID
    cursor.execute("UPDATE question SET is_active=0 WHERE question_ID=%s", (id, ))
    cnx.commit()

    #Close connection
    cnx.close()
    cursor.close()

# Remove images associated to a question based on it's ID
def deleteImages(id, UPLOAD_FOLDER):
    questionFilename = secure_filename('question_' + str(id) + '.jpeg')
    explanationFilename = secure_filename('question_' + str(id) + '_explanation.jpeg')

    try:
        os.remove(os.path.join(UPLOAD_FOLDER, questionFilename))
    except:
        print("No question image to delete")
    try:
        os.remove(os.path.join(UPLOAD_FOLDER, explanationFilename))
    except:
        print("No explanation image to delete")


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png', 'bmp'} 
    
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
