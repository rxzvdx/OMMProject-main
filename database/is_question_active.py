# SWE Team 6:
# Joseph, Tyler, Antonio, Ross, Kashan, Gavin
# File: is_question_active.py
# Purpose: check the status of a quention being active or not
# Last edited: 02/17/2025

from database.connection import makeConnection

#Checks to see if question is active or not based on it's ID, 
# returns TRUE if is_active = 1, FALSE otherwise
def is_active(id):
    # Start connection
    cnx = makeConnection()
    cursor = cnx.cursor()

    #Gather a question that is active, it it exists then check will not equal NONE
    cursor.execute(f"SELECT question_text FROM question WHERE question_ID = {id} AND is_active = 1")
    check = cursor.fetchone()

    cnx.close()
    cursor.close()

    if check:
        return True
    return False