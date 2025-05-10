# SWE Team 6:
# Joseph, Tyler, Antonio, Ross, Kashan, Gavin
# File: createTest.py
# Purpose: 
#   1.) The function creates a test by collecting user input, such as
#       the number of questions, selected categories, and test options
#   2.) It connects to the database, retrieves the user's ID, generates a test entry
#       and records the attempt. The user is then redirected to the test page
# Last edited: 02/06/2025. 

from flask import redirect, render_template, request, session, url_for
from connection import makeConnection


def create():
    firstName = session.get('user_firstName') 
    if request.method == 'POST':
        #Start connection
        cnx = makeConnection()
        
        isTutor = False
        isTimed = False

        if request.form.get("tutoredTest"):
            isTutor = True
        
        if request.form.get("timedTest"):
            isTimed = True
            
        # TODO MAKE SURE TO CHANGE FORM VALUES FOR SELECTED_TAGS
        # TODO TELL FRONTEND TO ADD IN MISSING TAGS
        
        select_tags = request.form.getlist('category') # contains list of categories chosen
        
        try:
            number_of_questions = int(request.form.get('numberInput')) # holds the number of questions student entered
        except (TypeError, ValueError): 
            number_of_questions = 1  # Default to 1 if conversion fails
            
        users_id = session.get('users_id') # Grab current person logged in user_id
        
        testName = request.form.get('testNameInput').strip() # Get name of test
        if len(testName) == 0: # If test is unnamed
          testName = "Unnamed Test"  

        from database.make_test import makeTest
        from datetime import date
        from database.make_attempt import makeAttempt
        date = str(date.today())

        test_id = makeTest(cnx, select_tags, number_of_questions, users_id, testName, isTutor, isTimed, date)
        attempt_num, attempt_id = makeAttempt(cnx, test_id)
        session['test_id'] = test_id
        session['attempt_num'] = attempt_num
        session['attempt_id'] = attempt_id

        cnx.close()

        return redirect(url_for('take_test', test_id=test_id, isTimed=isTimed, isTutor=isTutor))
    return render_template('createTest.html', firstName=firstName, user_state = session.get('user_state'))
