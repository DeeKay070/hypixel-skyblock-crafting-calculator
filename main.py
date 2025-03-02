import os
import json
import time
import requests
import base64
import gzip
from io import BytesIO
import nbtlib
from config import API_KEY, PLAYER_DATA_DIR, PLAYER_CACHE_DURATION, ITEMS_FOLDER  # Import settings


# ====== UTILITY FUNCTIONS ======
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def load_json_file(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception:
        return None

def save_json_file(filepath, data):
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving {filepath}: {e}")

def handle_response_status(response):
    status_code = response.status_code
    print(f"API Response: {status_code}")
    
    if status_code == 200:
        return response.json()
    elif status_code == 400:
        print("400: Some data is missing, usually a required field.")
    elif status_code == 403:
        print("403: Access is forbidden, possibly due to an invalid API key.")
    elif status_code == 422:
        print("422: Some data provided is invalid.")
    elif status_code == 429:
        print("429: Request limit reached; the key's limit may have been exceeded or a global throttle is in effect.")
    else:
        print(f"{status_code}: Unexpected response.")
    
    return None

# ====== FETCH PLAYER UUID AUTOMATICALLY ======
def get_uuid(username):
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    response = requests.get(url)
    data = handle_response_status(response)
    return data.get("id") if data else None

# ====== FETCH PLAYER PROFILES & CACHE ======
def get_player_profiles(username):
    ensure_dir(PLAYER_DATA_DIR)
    
    uuid = get_uuid(username)
    if not uuid:
        return None, None

    cache_file = os.path.join(PLAYER_DATA_DIR, f"{uuid}.json")
    current_time = time.time()

    cache = load_json_file(cache_file)
    if cache and current_time - cache.get("timestamp", 0) < PLAYER_CACHE_DURATION:
        print(f"Using cached player data for {username}.")
        return uuid, cache.get("profiles", {})

    try:
        url = f"https://api.hypixel.net/skyblock/profiles?key={API_KEY}&uuid={uuid}"
        response = requests.get(url)
        data = handle_response_status(response)
        
        if not data or not data.get("success"):
            raise Exception("Hypixel API error.")
        
        profiles = data.get("profiles", [])
        profile_data = {p['profile_id']: {'cute_name': p.get('cute_name', 'Unnamed'), 'data': p} for p in profiles}

    except Exception as e:
        print(f"Error fetching player profiles: {e}")
        profile_data = {}

    cache = {"timestamp": current_time, "profiles": profile_data}
    save_json_file(cache_file, cache)
    return uuid, profile_data

# ====== SELECT PROFILE ======
def select_profile(profiles):
    if not profiles:
        print("No profiles available.")
        return None
    
    print("\nAvailable Profiles:")
    for idx, (profile_id, profile) in enumerate(profiles.items(), 1):
        print(f"{idx}. {profile['cute_name']} (ID: {profile_id})")
    
    choice = input("Select a profile by number: ").strip()
    
    try:
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(profiles):
            return list(profiles.keys())[choice_idx]
    except ValueError:
        pass
    
    print("Invalid selection.")
    return None

# ====== DECODE INVENTORY DATA ======
def decode_inventory_data(encoded_data):
    try:
        compressed_data = base64.b64decode(encoded_data)
        with gzip.GzipFile(fileobj=BytesIO(compressed_data)) as f:
            return nbtlib.load(f).root
    except Exception as e:
        print(f"Error decoding inventory data: {e}")
        return {}

def parse_inventory(nbt_root):
    inventory = {}
    try:
        items = nbt_root.get('i', [])
        for item in items:
            if 'tag' in item and 'display' in item['tag'] and 'Name' in item['tag']['display']:
                name = item['tag']['display']['Name'].value
                count = item.get('Count', 1)
                inventory[name] = inventory.get(name, 0) + int(count)
    except Exception as e:
        print(f"Error parsing inventory: {e}")
    return inventory

# ====== LOAD CRAFTING RECIPES ======
def load_recipes():
    recipes = {}
    if not os.path.exists(ITEMS_FOLDER):
        print(f"Items folder '{ITEMS_FOLDER}' does not exist.")
        return {}

    for filename in os.listdir(ITEMS_FOLDER):
        if filename.endswith('.json'):
            filepath = os.path.join(ITEMS_FOLDER, filename)
            try:
                with open(filepath, 'r') as f:
                    recipe_data = json.load(f)
                    recipes[recipe_data["internalname"]] = recipe_data
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return recipes

# ====== FETCH BAZAAR DATA ======
def fetch_bazaar_data():
    url = f"https://api.hypixel.net/skyblock/bazaar?key={API_KEY}"
    response = requests.get(url)
    return handle_response_status(response).get("products", {})

# ====== CHECK CRAFTING REQUIREMENTS ======
def can_craft(recipe, inventory):
    if "Requires" in recipe.get("crafttext", ""):
        print(f"⚠ {recipe['displayname']} requires {recipe['crafttext']}.")

    for slot, item in recipe.get("recipe", {}).items():
        if item:
            item_name, qty = item.split(":")
            if inventory.get(item_name, 0) < int(qty):
                return False
    return True

# ====== FIND PROFITABLE CRAFTS ======
def find_profitable_crafts(recipes, inventory, bazaar_data):
    crafts = []

    for recipe in recipes.values():
        if not can_craft(recipe, inventory):
            continue

        item_id = recipe["internalname"]
        sell_price = bazaar_data.get(item_id, {}).get("quick_status", {}).get("buyPrice", 0)
        total_cost = sum(
            int(qty) * bazaar_data.get(mat, {}).get("quick_status", {}).get("sellPrice", 0)
            for slot, mat_qty in recipe.get("recipe", {}).items() if (mat_qty and (mat, qty := mat_qty.split(":")))
        )

        if total_cost > 0:
            profit = sell_price - total_cost
            crafts.append((recipe["displayname"], profit, (profit / total_cost) * 100))

    return sorted(crafts, key=lambda x: x[1], reverse=True)[:5]

# ====== MAIN PROGRAM ======
def main():
    username = input("Enter your Minecraft username: ").strip()
    uuid, profiles = get_player_profiles(username)

    if not uuid or not profiles:
        print("Failed to retrieve player data.")
        return

    profile_id = select_profile(profiles)
    if not profile_id:
        return

    inventory_data = profiles[profile_id]['data']['members'][uuid].get('inv_contents', {}).get('data')
    inventory = parse_inventory(decode_inventory_data(inventory_data)) if inventory_data else {}

    recipes = load_recipes()
    bazaar_data = fetch_bazaar_data()

    print("\nTop 5 Most Profitable Crafts:")
    for name, profit, pct in find_profitable_crafts(recipes, inventory, bazaar_data):
        print(f"🔹 {name} ➜ Profit: {profit:.2f} coins ({pct:.2f}%)")

if __name__ == "__main__":
    main()
