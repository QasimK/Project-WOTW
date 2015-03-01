# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Item.is_soulbound'
        db.add_column(u'game_item', 'is_soulbound',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Item.is_soulbound'
        db.delete_column(u'game_item', 'is_soulbound')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'game.activemonster': {
            'Meta': {'object_name': 'ActiveMonster'},
            'gold': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'hp': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'looted_armour': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'looted_weapon': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'monster_info': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['game.Monster']"})
        },
        u'game.character': {
            'Meta': {'object_name': 'Character'},
            'armour': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'character_armour'", 'to': u"orm['game.Item']"}),
            'fight': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['game.ActiveMonster']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'game_view': ('django.db.models.fields.CharField', [], {'default': "'village-in'", 'max_length': '100'}),
            'gold': ('django.db.models.fields.IntegerField', [], {'default': '300'}),
            'hp': ('django.db.models.fields.IntegerField', [], {'default': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inventory': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['game.Inventory']", 'unique': 'True'}),
            'inventory_mode': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'known_recipes': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['game.Recipe']", 'symmetrical': 'False'}),
            'max_hp': ('django.db.models.fields.IntegerField', [], {'default': '50'}),
            'user_account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'weapon': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'character_weapon'", 'to': u"orm['game.Item']"})
        },
        u'game.gameviewproperty': {
            'Meta': {'unique_together': "(('char', 'name'),)", 'object_name': 'GameViewProperty'},
            'char': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['game.Character']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'game.inventory': {
            'Meta': {'object_name': 'Inventory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_unlimited': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['game.Item']", 'through': u"orm['game.InventoryItemInfo']", 'symmetrical': 'False'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'game.inventoryiteminfo': {
            'Meta': {'object_name': 'InventoryItemInfo'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inventory': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['game.Inventory']"}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['game.Item']"}),
            'stack_size': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'game.item': {
            'Meta': {'object_name': 'Item'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_soulbound': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_unlimited_stack': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_stack_size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'game.itemproperty': {
            'Meta': {'object_name': 'ItemProperty'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['game.Item']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'game.message': {
            'Meta': {'object_name': 'Message'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'character': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['game.Character']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'game.monster': {
            'Meta': {'object_name': 'Monster'},
            'armour': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monster_armours'", 'to': u"orm['game.Item']"}),
            'gold': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'gold_dev': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'hp': ('django.db.models.fields.IntegerField', [], {}),
            'hp_dev': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'weapon': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monster_weapons'", 'to': u"orm['game.Item']"})
        },
        u'game.recipe': {
            'Meta': {'object_name': 'Recipe'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ingredients': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'recipe_ingredients_set'", 'symmetrical': 'False', 'through': u"orm['game.RecipeIngredientInfo']", 'to': u"orm['game.Item']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'recipe_products_set'", 'symmetrical': 'False', 'through': u"orm['game.RecipeProductInfo']", 'to': u"orm['game.Item']"})
        },
        u'game.recipeingredientinfo': {
            'Meta': {'object_name': 'RecipeIngredientInfo'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ingredient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['game.Item']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['game.Recipe']"})
        },
        u'game.recipeproductinfo': {
            'Meta': {'object_name': 'RecipeProductInfo'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['game.Item']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['game.Recipe']"})
        },
        u'game.shop': {
            'Meta': {'object_name': 'Shop'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inventory': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['game.Inventory']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        }
    }

    complete_apps = ['game']