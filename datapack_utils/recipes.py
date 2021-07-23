import json
from pathlib import Path
from string import Template
from typing import List
from typing import Tuple
from . import resources

recipe_template = {
    'ingredients': [],
    'result': {'id': '', 'count': 1},
    'type': ''
}
ingredient_template = {
    'count': 1,
    'slots': []
}

all_items = []

def __shapeless_recipe_to_nbt(result: str, count: int, ingredients: dict) -> dict:
    nbt = recipe_template.copy()
    nbt['result'] = {'id': '', 'count': 1}
    nbt['result']['id'] = result
    nbt['result']['count'] = count
    nbt['type'] = 'shapeless'
    nbt['ingredients'] = []
    for ingredient in ingredients:
        if isinstance(ingredient, list):
            nbt['ingredients'].append(__create_ingredient(ingredient[0], count))
            print(f'{result}: Unable to handle list ingredients. Writing with first ingredient of list')
        else:
            nbt['ingredients'].append(__create_ingredient(ingredient, count))
    return nbt

def __permute_slots(slots: list, cols_cofactor, rows_cofactor) -> list:
    perms = []
    for i in range(rows_cofactor):
        for j in range(cols_cofactor):
            perm = slots.copy()
            for k in range(len(perm)):
                perm[k] += j + i * 3
            perms.append(perm)
    return perms

def __create_ingredient(key: dict, count: int, slot_permutations: list = None):
    nbt = ingredient_template.copy()
    nbt['count'] = count
    if 'item' in key:
        nbt['type'] = 'id'
        nbt['id'] = key['item']
    elif 'tag' in key:
        nbt['type'] = 'tag'
        nbt['tag'] = key['tag']
    else:
        print('ERROR, no item or tag present')
    if slot_permutations:
        nbt['slots'] = slot_permutations
    else:
        nbt.pop('slots')
    return nbt

def __shaped_recipe_to_nbt(result: str, count: int, pattern_rows: list, keys: dict) -> dict:
    nbt = recipe_template.copy()
    nbt['result'] = {'id': '', 'count': 1}
    nbt['result']['id'] = result
    nbt['result']['count'] = count
    nbt['type'] = 'shaped'

    slot = 0
    initial_item_slots = {}
    item_counts = {}
    for row in pattern_rows:
        for symbol in row:
            if symbol in keys:
                if symbol not in initial_item_slots:
                    initial_item_slots[symbol] = []
                initial_item_slots[symbol].append(slot)
                if symbol not in item_counts:
                    item_counts[symbol] = 0
                item_counts[symbol] += 1
        
            slot += 1
        slot += 3 - len(row)
    cols_cofactor = 3 - len(pattern_rows[0]) + 1
    rows_cofactor = 3 - len(pattern_rows) + 1

    ingredients = []
    for symbol in initial_item_slots:
        # if result == 'minecraft:quartz_stairs':
        #     print(initial_item_slots[symbol])
        slots = __permute_slots(initial_item_slots[symbol], cols_cofactor, rows_cofactor)
        count = item_counts[symbol]
        if isinstance(keys[symbol], list):
            keys[symbol] = keys[symbol][0]
            # print(f'{result}: Unable to handle ingredient as list, using first: {keys[symbol]}')
        ingredients.append(__create_ingredient(keys[symbol], count, slots))
    nbt['ingredients'] = ingredients
    return nbt

def get_recipes_storage_dict():
    all_recipes_dict = {
        'recipes': []
    }

    for _,recipe_dict in resources.get_all_recipes():
        # print('Reading ' + recipe_dict)
        if 'result' not in recipe_dict:
            # print('Unsupported recipe: ' + file)
            continue

        nbt = {}
        if recipe_dict['type'] == "minecraft:crafting_shaped":
            # handle shaped crafting
            count = recipe_dict['result']['count'] if 'count' in recipe_dict['result'] else 1
            
            nbt = __shaped_recipe_to_nbt(recipe_dict['result']['item'], count, recipe_dict['pattern'], recipe_dict['key'])
            
        elif recipe_dict['type'] == "minecraft:crafting_shapeless":
            count = recipe_dict['result']['count'] if 'count' in recipe_dict['result'] else 1
            nbt = __shapeless_recipe_to_nbt(recipe_dict['result']['item'], count, recipe_dict['ingredients'])
        else:
            # print('Unsupported recipe type: ' + recipe_dict['type'] +  ' for ' + file)
            continue
        if nbt is not None:
            all_items.append(nbt['result']['id'])
            all_recipes_dict['recipes'].append(nbt)
    return all_recipes_dict

