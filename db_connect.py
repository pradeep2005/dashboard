import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",         # your MySQL username
        password="root",  # your MySQL password
        database="users"    # your database name
    )
