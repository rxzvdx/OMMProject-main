from connection import makeConnection

def get_admin_requests():
    conn = makeConnection()
    cursor = conn.cursor()

    query = "SELECT request_id, first_name, last_name, email FROM admin_requests"
    cursor.execute(query)
    requests = cursor.fetchall()

    cursor.close()
    conn.close()

    return requests

