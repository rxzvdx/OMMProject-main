# SWE Team 6:
# Joseph, Tyler, Antonio, Ross, Kashan, Gavin
# File: create_question.py
# Purpose: Retrieves all test attempts made by a specific user 
#          from a database and returns them as a list of lists.
# Last edited: 02/07/2025

import connection as dc

# Establish a connection to the database
cnx = dc.makeConnection()

# Function to fetch all test attempts of a given user
def getAttempts(cnx, user_id):

    cursor = cnx.cursor() # Create a cursor obj to interact with database
    # SQL query to retrieve attempt details for the given user_id
    query = (f"""select a.attempt_id, a.test_id, attempt_date, attempt_number, test_name
            from attempt a
            join test t on t.test_id = a.test_id
            where a.users_id = {user_id};""")
    
    """ POTENTIAL SQL INJECTION RISK 
    The query uses an f-string with {user_id}, making it 
    vulnerable to SQL injection. Use parameterized queries instead: 
    """
    # query = """SELECT a.attempt_id, a.test_id, attempt_date, attempt_number, test_name
         #  FROM attempt a
         #  JOIN test t ON t.test_id = a.test_id
         #  WHERE a.users_id = %s;"""
# cursor.execute(query, (user_id,))


    cursor.execute(query)

    results = cursor.fetchall()

    attempts = []

    for result in results:
        attempts.append([result[0], result[1], str(result[2]), result[3], result[4]])

    cnx.close()

    return attempts
