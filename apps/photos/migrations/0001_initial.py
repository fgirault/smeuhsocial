# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import photologue.models
from django.conf import settings
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('photologue', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=photologue.models.get_storage_path, verbose_name='image')),
                ('date_taken', models.DateTimeField(verbose_name='date taken', null=True, editable=False, blank=True)),
                ('view_count', models.PositiveIntegerField(default=0, editable=False)),
                ('crop_from', models.CharField(default=b'center', max_length=10, verbose_name='crop from', blank=True, choices=[(b'top', 'Top'), (b'right', 'Right'), (b'bottom', 'Bottom'), (b'left', 'Left'), (b'center', 'Center (Default)')])),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('title_slug', models.SlugField(verbose_name='slug')),
                ('caption', models.TextField(verbose_name='caption', blank=True)),
                ('date_added', models.DateTimeField(default=datetime.datetime.now, verbose_name='date added', editable=False)),
                ('is_public', models.BooleanField(default=True, help_text='Public photographs will be displayed in the default views.', verbose_name='is public')),
                ('safetylevel', models.IntegerField(default=1, verbose_name='safetylevel', choices=[(1, 'Safe'), (2, 'Not Safe')])),
                ('tags', tagging.fields.TagField(max_length=255, blank=True)),
                ('effect', models.ForeignKey(related_name='image_related', verbose_name='effect', blank=True, to='photologue.PhotoEffect', null=True)),
                ('member', models.ForeignKey(related_name='added_photos', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PhotoSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('description', models.TextField(verbose_name='description')),
                ('publish_type', models.IntegerField(default=1, verbose_name='publish_type', choices=[(1, 'Public'), (2, 'Private')])),
                ('tags', tagging.fields.TagField(max_length=255, blank=True)),
            ],
            options={
                'verbose_name': 'photo set',
                'verbose_name_plural': 'photo sets',
            },
        ),
        migrations.CreateModel(
            name='Pool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, verbose_name='created_at')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('photo', models.ForeignKey(to='photos.Image')),
            ],
            options={
                'verbose_name': 'pool',
                'verbose_name_plural': 'pools',
            },
        ),
        migrations.AddField(
            model_name='image',
            name='photoset',
            field=models.ManyToManyField(to='photos.PhotoSet', verbose_name='photo set', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='pool',
            unique_together=set([('photo', 'content_type', 'object_id')]),
        ),
    ]
