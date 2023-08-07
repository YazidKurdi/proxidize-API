import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from modems.models import Modem

User = get_user_model()

@pytest.fixture
def api_client():
    client = APIClient()
    return client

@pytest.fixture
def modem():
    # Create a sample Modem object
    modem_data = {
        'model': 'USB',
        'carrier': 'AT&T',
        'public_ip': '192.168.1.1',
        'ipv4': '192.168.1.2',
        'ipv6': '2001:0db8:85a3:0000:0000:8a2e:0370:7334',
        'phone_number': '123456789',
    }
    modem = Modem.objects.create(**modem_data)
    return modem



@pytest.fixture
def logged_in_user_token():
    # Create a user account
    user_data = {
        'username': 'testuser',
        'password': 'testpassword',
    }
    user = User.objects.create_user(**user_data)

    token, created = Token.objects.get_or_create(user=user)

    return token.key