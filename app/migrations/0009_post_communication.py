# Generated by Django 3.1.3 on 2021-08-15 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_following'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='communication',
            field=models.CharField(choices=[('In-Person', 'In-Person'), ('Online', 'Online')], default='Online', max_length=255),
        ),
    ]
