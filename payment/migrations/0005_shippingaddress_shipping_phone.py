# Generated by Django 4.2.11 on 2024-05-26 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_order_invoice_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingaddress',
            name='shipping_phone',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
