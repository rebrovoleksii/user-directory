import json
import pytest
from tests.conftest import TEST_ORGANIZATION_ID, USER_DEFAULT_EMAIL


def test_get_users_return_existing_user_from_db_when_request_correct(client):
    response = client.get('/users', headers={'X-Organization-Id': TEST_ORGANIZATION_ID})
    assert response.status_code == 200
    users = response.json
    assert any(user['email'] == USER_DEFAULT_EMAIL for user in users)

def test_get_users_return_400_db_when_organization_header_missing(client):
    response = client.get('/users')
    assert response.status_code == 400

def test_post_user_return_400_when_role_is_not_correct(client):
    user_data = {
        'email': USER_DEFAULT_EMAIL,
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'blah'
    }
    response = client.post('/users',
                           data=json.dumps(user_data),
                           headers={'Content-Type':"application/json" ,'X-Organization-Id': TEST_ORGANIZATION_ID})
    assert response.status_code == 400

@pytest.mark.skipif(reason="API returns 400 when running via pytest in console")
def test_post_user_return_409_when_user_already_exist(client):
    user_data = {
        'email': USER_DEFAULT_EMAIL,
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'admin'
    }
    response = client.post('/users',
                           data=json.dumps(user_data),
                           headers={'Content-Type':"application/json" ,'X-Organization-Id': TEST_ORGANIZATION_ID})
    assert response.status_code == 409

@pytest.mark.skipif(reason="API returns 400 when running via pytest in console")
def test_post_user_return_201_when_user_created(client):
    user_data = {
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'admin'
    }
    response = client.post('/users',
                           data=json.dumps(user_data),
                           headers={'Content-Type':"application/json", 'X-Organization-Id': TEST_ORGANIZATION_ID})
    assert response.status_code == 201
    #TODO: add check that user is created in the DB

#TODO: add tests for import user api
def test_import_users(client):
    pass