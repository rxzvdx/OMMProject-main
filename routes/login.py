# SWE Team 6:
# Joseph, Tyler, Antonio, Ross, Kashan, Gavin
# File: login.py
# Purpose:  
#   1.) Handles user login by validating email and password against the database.
#   2.) Encrypts the password using SHA-256 and checks for matching record in the users table
#       if a match is found, it stores user details in the session and redirects to the home page.
#       If the login is invalid, it flashes an error message.  
# Last edited: 02/06/2025 

from hashlib import sha256
from flask import flash, redirect, render_template, request, session, url_for
from database.connection import makeConnection


def userLogin():

    #   Grab user info
    if request.method == 'POST':
        
        email = request.form['email']
        password = request.form['password']

        password = sha256(password.encode('utf-8')).hexdigest() #encrypts the password to gather it from the user table
        #   Start connection
        dbConnect = makeConnection()
        cursor = dbConnect.cursor()

        #   Select username and password that match given
        query = 'SELECT * FROM users WHERE email = %s AND pass = %s'
        cursor.execute(query, (email, password))
        user = cursor.fetchone()
        #   Close Connection

        if user:
            users_id = user[0]
            user_state = user[1] 
            user_firstName = user[2]
            user_email = user[4]
            session['users_id'] = users_id
            session['user_state'] = user_state
            session['user_firstName'] = user_firstName
            session['user_email'] = user_email
            print("Session data:", session)
            return redirect(url_for('home'))
        else:
            flash("Invalid login", 'Invalid credentials')

        #Close connection
        dbConnect.close()
        cursor.close()

    return render_template('index.html')
