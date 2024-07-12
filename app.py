from flask import Flask, render_template, request, session
import random
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a real secret key

# Game state
class GameState:
    def __init__(self):
        self.location = "Dragonhome"
        self.reputation = {"Dragon Riders": 50, "Mage Guild": 50, "Merchants": 50}
        self.dragon = None
        self.inventory = {"Gold": 100}
        self.message = "Welcome to Dragon Rider's Quest!"

    def to_dict(self):
        return {
            'location': self.location,
            'reputation': self.reputation,
            'dragon': self.dragon,
            'inventory': self.inventory,
            'message': self.message
        }

    @classmethod
    def from_dict(cls, data):
        state = cls()
        state.location = data['location']
        state.reputation = data['reputation']
        state.dragon = data['dragon']
        state.inventory = data['inventory']
        state.message = data['message']
        return state

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

@app.route('/')
def home():
    game_state = GameState()
    session['game_state'] = json.dumps(game_state.to_dict())
    return render_template('game.html', game_state=game_state, 
                           options=locations[game_state.location]["options"])

@app.route('/game', methods=['POST'])
def game():
    game_state = GameState.from_dict(json.loads(session['game_state']))
    choice = request.form['choice']
    if choice.startswith("Sell "):
        item = choice[5:]  # Remove "Sell " prefix
        sell_item(game_state, item)
        options = locations[game_state.location]["options"]
    else:
        options = process_choice(game_state, choice)
    session['game_state'] = json.dumps(game_state.to_dict())
    return render_template('game.html', game_state=game_state, options=options)

def process_choice(state, choice):
    if choice == "Visit the Dragon Roost":
        state.location = "Dragon Roost"
        state.message = "You head to the Dragon Roost. " + locations["Dragon Roost"]["description"]
    elif choice == "Go to the Mage Quarter":
        state.location = "Mage Quarter"
        state.message = "You enter the Mage Quarter. " + locations["Mage Quarter"]["description"]
    elif choice == "Head to the Marketplace":
        state.location = "Marketplace"
        state.message = "You arrive at the Marketplace. " + locations["Marketplace"]["description"]
    elif choice == "Choose a dragon":
        if state.dragon is None:
            state.dragon = random.choice(["Fire Drake", "Storm Wyrm", "Frost Serpent"])
            state.reputation["Dragon Riders"] += 10
            state.message = f"You have bonded with a {state.dragon}! Your reputation with the Dragon Riders has increased."
        else:
            state.message = "You already have a dragon companion."
    elif choice == "Speak with the Archmage":
        state.reputation["Mage Guild"] += 5
        state.message = "The Archmage shares some magical wisdom. Your reputation with the Mage Guild has slightly increased."
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
    else:
        state.message = "Invalid choice. Please try again."
    return locations[state.location]["options"]

def buy_item(state, item):
    if state.inventory["Gold"] >= item_prices[item]["buy"]:
        state.inventory["Gold"] -= item_prices[item]["buy"]
        state.inventory[item] = state.inventory.get(item, 0) + 1
        state.message = f"You bought a {item} for {item_prices[item]['buy']} Gold."
    else:
        state.message = f"You don't have enough Gold to buy a {item}."

def sell_item(state, item):
    if item in state.inventory and state.inventory[item] > 0:
        state.inventory[item] -= 1
        state.inventory["Gold"] += item_prices[item]["sell"]
        if state.inventory[item] == 0:
            del state.inventory[item]
        state.message = f"You sold a {item} for {item_prices[item]['sell']} Gold."
    else:
        state.message = f"You don't have any {item} to sell."

if __name__ == '__main__':
    app.run(debug=True)
