# Generated by Django 3.1.3 on 2021-08-14 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='recentevent',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='recentphoto',
            field=models.ImageField(null=True, upload_to='photos/'),
        ),
    ]
