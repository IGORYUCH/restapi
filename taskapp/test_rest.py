import pytest
from main import app
from random import randrange


@pytest.fixture
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client


login = str(randrange(1000000)) + '@mail.com'
password = 'qweqwe123'


def test_create(test_client):
    res = test_client.post('/restapi/users/create', json={'username': login, 'password': password})
    print(res.status_code, res.get_json())
    assert res.status_code == 201


def test_login(test_client):
    res = test_client.post('/restapi/users/login', json={'username': login, 'password': password})
    assert res.status_code == 200
    return res.get_json()


def test_get_tasks(test_client):
    json = test_login(test_client)
    token = ' JWT ' + json['access_token']
    res = test_client.get('/restapi/tasks', headers={'Authorization': token})
    assert 'tasks_id' in res.get_json().keys()
    return res.get_json()


def test_create_task(test_client):
    json = test_login(test_client)
    token = ' JWT ' + json['access_token']
    task_json = {'title': 'Test task', 'description': 'task text', 'complete_date': '2020-12-25'}
    res = test_client.post('/restapi/tasks/create', headers={'Authorization': token}, json=task_json)
    assert res.status_code == 201


def test_get_task(test_client):
    json = test_login(test_client)
    token = ' JWT ' + json['access_token']
    tasks_id_json = test_get_tasks(test_client)
    task = str(tasks_id_json['tasks_id'][0])
    res = test_client.get('/restapi/tasks/{0}'.format(task), headers={'Authorization': token})
    assert res.status_code == 200


def test_complete_task(test_client):
    json = test_login(test_client)
    token = ' JWT ' + json['access_token']
    tasks_id_json = test_get_tasks(test_client)
    task = str(tasks_id_json['tasks_id'][0])
    res = test_client.put('/restapi/tasks/{0}/complete'.format(task), headers={'Authorization': token})
    assert res.status_code == 200


def test_delete_task(test_client):
    json = test_login(test_client)
    token = ' JWT ' + json['access_token']
    tasks_id_json = test_get_tasks(test_client)
    task = str(tasks_id_json['tasks_id'][0])
    res = test_client.delete('/restapi/tasks/{0}/delete'.format(task), headers={'Authorization': token})
    assert res.status_code == 200
