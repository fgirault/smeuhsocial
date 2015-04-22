# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import tagging.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('slug', models.SlugField(verbose_name='slug')),
                ('creator_ip', models.GenericIPAddressField(null=True, verbose_name='IP Address of the Post Creator', blank=True)),
                ('body', models.TextField(verbose_name='body')),
                ('tease', models.TextField(verbose_name='tease', blank=True)),
                ('status', models.IntegerField(default=2, verbose_name='status', choices=[(1, 'Draft'), (2, 'Public')])),
                ('allow_comments', models.BooleanField(default=True, verbose_name='allow comments')),
                ('publish', models.DateTimeField(default=datetime.datetime.now, verbose_name='publish')),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, verbose_name='created at')),
                ('updated_at', models.DateTimeField(verbose_name='updated at')),
                ('markup', models.CharField(blank=True, max_length=20, null=True, verbose_name='Post Content Markup', choices=[(b'markdown', 'Markdown'), (b'restructuredtext', 'reStructuredText')])),
                ('tags', tagging.fields.TagField(max_length=255, blank=True)),
                ('author', models.ForeignKey(related_name='added_posts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-publish'],
                'get_latest_by': 'publish',
                'verbose_name': 'post',
                'verbose_name_plural': 'posts',
            },
        ),
    ]
