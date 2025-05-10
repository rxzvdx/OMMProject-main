# SWE Team 6:
# Joseph, Tyler, Antonio, Ross, Kashan, Gavin
# File: create_question.py
# Purpose: This function retrieves the selected answer for 
#          a given question in a specific test attempt from the database. 
#          It uses an SQL query to find the answer_id based on the test_id, 
#          attempt_num, and question_id. 
# Last edited: 02/07/2025

"""
    Retrieves the answer ID for a given test attempt and question.
    
    Parameters:
        cnx (object): Database connection object.
        test_id (int): The ID of the test.
        attempt_num (int): The attempt number for the test.
        question_id (int): The ID of the question.
    
    Returns:
        int or None: The answer ID if found, otherwise None.
    """
def getAnswer(cnx, test_id, attempt_num, question_id):

    # Create a cursor object to execute SQL queries    
    cursor = cnx.cursor()

    # SQL query to retrieve the answer_id from the attempt_answer table
    # Using an INNER JOIN to link attempts and their answers
    query = (f"""select answer_id
            from attempt a
            join attempt_answer an on an.attempt_id = a.attempt_id
            where test_id = {test_id} and attempt_number = {attempt_num} and question_id = {question_id};""")

    # Execute the query with parameterized inputs to prevent SQL injection ???
    cursor.execute(query) 
    #cursor.execute(query, (test_id, attempt_num, question_id))

    result = cursor.fetchall()

    return result[0][0]
