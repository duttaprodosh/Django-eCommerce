# Generated by Django 4.2.11 on 2024-06-06 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0007_shippingaddress2_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='phone',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
