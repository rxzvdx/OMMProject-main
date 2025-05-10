# SWE Team 6:
# Joseph, Tyler, Antonio, Ross, Kashan, Gavin
# File: app.py
# Purpose: 
#   1.) This Flask application serves as the backend for a web-based test management system
#   2.) Handles user authentication, question management, test creation, and test-taking functionality
#   3.) Connects to a database to retrieve and store questions, answers, and test results
#   4.) Users can sign up, login, create and edit questions, search for questions, take tests, and view their test history and statistics
#   5.) Provides various routes for rendering different pages, processing form submissions, and managing user sessions
#   6.) Includes functionality for viewing past test attempts, submitting test data, and error handling
# Last edited: 04/03/2025
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from signup import signUpUser
from config import config
import os
import datetime 
from database import get_attempts, get_question, is_question_active
from models import Answer, Question
from login import userLogin
from searchQuestion import searchQuestions
from addQuestion import addQuestionToDB
from editQuestion import editQuestionByID
from submit_data import submit
from createTest import create
import connection as dc
from admin_route import admin_bp 

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_email'):
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


app = Flask(__name__)
app.secret_key = 'verySecretKey'
app.register_blueprint(admin_bp)
print("DEBUGGER: Admin blueprint registered")

#Current Version
version = "Alpha 1.5.5"

UPLOAD_FOLDER = config.upload_folder

@app.route('/success', methods=['GET', 'POST'])
@login_required
def success():
    return render_template('success_page.html', question=get_question.getquestionfromdatabase(38, UPLOAD_FOLDER), user_state=session.get('user_state'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return signUpUser()

@app.route('/test_database')
@app.route('/test_database.html')
def testDataBase():
    dbConnect = dc.makeConnection()
    cursor = dbConnect.cursor()

    query = """SELECT q.example_text, q.is_active, qa.is_correct, a.answer_text, t.dtype, t.tag_name
               FROM question q
               LEFT JOIN question_answer qa ON qa.question_ID = q.question_ID
               LEFT JOIN answer a ON a.answer_ID = qa.answer_ID
               LEFT JOIN tag_question tq ON tq.question_ID = q.question_ID
               LEFT JOIN tag t ON t.tag_ID = tq.tag_ID"""
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    dbConnect.close()

    return render_template('test_database.html', results=results)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index.html', methods=['GET', 'POST'])
def login():
    return userLogin()

@app.route('/addQuestion', methods=['GET', 'POST'])
@app.route('/addQuestion.html', methods=['GET', 'POST'])
@login_required
def addQuestion():
    return addQuestionToDB(UPLOAD_FOLDER)

@app.route('/editQuestion/<int:id>', methods=['GET', 'POST'])
@app.route('/editQuestion.html', methods=['GET', 'POST'])
@login_required
def editQuestion(id):
    if is_question_active.is_active(id):
        return editQuestionByID(id, UPLOAD_FOLDER)
    return render_template("404.html", msg="Question does not exist", user_state=session.get('user_state'))

@app.route('/home')
@app.route('/home.html')
@login_required
def home():
    firstName = session.get('user_firstName')
    lastName = session.get('user_lastName')
    user_state = session.get('user_state')
    if firstName:
        return render_template('home.html', firstName=firstName, lastName=lastName, user_state=user_state, version=version)
    else:
        flash("please log in to access the dashboard.", 'error')
        return redirect(url_for('index.html'))

@app.route('/dashboard')
@app.route('/dashboard.html')
@login_required
def dashboard():
    user_email = session.get('user_email')
    if user_email:
        return render_template('home.html', user_email=user_email)
    else:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('index'))

@app.route('/createTest', methods=['POST', 'GET'])
@app.route('/createTest.html', methods=['POST', 'GET'])
@login_required
def createTest():
    return create()

@app.route('/test', methods=['GET', 'POST'])
@app.route('/test.html', methods=['GET', 'POST'])
@login_required
def take_test():
    test_id = request.args.get('test_id')
    isTimed = request.args.get('isTimed')
    isTutor = request.args.get('isTutor')

    cnx = dc.makeConnection()
    from database.get_test import getTest
    testSet = getTest(cnx, test_id, UPLOAD_FOLDER)
    return render_template('test.html', test_id=test_id, testList=testSet, isTimed=isTimed, isTutor=isTutor, user_state=session.get('user_state'))

@app.route('/testTemp', methods=['GET', 'POST'])
@app.route('/testTemp.html', methods=['GET', 'POST'])
@login_required
def take_temp_test():
    test_id = 43
    isTimed = True
    isTutor = True

    cnx = dc.makeConnection()
    from database.get_test import getTest
    testSet = getTest(cnx, test_id, UPLOAD_FOLDER)
    return render_template('testTemp.html', test_id=test_id, testList=testSet, isTimed=isTimed, isTutor=isTutor, user_state=session.get('user_state'))

@app.route('/viewStats')
@app.route('/viewStats.html')
@login_required
def viewStats():
    user_id = session.get('users_id')
    cnx = dc.makeConnection()
    import stats
    result = stats.getStats(cnx, user_id)
    return render_template('viewStats.html', stats=result, user_state=session.get('user_state'))

@app.route('/viewAttempt/<test_id>/<attempt_num>')
@app.route('/viewAttempt.html')
@login_required
def viewAttempt(test_id, attempt_num):
    cnx = dc.makeConnection()
    from database.get_test import getTest
    from database.get_answer import getAnswer
    testSet = getTest(cnx, test_id, UPLOAD_FOLDER)
    for question in testSet.getTestSet():
        question_id = question.getID()
        question.setGivenAnswer(getAnswer(cnx, test_id, attempt_num, question_id))
    cnx.close()
    return render_template('viewAttempt.html', test_id=test_id, testList=testSet, user_state=session.get('user_state'))

@app.route('/success_page')
@app.route('/success_page.html')
@login_required
def success_page():
    question_id = session.get('edited_question_id')
    question = get_question.getquestionfromdatabase(question_id, UPLOAD_FOLDER)
    return render_template('success_page.html', question=question, user_state=session.get('user_state'))

@app.route('/viewTests')
@app.route('/viewTests.html')
@login_required
def viewTests():
    user_id = session.get('users_id')
    cnx = dc.makeConnection()
    attempts = get_attempts.getAttempts(cnx, user_id)
    return render_template('viewTests.html', attempts=attempts, user_state=session.get('user_state'))

@app.route('/submit_data', methods=['POST'])
def submit_data():
    return submit()

@app.route('/testResult')
@app.route('/testResult.html')
@login_required
def testResult():
    examTime = session.get('exam_time')
    score = session.get('score')
    question_states = session.get('question_states')
    format_time = datetime.timedelta(seconds=examTime)
    return render_template('testResult.html', examTime=format_time, score=score, question_states=question_states, user_state=session.get('user_state'))

@app.route('/searchQuestion', methods=['GET', 'POST'])
@app.route('/searchQuestion.html', methods=['GET', 'POST'])
@login_required
def searchQuestion():
    return searchQuestions(UPLOAD_FOLDER)

@app.route('/404', methods=['GET', 'POST'])
def error():
    return render_template('404.html', msg="No error", user_state=session.get('user_state'))

# New admin toggle route
@app.route('/toggle_admin/<int:user_id>', methods=['POST'])
def toggle_admin(user_id):
    user_state = session.get('user_state')
    if user_state != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    result = toggleAdminStatus(user_id)
    return jsonify(result, user_state)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)

