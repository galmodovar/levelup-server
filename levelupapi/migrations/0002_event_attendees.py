# Generated by Django 3.2.9 on 2021-11-03 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('levelupapi', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='attendees',
            field=models.ManyToManyField(related_name='attending', through='levelupapi.EventGamer', to='levelupapi.Gamer'),
        ),
    ]
