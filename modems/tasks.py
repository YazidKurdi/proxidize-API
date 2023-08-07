from celery import shared_task
from .models import Modem


@shared_task
def rotate_ip(modem_id):
    modem = Modem.objects.get(pk=modem_id)
    modem.reboot_modem()
