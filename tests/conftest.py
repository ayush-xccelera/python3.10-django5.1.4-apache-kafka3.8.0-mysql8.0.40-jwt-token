import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username='tester', email='tester@example.com', password='TesterPass123!')


@pytest.fixture
def auth_token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


@pytest.fixture
def auth_client(api_client, auth_token):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_token}')
    return api_client
