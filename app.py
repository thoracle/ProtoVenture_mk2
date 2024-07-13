from flask import Flask, render_template, request, session
import random
import json
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a real secret key

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Quest:
    def __init__(self, name, description, objective, reward):
        self.name = name
        self.description = description
        self.objective = objective
        self.progress = 0
        self.completed = False
        self.reward = reward

    def update_progress(self, amount=1):
        self.progress += amount
        if self.progress >= self.objective:
            self.completed = True

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'objective': self.objective,
            'progress': self.progress,
            'completed': self.completed,
            'reward': self.reward
        }

    @classmethod
    def from_dict(cls, data):
        quest = cls(data['name'], data['description'], data['objective'], data['reward'])
        quest.progress = data['progress']
        quest.completed = data['completed']
        return quest

class GameState:
    def __init__(self):
        self.location = "Dragonhome"
        self.reputation = {"Dragon Riders": 50, "Mage Guild": 50, "Merchants": 50}
        self.dragon = None
        self.inventory = {"Gold": 100}
        self.message = "Welcome to Dragon Rider's Quest!"
        self.quests = {}
        self.level = 1
        self.exp = 0
        self.max_hp = 100
        self.current_hp = 100
        self.attack = 10
        self.defense = 5

    def add_quest(self, quest):
        self.quests[quest.name] = quest

    def update_quest_progress(self, quest_name, amount=1):
        if quest_name in self.quests:
            self.quests[quest_name].update_progress(amount)
            if self.quests[quest_name].completed:
                self.claim_quest_reward(quest_name)

    def claim_quest_reward(self, quest_name):
        if quest_name in self.quests and self.quests[quest_name].completed:
            reward = self.quests[quest_name].reward
            if isinstance(reward, dict):
                for item, amount in reward.items():
                    if item == "Gold":
                        self.inventory["Gold"] += amount
                    elif item in self.reputation:
                        self.reputation[item] += amount
                    else:
                        self.inventory[item] = self.inventory.get(item, 0) + amount
            self.message += f" You completed the quest '{quest_name}' and received your reward!"

    def gain_exp(self, amount):
        self.exp += amount
        while self.exp >= self.exp_to_next_level():
            self.level_up()

    def exp_to_next_level(self):
        return self.level * 100

    def level_up(self):
        self.level += 1
        self.max_hp += 20
        self.current_hp = self.max_hp
        self.attack += 2
        self.defense += 1
        self.exp -= self.exp_to_next_level()
        self.message += f" You leveled up to level {self.level}!"

    def to_dict(self):
        return {
            'location': self.location,
            'reputation': self.reputation,
            'dragon': self.dragon,
            'inventory': self.inventory,
            'message': self.message,
            'quests': {name: quest.to_dict() for name, quest in self.quests.items()},
            'level': self.level,
            'exp': self.exp,
            'max_hp': self.max_hp,
            'current_hp': self.current_hp,
            'attack': self.attack,
            'defense': self.defense
        }

    @classmethod
    def from_dict(cls, data):
        state = cls()
        state.location = data['location']
        state.reputation = data['reputation']
        state.dragon = data['dragon']
        state.inventory = data['inventory']
        state.message = data['message']
        state.quests = {name: Quest.from_dict(quest_data) for name, quest_data in data['quests'].items()}
        state.level = data['level']
        state.exp = data['exp']
        state.max_hp = data['max_hp']
        state.current_hp = data['current_hp']
        state.attack = data['attack']
        state.defense = data['defense']
        return state

class Enemy:
    def __init__(self, name, hp, attack, defense, exp_reward):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.exp_reward = exp_reward

# Game content
locations = {
    "Dragonhome": {
        "description": "The majestic city of Dragonhome, where riders and dragons bond.",
        "options": ["Visit the Dragon Roost", "Go to the Mage Quarter", "Head to the Marketplace"]
    },
    "Dragon Roost": {
        "description": "A place where young dragons await their riders.",
        "options": ["Choose a dragon", "Return to Dragonhome"]
    },
    "Mage Quarter": {
        "description": "The air crackles with magical energy in this part of the city.",
        "options": ["Speak with the Archmage", "Buy a Spell Book", "Return to Dragonhome"]
    },
    "Marketplace": {
        "description": "A bustling area filled with merchants from all over the realm.",
        "options": ["Buy Dragon Food", "Sell Items", "Return to Dragonhome"]
    }
}

item_prices = {
    "Spell Book": {"buy": 50, "sell": 30},
    "Dragon Food": {"buy": 20, "sell": 15}
}

def combat(game_state, enemy):
    combat_log = []
    while game_state.current_hp > 0 and enemy.hp > 0:
        # Player's turn
        damage = max(0, game_state.attack - enemy.defense)
        enemy.hp -= damage
        combat_log.append(f"You deal {damage} damage to {enemy.name}.")

        if enemy.hp <= 0:
            combat_log.append(f"You defeated {enemy.name}!")
            game_state.gain_exp(enemy.exp_reward)
            combat_log.append(f"You gained {enemy.exp_reward} experience points.")
            break

        # Enemy's turn
        damage = max(0, enemy.attack - game_state.defense)
        game_state.current_hp -= damage
        combat_log.append(f"{enemy.name} deals {damage} damage to you.")

        if game_state.current_hp <= 0:
            combat_log.append("You have been defeated!")
            break

    return "\n".join(combat_log)

@app.route('/')
def home():
    game_state = GameState()
    session['game_state'] = json.dumps(game_state.to_dict())
    logger.debug(f"Initial game state: {game_state.to_dict()}")
    return render_template('game.html', game_state=game_state, 
                           options=locations[game_state.location]["options"],
                           current_tab='Inventory')

@app.route('/game', methods=['POST'])
def game():
    logger.debug(f"Session before processing: {session.get('game_state')}")
    game_state = GameState.from_dict(json.loads(session['game_state']))
    logger.debug(f"Game state loaded from session: {game_state.to_dict()}")
    
    choice = request.form['choice']
    current_tab = request.form.get('current_tab', 'Inventory')  # Default to 'Inventory' if not provided
    logger.debug(f"User choice: {choice}")
    
    if choice == "Sell Items":
        options = process_choice(game_state, choice)
    elif choice.startswith("Sell "):
        item = choice[5:]  # Remove "Sell " prefix
        sell_item(game_state, item)
        options = locations[game_state.location]["options"]
    else:
        options = process_choice(game_state, choice)
    
    logger.debug(f"Game state after processing choice: {game_state.to_dict()}")
    session['game_state'] = json.dumps(game_state.to_dict())
    logger.debug(f"Session after processing: {session['game_state']}")
    
    return render_template('game.html', game_state=game_state, options=options, current_tab=current_tab)

def process_choice(state, choice):
    logger.debug(f"Processing choice: {choice}")
    if choice == "Visit the Dragon Roost":
        state.location = "Dragon Roost"
        state.message = "You head to the Dragon Roost. " + locations["Dragon Roost"]["description"]
        if "Bond with a dragon" not in state.quests:
            state.add_quest(Quest("Bond with a dragon", "Choose your dragon companion", 1, {"Dragon Riders": 10}))
    elif choice == "Go to the Mage Quarter":
        state.location = "Mage Quarter"
        state.message = "You enter the Mage Quarter. " + locations["Mage Quarter"]["description"]
        if "Learn basic spells" not in state.quests:
            state.add_quest(Quest("Learn basic spells", "Study and master 3 basic spells", 3, {"Mage Guild": 10, "Spell Book": 1}))
    elif choice == "Head to the Marketplace":
        state.location = "Marketplace"
        state.message = "You arrive at the Marketplace. " + locations["Marketplace"]["description"]
        if "Master of trade" not in state.quests:
            state.add_quest(Quest("Master of trade", "Complete 5 trades in the marketplace", 5, {"Merchants": 10, "Gold": 50}))
    elif choice == "Choose a dragon":
        if state.dragon is None:
            state.dragon = random.choice(["Fire Drake", "Storm Wyrm", "Frost Serpent"])
            state.message = f"You have bonded with a {state.dragon}! Your reputation with the Dragon Riders has increased."
            state.update_quest_progress("Bond with a dragon")
        else:
            state.message = "You already have a dragon companion."
    elif choice == "Speak with the Archmage":
        state.reputation["Mage Guild"] += 5
        state.message = "The Archmage shares some magical wisdom. Your reputation with the Mage Guild has slightly increased."
        state.update_quest_progress("Learn basic spells")
    elif choice == "Buy a Spell Book":
        buy_item(state, "Spell Book")
    elif choice == "Buy Dragon Food":
        buy_item(state, "Dragon Food")
    elif choice == "Sell Items":
        sellable_items = [item for item, quantity in state.inventory.items() if item != "Gold" and quantity > 0]
        if sellable_items:
            state.message = "Select an item to sell:"
            return [f"Sell {item}" for item in sellable_items]
        else:
            state.message = "You don't have any items to sell."
    elif choice == "Return to Dragonhome":
        state.location = "Dragonhome"
        state.message = "You return to Dragonhome. " + locations["Dragonhome"]["description"]
    elif choice == "Fight Enemy":
        enemy = Enemy("Goblin", 50, 8, 3, 50)  # Example enemy
        combat_result = combat(state, enemy)
        state.message = combat_result
    else:
        state.message = "Invalid choice. Please try again."
    return locations[state.location]["options"]

def buy_item(state, item):
    logger.debug(f"Buying item: {item}")
    logger.debug(f"Inventory before buying: {state.inventory}")
    if state.inventory["Gold"] >= item_prices[item]["buy"]:
        state.inventory["Gold"] -= item_prices[item]["buy"]
        state.inventory[item] = state.inventory.get(item, 0) + 1
        state.message = f"You bought a {item} for {item_prices[item]['buy']} Gold."
        if "Master of trade" not in state.quests:
            state.add_quest(Quest("Master of trade", "Complete 5 trades in the marketplace", 5, {"Merchants": 10, "Gold": 50}))
        state.update_quest_progress("Master of trade")
    else:
        state.message = f"You don't have enough Gold to buy a {item}."
    logger.debug(f"Inventory after buying: {state.inventory}")

def sell_item(state, item):
    logger.debug(f"Attempting to sell item: {item}")
    logger.debug(f"Inventory before selling: {state.inventory}")
    if item in state.inventory and state.inventory[item] > 0:
        state.inventory[item] -= 1
        state.inventory["Gold"] += item_prices[item]["sell"]
        if state.inventory[item] == 0:
            del state.inventory[item]
        state.message = f"You sold a {item} for {item_prices[item]['sell']} Gold."
        if "Master of trade" not in state.quests:
            state.add_quest(Quest("Master of trade", "Complete 5 trades in the marketplace", 5, {"Merchants": 10, "Gold": 50}))
        state.update_quest_progress("Master of trade")
        logger.debug(f"Successfully sold {item}")
    else:
        state.message = f"You don't have any {item} to sell."
        logger.debug(f"Failed to sell {item} - not in inventory or quantity is 0")
    logger.debug(f"Inventory after selling attempt: {state.inventory}")

if __name__ == '__main__':
    app.run(debug=True)
