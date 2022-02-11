"""
Crea la tabla base en la que se alamacena mediante sqlite3 los usuarios que pueden hacer API calls  
------> Se puede mejorar cambiando la base de datos por una mejor y usando SQLAlchemy pero una paja
"""

import sqlite3

connection = sqlite3.connect('data.db')
cursor = connection.cursor()

create_table = 'CREATE TABLE user (id INTEGER PRIMARY KEY, username text, password text)'
cursor.execute(create_table)

connection.commit()
connection.close()