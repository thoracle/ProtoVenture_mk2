import unittest
from app import GameState, Quest, Enemy, combat, process_choice, buy_item, sell_item, item_prices, locations

class TestDragonRiderQuest(unittest.TestCase):

    def setUp(self):
        self.game_state = GameState()

    def test_initial_state(self):
        self.assertEqual(self.game_state.location, "Dragonhome")
        self.assertEqual(self.game_state.inventory["Gold"], 100)
        self.assertIsNone(self.game_state.dragon)
        self.assertEqual(self.game_state.quests, {})
        self.assertEqual(self.game_state.level, 1)
        self.assertEqual(self.game_state.exp, 0)
        self.assertEqual(self.game_state.max_hp, 100)
        self.assertEqual(self.game_state.current_hp, 100)
        self.assertEqual(self.game_state.attack, 10)
        self.assertEqual(self.game_state.defense, 5)

    def test_add_quest(self):
        quest = Quest("Test Quest", "A test quest", 3, {"Gold": 50})
        self.game_state.add_quest(quest)
        self.assertIn("Test Quest", self.game_state.quests)
        self.assertEqual(self.game_state.quests["Test Quest"].objective, 3)

    def test_update_quest_progress(self):
        quest = Quest("Test Quest", "A test quest", 3, {"Gold": 50})
        self.game_state.add_quest(quest)
        self.game_state.update_quest_progress("Test Quest", 2)
        self.assertEqual(self.game_state.quests["Test Quest"].progress, 2)
        self.assertFalse(self.game_state.quests["Test Quest"].completed)

    def test_complete_quest(self):
        quest = Quest("Test Quest", "A test quest", 3, {"Gold": 50})
        self.game_state.add_quest(quest)
        self.game_state.update_quest_progress("Test Quest", 3)
        self.assertTrue(self.game_state.quests["Test Quest"].completed)
        self.assertEqual(self.game_state.inventory["Gold"], 150)  # Initial 100 + 50 reward

    def test_buy_item(self):
        buy_item(self.game_state, "Spell Book")
        self.assertEqual(self.game_state.inventory["Gold"], 50)
        self.assertEqual(self.game_state.inventory.get("Spell Book", 0), 1)
        self.assertIn("Master of trade", self.game_state.quests)
        self.assertEqual(self.game_state.quests["Master of trade"].progress, 1)

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
        self.assertIn("Master of trade", self.game_state.quests)
        self.assertEqual(self.game_state.quests["Master of trade"].progress, 1)

    def test_sell_item_none_available(self):
        initial_gold = self.game_state.inventory["Gold"]
        sell_item(self.game_state, "Spell Book")
        self.assertEqual(self.game_state.inventory["Gold"], initial_gold)
        self.assertEqual(self.game_state.message, "You don't have any Spell Book to sell.")

    def test_process_choice_buy(self):
        process_choice(self.game_state, "Buy a Spell Book")
        self.assertEqual(self.game_state.inventory["Gold"], 50)
        self.assertEqual(self.game_state.inventory.get("Spell Book", 0), 1)
        self.assertIn("Master of trade", self.game_state.quests)
        self.assertEqual(self.game_state.quests["Master of trade"].progress, 1)

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
        options = process_choice(self.game_state, "Go to the Mage Quarter")
        self.assertEqual(self.game_state.location, "Mage Quarter")
        self.assertEqual(options, locations["Mage Quarter"]["options"])
        self.assertIn("Learn basic spells", self.game_state.quests)

        options = process_choice(self.game_state, "Head to the Marketplace")
        self.assertEqual(self.game_state.location, "Marketplace")
        self.assertEqual(options, locations["Marketplace"]["options"])
        self.assertIn("Master of trade", self.game_state.quests)

        options = process_choice(self.game_state, "Return to Dragonhome")
        self.assertEqual(self.game_state.location, "Dragonhome")
        self.assertEqual(options, locations["Dragonhome"]["options"])

    def test_choose_dragon(self):
        process_choice(self.game_state, "Visit the Dragon Roost")
        process_choice(self.game_state, "Choose a dragon")
        self.assertIsNotNone(self.game_state.dragon)
        self.assertIn("Bond with a dragon", self.game_state.quests)
        self.assertTrue(self.game_state.quests["Bond with a dragon"].completed)

    def test_speak_with_archmage(self):
        process_choice(self.game_state, "Go to the Mage Quarter")
        process_choice(self.game_state, "Speak with the Archmage")
        self.assertEqual(self.game_state.reputation["Mage Guild"], 55)
        self.assertIn("Learn basic spells", self.game_state.quests)
        self.assertEqual(self.game_state.quests["Learn basic spells"].progress, 1)

    def test_combat(self):
        enemy = Enemy("Test Enemy", 30, 5, 2, 20)
        initial_hp = self.game_state.current_hp
        result = combat(self.game_state, enemy)
        self.assertIn("You defeated Test Enemy!", result)
        self.assertGreater(self.game_state.exp, 0)
        self.assertLess(self.game_state.current_hp, initial_hp)
        self.assertGreater(self.game_state.current_hp, 0)  # Ensure player survives
        self.assertIn("deals 1 damage to you", result)  # Check that enemy deals minimum damage
        self.assertIn("You deal 8 damage to Test Enemy", result)  # Check player damage
    
    def test_combat_defeat(self):
        enemy = Enemy("Strong Enemy", 200, 50, 10, 100)
        result = combat(self.game_state, enemy)
        self.assertIn("You have been defeated!", result)
        self.assertEqual(self.game_state.current_hp, 0)

    def test_gain_exp(self):
        initial_level = self.game_state.level
        self.game_state.gain_exp(50)
        self.assertEqual(self.game_state.level, initial_level)
        self.assertEqual(self.game_state.exp, 50)

    def test_level_up(self):
        initial_level = self.game_state.level
        initial_max_hp = self.game_state.max_hp
        initial_attack = self.game_state.attack
        initial_defense = self.game_state.defense

        self.game_state.gain_exp(100)  # Assuming 100 exp is enough to level up
        
        self.assertEqual(self.game_state.level, initial_level + 1)
        self.assertGreater(self.game_state.max_hp, initial_max_hp)
        self.assertGreater(self.game_state.attack, initial_attack)
        self.assertGreater(self.game_state.defense, initial_defense)
        self.assertEqual(self.game_state.current_hp, self.game_state.max_hp)

    def test_exp_to_next_level(self):
        self.assertEqual(self.game_state.exp_to_next_level(), 100)  # At level 1
        self.game_state.level = 2
        self.assertEqual(self.game_state.exp_to_next_level(), 200)  # At level 2

    def test_to_dict_and_from_dict(self):
        original_state = GameState()
        original_state.dragon = "Fire Drake"
        original_state.add_quest(Quest("Test Quest", "A test quest", 3, {"Gold": 50}))
        original_state.level = 2
        original_state.exp = 50
        state_dict = original_state.to_dict()
        
        new_state = GameState.from_dict(state_dict)
        self.assertEqual(new_state.location, original_state.location)
        self.assertEqual(new_state.reputation, original_state.reputation)
        self.assertEqual(new_state.dragon, original_state.dragon)
        self.assertEqual(new_state.inventory, original_state.inventory)
        self.assertEqual(new_state.message, original_state.message)
        self.assertEqual(len(new_state.quests), len(original_state.quests))
        self.assertEqual(new_state.quests["Test Quest"].name, original_state.quests["Test Quest"].name)
        self.assertEqual(new_state.quests["Test Quest"].objective, original_state.quests["Test Quest"].objective)
        self.assertEqual(new_state.level, original_state.level)
        self.assertEqual(new_state.exp, original_state.exp)
        self.assertEqual(new_state.max_hp, original_state.max_hp)
        self.assertEqual(new_state.current_hp, original_state.current_hp)
        self.assertEqual(new_state.attack, original_state.attack)
        self.assertEqual(new_state.defense, original_state.defense)

if __name__ == '__main__':
    unittest.main()
