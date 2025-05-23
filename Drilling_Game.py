import os
import json
import datetime
import time
import random

class Color:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

class UserDataManager:
    def __init__(self, file_path='user_data.json'):
        self.file_path = file_path
        self.default_data = {
            "name": "Miner",
            "coins": 0,
            "luck": 0,
            "energy": 100,
            "max_energy": 100,
            "drill": "Beginner Drill",
            "inventory": {},
            "drills_used": 0,
            "last_played": datetime.datetime.now().isoformat()
        }
        self.data = self.load()

    def load(self):
        if not os.path.exists(self.file_path):
            return self.default_data.copy()
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                # Add missing keys
                for key, value in self.default_data.items():
                    if key not in data:
                        data[key] = value
                return data
        except:
            return self.default_data.copy()

    def save(self):
        self.data["last_played"] = datetime.datetime.now().isoformat()
        try:
            with open(self.file_path, 'w') as file:
                json.dump(self.data, file)
        except:
            print(f"{Color.RED}Failed to save game data{Color.END}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def add(self, key, amount=1):
        self.data[key] = self.get(key, 0) + amount
        self.save()

    def update_inventory(self, ore, quantity):
        inventory = self.get("inventory", {})
        inventory[ore] = inventory.get(ore, 0) + quantity
        if inventory[ore] <= 0:
            inventory.pop(ore)
        self.data["inventory"] = inventory
        self.save()

    def reset(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        self.data = self.default_data.copy()
        self.save()

class MiningGame:
    def __init__(self):
        self.data = UserDataManager()
        self.ores = self.define_ores()
        self.drill_speeds = {
            "Beginner Drill": 0.5,
            "Novice Drill": 0.4,
            "Advanced Drill": 0.2,
            "Expert Drill": 0.1,
            "Master Drill": 0.05
        }
        self.drill_costs = {
            "Beginner Drill": 0,
            "Novice Drill": 100, 
            "Advanced Drill": 300,
            "Expert Drill": 600,
            "Master Drill": 1200
        }
        self.luck_cost = lambda level: (level + 1) * 50
        self.energy_cost = lambda level: level * 100
        self.check_energy_regen()

    def define_ores(self):
        return [
            {"name": "Coal", "price": 1, "min_luck": 0, "max_luck": 20, "color": "", "weight": 10},
            {"name": "Iron", "price": 3, "min_luck": 0, "max_luck": 20, "color": Color.BOLD, "weight": 8},
            {"name": "Copper", "price": 5, "min_luck": 2, "max_luck": 20, "color": Color.YELLOW, "weight": 6},
            {"name": "Silver", "price": 10, "min_luck": 4, "max_luck": 20, "color": Color.BOLD, "weight": 4},
            {"name": "Gold", "price": 25, "min_luck": 6, "max_luck": 20, "color": Color.YELLOW + Color.BOLD, "weight": 3},
            {"name": "Diamond", "price": 60, "min_luck": 8, "max_luck": 20, "color": Color.BLUE + Color.BOLD, "weight": 2},
            {"name": "Ruby", "price": 150, "min_luck": 10, "max_luck": 20, "color": Color.RED + Color.BOLD, "weight": 1.5},
            {"name": "Emerald", "price": 350, "min_luck": 12, "max_luck": 20, "color": Color.GREEN + Color.BOLD, "weight": 1},
            {"name": "Obsidian", "price": 800, "min_luck": 14, "max_luck": 20, "color": Color.PURPLE + Color.BOLD, "weight": 0.7},
            {"name": "Mythril", "price": 1800, "min_luck": 16, "max_luck": 20, "color": Color.BLUE, "weight": 0.4},
            {"name": "Voidcore", "price": 4000, "min_luck": 18, "max_luck": 20, "color": Color.PURPLE, "weight": 0.2}
        ]

    def check_energy_regen(self):
        try:
            last_played_str = self.data.get("last_played")
            last_played = datetime.datetime.fromisoformat(last_played_str)
            now = datetime.datetime.now()
            minutes_passed = (now - last_played).total_seconds() / 60
            energy_to_add = min(int(minutes_passed / 2), self.data.get("max_energy"))
            
            if energy_to_add > 0:
                current = self.data.get("energy")
                max_energy = self.data.get("max_energy")
                new_energy = min(current + energy_to_add, max_energy)
                self.data.set("energy", new_energy)
                if new_energy > current:
                    print(f"{Color.GREEN}+{new_energy - current} energy regenerated while away{Color.END}")
        except:
            self.data.set("last_played", datetime.datetime.now().isoformat())

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_header(self):
        name = self.data.get("name")
        coins = self.data.get("coins")
        luck = self.data.get("luck")
        energy = self.data.get("energy")
        max_energy = self.data.get("max_energy")
        drill = self.data.get("drill")
        
        print(f"{Color.BLUE}===== UNDERGROUND MINER ====={Color.END}")
        print(f"Miner: {name} | 💰 {coins} | 🍀 {luck} | ⚡ {energy}/{max_energy}")
        print(f"Drill: {drill}")
        print(f"{Color.BLUE}============================={Color.END}")

    def wait_for_key(self):
        input("\nPress Enter to continue...")

    def mine(self):
        luck = self.data.get("luck")
        energy = self.data.get("energy")
        drill = self.data.get("drill")
        
        unlocked_ores = [ore for ore in self.ores if ore["min_luck"] <= luck]
        if not unlocked_ores:
            print(f"{Color.RED}No ores available with your current luck!{Color.END}")
            return
            
        print(f"\n{Color.BLUE}MINING{Color.END}")
        print(f"Energy: {energy}")
        print("How many times to mine?")
        print("1) Once")
        print("2) Five times")
        print("3) Ten times")
        print("4) Until out of energy")
        print("0) Back")
        
        choice = input("> ")
        if choice == '0':
            return
            
        count = 0
        if choice == '1':
            count = 1
        elif choice == '2':
            count = 5
        elif choice == '3':
            count = 10
        elif choice == '4':
            count = energy // 5  # 5 energy per mine
        else:
            print(f"{Color.RED}Invalid choice{Color.END}")
            return
            
        if count <= 0:
            print(f"{Color.RED}Cannot mine that many times{Color.END}")
            return
            
        max_possible = energy // 5
        if count > max_possible:
            print(f"{Color.YELLOW}Only enough energy for {max_possible} mines{Color.END}")
            count = max_possible
        
        drill_speed = self.drill_speeds.get(drill, 0.5)
        
        self.clear_screen()
        print(f"{Color.BLUE}Mining in progress...{Color.END}")
        
        for i in range(count):
            # Calculate weighted probability
            total_weight = sum(ore["weight"] for ore in unlocked_ores)
            r = random.uniform(0, total_weight)
            cumulative = 0
            selected_ore = unlocked_ores[0]
            
            for ore in unlocked_ores:
                cumulative += ore["weight"]
                if r <= cumulative:
                    selected_ore = ore
                    break
            
            # Random events (10% chance)
            if random.random() < 0.1:
                event_type = random.choice(["bonus", "energy", "double", "empty"])
                if event_type == "bonus":
                    coins = random.randint(1, 10)
                    self.data.add("coins", coins)
                    print(f"{Color.GREEN}Found a small treasure! +{coins} coins{Color.END}")
                elif event_type == "energy":
                    e_gain = random.randint(5, 15)
                    self.data.add("energy", e_gain)
                    print(f"{Color.GREEN}Found an energy crystal! +{e_gain} energy{Color.END}")
                elif event_type == "double":
                    print(f"{Color.GREEN}Found a double deposit!{Color.END}")
                    self.data.update_inventory(selected_ore["name"], 1)  # Double ore
                elif event_type == "empty":
                    print(f"{Color.RED}Hit a empty patch. Nothing found.{Color.END}")
                    # Still costs energy but no ore
            
            # Add ore to inventory
            self.data.update_inventory(selected_ore["name"], 1)
            
            # Use energy
            self.data.add("energy", -5)
            self.data.add("drills_used")
            
            print(f"[{i+1}/{count}] Found: {selected_ore['color']}{selected_ore['name']}{Color.END}")
            time.sleep(drill_speed)
        
        # Summary
        print(f"\n{Color.GREEN}Mining complete!{Color.END}")
        print(f"Energy remaining: {self.data.get('energy')}/{self.data.get('max_energy')}")
    
    def show_shop(self):
        while True:
            self.clear_screen()
            self.display_header()
            
            print(f"\n{Color.BLUE}SHOP{Color.END}")
            print("1) Buy Upgrades")
            print("2) Sell Ores")
            print("3) Rest (Recover Energy)")
            print("0) Back")
            
            choice = input("> ")
            
            if choice == '1':
                self.show_upgrades()
            elif choice == '2':
                self.sell_ores()
            elif choice == '3':
                self.rest()
            elif choice == '0':
                break
            else:
                print(f"{Color.RED}Invalid choice{Color.END}")
    
    def show_upgrades(self):
        while True:
            self.clear_screen()
            self.display_header()
            
            coins = self.data.get("coins")
            luck = self.data.get("luck")
            drill = self.data.get("drill")
            max_energy = self.data.get("max_energy")
            
            next_luck_cost = self.luck_cost(luck)
            next_energy_cost = self.energy_cost(max_energy // 100)
            
            drills = list(self.drill_costs.keys())
            current_drill_index = drills.index(drill)
            next_drill = None
            next_drill_cost = None
            
            if current_drill_index < len(drills) - 1:
                next_drill = drills[current_drill_index + 1]
                next_drill_cost = self.drill_costs[next_drill]
            
            print(f"\n{Color.BLUE}UPGRADES{Color.END}")
            print(f"Available coins: {coins}")
            
            print("\n1) Upgrade Luck")
            if luck < 20:
                print(f"   Current: {luck}/20 | Cost: {next_luck_cost} coins")
            else:
                print(f"   {Color.GREEN}MAXED{Color.END}")
                
            print("\n2) Upgrade Drill")
            if next_drill:
                print(f"   Current: {drill}")
                print(f"   Next: {next_drill} | Cost: {next_drill_cost} coins")
            else:
                print(f"   {Color.GREEN}MAXED{Color.END}")
                
            print("\n3) Upgrade Energy Capacity")
            print(f"   Current: {max_energy} | Cost: {next_energy_cost} coins")
            
            print("\n0) Back")
            
            choice = input("> ")
            
            if choice == '1' and luck < 20:
                # Upgrade luck
                if coins >= next_luck_cost:
                    self.data.add("coins", -next_luck_cost)
                    self.data.add("luck")
                    print(f"{Color.GREEN}Luck upgraded to {luck + 1}!{Color.END}")
                    
                    # Check for newly unlocked ores
                    new_luck = luck + 1
                    new_ores = [ore for ore in self.ores if ore["min_luck"] == new_luck]
                    
                    if new_ores:
                        print(f"{Color.BLUE}New ores unlocked:{Color.END}")
                        for ore in new_ores:
                            print(f"- {ore['color']}{ore['name']}{Color.END}")
                else:
                    print(f"{Color.RED}Not enough coins{Color.END}")
                self.wait_for_key()
                
            elif choice == '2' and next_drill:
                # Upgrade drill
                if coins >= next_drill_cost:
                    self.data.add("coins", -next_drill_cost)
                    self.data.set("drill", next_drill)
                    print(f"{Color.GREEN}Drill upgraded to {next_drill}!{Color.END}")
                else:
                    print(f"{Color.RED}Not enough coins{Color.END}")
                self.wait_for_key()
                
            elif choice == '3':
                # Upgrade energy
                if coins >= next_energy_cost:
                    self.data.add("coins", -next_energy_cost)
                    new_max = max_energy + 25
                    self.data.set("max_energy", new_max)
                    self.data.set("energy", new_max)  # Refill on upgrade
                    print(f"{Color.GREEN}Energy capacity upgraded to {new_max}!{Color.END}")
                else:
                    print(f"{Color.RED}Not enough coins{Color.END}")
                self.wait_for_key()
                
            elif choice == '0':
                break
                
            else:
                print(f"{Color.RED}Invalid choice{Color.END}")
                self.wait_for_key()
    
    def sell_ores(self):
        inventory = self.data.get("inventory", {})
        
        if not inventory:
            print(f"{Color.RED}No ores to sell{Color.END}")
            self.wait_for_key()
            return
            
        while True:
            self.clear_screen()
            self.display_header()
            
            total_value = 0
            ore_values = {}
            
            print(f"\n{Color.BLUE}SELL ORES{Color.END}")
            print("Your inventory:")
            
            # Find ore info and calculate values
            for i, (ore_name, count) in enumerate(inventory.items(), 1):
                ore_info = next((ore for ore in self.ores if ore["name"] == ore_name), None)
                if ore_info:
                    value = count * ore_info["price"]
                    total_value += value
                    ore_values[ore_name] = value
                    print(f"{i}) {ore_info['color']}{ore_name}{Color.END}: {count} (Value: {value} coins)")
            
            print(f"\nTotal value: {total_value} coins")
            print("\nOptions:")
            print("1) Sell all ores")
            print("2) Sell specific ore")
            print("0) Back")
            
            choice = input("> ")
            
            if choice == '1':
                # Sell all
                if total_value > 0:
                    self.data.add("coins", total_value)
                    for ore_name in list(inventory.keys()):
                        inventory[ore_name] = 0
                    self.data.set("inventory", {})
                    print(f"{Color.GREEN}Sold all ores for {total_value} coins{Color.END}")
                else:
                    print(f"{Color.RED}No ores to sell{Color.END}")
                self.wait_for_key()
                break
                
            elif choice == '2':
                # Sell specific
                print("\nEnter the number of the ore to sell:")
                try:
                    ore_idx = int(input("> ")) - 1
                    ore_names = list(inventory.keys())
                    if 0 <= ore_idx < len(ore_names):
                        ore_name = ore_names[ore_idx]
                        count = inventory[ore_name]
                        value = ore_values[ore_name]
                        
                        self.data.add("coins", value)
                        inventory.pop(ore_name)
                        self.data.set("inventory", inventory)
                        
                        print(f"{Color.GREEN}Sold {count} {ore_name} for {value} coins{Color.END}")
                    else:
                        print(f"{Color.RED}Invalid selection{Color.END}")
                except ValueError:
                    print(f"{Color.RED}Invalid input{Color.END}")
                self.wait_for_key()
                
            elif choice == '0':
                break
                
            else:
                print(f"{Color.RED}Invalid choice{Color.END}")
                self.wait_for_key()
    
    def rest(self):
        energy = self.data.get("energy")
        max_energy = self.data.get("max_energy")
        
        if energy >= max_energy:
            print(f"{Color.YELLOW}Energy already full!{Color.END}")
        else:
            gain = max_energy // 4
            new_energy = min(energy + gain, max_energy)
            self.data.set("energy", new_energy)
            print(f"{Color.GREEN}Rested and recovered {gain} energy.{Color.END}")
            print(f"Energy: {new_energy}/{max_energy}")
        
        self.wait_for_key()
    
    def show_inventory(self):
        inventory = self.data.get("inventory", {})
        
        self.clear_screen()
        self.display_header()
        
        print(f"\n{Color.BLUE}INVENTORY{Color.END}")
        
        if not inventory:
            print("Empty")
        else:
            total_value = 0
            for ore_name, count in inventory.items():
                ore_info = next((ore for ore in self.ores if ore["name"] == ore_name), None)
                if ore_info:
                    value = count * ore_info["price"]
                    total_value += value
                    print(f"{ore_info['color']}{ore_name}{Color.END}: {count} (Value: {value} coins)")
            
            print(f"\nTotal value: {total_value} coins")
        
        # Show available ores
        luck = self.data.get("luck")
        print(f"\n{Color.BLUE}AVAILABLE ORES:{Color.END}")
        current_ores = [ore for ore in self.ores if ore["min_luck"] <= luck]
        for ore in current_ores:
            print(f"- {ore['color']}{ore['name']}{Color.END} (Value: {ore['price']} coins)")
        
        next_ore = next((ore for ore in self.ores if ore["min_luck"] > luck), None)
        if next_ore:
            print(f"\nNext ore at luck {next_ore['min_luck']}: {next_ore['color']}{next_ore['name']}{Color.END}")
        
        self.wait_for_key()
    
    def show_stats(self):
        self.clear_screen()
        self.display_header()
        
        print(f"\n{Color.BLUE}STATS{Color.END}")
        print(f"Total mines: {self.data.get('drills_used', 0)}")
        
        drills = list(self.drill_costs.keys())
        current_drill = self.data.get("drill")
        drill_idx = drills.index(current_drill)
        drill_progress = f"{drill_idx + 1}/{len(drills)}"
        
        luck = self.data.get("luck")
        luck_progress = f"{luck}/20"
        
        print(f"Luck progress: {luck_progress}")
        print(f"Drill progress: {drill_progress}")
        
        self.wait_for_key()
    
    def show_settings(self):
        while True:
            self.clear_screen()
            self.display_header()
            
            print(f"\n{Color.BLUE}SETTINGS{Color.END}")
            print("1) Change miner name")
            print("2) Reset game")
            print("0) Back")
            
            choice = input("> ")
            
            if choice == '1':
                print("\nEnter new miner name:")
                new_name = input("> ").strip()
                if new_name:
                    self.data.set("name", new_name)
                    print(f"{Color.GREEN}Name changed to {new_name}{Color.END}")
                else:
                    print(f"{Color.YELLOW}Name unchanged{Color.END}")
                self.wait_for_key()
                
            elif choice == '2':
                print(f"{Color.RED}WARNING: This will delete all progress!{Color.END}")
                print("Type 'reset' to confirm:")
                confirm = input("> ")
                
                if confirm.lower() == 'reset':
                    self.data.reset()
                    print(f"{Color.GREEN}Game reset complete{Color.END}")
                    self.wait_for_key()
                    return True  # Signal game reset
                else:
                    print("Reset cancelled")
                self.wait_for_key()
                
            elif choice == '0':
                break
                
            else:
                print(f"{Color.RED}Invalid choice{Color.END}")
                self.wait_for_key()
        
        return False
    
    def main_loop(self):
        while True:
            self.clear_screen()
            self.display_header()
            
            print("\nMAIN MENU:")
            print("1) Mine")
            print("2) Inventory")
            print("3) Shop")
            print("4) Stats")
            print("5) Settings")
            print("0) Exit")
            
            choice = input("> ")
            
            if choice == '1':
                self.mine()
            elif choice == '2':
                self.show_inventory()
            elif choice == '3':
                self.show_shop()
            elif choice == '4':
                self.show_stats()
            elif choice == '5':
                if self.show_settings():
                    # Reset happened, reinitialize
                    self.__init__()
            elif choice == '0':
                print(f"{Color.GREEN}Thanks for playing!{Color.END}")
                break
            else:
                print(f"{Color.RED}Invalid choice{Color.END}")
                self.wait_for_key()

def main():
    try:
        game = MiningGame()
        game.main_loop()
    except KeyboardInterrupt:
        print("\nGame interrupted. Saving progress...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        print("Game exited.")

if __name__ == "__main__":
    main()
