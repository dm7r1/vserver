# Generated by Django 2.0.2 on 2018-03-14 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('intro', '0010_auto_20180308_2239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vuser',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AlterField(
            model_name='vuser',
            name='password',
            field=models.CharField(max_length=64),
        ),
    ]