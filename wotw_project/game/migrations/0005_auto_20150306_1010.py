# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_auto_20150305_1147'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopStockInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('initial_stock', models.PositiveIntegerField(null=True, blank=True)),
                ('item', models.ForeignKey(to='game.Item')),
                ('shop', models.ForeignKey(to='game.Shop')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='shopstockinfo',
            unique_together=set([('shop', 'item')]),
        ),
        migrations.AddField(
            model_name='shop',
            name='stock',
            field=models.ManyToManyField(to='game.Item', through='game.ShopStockInfo'),
            preserve_default=True,
        ),
    ]
