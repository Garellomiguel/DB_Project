import os
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required
import mysql.connector
from mysql.connector import Error
import json

from security import authenticate, identity
from user import UserRegister

app = Flask(__name__)
app.secret_key = 'secret'
api = Api(app)

jwt = JWT(app, authenticate, identity) # /auth

def create_user_if_not_exist():    
    """
    Crea el usuario con los permisos correspondientes que se va a usar en los metodos de la api para ingresar valores a la base. 
    """
    try:
        connection = create_connector_to_database(root=True)
        cursor = connection.cursor()
        cursor.execute("CREATE USER 'iot'@'%' IDENTIFIED BY 'supersecurepassword';")
        cursor.execute("GRANT ALL PRIVILEGES ON sensores TO 'iot'@'%';")  # Revisar esto de los privilegios que le doy
        cursor.close()
        connection.close()
        return
    except: return "User already exists"

def create_connector_to_database(root=False):
    """
    Para no repetir creo la coneccion aca y la tomo despues en los metodos
    """
    if root:
        ## Se va correr con kubernetes, ver como poner estos archivos como secreto
        with open("user_credentials.json") as json_file:
            config = json.load(json_file)
            config["host"] = os.environ["DB_HOST"]
    else:
        with open("root_credentials.json") as json_file:
            config = json.load(json_file)
            config["host"] = os.environ["DB_HOST"]
    try:
        connection = mysql.connector.connection.MySQLConnection(**config)
        return connection
    except Error as err: return f"Error connecting to database: {err}"

class CreateDB(Resource):

    def post(self, db_name):
        """
        API metodo para crear un dataset en mysql con el usuario por default
        ej: empy body
        """
        try:
            connection = create_connector_to_database(root=False)
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE {db_name} DEFAULT CHARACTER SET 'utf8'")
            res = "CREATE DATABASE COMPLETED SUCCESSFULLY"
        except Error as err:
            return {"result": f"{err}"}, 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()   
        return {"result": f"{res}"}

class Createtable(Resource):

    """
    API metodo para crear una tabla en un dataset
    """

    #parser = reqparse.RequestParser()
    #parser.add_argument("schema", required=True, help='Schema is required')

    def post(self, db_name, table_name):
        """
        ej: data = {"schema": [{"name": "number", "type": "int"}, {"name": "value", "type": "varchar(25)"}]}
        """
        try:
            connection = create_connector_to_database(root=False)
            cursor = connection.cursor()
            #data = Createtable.parser.parse_args()
            data = request.get_json()
            print(data,flush=True)
            print(data['schema'],flush=True)
            schema = [f"{x['name']} {x['type']}" for x in data['schema']]
            schema = ', '.join(schema)
            cursor.execute(f"USE {db_name};")
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")
            res = 'CREATE TABLE COMPLETED SUCCESSFULLY'
        except Error as err:
            return {"result": f"{err}"}, 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
        return {"result": f"{res}"}, 200 if res else 404

class Insert(Resource):

    """
    API meteodo para ingresar valores a la base de mysql  ------> Ver de mejorar en algun momento con SQLalchemy
    """

    #with open("user_credentials.json") as json_file:
    #    config = json.load(json_file)

    parser = reqparse.RequestParser()
    parser.add_argument('insert', type=dict, required=True, help='cannot be blank')

    @jwt_required()
    def post(self, db_name, table_name):
        """
        ej: data = {'insert':{'number': 1, 'value': 'hola'}}
        """
        try:
            connection = create_connector_to_database(root=False)
            #connection = mysql.connector.connection.MySQLConnection(host='mysqlDB', port=3306, database=db_name, user='iot', password='supersecurepassword')
            cursor = connection.cursor()
            data = Insert.parser.parse_args()
            fields = [x for x in data['insert'].keys()]
            values = [str(x) if type(x) is int else f"'{x}'" for x in data['insert'].values()]
            cursor.execute(f"INSERT INTO {db_name}.{table_name} ({', '.join(fields)}) VALUES ({', '.join(values)})")
            connection.commit()
            res = 'INSERT COMPLETED SUCCESSFULLY'
        except Error as err:
            return {"result": f"{err}"}, 500
        finally:
            #print(f"INSERT INTO {db_name}.{table_name} ({', '.join(fields)}) VALUES ({', '.join(values)})",flush=True)
            if connection.is_connected():
                cursor.close()
                connection.close()
        return {"result": f"{res}"}


## Agrega los metodos a la API
api.add_resource(CreateDB, '/<string:db_name>/create')
api.add_resource(Createtable, '/<string:db_name>/<string:table_name>/create')
api.add_resource(Insert, '/<string:db_name>/<string:table_name>/insert')
api.add_resource(UserRegister, '/register')

if __name__ == '__main__':
    create_user_if_not_exist()
    app.run(host='0.0.0.0',port=5000, debug = True)