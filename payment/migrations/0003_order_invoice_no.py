# Generated by Django 4.2.11 on 2024-05-25 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_order_date_shipped'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='invoice_no',
            field=models.CharField(default=None, max_length=250, null=True),
        ),
    ]
