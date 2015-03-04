# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(max_length=100, unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='shop',
            name='inventory',
            field=models.ForeignKey(to='game.Inventory', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='itemitemactioninfo',
            unique_together=set([('item', 'item_action')]),
        ),
        migrations.AlterUniqueTogether(
            name='itemproperty',
            unique_together=set([('item', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='recipeingredientinfo',
            unique_together=set([('recipe', 'ingredient')]),
        ),
        migrations.AlterUniqueTogether(
            name='recipeproductinfo',
            unique_together=set([('recipe', 'product')]),
        ),
    ]
