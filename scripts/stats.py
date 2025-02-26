# SWE Team 6:
# Joseph, Tyler, Antonio, Ross, Kashan, Gavin
# File: stats.py
# Purpose:  
#   1.) Retrieves and calculates statistics for a specific student based on their attempted questions 
#       for different tags.
#   2.) Queries the database for the total number of questions, the total attempted questions, and the total correct attempts for each tag.
#   3.) Calculates the percentage of answered and correct attempts for each tag, the results are then stored in a dictionary with the tag
#       as the key and the total, answered percentage, and correct percentages as values.
#   4.) Closes the database connection and returns the result dictionary.
# Last edited: 02/06/2025 

def getStats(cnx, student_id):
    cursor = cnx.cursor()

    # get total number of questions for each tag type
    query = ("""select * from vw_question_tags_count""")

    cursor.execute(query)

    columns = cursor.description 
    result = cursor.fetchall()

    question_tags_count = {}

    for i,column in enumerate(columns):
        question_tags_count.update({column[0] : str(result[0][i])})

    # get total attempted question count for each tage type
    query = (f"""select * from vw_attempted_question_tags_count where users_id = {student_id}""")

    cursor.execute(query)

    columns = cursor.description 
    result = cursor.fetchall()

    attempted_question_tags_count = {}

    for i,column in enumerate(columns):
            attempted_question_tags_count.update({column[0] : str(result[0][i])})        


    # get total attempted question correct count for each tage type
    query = (f"""select * from vw_attempted_question_tags_correct_count where users_id = {student_id}""")

    cursor.execute(query)

    columns = cursor.description 
    result = cursor.fetchall()

    attempted_question_tags_correct_count = {}

    for i,column in enumerate(columns):
        attempted_question_tags_correct_count.update({column[0] : str(result[0][i])})

    # calculate percents and put everything into a dict
    result = {}

    for tag in question_tags_count.keys():

        total = int(question_tags_count.get(tag))
        attempted = int(attempted_question_tags_count.get(tag))
        unattempted = total - attempted
        right = int(attempted_question_tags_correct_count.get(tag))
        wrong = attempted - right

        try:
            answered_p = (attempted / total) * 100
        except:
            answered_p = 0

        try:
            correct_p = (right / attempted) * 100
        except:
            correct_p = 0
        
        result.update({tag: {'total' : total, 'answered' : round(answered_p, 2), 'correct' : round(correct_p, 2)}})
    print(result)
    cnx.close()

    return result