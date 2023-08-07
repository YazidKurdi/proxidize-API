import pytest
from django.urls import reverse
from rest_framework import status

from sms.models import SMS


@pytest.mark.django_db
def test_sms_list_view_authenticated(api_client, logged_in_user_token):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    url = reverse('sms-list-index')

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_sms_list_view_unauthenticated(api_client):
    url = reverse('sms-list-index')

    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_sms_list_view_invalid_index(api_client, logged_in_user_token):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    url = reverse('sms-list-index')
    response = api_client.get(url, {'index': 'invalid'})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['message'] == 'Invalid index value. Please provide a valid integer.'


@pytest.mark.django_db
def test_sms_list_view_nonexistent_modem(api_client, logged_in_user_token):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    url = reverse('sms-list-index')
    response = api_client.get(url, {'index': '999'})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['message'] == 'Modem with the provided index does not exist.'


@pytest.mark.django_db
def test_sms_list_view_correct_index(api_client, logged_in_user_token, modem):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    # Create a sample SMS and Modem objects
    sms_data = {
        'modem': modem,
        'date': '2023-08-06T12:00:00Z',
        'phone_number': '123456789',
        'content': 'Test message content',
        'timestamp': 1234567890.0,
    }
    sms = SMS.objects.create(**sms_data)

    url = reverse('sms-list-index')
    response = api_client.get(url, {'index': modem.id})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['phone_number'] == sms_data['phone_number']


@pytest.mark.django_db
def test_sms_list_view_no_index(api_client, logged_in_user_token, modem):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)
    # Create a sample SMS and Modem objects
    sms_data = {
        'modem': modem,
        'date': '2023-08-06T12:00:00Z',
        'phone_number': '123456789',
        'content': 'Test message content',
        'timestamp': 1234567890.0,
    }

    num_sms_instances = 2

    for _ in range(num_sms_instances):
        sms = SMS.objects.create(**sms_data)

    url = reverse('sms-list-index')
    response = api_client.get(url, {'index': modem.id})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == num_sms_instances


@pytest.mark.django_db
def test_sms_by_phone_view_phone_number_not_found(api_client, logged_in_user_token):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    url = reverse('sms-list-number')
    response = api_client.get(url, {'phone_number': 'invalid'})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['message'] == 'Phone number not found'


@pytest.mark.django_db
def test_sms_by_phone_view_single_result(api_client, logged_in_user_token, modem):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    sms_data = {
        'modem': modem,
        'date': '2023-08-06T12:00:00Z',
        'content': 'Test message content',
        'timestamp': 1234567890.0,
    }
    sms_instance = SMS.objects.create(**sms_data)

    url = reverse('sms-list-number')
    response = api_client.get(url, {'phone_number': modem.phone_number})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['sms_messages'][0]['content'] == sms_data['content']
    assert response.data[0]['message'] == 'SMS messages fetched successfully.'


@pytest.mark.django_db
def test_sms_by_phone_view_single_result(api_client, logged_in_user_token, modem):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    sms_data = {
        'modem': modem,
        'date': '2023-08-06T12:00:00Z',
        'content': 'Test message content',
        'timestamp': 1234567890.0,
    }

    num_sms_instances = 2

    for _ in range(num_sms_instances):
        sms = SMS.objects.create(**sms_data)

    url = reverse('sms-list-number')
    response = api_client.get(url, {'phone_number': modem.phone_number})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data[0]['sms_messages']) == num_sms_instances
