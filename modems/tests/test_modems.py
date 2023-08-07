import pytest
from django.urls import reverse
from django_celery_beat.models import PeriodicTask
from rest_framework import status

from modems.models import FeatureSettings, Modem


@pytest.mark.django_db
def test_sms_list_view_authenticated(api_client, logged_in_user_token):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    url = reverse('modem-list')

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_sms_list_view_unauthenticated(api_client):
    url = reverse('modem-list')

    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_sms_list_view_empty_database(api_client, logged_in_user_token):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    url = reverse('modem-list')

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 0


@pytest.mark.django_db
def test_sms_list_view_database_paginated(api_client, logged_in_user_token, modem):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    url = reverse('modem-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3
    assert response.data['count'] == 3
    assert response.data['results'][0]['model'] == 'USB'
    assert response.data['results'][1]['model'] == 'Android'
    assert response.data['results'][2]['model'] == 'iPhone'


@pytest.mark.django_db
def test_critical_mode_enabled(api_client, logged_in_user_token, modem):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    FeatureSettings.objects.create(critical_mode_enabled=True)

    url = reverse('modem-list')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['results'][0]['public_ip'] == '***.***.***.***'
    assert response.data['results'][0]['ipv6'] == '****:****:****:****:****:****:****:****'


@pytest.mark.django_db
def test_update_critical_mode_enabled(api_client, logged_in_user_token):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    FeatureSettings.objects.create(critical_mode_enabled=False)

    url = reverse('critical-mode-update') + '?toggle=enable'
    response = api_client.put(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['critical_mode_enabled'] is True


@pytest.mark.django_db
def test_update_critical_mode_disabled(api_client, logged_in_user_token):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    FeatureSettings.objects.create(critical_mode_enabled=False)

    url = reverse('critical-mode-update') + '?toggle=disable'
    response = api_client.put(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['critical_mode_enabled'] is False


@pytest.mark.django_db
def test_invalid_toggle_value(api_client, logged_in_user_token):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    FeatureSettings.objects.create(critical_mode_enabled=False)

    url = reverse('critical-mode-update') + '?toggle=invalid'
    response = api_client.put(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_reboot_specific_modem_success(api_client, logged_in_user_token, modem):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    first_modem = Modem.objects.first()

    url = reverse('reboot-modem')
    response = api_client.get(url, {'index': first_modem.pk})

    assert response.status_code == 200
    assert Modem.objects.get(pk=first_modem.pk).public_ip != first_modem.public_ip
    assert Modem.objects.get(pk=first_modem.pk).ipv4 != first_modem.ipv4
    assert Modem.objects.get(pk=first_modem.pk).ipv6 != first_modem.ipv6


@pytest.mark.django_db
def test_reboot_invalid_index(api_client, logged_in_user_token, modem):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    url = reverse('reboot-modem')
    response = api_client.get(url, {'index': 999})

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_custom_modem_rotation(api_client, logged_in_user_token, modem):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    url = reverse('custom-rot')
    index = 1
    response = api_client.get(url, {'index': index, 'min': 1})

    task_name = f'Rotating IP for Modem {index}'
    task = PeriodicTask.objects.get(name=task_name)

    assert task is not None
    assert task.interval.every == 1
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_all_modem_rotation(api_client, logged_in_user_token, modem):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    url = reverse('custom-rot')
    response = api_client.get(url, {'index': 'all', 'min': 1})

    tasks = PeriodicTask.objects.all()
    assert len(tasks) == 3
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_modem_rotation_no_index(api_client, logged_in_user_token, modem):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    url = reverse('custom-rot')
    response = api_client.get(url, {'min': 1})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_modem_rotation_0_min(api_client, logged_in_user_token, modem):
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + logged_in_user_token)

    url = reverse('custom-rot')
    response = api_client.get(url, {'index': 1, 'min': 0})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
