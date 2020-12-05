from flask import Flask, request, make_response, jsonify
from psycopg2 import connect
from flask_jwt import JWT, jwt_required, current_identity
from datetime import timedelta
from werkzeug.security import check_password_hash, generate_password_hash
DBNAME = 'restapi3'
USER = 'postgres'
PASSWORD = '123q'
PORT = 5432
HOST = 'localhost'
USERSTABLE = 'users'
TASKSTABLE = 'tasks'

app = Flask(__name__)
client = app.test_client()

app.config['SECRET_KEY'] = 'I like anime'
app.config['JWT_AUTH_URL_RULE'] = '/restapi/users/login'
app.config['JWT_EXPIRATION_DELTA'] = timedelta(hours=1)

connection = connect(dbname=DBNAME, user=USER, password=PASSWORD, port=PORT, host=HOST)
cursor = connection.cursor()


class User(object):

    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def get_user_by_login_and_pasword(username, password):
    cursor.execute('select user_id, username, password from users where username=\'{0}\';'.format(username))
    if cursor.rowcount:
        result = cursor.fetchone()
        user = User(result[0], result[1], result[2])
        if check_password_hash(user.password, password):
            return user


def get_user_by_id(user_id):
    cursor.execute('select user_id, username, password from users where user_id=\'{0}\';'.format(user_id))
    if cursor.rowcount:
        result = cursor.fetchone()
        user = User(result[0], result[1], result[2])
        return user


def authenticate(username, password):
    user = get_user_by_login_and_pasword(username, password)
    return user


def identity(payload):
    user_id = payload['identity']
    user = get_user_by_id(user_id)
    return user


jwt = JWT(app, authenticate, identity)


@app.route('/restapi/users/create', methods=['POST'])
def create_user():
    username = request.json['username']
    password = request.json['password']
    cursor.execute('select count(username) from {0} where username=\'{1}\';'.format(USERSTABLE, username))
    if not cursor.fetchone()[0]:
        md5_hash = generate_password_hash(password, 'md5')
        cursor.execute('insert into {0} values(default, \'{1}\', \'{2}\');'.format(USERSTABLE, username, md5_hash))
        connection.commit()
        return make_response(jsonify({}), 201)
    else:
        return make_response(jsonify({'error': 'this login is being used'}), 409)


@app.route('/restapi/tasks/create', methods=['POST'])
@jwt_required()
def create_task():
    title = request.json['title']
    description = request.json['description']
    complete_date = request.json['complete_date']
    cursor.execute('insert into {0} values(default, \'{1}\', \'{2}\', \'{3}\', false, \'{4}\');'.format(TASKSTABLE, current_identity.id, title, description, complete_date))
    connection.commit()
    return make_response(jsonify({}), 201)


@app.route('/restapi/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    tasks = {'tasks_id':[]}
    cursor.execute('select task_id from {0} where user_id=\'{1}\''.format(TASKSTABLE, current_identity.id))
    rows = cursor.fetchall()
    for row in rows:
        tasks['tasks_id'].append(row[0])
    return jsonify(tasks)


@app.route('/restapi/tasks/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    cursor.execute('select title, description, complete_date, completed from {0} where user_id=\'{1}\' and task_id=\'{2}\';'.format(TASKSTABLE, current_identity.id, task_id))
    row = cursor.fetchone()
    if row:
        return jsonify({'task':{'title':row[0], 'description':row[1], 'date':row[2], 'completed':row[3]}})
    else:
        return make_response(jsonify({'error': 'no task with id {0}'.format(task_id)}), 404)


@app.route('/restapi/tasks/<task_id>/complete', methods=['PUT'])
@jwt_required()
def complete_task(task_id):
    cursor.execute('update {0} set completed=true where user_id=\'{1}\' and task_id=\'{2}\';'.format(TASKSTABLE, current_identity.id, task_id))
    connection.commit()
    if cursor.rowcount:
        return jsonify({})
    else:
        return make_response(jsonify({'error': 'no task with id {0} and user {1}'.format(task_id, current_identity.id)}), 404)


@app.route('/restapi/tasks/<task_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    cursor.execute('delete from {0} where user_id = \'{1}\' and task_id=\'{2}\';'.format(TASKSTABLE, current_identity.id, task_id))
    connection.commit()
    if cursor.rowcount:
        return jsonify({})
    else:
        return make_response(jsonify({'error': 'no task with id {0} and user {1}'.format(task_id, current_identity.id)}), 404)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=80)
