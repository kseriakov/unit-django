# Generated by Django 4.1.1 on 2022-09-25 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_alter_book_owner_userbookrelation_book_reader'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbookrelation',
            name='rate',
            field=models.SmallIntegerField(blank=True, choices=[(1, 'Bad'), (2, 'Not bad'), (3, 'Normal'), (4, 'Good'), (5, 'Excellent')], null=True),
        ),
    ]
