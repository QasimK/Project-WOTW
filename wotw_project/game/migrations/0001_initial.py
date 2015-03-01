# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActiveMonster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('hp', models.IntegerField()),
                ('gold', models.IntegerField(default=0)),
                ('looted_weapon', models.BooleanField(default=False)),
                ('looted_armour', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('max_hp', models.IntegerField(default=50)),
                ('hp', models.IntegerField(default=50)),
                ('inventory_mode', models.CharField(max_length=1, default='A', choices=[('A', 'Edit/View'), ('B', 'View-only'), ('C', 'No access')])),
                ('gold', models.IntegerField(default=300)),
                ('game_view', models.CharField(max_length=100, default='village-in')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GameViewProperty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=100)),
                ('char', models.ForeignKey(to='game.Character')),
            ],
            options={
                'verbose_name': 'game view property',
                'verbose_name_plural': 'game view properties',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('is_unlimited', models.BooleanField(default=True)),
                ('size', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'inventory',
                'verbose_name_plural': 'inventories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InventoryItemInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('stack_size', models.PositiveIntegerField()),
                ('inventory', models.ForeignKey(to='game.Inventory')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('is_unlimited_stack', models.BooleanField(default=False)),
                ('max_stack_size', models.PositiveIntegerField(default=1)),
                ('is_soulbound', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ItemAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('func', models.CharField(unique=True, max_length=100, choices=[('damage target; one use', 'damage target; one use'), ('self heal; one use', 'self heal; one use')])),
                ('target', models.CharField(max_length=1, choices=[('c', 'Character'), ('f', 'Fight'), ('i', 'Inventory Item')])),
                ('allow_in_combat', models.BooleanField(default=False)),
                ('allow_out_combat', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ItemItemActionInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('display_text', models.CharField(max_length=100)),
                ('item', models.ForeignKey(to='game.Item')),
                ('item_action', models.ForeignKey(to='game.ItemAction')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ItemProperty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=3, choices=[('cst', 'Cost'), ('dmg', 'Damage Dealt'), ('hh', 'Health Healed'), ('da', 'Damage Absorbed')])),
                ('value', models.CharField(max_length=100)),
                ('item', models.ForeignKey(to='game.Item')),
            ],
            options={
                'verbose_name': 'item property',
                'verbose_name_plural': 'item properties',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('can_goto_views', models.ManyToManyField(null=True, to='game.Location', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('body', models.TextField()),
                ('character', models.ForeignKey(to='game.Character')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Monster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('hp', models.IntegerField()),
                ('hp_dev', models.IntegerField(default=0)),
                ('gold', models.IntegerField(default=0)),
                ('gold_dev', models.IntegerField(default=0)),
                ('armour', models.ForeignKey(related_name='monster_armours', to='game.Item')),
                ('weapon', models.ForeignKey(related_name='monster_weapons', to='game.Item')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RecipeIngredientInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('quantity', models.IntegerField(default=1)),
                ('ingredient', models.ForeignKey(to='game.Item')),
                ('recipe', models.ForeignKey(to='game.Recipe')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RecipeProductInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('quantity', models.IntegerField(default=1)),
                ('product', models.ForeignKey(to='game.Item')),
                ('recipe', models.ForeignKey(to='game.Recipe')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('inventory', models.ForeignKey(to='game.Inventory')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipe_ingredients_set', to='game.Item', through='game.RecipeIngredientInfo'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recipe',
            name='products',
            field=models.ManyToManyField(related_name='recipe_products_set', to='game.Item', through='game.RecipeProductInfo'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='itemproperty',
            unique_together=set([('item', 'name', 'value')]),
        ),
        migrations.AddField(
            model_name='item',
            name='item_actions',
            field=models.ManyToManyField(through='game.ItemItemActionInfo', to='game.ItemAction'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inventoryiteminfo',
            name='item',
            field=models.ForeignKey(to='game.Item'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inventory',
            name='items',
            field=models.ManyToManyField(through='game.InventoryItemInfo', to='game.Item'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='gameviewproperty',
            unique_together=set([('char', 'name')]),
        ),
        migrations.AddField(
            model_name='character',
            name='armour',
            field=models.ForeignKey(related_name='character_armour', to='game.Item'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='character',
            name='fight',
            field=models.OneToOneField(to='game.ActiveMonster', blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='character',
            name='inventory',
            field=models.OneToOneField(to='game.Inventory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='character',
            name='known_recipes',
            field=models.ManyToManyField(to='game.Recipe'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='character',
            name='user_account',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='character',
            name='weapon',
            field=models.ForeignKey(related_name='character_weapon', to='game.Item'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activemonster',
            name='monster_info',
            field=models.ForeignKey(to='game.Monster'),
            preserve_default=True,
        ),
    ]
