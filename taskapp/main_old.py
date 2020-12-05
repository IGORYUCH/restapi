from flask import Flask, request, make_response, jsonify
from psycopg2 import connect
from hashlib import md5

DBNAME = 'restapi'
USER = 'postgres'
PASSWORD = '123q'
PORT = 5432
HOST = 'localhost'
USERSTABLE = 'users'
TASKSTABLE = 'tasks'

app = Flask(__name__)

client = app.test_client()
connection = connect(dbname=DBNAME, user=USER, password=PASSWORD, port=PORT, host=HOST)
cursor = connection.cursor()

#Возвращать 406 и список характеристик, требуемых для корректного запроса


@app.route('/restapi/users/create', methods=['POST'])
def create_user():
    login = request.headers['login']
    password = request.headers['password']
    cursor.execute('select count(login) from {0} where login=\'{1}\';'.format(USERSTABLE, login))
    same_logins_count = cursor.fetchone()
    if not same_logins_count[0]:
        token = md5(login.encode('utf-8') + password.encode('utf-8')).hexdigest()
        cursor.execute('insert into {0} values(default, \'{1}\', \'{2}\', \'{3}\');'.format(USERSTABLE, login, token, password))
        connection.commit()
        return make_response(jsonify({}), 201)
    else:
        return make_response(jsonify({'error': 'this login is being used'}), 409)


@app.route('/restapi/users/login', methods=['GET'])
def login_user():
    login = request.headers['login']
    password = request.headers['password']
    cursor.execute('select token from {0} where login=\'{1}\' and password=\'{2}\';'.format(USERSTABLE, login, password))
    token = cursor.fetchone()
    if token:
        return jsonify({'token': token[0]})
    else:
        return make_response(jsonify({'error': 'invalid username or password'}), 404)


@app.route('/restapi/tasks/create', methods=['POST'])
def create_task():
    token = request.headers['authorization']
    title = request.headers['title']
    text = request.headers['text']
    complete_date = request.headers['complete_date']
    cursor.execute('select user_id from {0} where token=\'{1}\';'.format(USERSTABLE, token))
    user_id = cursor.fetchone()
    if user_id:
        cursor.execute('insert into {0} values(default, \'{1}\', \'{2}\', \'{3}\', false, \'{4}\');'.format(TASKSTABLE, user_id[0], title, text, complete_date))
        connection.commit()
        return jsonify({})
    else:
        return make_response(jsonify({'error': 'not enough rights'}), 403)


@app.route('/restapi/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    token = request.headers['authorization']
    cursor.execute('select user_id from {0} where token=\'{1}\';'.format(USERSTABLE, token))
    user_id = cursor.fetchone()
    if user_id:
        cursor.execute('select title, text, complete_date, completed from {0} where user_id=\'{1}\' and task_id=\'{2}\';'.format(TASKSTABLE, user_id[0], task_id))
        row = cursor.fetchone()
        if row:
            return jsonify({'task':{'title':row[0], 'text':row[1], 'date':row[2], 'completed':row[3]}})
        else:
            return make_response(jsonify({'error': 'no task with id {0}'.format(task_id)}), 404)
    else:
        return make_response(jsonify({'error': 'not enough rights'}), 403)


@app.route('/restapi/tasks', methods=['GET'])
def get_tasks():
    token = request.headers['authorization']
    cursor.execute('select user_id from {0} where token=\'{1}\''.format(USERSTABLE, token))
    user_id = cursor.fetchone()
    if user_id:
        tasks = {'tasks_id':[]}
        cursor.execute('select task_id from {0} where user_id=\'{1}\''.format(TASKSTABLE, user_id[0]))
        rows = cursor.fetchall()
        for row in rows:
            tasks['tasks_id'].append(row[0])
        return jsonify(tasks)
    else:
        return make_response(jsonify({'error': 'not enough rights'}), 403)


@app.route('/restapi/tasks/<task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    token = request.headers['authorization']
    cursor.execute('select user_id from {0} where token=\'{1}\';'.format(USERSTABLE, token))
    user_id = cursor.fetchone()
    if user_id:
        cursor.execute('update {0} set completed=true where user_id=\'{1}\' and task_id=\'{2}\';'.format(TASKSTABLE, user_id[0], task_id))
        connection.commit()
        if cursor.rowcount:
            return jsonify({})
        else:
            return make_response(jsonify({'error': 'no task with id {0} and user {1}'.format(task_id, user_id[0])}), 404)
    else:
        return make_response(jsonify({'error': 'not enough rights'}), 403)


@app.route('/restapi/tasks/<task_id>/delete', methods=['DELETE'])
def delete_task(task_id):
    token = request.headers['authorization']
    cursor.execute('select user_id from {0} where token=\'{1}\';'.format(USERSTABLE, token))
    user_id = cursor.fetchone()
    if user_id:
        cursor.execute('delete from {0} where user_id = \'{1}\' and task_id=\'{2}\';'.format(TASKSTABLE, user_id[0], task_id))
        connection.commit()
        if cursor.rowcount:
            return jsonify({})
        else:
            return make_response(jsonify({'error': 'no task with id {0} and user {1}'.format(task_id,user_id[0])}), 404)
    else:
        return make_response(jsonify({'error': 'not enough rights'}), 403)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=80)
