# Generated by Django 2.0.2 on 2018-02-21 16:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('intro', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='User',
            new_name='SimpleUser',
        ),
    ]
