'''
---DISCLAIMER---
ALL EQUATIONS IS PROVIDED BY aguy5235 IN DISCORD WITH https://www.desmos.com/calculator/qbqqylyvvi
THIS SCRIPT IS PROVIDED BY iicookie IN DISCORD (me)
ALL STATS IS COLLECTED FROM WIKI https://desktopdefender.miraheze.org/wiki/Main_Page
'''


import json
import math

def load_json_file(file_path):
    """
    Reads a JSON file and returns its contents.
    
    Args:
        file_path (str): Path to the JSON file.
        
    Returns:
        dict: The parsed JSON data, or None if an error occurs.
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {file_path}.")
        return None

def damage_percent(level):
    return 0.0000103078 * level**3 - 0.00309212 * level**2 + 0.309199 * level - 0.306333

def flat_damage(level):
    return (50 / 49) * level - 50 / 49

def damage_mult(level):
    if level < 4:
        return 1
    elif level < 10:
        return 1.2
    elif level < 21:
        return 1.2 ** 2
    else:
        return 1.2 ** 3

def damage(level, weapon_damage, weapon_added_mult, damage_level, flat_level, loot_percentage, loot_damage):
    return (weapon_damage * (1 + damage_percent(damage_level) + loot_percentage) +
            (flat_damage(flat_level) + loot_damage) * weapon_added_mult) * damage_mult(level)

def firerate_upgrade(level):
    return (7.73341e-7) * level**3 - 0.000231949 * level**2 + 0.0231915 * level - 0.0229862

def firerate(weapon_firerate, firerate_level, loot_firerate):
    return (1 / weapon_firerate) * (1 - (firerate_upgrade(firerate_level) + loot_firerate))

def projectiles_per_shot(extra_projectile_level, loot_projectile):
    return 1 + math.ceil((extra_projectile_level - 1) * 1.5) + loot_projectile

def total_damage_per_shot(level, weapon_damage, weapon_added_mult, damage_level, flat_level, loot_percentage, loot_damage, extra_projectile_level, loot_projectile):
    return damage(level, weapon_damage, weapon_added_mult, damage_level, flat_level, loot_percentage, loot_damage) * projectiles_per_shot(extra_projectile_level, loot_projectile)

def get_weapon_damage(weapon):
    """
    Returns the damage value of a single weapon.
    
    Args:
        weapon (dict): A dictionary containing weapon stats.
        
    Returns:
        float: The damage value of the weapon, or 0 if not found.
    """
    return weapon.get('stats', {}).get('Damage', 0)

def get_weapon_added_mult(weapon):
    """
    Returns the added damage multiplier for a weapon.
    Returns 0.1 for Flamethrower, 1 for all other weapons.
    
    Args:
        weapon (dict): A dictionary containing weapon stats.
        
    Returns:
        float: The added damage multiplier (0.1 for Flamethrower, 1 otherwise).
    """
    if weapon.get('name', '').lower() == 'flamethrower':
        return 0.1
    return weapon.get('stats', {}).get('Added Damage Mult', 1)

def get_loot_percentage(loots):
    """
    Calculates the sum of projectile damage percentages from multiple loot objects.
    
    Args:
        loots (list): A list of loot dictionaries.
        
    Returns:
        float: Sum of projectile damage percentages.
    """
    total_percentage = 0
    for loot in loots:
        total_percentage += loot.get('stats', {}).get('Projectile Damage', 0)
    return total_percentage

def get_loot_damage(loots):
    """
    Calculates the sum of shot damage from multiple loot objects.
    
    Args:
        loots (list): A list of loot dictionaries.
        
    Returns:
        float: Sum of shot damage values.
    """
    total_damage = 0
    for loot in loots:
        total_damage += loot.get('stats', {}).get('Shot Damage', 0)
    return total_damage

def get_loot_projectile(loots):
    """
    Calculates the sum of projectile shot counts from multiple loot objects.
    
    Args:
        loots (list): A list of loot dictionaries.
        
    Returns:
        int: Sum of projectile shot counts.
    """
    total_projectiles = 0
    for loot in loots:
        total_projectiles += loot.get('stats', {}).get('Projectile Shot', 0)
    return total_projectiles

def get_weapon_fire_rate(weapon):
    """
    Returns the fire rate value of a single weapon.
    
    Args:
        weapon (dict): A dictionary containing weapon stats.
        
    Returns:
        float: The fire rate value of the weapon, or 0 if not found.
    """
    return weapon.get('stats', {}).get('Fire Rate', 0)

def get_loot_fire_rate(loots):
    """
    Calculates the sum of fire rate percentages from multiple loot objects.
    
    Args:
        loots (list): A list of loot dictionaries.
        
    Returns:
        float: Sum of fire rate percentages.
    """
    total_fire_rate = 0
    for loot in loots:
        total_fire_rate += loot.get('stats', {}).get('Fire Rate', 0)
    return total_fire_rate

def string_to_weapon(weapon_string):
    weapon = next((w for w in weapons_data['weapons'] if w['name'].lower() == weapon_string.lower()), None)
    return weapon

def stringList_to_loot(loot_string_list):
    """
    Converts a list of loot names to a list of loot dictionaries, allowing duplicates.
    
    Args:
        loot_string_list (list): List of loot names (case-insensitive).
        
    Returns:
        list: List of loot dictionaries, including duplicates as specified.
    """
    selected_loots = []
    for loot_name in loot_string_list:
        # Search for the loot in each rarity tier
        for rarity in ['B', 'C', 'D', 'E']:
            loot = next((l for l in loot_data['loot'][rarity] if l['name'].lower() == loot_name.lower()), None)
            if loot:
                selected_loots.append(loot)
                break  # Found the loot, move to the next loot name
    return selected_loots

if __name__ == "__main__":
    # Load JSON files
    weapons_data = load_json_file('weapons.json')
    loot_data = load_json_file('loot.json')

    if not (weapons_data and loot_data):
        print("Failed to load JSON files. Exiting.")
        exit(1)

    # Get user input
    weapon_name = input("Enter the weapon name: ").strip()
    loot_input = input("Enter the list of loot names (separated by /): ").strip()
    loot_names = [name.strip() for name in loot_input.split('/') if name.strip()]

    # Convert inputs to data
    weapon = string_to_weapon(weapon_name)
    if not weapon:
        print(f"Error: Weapon '{weapon_name}' not found.")
        exit(1)

    selected_loots = stringList_to_loot(loot_names)
    if not selected_loots and loot_names:
        print("Warning: No valid loot items found. Proceeding with empty loot list.")

    # Hard-coded levels (based on commented code)
    level = 30
    damage_level = 100
    flat_level = 50
    extra_projectile_level = 3
    firerate_level = 100

    # Calculate stats
    weapon_damage = get_weapon_damage(weapon)
    weapon_added_mult = get_weapon_added_mult(weapon)
    loot_percentage = get_loot_percentage(selected_loots)
    loot_damage = get_loot_damage(selected_loots)
    loot_projectile = get_loot_projectile(selected_loots)
    weapon_firerate = get_weapon_fire_rate(weapon)
    loot_firerate = get_loot_fire_rate(selected_loots)

    # Perform calculations
    dmg = damage(level, weapon_damage, weapon_added_mult, damage_level, flat_level, loot_percentage, loot_damage)
    proj = projectiles_per_shot(extra_projectile_level, loot_projectile)
    fr = firerate(weapon_firerate, firerate_level, loot_firerate)
    total_dmg = total_damage_per_shot(level, weapon_damage, weapon_added_mult, damage_level, flat_level, loot_percentage, loot_damage, extra_projectile_level, loot_projectile)

    # Print results
    print(f"Damage: {dmg:.2f}")
    print(f"Projectiles per Shot: {proj}")
    print(f"Firerate: {fr:.2f}")
    print(f"Total Damage per Shot: {total_dmg:.2f}")