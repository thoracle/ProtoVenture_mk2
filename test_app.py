import unittest
from app import GameState, process_choice, buy_item, sell_item, item_prices, locations

class TestDragonRiderQuest(unittest.TestCase):

    def setUp(self):
        self.game_state = GameState()

    def test_initial_state(self):
        self.assertEqual(self.game_state.location, "Dragonhome")
        self.assertEqual(self.game_state.inventory["Gold"], 100)
        self.assertIsNone(self.game_state.dragon)

    def test_buy_item(self):
        buy_item(self.game_state, "Spell Book")
        self.assertEqual(self.game_state.inventory["Gold"], 50)
        self.assertEqual(self.game_state.inventory.get("Spell Book", 0), 1)

    def test_buy_item_not_enough_gold(self):
        self.game_state.inventory["Gold"] = 10
        buy_item(self.game_state, "Spell Book")
        self.assertEqual(self.game_state.inventory["Gold"], 10)
        self.assertNotIn("Spell Book", self.game_state.inventory)

    def test_sell_item(self):
        self.game_state.inventory["Spell Book"] = 1
        sell_item(self.game_state, "Spell Book")
        self.assertEqual(self.game_state.inventory["Gold"], 130)
        self.assertNotIn("Spell Book", self.game_state.inventory)

    def test_sell_item_none_available(self):
        initial_gold = self.game_state.inventory["Gold"]
        sell_item(self.game_state, "Spell Book")
        self.assertEqual(self.game_state.inventory["Gold"], initial_gold)
        self.assertEqual(self.game_state.message, "You don't have any Spell Book to sell.")

    def test_process_choice_buy(self):
        process_choice(self.game_state, "Buy a Spell Book")
        self.assertEqual(self.game_state.inventory["Gold"], 50)
        self.assertEqual(self.game_state.inventory.get("Spell Book", 0), 1)

    def test_process_choice_sell_items(self):
        self.game_state.inventory["Spell Book"] = 1
        options = process_choice(self.game_state, "Sell Items")
        self.assertIn("Sell Spell Book", options)
        self.assertEqual(self.game_state.message, "Select an item to sell:")

    def test_process_choice_sell_items_none_available(self):
    self.game_state.location = "Marketplace"  # Ensure we're in the Marketplace
    options = process_choice(self.game_state, "Sell Items")
    self.assertEqual(self.game_state.message, "You don't have any items to sell.")
    self.assertEqual(options, locations["Marketplace"]["options"])

    def test_full_buy_sell_cycle(self):
        # Buy an item
        process_choice(self.game_state, "Buy a Spell Book")
        self.assertEqual(self.game_state.inventory["Gold"], 50)
        self.assertEqual(self.game_state.inventory.get("Spell Book", 0), 1)

        # Try to sell items
        options = process_choice(self.game_state, "Sell Items")
        self.assertIn("Sell Spell Book", options)

        # Sell the item
        sell_item(self.game_state, "Spell Book")
        self.assertEqual(self.game_state.inventory["Gold"], 80)
        self.assertNotIn("Spell Book", self.game_state.inventory)

    def test_multiple_items(self):
        # Buy multiple items
        buy_item(self.game_state, "Spell Book")
        buy_item(self.game_state, "Dragon Food")
        self.assertEqual(self.game_state.inventory["Gold"], 30)
        self.assertEqual(self.game_state.inventory["Spell Book"], 1)
        self.assertEqual(self.game_state.inventory["Dragon Food"], 1)

        # Try to sell items
        options = process_choice(self.game_state, "Sell Items")
        self.assertIn("Sell Spell Book", options)
        self.assertIn("Sell Dragon Food", options)

        # Sell one item
        sell_item(self.game_state, "Spell Book")
        self.assertEqual(self.game_state.inventory["Gold"], 60)
        self.assertNotIn("Spell Book", self.game_state.inventory)
        self.assertEqual(self.game_state.inventory["Dragon Food"], 1)

if __name__ == '__main__':
    unittest.main()
