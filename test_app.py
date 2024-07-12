import unittest
from app import GameState, process_choice, buy_item, sell_item, item_prices, locations

class TestDragonRiderQuest(unittest.TestCase):

    def setUp(self):
        self.game_state = GameState()

    def test_initial_state(self):
        self.assertEqual(self.game_state.location, "Dragonhome")
        self.assertEqual(self.game_state.inventory["Gold"], 100)
        self.assertIsNone(self.game_state.dragon)
        self.assertEqual(self.game_state.quests, [])

    def test_buy_item(self):
        buy_item(self.game_state, "Spell Book")
        self.assertEqual(self.game_state.inventory["Gold"], 50)
        self.assertEqual(self.game_state.inventory.get("Spell Book", 0), 1)
        self.assertIn("Study your Spell Book", self.game_state.quests)

    def test_buy_item_not_enough_gold(self):
        self.game_state.inventory["Gold"] = 10
        buy_item(self.game_state, "Spell Book")
        self.assertEqual(self.game_state.inventory["Gold"], 10)
        self.assertNotIn("Spell Book", self.game_state.inventory)
        self.assertNotIn("Study your Spell Book", self.game_state.quests)

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
        self.assertIn("Study your Spell Book", self.game_state.quests)

    def test_process_choice_sell_items(self):
        self.game_state.inventory["Spell Book"] = 1
        options = process_choice(self.game_state, "Sell Items")
        self.assertIn("Sell Spell Book", options)
        self.assertEqual(self.game_state.message, "Select an item to sell:")

    def test_process_choice_sell_items_none_available(self):
        self.game_state.location = "Marketplace"
        options = process_choice(self.game_state, "Sell Items")
        self.assertEqual(self.game_state.message, "You don't have any items to sell.")
        self.assertEqual(options, locations["Marketplace"]["options"])

    def test_change_location(self):
        self.game_state.location = "Dragonhome"
        options = process_choice(self.game_state, "Go to the Mage Quarter")
        self.assertEqual(self.game_state.location, "Mage Quarter")
        self.assertEqual(options, locations["Mage Quarter"]["options"])

        options = process_choice(self.game_state, "Head to the Marketplace")
        self.assertEqual(self.game_state.location, "Marketplace")
        self.assertEqual(options, locations["Marketplace"]["options"])

        options = process_choice(self.game_state, "Return to Dragonhome")
        self.assertEqual(self.game_state.location, "Dragonhome")
        self.assertEqual(options, locations["Dragonhome"]["options"])

    def test_speak_with_archmage(self):
        process_choice(self.game_state, "Speak with the Archmage")
        self.assertEqual(self.game_state.reputation["Mage Guild"], 55)
        self.assertIn("Learn basic spells", self.game_state.quests)

    def test_choose_dragon(self):
        process_choice(self.game_state, "Choose a dragon")
        self.assertIsNotNone(self.game_state.dragon)
        self.assertEqual(self.game_state.reputation["Dragon Riders"], 60)
        self.assertIn("Bond with a dragon", self.game_state.quests)

    def test_choose_dragon_already_have_one(self):
        self.game_state.dragon = "Fire Drake"
        process_choice(self.game_state, "Choose a dragon")
        self.assertEqual(self.game_state.dragon, "Fire Drake")
        self.assertEqual(self.game_state.reputation["Dragon Riders"], 50)
        self.assertNotIn("Bond with a dragon", self.game_state.quests)

    def test_buy_dragon_food(self):
        process_choice(self.game_state, "Buy Dragon Food")
        self.assertEqual(self.game_state.inventory["Gold"], 80)
        self.assertEqual(self.game_state.inventory.get("Dragon Food", 0), 1)
        self.assertIn("Feed your dragon", self.game_state.quests)

if __name__ == '__main__':
    unittest.main()
