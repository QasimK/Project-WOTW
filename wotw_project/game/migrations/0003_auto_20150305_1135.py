# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_auto_20150304_1633'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemTable',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(unique=True, max_length=80)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ItemTableItemInfo',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('item', models.ForeignKey(to='game.Item')),
                ('item_table', models.ForeignKey(to='game.ItemTable')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='itemtable',
            name='items',
            field=models.ManyToManyField(to='game.Item', through='game.ItemTableItemInfo'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='shop',
            name='item_table',
            field=models.ForeignKey(blank=True, to='game.ItemTable', default=None, null=True),
            preserve_default=True,
        ),
    ]
