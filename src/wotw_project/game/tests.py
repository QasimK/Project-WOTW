'''
Created on 11 Sep 2011

@author: Qasim

MUST USE manage.py test
'''

from django.test import TestCase, TransactionTestCase
from wotw_project.game.models import (
    Item, Inventory, InventoryItemInfo,
    InventoryLacksSpace, InventoryDoesNotHaveItem,
    InventoryDoesNotHaveEnoughItems)

class TestInventory(TestCase):
    def setUp(self):
        self.item_unlimited = Item.objects.create(name="item_unlimited",
            is_unlimited_stack=True)
        self.item_stack3 = Item.objects.create(name="item_stack3",
            is_unlimited_stack=False, max_stack_size=3)
        self.item_stack4 = Item.objects.create(name="item_stack4",
            is_unlimited_stack=False, max_stack_size=4)
        
        self.inv_unlimited = Inventory.objects.create(is_unlimited=True)
        self.inv_size3 = Inventory.objects.create(is_unlimited=False, size=3)
        self.inv_size4 = Inventory.objects.create(is_unlimited=False, size=4)
        
    def test_unlimited_inventory(self):
        self.assertTrue(self.inv_unlimited.is_space_for_item(self.item_unlimited, 1000))
        self.inv_unlimited.add_item(self.item_unlimited, 1000)
        self.assertEqual(self.inv_unlimited.num_item(self.item_unlimited), 1000)
        
        self.assertTrue(self.inv_unlimited.is_space_for_item(self.item_stack3, 2000))
        self.inv_unlimited.add_item(self.item_stack3, 2000)
        self.assertEqual(self.inv_unlimited.num_item(self.item_stack3), 2000)
        
        self.assertTrue(self.inv_unlimited.is_space_for_item(self.item_unlimited, 10))
        self.assertTrue(self.inv_unlimited.is_space_for_item(self.item_stack3, 10))
    
    def test_limited_inventory(self):
        self.assertEqual(self.inv_size3.num_item(self.item_stack3), 0)
        self.assertTrue(self.inv_size3.is_space_for_item(self.item_stack3, 9))
        self.assertFalse(self.inv_size3.is_space_for_item(self.item_stack3, 10))
        
        self.inv_size3.add_item(self.item_stack3, 9)
        self.inv_size3.add_item(self.item_stack3, 0)
        
        self.assertTrue(self.inv_size3.is_space_for_item(self.item_stack3, 0))
        self.assertFalse(self.inv_size3.is_space_for_item(self.item_stack3, 1))
        
        with self.assertRaises(InventoryLacksSpace):
            self.inv_size3.add_item(self.item_stack3, 1)
    
    def test_free_slots(self):
        self.inv_size3.add_item(self.item_stack3, 6)
        self.assertTrue(self.inv_size3.has_free_slot())
        self.assertEqual(self.inv_size3.num_free_slots(), 1)
        self.assertEqual(self.inv_size3.num_item(self.item_stack3), 6)
        
        self.inv_size3.add_item(self.item_stack3, 1)
        self.assertEqual(self.inv_size3.num_free_slots(), 0)
        self.assertFalse(self.inv_size3.has_free_slot())
        
        self.assertTrue(self.inv_unlimited.has_free_slot())
        self.inv_unlimited.add_item(self.item_stack3, 100)
        self.assertTrue(self.inv_unlimited.has_free_slot())
    
    def test_unlimited_item_stacking(self):
        self.inv_size3.add_item(self.item_unlimited, 100)
        self.assertEqual(self.inv_size3.num_free_slots(), 2)
    
    def test_remove_item_unlimited(self):
        self.inv_unlimited.add_item(self.item_unlimited, 50)
        self.inv_unlimited.remove_item(self.item_unlimited, 50)
        self.assertEqual(self.inv_unlimited.num_item(self.item_unlimited), 0)
        
        self.inv_unlimited.remove_item(self.item_unlimited, 10)
        self.assertEqual(self.inv_unlimited.num_item(self.item_unlimited), 0)
        
        self.inv_unlimited.add_item(self.item_unlimited, 50)
        self.assertEqual(self.inv_unlimited.num_item(self.item_unlimited), 50)
        self.inv_unlimited.remove_item(self.item_unlimited, 51)
        self.assertEqual(self.inv_unlimited.num_item(self.item_unlimited), 0)
    
    def test_remove_item_limited(self):
        self.inv_size3.add_item(self.item_stack3, 7)
        self.assertEqual(self.inv_size3.num_free_slots(), 0)
        self.inv_size3.remove_item(self.item_stack3, 1)
        self.assertEqual(self.inv_size3.num_free_slots(), 1)
        
        self.inv_size3.add_item(self.item_stack4, 4)
        self.assertEqual(self.inv_size3.num_free_slots(), 0)
        
        self.inv_size3.remove_item(self.item_stack3, 3)
        self.assertEqual(self.inv_size3.num_free_slots(), 1)
        
        self.inv_size3.remove_item(self.item_stack3, 4)
        self.assertEqual(self.inv_size3.num_item(self.item_stack3), 0)
        self.inv_size3.remove_item(self.item_stack4, 5)
        self.assertEqual(self.inv_size3.num_item(self.item_stack3), 0)
        
        self.assertEqual(self.inv_size3.num_free_slots(), 3)
    
    def test_pickup_from_full(self):
        self.inv_unlimited.add_item(self.item_stack3, 5)
        self.inv_size3.pickup_from(self.inv_unlimited, self.item_stack3, 5)
        
        self.assertEqual(self.inv_unlimited.num_item(self.item_stack3), 0)
        self.assertEqual(self.inv_size3.num_item(self.item_stack3), 5)
    
    def test_pickup_from_partial(self):
        self.inv_size3.add_item(self.item_unlimited, 1000)
        self.inv_size4.pickup_from(self.inv_size3, self.item_unlimited, 400)
        
        self.assertEqual(self.inv_size3.num_item(self.item_unlimited), 600)
        self.assertEqual(self.inv_size4.num_item(self.item_unlimited), 400)
    
    def test_pickup_from_noitems(self):
        with self.assertRaises(InventoryDoesNotHaveItem):
            self.inv_size3.pickup_from(self.inv_unlimited, self.item_unlimited, 5)
        
        self.inv_unlimited.add_item(self.item_unlimited, 1)
        with self.assertRaises(InventoryDoesNotHaveEnoughItems):
            self.inv_size3.pickup_from(self.inv_unlimited, self.item_unlimited, 2)
    
    def test_pickup_from_nospace(self):
        self.inv_unlimited.add_item(self.item_stack3, 100)
        with self.assertRaises(InventoryLacksSpace):
            self.inv_size3.pickup_from(self.inv_unlimited, self.item_stack3, 100)
        
        self.inv_size3.pickup_from(self.inv_unlimited, self.item_stack3, 9)
    
    def test_pickup_overstacked(self):
        InventoryItemInfo.objects.create(inventory=self.inv_unlimited,
            item=self.item_stack3, stack_size=10)
        
        self.inv_size3.pickup_from(self.inv_unlimited, self.item_stack3, 5)
        
        self.assertEqual(self.inv_unlimited.num_item(self.item_stack3), 5)
        self.assertEqual(self.inv_size3.num_item(self.item_stack3), 5)
    
    def test_get_condensed_view(self):
        self.inv_size4.add_item(self.item_unlimited, 6)
        self.inv_size4.add_item(self.item_stack3, 6)
        self.inv_size4.add_item(self.item_stack4, 4)
        
        cv = [(self.item_unlimited, 6), (self.item_stack3, 6), (self.item_stack4, 4)]
        self.assertItemsEqual(self.inv_size4.get_condensed_view(), cv)


#These are slow.
#MUST USE manage.py test OTHERWISE USES REAL DATABASE!
class TestInventoryTransactions(TransactionTestCase):
    def setUp(self):
        self.item_unlimited = Item.objects.create(name="item_unlimited",
            is_unlimited_stack=True)
        self.item_stack3 = Item.objects.create(name="item_stack3",
            is_unlimited_stack=False, max_stack_size=3)
        self.item_stack4 = Item.objects.create(name="item_stack4",
            is_unlimited_stack=False, max_stack_size=4)
        
        self.inv_unlimited = Inventory.objects.create(is_unlimited=True)
        self.inv_size3 = Inventory.objects.create(is_unlimited=False, size=3)
        self.inv_size4 = Inventory.objects.create(is_unlimited=False, size=4)
    
    def test_change_items(self):
        self.inv_size3.add_item(self.item_stack3, 6)
        self.inv_size3.change_items(True, [(self.item_stack4, 6)],
                               [(self.item_stack3, 4)])
        self.assertEqual(self.inv_size3.num_item(self.item_stack3), 2)
        self.assertEqual(self.inv_size3.num_item(self.item_stack4), 6)
    
    def test_change_items_fail(self):
        self.inv_size4.add_item(self.item_stack3, 10)
        with self.assertRaises(InventoryLacksSpace):
            self.inv_size4.change_items(True, [(self.item_stack4, 8)],
                                        [(self.item_stack3, 1)])
        self.assertEqual(self.inv_size4.num_item(self.item_stack3), 10)
        self.assertEqual(self.inv_size4.num_item(self.item_stack4), 0)
    
    def test_change_items_ability(self):
        #Test checking if change is possible without doing it.
        self.inv_size4.add_item(self.item_stack4, 10)
        
        self.assertTrue(self.inv_size4.change_items(False,
                        [(self.item_stack3, 1)]))
        self.assertEqual(self.inv_size4.num_item(self.item_stack3), 0)
        
        self.assertFalse(self.inv_size4.change_items(False,
                        [(self.item_stack3, 4)]))
        self.assertEqual(self.inv_size4.num_item(self.item_stack3), 0)
