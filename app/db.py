# mysql.py
from flask_mysqldb import MySQL

mysql = MySQL()

class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    @staticmethod
    def get_all():
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users")
        data = cursor.fetchall()
        users = [User(*row) for row in data]
        return users

    @staticmethod
    def get_by_id(id):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
        data = cursor.fetchone()
        user = User(*data) if data else None
        return user