from random import shuffle
import random
from django.db import models, transaction


class Modem(models.Model):

    model_choices = (
        ('USB', 'USB'),
        ('Android', 'Android'),
        ('iPhone', 'iPhone'),
    )

    carrier_choices = (
        ('AT&T', 'AT&T'),
        ('Verizon', 'Verizon'),
        ('T-Mobile', 'T-Mobile'),
    )

    class Meta:
        ordering = ['id']

    model = models.CharField(max_length=10, choices=model_choices)
    carrier = models.CharField(max_length=10, choices=carrier_choices)
    public_ip = models.GenericIPAddressField()
    ipv4 = models.GenericIPAddressField(protocol='IPv4')
    ipv6 = models.GenericIPAddressField(protocol='IPv6')
    phone_number = models.CharField(max_length=15)


    def generate_public_ip(self):
        return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

    def generate_ipv4(self):
        return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

    def generate_ipv6(self):
        segments = [f'{random.randint(0, 65535):04x}' for _ in range(8)]

        # Join the segments to form the IPv6 address
        ipv6_address = ":".join(segments)

        return ipv6_address

    # Simulate modem reboot
    def reboot_modem(self):
        self.public_ip = self.generate_public_ip()
        self.ipv4 = self.generate_ipv4()
        self.ipv6 = self.generate_ipv6()
        self.save()

    # Simulate all modems rotating
    @classmethod
    def rotate_all(cls):
        # Retrieve all instances of the Modem model from the database
        modems = list(cls.objects.all())

        # Shuffle the instances
        shuffle(modems)

        # Use a transaction to ensure atomicity
        with transaction.atomic():
            # Update each instance in the original order with the shuffled instances
            for original_modem, shuffled_modem in zip(cls.objects.all(), modems):
                original_modem.public_ip = shuffled_modem.public_ip
                original_modem.ipv4 = shuffled_modem.ipv4
                original_modem.ipv6 = shuffled_modem.ipv6
                original_modem.save()

    def __str__(self):
        return f'{self.model} {self.public_ip}'



class FeatureSettings(models.Model):
    critical_mode_enabled = models.BooleanField(default=False)

    def __str__(self):
        return f'Critical Mode Enabled: {self.critical_mode_enabled}'