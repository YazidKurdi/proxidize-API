# Generated by Django 4.2.4 on 2023-08-04 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modems', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='modem',
            name='carrier',
            field=models.CharField(choices=[('AT&T', 'AT&T'), ('Verizon', 'Verizon'), ('T-Mobile', 'T-Mobile')], default=1, max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='modem',
            name='ipv4',
            field=models.GenericIPAddressField(protocol='IPv4'),
        ),
        migrations.AlterField(
            model_name='modem',
            name='ipv6',
            field=models.GenericIPAddressField(protocol='IPv6'),
        ),
    ]
