import os
import django
from datetime import datetime

from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from modems.models import Modem
from sms.models import SMS


def reset_database():
    """
    Function to reset the database.

    This function deletes the entire database and then applies migrations to recreate the tables.

    Parameters:
        None

    Returns:
        None
    """
    # Delete the database and recreate it
    call_command('flush', '--noinput')
    # Apply migrations to recreate the tables
    call_command('migrate')


def populate_data():
    """
    Function to populate data into the Modem and SMS models.

    This function creates sample Modem and SMS data and saves them into the database.

    Parameters:
        None

    Returns:
        None
    """
    modem_data = [
        {'model': 'USB', 'carrier': 'AT&T', 'public_ip': '192.168.1.1', 'ipv4': '192.168.1.10',
         'ipv6': 'dc11:cd63:bb56:3e09:2ffc:b498:98b1:336c', 'phone_number': '1234'},
        {'model': 'Android', 'carrier': 'Verizon', 'public_ip': '192.168.1.2', 'ipv4': '192.168.1.11',
         'ipv6': 'dc11:cd63:bb56:3e09:2ffc:b498:98b1:336d', 'phone_number': '5678'},
        {'model': 'iPhone', 'carrier': 'T-Mobile', 'public_ip': '192.168.1.3', 'ipv4': '192.168.1.12',
         'ipv6': 'dc11:cd63:bb56:3e09:2ffc:b498:98b1:336e', 'phone_number': '9101'},
    ]

    for data in modem_data:
        modem = Modem.objects.create(**data)
        for _ in range(3):
            SMS.objects.create(
                modem=modem,
                date=datetime.now(),
                phone_number='XXXXXXXXX',
                content='Example API message',
                timestamp=1675484514.0
            )


if __name__ == "__main__":
    # reset_database()
    populate_data()
