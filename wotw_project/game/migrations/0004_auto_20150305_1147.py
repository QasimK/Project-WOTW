# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_auto_20150305_1135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='item_table',
            field=models.ForeignKey(default=0, to='game.ItemTable'),
            preserve_default=False,
        ),
    ]
