# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('email', models.EmailField(max_length=254)),
                ('added', models.DateField(default=datetime.date.today)),
                ('user', models.ForeignKey(related_name='contacts', to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateField(default=datetime.date.today)),
                ('from_user', models.ForeignKey(related_name='_unused_', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(related_name='friends', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FriendshipInvitation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('sent', models.DateField(default=datetime.date.today)),
                ('status', models.CharField(max_length=1, choices=[(b'1', b'Created'), (b'2', b'Sent'), (b'3', b'Failed'), (b'4', b'Expired'), (b'5', b'Accepted'), (b'6', b'Declined'), (b'7', b'Joined Independently'), (b'8', b'Deleted')])),
                ('from_user', models.ForeignKey(related_name='invitations_from', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(related_name='invitations_to', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FriendshipInvitationHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('sent', models.DateField(default=datetime.date.today)),
                ('status', models.CharField(max_length=1, choices=[(b'1', b'Created'), (b'2', b'Sent'), (b'3', b'Failed'), (b'4', b'Expired'), (b'5', b'Accepted'), (b'6', b'Declined'), (b'7', b'Joined Independently'), (b'8', b'Deleted')])),
                ('from_user', models.ForeignKey(related_name='invitations_from_history', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(related_name='invitations_to_history', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='JoinInvitation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('sent', models.DateField(default=datetime.date.today)),
                ('status', models.CharField(max_length=1, choices=[(b'1', b'Created'), (b'2', b'Sent'), (b'3', b'Failed'), (b'4', b'Expired'), (b'5', b'Accepted'), (b'6', b'Declined'), (b'7', b'Joined Independently'), (b'8', b'Deleted')])),
                ('confirmation_key', models.CharField(max_length=40)),
                ('contact', models.ForeignKey(to='friends.Contact')),
                ('from_user', models.ForeignKey(related_name='join_from', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='friendship',
            unique_together=set([('to_user', 'from_user')]),
        ),
    ]
