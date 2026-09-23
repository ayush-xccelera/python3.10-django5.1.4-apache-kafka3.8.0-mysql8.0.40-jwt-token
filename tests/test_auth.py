import pytest

REGISTER_URL = '/api/v1/auth/register'
LOGIN_URL = '/api/v1/auth/login'
ME_URL = '/api/v1/auth/me'


@pytest.mark.django_db
def test_register_success(api_client):
    resp = api_client.post(REGISTER_URL, {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'StrongPass123!',
    })
    assert resp.status_code == 201


@pytest.mark.django_db
def test_login_success(api_client, user):
    resp = api_client.post(LOGIN_URL, {
        'username': 'tester',
        'password': 'TesterPass123!',
    })
    assert resp.status_code == 200
    assert 'access' in resp.data


@pytest.mark.django_db
def test_login_invalid_credentials(api_client, user):
    resp = api_client.post(LOGIN_URL, {
        'username': 'tester',
        'password': 'WrongPassword',
    })
    assert resp.status_code == 401


@pytest.mark.django_db
def test_me_authenticated(auth_client):
    resp = auth_client.get(ME_URL)
    assert resp.status_code == 200
    assert resp.data['username'] == 'tester'


@pytest.mark.django_db
def test_me_unauthenticated(api_client):
    resp = api_client.get(ME_URL)
    assert resp.status_code == 401


@pytest.mark.django_db
def test_invalid_token_rejected(api_client):
    api_client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken123')
    resp = api_client.get(ME_URL)
    assert resp.status_code == 401
