# SWE Team 6:
# Joseph, Tyler, Antonio, Ross, Kashan, Gavin
# File: searchQuestion.py
# Purpose:  
#   1.) Handles searching for questions based on their ID or tag.
#   2.) Allows users to search for a question by its ID and reedirects to an edit page, 
#       or search for questions by a specific tag, displaying results on the search page.
#   3.) Queries the database for questions with the selected tag and returns the results as a list of 
#       dictionaries containing the question ID, text, and tag
# Last edited: 02/06/2025 

from database import get_question
from connection import makeConnection
from flask import flash, redirect, render_template, request, session


def searchQuestions(UPLOAD_FOLDER):
    tagQuestions = []
    tag = ""
    if request.method == 'POST':
        if request.form['button'] == "idSearch":
            if request.form['searchQuestionID']:
                question_id = request.form.get('searchQuestionID')
                try:
                    question = get_question.getquestionfromdatabase(int(question_id), UPLOAD_FOLDER)
                    return redirect((f'/editQuestion/{question_id}'))
                except Exception as e:
                    flash(f"An error occurred while searching for that question.", "danger")
                    return redirect((f'/searchQuestion'))

        if request.form['button'] == "tagSearch":
          tag = request.form.get('tagDropdown')
    
          #tagQuestions is a list of question dictionaries containing questionID, questionText, and tag
          tagQuestions = getQuestionListByTag(tag)
 
          #Passes the question list to searchQuestions.html 
          return render_template('searchQuestion.html', tagQuestions = tagQuestions, tag = tag, user_state = session.get('user_state'))
    return render_template('searchQuestion.html', tagQuestions = tagQuestions, tag=tag, user_state = session.get('user_state'))



# Give a tag and the function will return all the questions that have that tag
def getQuestionListByTag(tag):
    
    # Start connection
    cnx = makeConnection()
    cursor = cnx.cursor()
    
    
    # tag to search questions from
    question_tag = tag

    # querying from the database for questions that have tag
    query = (f"""SELECT q.question_ID, q.question_text, t.tag_name AS 'tag' 
             FROM omm.question q
            JOIN omm.tag_question tq ON (q.question_ID = tq.question_ID)
            JOIN omm.tag t ON (tq.tag_ID = t.tag_ID)
            WHERE q.is_active = 1 AND t.tag_name = \"{question_tag}\"; """)
    
    
    cursor.execute(query)

    results = cursor.fetchall()

    #current question
    index = 0

    questions = []

    # Storing all the questions into dictionaries and then into the questions list
    for question in results:
        searchResult = {
            'questionID' : results[index][0],
            'questionText' : results[index][1],
            'tag' : results[index][2]
        }

        questions.append(searchResult)

        index += 1

     #Close connection
    cnx.close()
    cursor.close()

    return questions
