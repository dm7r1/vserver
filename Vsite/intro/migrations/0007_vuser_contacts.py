# Generated by Django 2.0.2 on 2018-02-23 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('intro', '0006_auto_20180221_1634'),
    ]

    operations = [
        migrations.AddField(
            model_name='vuser',
            name='contacts',
            field=models.ManyToManyField(to='intro.VUser'),
        ),
    ]
