# Generated by Django 2.0.2 on 2018-02-21 16:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('intro', '0005_auto_20180221_1632'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vuser',
            old_name='id',
            new_name='_id',
        ),
    ]
