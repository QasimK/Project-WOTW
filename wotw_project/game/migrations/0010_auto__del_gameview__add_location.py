# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'GameView'
        db.delete_table(u'game_gameview')

        # Removing M2M table for field can_goto_views on 'GameView'
        db.delete_table(db.shorten_name(u'game_gameview_can_goto_views'))

        # Adding model 'Location'
        db.create_table(u'game_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'game', ['Location'])

        # Adding M2M table for field can_goto_views on 'Location'
        m2m_table_name = db.shorten_name(u'game_location_can_goto_views')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_location', models.ForeignKey(orm[u'game.location'], null=False)),
            ('to_location', models.ForeignKey(orm[u'game.location'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_location_id', 'to_location_id'])


    def backwards(self, orm):
        # Adding model 'GameView'
        db.create_table(u'game_gameview', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'game', ['GameView'])

        # Adding M2M table for field can_goto_views on 'GameView'
        m2m_table_name = db.shorten_name(u'game_gameview_can_goto_views')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_gameview', models.ForeignKey(orm[u'game.gameview'], null=False)),
            ('to_gameview', models.ForeignKey(orm[u'game.gameview'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_gameview_id', 'to_gameview_id'])

        # Deleting model 'Location'
        db.delete_table(u'game_location')

        # Removing M2M table for field can_goto_views on 'Location'
        db.delete_table(db.shorten_name(u'game_location_can_goto_views'))


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
            'item_actions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['game.ItemAction']", 'through': u"orm['game.ItemItemActionInfo']", 'symmetrical': 'False'}),
            'max_stack_size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'game.itemaction': {
            'Meta': {'object_name': 'ItemAction'},
            'allow_in_combat': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_out_combat': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'func': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'target': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'game.itemitemactioninfo': {
            'Meta': {'object_name': 'ItemItemActionInfo'},
            'display_text': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['game.Item']"}),
            'item_action': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['game.ItemAction']"})
        },
        u'game.itemproperty': {
            'Meta': {'unique_together': "(('item', 'name', 'value'),)", 'object_name': 'ItemProperty'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['game.Item']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'game.location': {
            'Meta': {'object_name': 'Location'},
            'can_goto_views': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['game.Location']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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