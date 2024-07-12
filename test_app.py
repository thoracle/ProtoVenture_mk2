import unittest
from app import GameState, process_choice, buy_item, sell_item, item_prices

class TestDragonRiderQuest(unittest.TestCase):

    def setUp(self):
        self.game_state = GameState()

    def test_initial_state(self):
        self.assertEqual(self.game_state.location, "Dragonhome")
        self.assertEqual(self.game_state.inventory["Gold"], 100)
        self.assertIsNone(self.game_state.dragon)

    def test_buy_item(self):
        buy_item("Spell Book")
        self.assertEqual(self.game_state.inventory["Gold"], 50)
        self.assertEqual(self.game_state.inventory.get("Spell Book", 0), 1)

    def test_buy_item_not_enough_gold(self):
        self.game_state.inventory["Gold"] = 10
        buy_item("Spell Book")
        self.assertEqual(self.game_state.inventory["Gold"], 10)
        self.assertNotIn("Spell Book", self.game_state.inventory)

    def test_sell_item(self):
        self.game_state.inventory["Spell Book"] = 1
        sell_item("Spell Book")
        self.assertEqual(self.game_state.inventory["Gold"], 130)
        self.assertNotIn("Spell Book", self.game_state.inventory)

    def test_sell_item_none_available(self):
        initial_gold = self.game_state.inventory["Gold"]
        sell_item("Spell Book")
        self.assertEqual(self.game_state.inventory["Gold"], initial_gold)

    def test_process_choice_buy(self):
        process_choice("Buy a Spell Book")
        self.assertEqual(self.game_state.inventory["Gold"], 50)
        self.assertEqual(self.game_state.inventory.get("Spell Book", 0), 1)

    def test_process_choice_sell_items(self):
        self.game_state.inventory["Spell Book"] = 1
        options = process_choice("Sell Items")
        self.assertIn("Sell Spell Book", options)

    def test_process_choice_sell_items_none_available(self):
        options = process_choice("Sell Items")
        self.assertNotIn("Sell", " ".join(options))

if __name__ == '__main__':
    unittest.main()
