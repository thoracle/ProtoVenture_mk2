from flask import Flask, render_template, request, session
import random

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

game_state = GameState()

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
    return render_template('game.html', game_state=game_state, 
                           options=locations[game_state.location]["options"])

@app.route('/game', methods=['POST'])
def game():
    choice = request.form['choice']
    if choice.startswith("Sell "):
        item = choice[5:]  # Remove "Sell " prefix
        sell_item(item)
    else:
        process_choice(choice)
    return render_template('game.html', game_state=game_state, 
                           options=locations[game_state.location]["options"])

def process_choice(choice):
    if choice == "Visit the Dragon Roost":
        game_state.location = "Dragon Roost"
        game_state.message = "You head to the Dragon Roost. " + locations["Dragon Roost"]["description"]
    elif choice == "Go to the Mage Quarter":
        game_state.location = "Mage Quarter"
        game_state.message = "You enter the Mage Quarter. " + locations["Mage Quarter"]["description"]
    elif choice == "Head to the Marketplace":
        game_state.location = "Marketplace"
        game_state.message = "You arrive at the Marketplace. " + locations["Marketplace"]["description"]
    elif choice == "Choose a dragon":
        if game_state.dragon is None:
            game_state.dragon = random.choice(["Fire Drake", "Storm Wyrm", "Frost Serpent"])
            game_state.reputation["Dragon Riders"] += 10
            game_state.message = f"You have bonded with a {game_state.dragon}! Your reputation with the Dragon Riders has increased."
        else:
            game_state.message = "You already have a dragon companion."
    elif choice == "Speak with the Archmage":
        game_state.reputation["Mage Guild"] += 5
        game_state.message = "The Archmage shares some magical wisdom. Your reputation with the Mage Guild has slightly increased."
    elif choice == "Buy a Spell Book":
        buy_item("Spell Book")
    elif choice == "Buy Dragon Food":
        buy_item("Dragon Food")
    elif choice == "Sell Items":
        game_state.message = "Select an item to sell:"
        return [f"Sell {item}" for item, quantity in game_state.inventory.items() if item != "Gold" and quantity > 0]
    elif choice == "Return to Dragonhome":
        game_state.location = "Dragonhome"
        game_state.message = "You return to Dragonhome. " + locations["Dragonhome"]["description"]
    else:
        game_state.message = "Invalid choice. Please try again."

def buy_item(item):
    if game_state.inventory["Gold"] >= item_prices[item]["buy"]:
        game_state.inventory["Gold"] -= item_prices[item]["buy"]
        game_state.inventory[item] = game_state.inventory.get(item, 0) + 1
        game_state.message = f"You bought a {item} for {item_prices[item]['buy']} Gold."
    else:
        game_state.message = f"You don't have enough Gold to buy a {item}."

def sell_item(item):
    if item in game_state.inventory and game_state.inventory[item] > 0:
        game_state.inventory[item] -= 1
        game_state.inventory["Gold"] += item_prices[item]["sell"]
        if game_state.inventory[item] == 0:
            del game_state.inventory[item]
        game_state.message = f"You sold a {item} for {item_prices[item]['sell']} Gold."
    else:
        game_state.message = f"You don't have a {item} to sell."

if __name__ == '__main__':
    app.run(debug=True)
