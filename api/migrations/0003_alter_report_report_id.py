# Generated by Django 4.2.3 on 2023-09-21 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20230923_1639'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='report_id',
            field=models.CharField(editable=False, max_length=255, primary_key=True, serialize=False),
        ),
    ]
