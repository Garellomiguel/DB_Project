"""
Dos clases: la primera (User) se utiliza junto con el script de security para autentificar. 
La segunda es para agregar nuevos usuarios que tengan permisos para hacer calls
"""

import sqlite3
from flask_restful import Resource, reqparse


class User:
    def __init__(self, _id, username, password):
        self.id = _id
        self.username = username
        self.password = password

    @classmethod
    def find_by_username(cls, username):
        connection = sqlite3.connect('data/data.db')
        cursor = connection.cursor()

        query = 'SELECT * FROM user WHERE username=?'
        result = cursor.execute(query, (username,))

        row = result.fetchone()
        if row:
            user = cls(*row) # *row = row[0], row[1], row[2]
        else: user = None
        
        connection.close()
        return user

    @classmethod
    def find_by_id(cls, id):
        connection = sqlite3.connect('data/data.db')
        cursor = connection.cursor()

        query = 'SELECT * FROM user WHERE id=?'
        result = cursor.execute(query, (id,))

        row = result.fetchone()
        if row:
            user = cls(*row) # *row = row[0], row[1], row[2]
        else: user = None
        
        connection.close()
        return user

class UserRegister(Resource):
    
    parser = reqparse.RequestParser()
    parser.add_argument('username', required=True, help='This field cannot be blank')
    parser.add_argument('password', required=True, help='This field cannot be blank')

    def post(self):
        
        data = UserRegister.parser.parse_args()

        if User.find_by_username(data['username']):
            return {"message": "User already exists"}, 400

        connection = sqlite3.connect('data/data.db')
        cursor = connection.cursor()

        query = 'INSERT INTO user VALUES (NULL, ?, ?)'
        cursor.execute(query, (data['username'], data['password'],))

        connection.commit()
        connection.close()

        return {"messege": "User created successfully"}, 201