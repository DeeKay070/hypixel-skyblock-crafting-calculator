# Hypixel SkyBlock Crafting Profit Calculator  

This Python script retrieves **player inventory data from Hypixel SkyBlock** and calculates the **most profitable items to craft** based on Bazaar prices.

## Features  
✅ **Fetch Minecraft UUID Automatically** (No need to input manually)  
✅ **Retrieve and Cache SkyBlock Profiles** for a Player  
✅ **List and Select a SkyBlock Profile** Before Running Calculations  
✅ **Parse Inventory Data** and Match Against Crafting Recipes  
✅ **Load All Crafting Recipes from `items/` Folder**  
✅ **Ensure Crafting Requirements (`crafttext`) Are Met**  
✅ **Fetch Bazaar Prices** and **Calculate Profitability**  
✅ **Display the Top 5 Most Profitable Crafts**  

---

## 📥 Installation  

### **1. Clone the Repository**  
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/hypixel-crafting-calculator.git
cd hypixel-crafting-calculator


### **2. Install Dependencies**
pip install -r requirements.txt

### **3. Add your API key**
Open config.py and add your API key. This has recently changed go to developer.hypixel.net

### **4. Run the Program**
Start the script by running:
python main.py



🔄 How It Works
Fetches Your UUID Automatically

The script uses the Mojang API to get your UUID from your Minecraft username.
Retrieves Your SkyBlock Profiles

If you have multiple SkyBlock profiles, you will be asked to select one.
Parses Your Inventory

The script reads compressed inventory data and extracts your items.
Loads Crafting Recipes from items/ Folder

Recipes are stored as JSON files in items/, so you can modify or add new ones.
Checks Crafting Requirements (crafttext)

If a recipe has slayer, skill, or collection requirements, the script will warn you.
Fetches Bazaar Prices

The script queries Hypixel's Bazaar API for the latest buy & sell prices.
Calculates Profitability

Compares raw material costs vs. crafted item value to find the most profitable crafts.
Displays the Top 5 Most Profitable Crafts

Shows how much profit you make per craft and the percentage gain.


🚀 Future Features
 Auction House Profit Calculation
 SkyBlock Flipping Suggestions
 GUI Interface for Easier Use

👤 Author
GitHub: Deekay070
Discord: daytuh

📜 License
This project is open-source and licensed under the MIT License.