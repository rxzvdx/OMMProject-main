# SWE Team 6:
# Joseph, Tyler, Antonio, Ross, Kashan, Gavin
# File: signup.py
# Purpose:  
#   1.) Handles user sign up functionality, allowing users to create an account
#       as either a student or faculty member.
#   2.) Checks if the account already exists and validates the input fields
#       ensuring required information like email, name, and password are provided.
#   3.) If the input is valid, the password is encrypted, and the user is added to the database.
#       The user is then redirected to the index page.
#   4.) Includes a helper function getID to retrieve the user's ID based on their email.
# Last edited: 02/06/2025 

#
#           ACCOUNT FLOW:
#           USER IS PROMPTED ON WHETHER THEY ARE FACULTY OR STUDENT
#           BASED ON ANSWER, THEY WILL GET RECEIVE RESPECTIVE ACCOUNT
#           FACULTY: "@ROWAN.EDU" END HANDLE
#           STUDENTS: "@STUDENTS.ROWAN.EDU" END HANDLE
#           OTHER HANDLES WILL NOT BE ACCEPTED

from hashlib import sha256
from flask import Flask, render_template, request, redirect, url_for, session, flash
from connection import makeConnection

# NEW: added for admin role
import uuid
app = Flask(__name__) 

print("[DEBUG] signUpUser() triggered")
def signUpUser():
    msg = ""

    if request.method == 'POST':
        dbConnect = makeConnection()
        cursor = dbConnect.cursor()

        # Role selection
        role = request.form.get('role')
        firstName = request.form['fName']
        lastName = request.form['lName']
        password = request.form['password']
        email = request.form['email']

        eligibleToCreateUser = True

        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()

        cursor.close()

        if account:  # If that account already exists, we won't let the user create that account.
            msg = "Account already exists with that email\n"
            eligibleToCreateUser = False

        # Checks to make sure required fields are filled
        if not email:
            msg += "Email required\n"
            eligibleToCreateUser = False

        if not firstName:
            msg += "First name required\n"
            eligibleToCreateUser = False

        if not lastName:
            msg += "Last name required\n"
            eligibleToCreateUser = False

        if not password:
            msg += "Password required\n"
            eligibleToCreateUser = False

        if not role:
            msg += "Role selection required\n"
            eligibleToCreateUser = False

        # If the account doesn't already exist and fields are valid
        if eligibleToCreateUser:
            password = sha256(password.encode('utf-8')).hexdigest()  # Encrypts the password before saving to the database.
            
            userCursor = dbConnect.cursor()
            idCursor = dbConnect.cursor()

        # NEW: admin role creation and request sent to db
            if role == 'admin':
                print(f"[DEBUG] Admin signup submitted for {email}")
                verification_token = str(uuid.uuid4())
                userCursor.execute('''
                    INSERT INTO admin_requests(first_name, last_name, email, pass, verification_token)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (firstName, lastName, email, password, verification_token))
                dbConnect.commit()
                
            # Email domain check for student or faculty
            elif email.endswith('@students.rowan.edu'):
                userCursor.execute('INSERT INTO users(dtype, first_name, last_name, email, pass) VALUES ("student", %s, %s, %s, %s)', (firstName, lastName, email, password))
                dbConnect.commit()
                newUserID = getID(email)
                idCursor.execute('INSERT INTO student(users_ID) VALUES(%s)', (newUserID,))
            elif email.endswith('@rowan.edu'):
                userCursor.execute('INSERT INTO users(dtype, first_name, last_name, email, pass) VALUES ("faculty", %s, %s, %s, %s)', (firstName, lastName, email, password))
                dbConnect.commit()
                newUserID = getID(email)
                idCursor.execute('INSERT INTO faculty(users_ID) VALUES(%s)', (newUserID,))
            else:
                msg += "Invalid email domain. Please use a valid Rowan email address.\n"
                eligibleToCreateUser = False

            userCursor.close()
            idCursor.close()  # Closing all connections

            dbConnect.commit()  # Committing all of the information to the database
            if eligibleToCreateUser and role != 'admin':
                # admin will await request approval, inelligble will jsut be redirected.
                return redirect('/index')
        
    return render_template("signup.html", msg=msg)

def getID(email):
    dbConnect = makeConnection()
    cursor = dbConnect.cursor()

    cursor.execute("SELECT users_ID FROM users WHERE email=%s", (email,))
    id = cursor.fetchone()[0]  # [0] is the ID in the 2D list returned from the database
    
    cursor.close()
    dbConnect.close()

    return id

# NEW: email sender
def send_verification_email(email, token):
    verification_link = f"http://localhost:5000/verify-admin{token}"
    print(f"Admin accesses this link: {verification_link}")
    # we can add more email sending logic here
    
# NEW: route to verify admin acct
@app.route('/verify-admin/<token>')
def verify_admin(token):
    dbConnect = makeConnection()
    cursor = dbConnect.cursor()
    
    cursor.execute("SELECT * FROM admin_requests WHERE verification_token = %s", (token,))
    request_info = cursor.fetchone()
    
    if request_info:
        _, first, last, email, password, _, _ = request_info
        
        cursor.execute('''
            INSERT INTO users(dtype, first_name, last_name, email, pass)
            VALUES ('admin', %s, %s, %s, %s)
            ''', (first, last, email, password))
        dbConnect.commit()
        
        cursor.execute("DELETE FROM admin_requests WHERE verification_token = %s", (token,))
        dbConnect.commit()

        msg = "Admin account verified and created. You can now log in."
    else:
        msg = "Invalid or expired verification link."

    cursor.close()
    dbConnect.close()

    return render_template("verify_admin.html", msg=msg)

