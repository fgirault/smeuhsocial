# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Following',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('follower_object_id', models.PositiveIntegerField()),
                ('followed_object_id', models.PositiveIntegerField()),
                ('followed_content_type', models.ForeignKey(related_name='followers', verbose_name='followed', to='contenttypes.ContentType')),
                ('follower_content_type', models.ForeignKey(related_name='followed', verbose_name='follower', to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=140, verbose_name='text')),
                ('sender_id', models.PositiveIntegerField()),
                ('sent', models.DateTimeField(default=datetime.datetime.now, verbose_name='sent')),
                ('sender_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('-sent',),
            },
        ),
        migrations.CreateModel(
            name='TweetInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=140, verbose_name='text')),
                ('sender_id', models.PositiveIntegerField()),
                ('sent', models.DateTimeField(verbose_name='sent')),
                ('recipient_id', models.PositiveIntegerField()),
                ('recipient_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('sender_type', models.ForeignKey(related_name='tweet_instances', to='contenttypes.ContentType')),
            ],
        ),
    ]
