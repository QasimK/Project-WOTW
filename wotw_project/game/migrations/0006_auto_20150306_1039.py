# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_auto_20150306_1010'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itemtable',
            name='items',
        ),
        migrations.RemoveField(
            model_name='itemtableiteminfo',
            name='item',
        ),
        migrations.RemoveField(
            model_name='itemtableiteminfo',
            name='item_table',
        ),
        migrations.DeleteModel(
            name='ItemTableItemInfo',
        ),
        migrations.RemoveField(
            model_name='shop',
            name='item_table',
        ),
        migrations.DeleteModel(
            name='ItemTable',
        ),
        migrations.AlterField(
            model_name='itemaction',
            name='func',
            field=models.CharField(max_length=100, unique=True, choices=[('self heal; one use', 'self heal; one use'), ('damage target; one use', 'damage target; one use')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='shopstockinfo',
            name='initial_stock',
            field=models.PositiveIntegerField(null=True, default=0, blank=True),
            preserve_default=True,
        ),
    ]
