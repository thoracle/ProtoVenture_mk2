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

@app.route('/')
def home():
    return render_template('game.html', message="Welcome to Dragon Rider's Quest!", 
                           location=game_state.location, 
                           options=locations[game_state.location]["options"],
                           inventory=game_state.inventory)

@app.route('/game', methods=['POST'])
def game():
    choice = request.form['choice']
    message = process_choice(choice)
    return render_template('game.html', message=message, 
                           location=game_state.location, 
                           options=locations[game_state.location]["options"],
                           inventory=game_state.inventory)

def process_choice(choice):
    if choice == "Visit the Dragon Roost":
        game_state.location = "Dragon Roost"
        return "You head to the Dragon Roost. " + locations["Dragon Roost"]["description"]
    elif choice == "Go to the Mage Quarter":
        game_state.location = "Mage Quarter"
        return "You enter the Mage Quarter. " + locations["Mage Quarter"]["description"]
    elif choice == "Head to the Marketplace":
        game_state.location = "Marketplace"
        return "You arrive at the Marketplace. " + locations["Marketplace"]["description"]
    elif choice == "Choose a dragon":
        if game_state.dragon is None:
            game_state.dragon = random.choice(["Fire Drake", "Storm Wyrm", "Frost Serpent"])
            game_state.reputation["Dragon Riders"] += 10
            return f"You have bonded with a {game_state.dragon}! Your reputation with the Dragon Riders has increased."
        else:
            return "You already have a dragon companion."
    elif choice == "Speak with the Archmage":
        game_state.reputation["Mage Guild"] += 5
        return "The Archmage shares some magical wisdom. Your reputation with the Mage Guild has slightly increased."
    elif choice == "Buy a Spell Book":
        if game_state.inventory["Gold"] >= 50:
            game_state.inventory["Gold"] -= 50
            game_state.inventory["Spell Book"] = game_state.inventory.get("Spell Book", 0) + 1
            return "You bought a Spell Book for 50 Gold."
        else:
            return "You don't have enough Gold to buy a Spell Book."
    elif choice == "Buy Dragon Food":
        if game_state.inventory["Gold"] >= 20:
            game_state.inventory["Gold"] -= 20
            game_state.inventory["Dragon Food"] = game_state.inventory.get("Dragon Food", 0) + 1
            return "You bought Dragon Food for 20 Gold."
        else:
            return "You don't have enough Gold to buy Dragon Food."
    elif choice == "Sell Items":
        if "Spell Book" in game_state.inventory and game_state.inventory["Spell Book"] > 0:
            game_state.inventory["Spell Book"] -= 1
            game_state.inventory["Gold"] += 30
            return "You sold a Spell Book for 30 Gold."
        elif "Dragon Food" in game_state.inventory and game_state.inventory["Dragon Food"] > 0:
            game_state.inventory["Dragon Food"] -= 1
            game_state.inventory["Gold"] += 15
            return "You sold Dragon Food for 15 Gold."
        else:
            return "You have nothing to sell."
    elif choice == "Return to Dragonhome":
        game_state.location = "Dragonhome"
        return "You return to Dragonhome. " + locations["Dragonhome"]["description"]
    else:
        return "Invalid choice. Please try again."

if __name__ == '__main__':
    app.run(debug=True)
