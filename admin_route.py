from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from database.get_admin_requests import get_admin_requests
from connection import makeConnection
import hashlib

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

# Route: Admin Dashboard
@admin_bp.route('/dashboard')
def admin_dashboard():
    if 'users_id' not in session:
        return redirect(url_for('login'))

    db = makeConnection()
    cur = db.cursor()

    # Check if user is an admin
    cur.execute("SELECT dtype FROM users WHERE users_ID = %s", (session['users_id'],))
    role = cur.fetchone()
    if not role or role[0] != 'admin':
        return "Access Denied"
    
    session['user_state'] = role[0]

    # Get all users who are students or faculty
    cur.execute("SELECT users_ID, first_name, last_name, email, dtype FROM users WHERE dtype IN ('student', 'faculty')")
    users = cur.fetchall()

    # Get pending admin requests
    admin_requests = get_admin_requests()

    cur.close()
    db.close()
    return render_template("admin/admin_dashboard.html", users=users, requests=admin_requests, user_state=session.get('user_state'))


# Route: Change Role (student ⇄ faculty) with password confirmation
@admin_bp.route('/change-role', methods=['POST'])
def change_user_role():
    if 'users_id' not in session:
        return redirect(url_for('login'))

    db = makeConnection()
    cur = db.cursor()

    admin_id = session.get('users_id')
    admin_input = request.form['admin_password']

    # Hash the provided password using SHA-256
    hashed_input = hashlib.sha256(admin_input.encode()).hexdigest()

    # Get stored hash from DB
    cur.execute("SELECT dtype, pass FROM users WHERE users_ID = %s", (admin_id,))
    result = cur.fetchone()

    if not result or result[0] != 'admin':
        return "Access Denied"

    db_password = result[1]

    if hashed_input != db_password:
        return "Incorrect password"

    # Toggle target user role
    target_id = request.form['user_id']
    current_role = request.form['current_role']
    new_role = 'faculty' if current_role == 'student' else 'student'

    cur.execute("UPDATE users SET dtype = %s WHERE users_ID = %s", (new_role, target_id))

    # Update role-specific tables
    if current_role == 'student':
        cur.execute("DELETE FROM student WHERE users_ID = %s", (target_id,))
        cur.execute("INSERT INTO faculty(users_ID) VALUES(%s)", (target_id,))
    else:
        cur.execute("DELETE FROM faculty WHERE users_ID = %s", (target_id,))
        cur.execute("INSERT INTO student(users_ID) VALUES(%s)", (target_id,))

    db.commit()
    cur.close()
    db.close()

    flash("User role updated successfully.", "success")
    return redirect(url_for('admin_bp.admin_dashboard'))

# Route: Handle admin request approval/denial
@admin_bp.route('/handle-request', methods=['POST'])
def handle_admin_request():
    if 'users_id' not in session:
        return redirect(url_for('login'))

    email = request.form.get('email')
    action = request.form.get('action')

    conn = makeConnection()
    cursor = conn.cursor()

    if action == 'approve':
        # Check if already in users table
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if not existing_user:
            # Get info from admin_requests
            cursor.execute("SELECT first_name, last_name, pass FROM admin_requests WHERE email = %s", (email,))
            data = cursor.fetchone()

            if data:
                first_name, last_name, pw_hash = data
                cursor.execute(
                    "INSERT INTO users (dtype, first_name, last_name, email, pass) VALUES ('admin', %s, %s, %s, %s)",
                    (first_name, last_name, email, pw_hash)
                )
        else:
            # If already exists, promote to admin
            cursor.execute("UPDATE users SET dtype = 'admin' WHERE email = %s", (email,))

    # Delete the request regardless of action
    cursor.execute("DELETE FROM admin_requests WHERE email = %s", (email,))

    conn.commit()
    cursor.close()
    conn.close()

    flash(f"Request for {email} {action}d successfully.", 'success')
    return redirect(url_for('admin_bp.admin_dashboard'))
