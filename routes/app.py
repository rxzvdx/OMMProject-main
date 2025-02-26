# SWE Team 6:
# Joseph, Tyler, Antonio, Ross, Kashan, Gavin
# File: app.py
# Purpose: 
#   1.) This Flash application serves as the backend for a web-based test management system
#   2.) Handles user authentication, question management, test creation, and test-taking functionality
#   3.) Connects to a database to retreive and store questions, answers, and test results
#   4.) Users can sign up, login, create and edit questions, search for questions, take tests, and view their test history and statistics
#   5.) Provides various routes for rendering different pages, processing form submissions, and managing user sessions
#   6.) Includes functionality for viewing past test attempts, submitting test data, and error handling
# Last edited: 02/06/2025 


from flask import Flask, render_template, request, redirect, url_for, session,  flash, jsonify
from routes.signup import signUpUser
from config.config import config
import os
import datetime 
from database import get_attempts, get_question, is_question_active
from models import answer, question
from routes.login import userLogin
from routes.search_question import searchQuestions
from routes.add_question import addQuestionToDB
from routes.edit_question import editQuestionByID
from routes.submit_data import submit
from scripts.create_test import create
import database.connection as dc

app = Flask(__name__)
app.secret_key = 'verySecretKey'

#Current Version
version = "Alpha 1.5.5"

UPLOAD_FOLDER = config.upload_folder

# A test route for us to to test certain things.
@app.route('/success', methods = ['GET', 'POST'])
def success():
    return render_template('success_page.html', question = get_question.getquestionfromdatabase(38, UPLOAD_FOLDER), user_state = session.get('user_state'))

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    return signUpUser()

#   Test Successful Connection
@app.route('/test_database')
@app.route('/test_database.html')
def testDataBase():

    #   Initialize connection
    dbConnect = dc.makeConnection()
    cursor = dbConnect.cursor()

    #   Grab data
    query = "SELECT q.example_text, q.is_active, qa.is_correct, a.answer_text, t.dtype, t.tag_name FROM question q  LEFT JOIN question_answer qa  ON  qa.question_ID = q.question_ID LEFT JOIN answer a ON a.answer_ID = qa.answer_ID LEFT JOIN tag_question tq ON tq.question_ID = q.question_ID LEFT JOIN tag t ON t.tag_ID = tq.tag_ID"
    cursor.execute(query)
    results = cursor.fetchall()

    #   close connection
    cursor.close()
    dbConnect.close()

    return render_template('test_database.html', results=results)

#   Get user to login
@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/index.html', methods = ['GET', 'POST'])
def login():
    return userLogin()

#   Adding a question
@app.route('/addQuestion', methods=['GET', 'POST'])
@app.route('/addQuestion.html', methods=['GET', 'POST'])
def addQuestion():
    return addQuestionToDB(UPLOAD_FOLDER)

# Edit a question route
@app.route('/editQuestion/<int:id>', methods=['GET', 'POST'])
@app.route('/editQuestion.html', methods=['GET', 'POST'])
def editQuestion(id):
    #Redirect user to an editable question, only active questions are editable.
    if (is_question_active.is_active(id)):
        return editQuestionByID(id, UPLOAD_FOLDER)
    
    return render_template("404.html", msg = "Question does not exist", user_state = session.get('user_state'))



# User auth complete, send them to home page
@app.route('/home')
@app.route('/home.html')
def home():
    firstName = session.get('user_firstName')
    user_state = session.get('user_state')

    if firstName:
        return render_template('home.html', firstName = firstName, user_state = user_state, version = version)
    else:
        flash("please log in to access the dashboard.", 'error')
        return redirect(url_for('index.html'))

@app.route('/dashboard')
@app.route('/dashboard.html')
def dashboard():

    user_email = session.get('user_email')
    if user_email:
        return render_template('home.html', user_email=user_email)
    else:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('index'))


# User wants to go to create test page
@app.route('/createTest', methods=['POST', 'GET'])
@app.route('/createTest.html', methods=['POST', 'GET'])
def createTest():
    return create()

# User is going to take test
@app.route('/test', methods = ['GET', 'POST'])
@app.route('/test.html', methods = ['GET', 'POST']) 
def take_test():

    test_id = request.args.get('test_id')
    isTimed = request.args.get('isTimed')
    isTutor = request.args.get('isTutor')


    # TODO CHECK IF TEST_ID IS LINKED WITH USER_ID IF NOT THROW 404

    cnx = dc.makeConnection()

    from database.get_test import getTest
    testSet = getTest(cnx, test_id, UPLOAD_FOLDER)


    return render_template('test.html', test_id=test_id, testList=testSet, isTimed=isTimed, isTutor=isTutor, user_state = session.get('user_state'))


#Testing Environment for taking a test
@app.route('/testTemp', methods = ['GET', 'POST'])
@app.route('/testTemp.html', methods = ['GET', 'POST']) 
def take_temp_test():

    test_id = 43
    isTimed = True
    isTutor = True


    # TODO CHECK IF TEST_ID IS LINKED WITH USER_ID IF NOT THROW 404

    cnx = dc.makeConnection()

    from database.get_test import getTest
    testSet = getTest(cnx, test_id, UPLOAD_FOLDER)


    return render_template('testTemp.html', test_id=test_id, testList=testSet, isTimed=isTimed, isTutor=isTutor, user_state = session.get('user_state'))


# User wants to go to view statistics
@app.route('/viewStats')
@app.route('/viewStats.html')
def viewStats():
    user_id = session.get('users_id')
    cnx = dc.makeConnection()

    import scripts.stats as stats
    result = stats.getStats(cnx, user_id)

    # If result is None or empty, trigger a 404 error
    if not result or (isinstance(result, dict) and not any(result.values())):
        abort(404)  # This will trigger Flask's built-in 404 handling

    return render_template('viewStats.html', stats=result, user_state=session.get('user_state'))


@app.route('/viewAttempt/<test_id>/<attempt_num>')
@app.route('/viewAttempt.html')
def viewAttempt(test_id, attempt_num):

    cnx = dc.makeConnection()

    from database.get_test import getTest
    from database.get_answer import getAnswer
    testSet = getTest(cnx, test_id, UPLOAD_FOLDER)

    for question in testSet.getTestSet():
        question_id = question.getID()
        question.setGivenAnswer(getAnswer(cnx, test_id, attempt_num, question_id))

    cnx.close()

    return render_template('viewAttempt.html', test_id=test_id, testList=testSet, user_state = session.get('user_state'))


@app.route('/success_page')
@app.route('/success_page.html')
def success_page():
    question_id = session.get('edited_question_id')
    question = get_question.getquestionfromdatabase(question_id, UPLOAD_FOLDER)
    
    return render_template('success_page.html', question = question, user_state = session.get('user_state'))

# User wants to go to view tests
@app.route('/viewTests')
@app.route('/viewTests.html')
def viewTests():

    user_id = session.get('users_id')
    cnx = dc.makeConnection()

    attempts = get_attempts.getAttempts(cnx, user_id)
    
    return render_template('viewTests.html', attempts = attempts, user_state = session.get('user_state'))


@app.route('/submit_data', methods=['POST'])
def submit_data():
    return submit()

@app.route('/testResult')
@app.route('/testResult.html')
def testResult():

    examTime = session.get('exam_time')
    score = session.get('score')
    question_states = session.get('question_states')

    # Format for better output on results page. 
    format_time = datetime.timedelta(seconds=examTime)
    print("format_time: ", format_time)
    return render_template('testResult.html', examTime=format_time, score=score, question_states=question_states, user_state = session.get('user_state'))

# Searching for a question route (You can either search based off of a question ID or a question's tag)
@app.route('/searchQuestion', methods=['GET', 'POST'])
@app.route('/searchQuestion.html',methods=['GET', 'POST'])
def searchQuestion():
    return searchQuestions(UPLOAD_FOLDER)

@app.route('/404', methods=['GET', 'POST'])
def error():
    return render_template('404.html', msg = "No error", user_state = session.get('user_state'))


if __name__ == '__main__':
    app.run(debug=True, port=8000)  # This is on Port 8000 for testing purposes