# Generated by Django 2.2.16 on 2023-01-10 09:37

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0013_auto_20230110_1230'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='unique_followins',
        ),
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together={('author', 'user')},
        ),
    ]
