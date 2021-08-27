from typing import List
from . import resources

CRAFTING_NAMESPACE = 'dt.crafting:'
INV_SORT_NAMESPACE = 'dt.inv_sort:'
item_ids = resources.get_items(strip_prefix=True)

def __update_tagged_blocks_for_group(name: str, groups: dict) -> list:
    """Gets a list of blocks for the given group, expanding referenced groups"""
    additional = []
    prefix = "#minecraft:"
    for value in groups[name]:
        if value.find(prefix) == 0:
            sub_key = value[len(prefix):]
            if sub_key in groups:
                additional = additional + __update_tagged_blocks_for_group(value[len(prefix):], groups)
            else:
                print('tag not found:', sub_key, 'in group:', name)
    groups[name] = [value for value in groups[name] if value.find(prefix) == -1]
    groups[name] = groups[name] + additional
    return groups[name]

def __read_existing_groups() -> dict:
    """Reads builtin JSON tag files as a dictionary"""
    groups = {}
    for tag_path, tag_dict in resources.get_item_tags():
        group_name = tag_path.stem
        groups[group_name] = tag_dict['values']
    
    for name in groups:
        __update_tagged_blocks_for_group(name, groups)
    return groups


def __contains_any_keyword(id: str, keywords: list) -> bool:
    """Returns whether any of the keywords in the list are a substring of the given string"""
    return any([keyword in id for keyword in keywords])


def string_matches_terms(string: str, and_list: List[List[str]]) -> bool:
    if not and_list:
        return False
    for or_list in and_list:
        if not any([keyword in string for keyword in or_list]):
            return False
    return True


def __create_or_append_group(name, groups, all_items, partial_matches = [], and_or_lists = [], exact_matches = [], partial_filter_out = []) -> None:
    """Create a new block group by filtering the list of all blocks"""
    filtered = [id for id in all_items if __contains_any_keyword(id, partial_matches)]
    filtered = filtered + [id for id in all_items if string_matches_terms(id, and_or_lists)]
    filtered = filtered + [id for id in all_items if id in exact_matches]
    filtered = [id for id in filtered if not __contains_any_keyword(id, partial_filter_out)]
    if name not in groups:
        groups[name] = []
    
    deduplicated = groups[name]
    for id in filtered:
        if not id in deduplicated:
            deduplicated.append(id)
    groups[name] = deduplicated


def __build_custom_groups(custom_prefix=''):
    new_groups = {}
    
    # mining
    mining_partials = ['ore', 'dirt', 'cobblestone']
    mining_types = ['cobblestone', 'andesite', 'diorite', 'granite', 'gravel', 'iron', 'gold','diamond','emerald','netherite','quartz','coal','flint','redstone', 'stone','blackstone', 'basalt', 'deepslate', 'copper', 'nether_brick', 'sandstone', 'red_sandstone']
    mining_forms = ['ingot','scrap', 'nugget']
    and_list = [mining_types, mining_forms]
    __create_or_append_group('mining', new_groups, item_ids, partial_matches=mining_partials, and_or_lists=and_list, exact_matches=mining_types)

    # mining_products
    mining_forms = ['block','stairs','slab','wall', 'bricks','smooth','cut']
    and_list = [mining_types, mining_forms]
    
    __create_or_append_group('mining_products', new_groups, item_ids, and_or_lists=and_list)
    __create_or_append_group('mining_products', new_groups, item_ids, and_or_lists=[['polished','chiseled'],mining_types])
    
    # plantables
    plantable_partials = [
        'sapling', 'seed', 'flower', 'bean','cactus', 'grass', 'fern', 'bush', 
        'stem, berries','tulip','rose', 'poppy', 'orchid','beetroot', 'kelp', 'lilac'
        ]
    plantable_whole = [
        'potato', 'sugar_cane','red_mushroom','brown_mushroom','azure_bluet','dandelion'
        ]
    partial_filter_out = ['baked', '_pot','soup', 'block']
    __create_or_append_group('plantables', new_groups, item_ids, partial_matches=plantable_partials, exact_matches=plantable_whole, partial_filter_out=partial_filter_out)

    # consumables
    consumables_partials = ['baked','apple', 'beef', 'chicken', 'cod', 'mutton','pork', 'stew', 'soup','melon','pumpkin', 'fish', 'pufferfish', 'salmon']
    consumables_wholes = ['wheat', 'rabbit','cooked_rabbit','bread','cookie','cake','egg']
    __create_or_append_group('consumables', new_groups, item_ids, partial_matches=consumables_partials, exact_matches=consumables_wholes, partial_filter_out=['seed','spawn', 'bucket','carved', 'fishing'])
    
    wood_types = [
        'dark_oak',
        'oak',
        'acacia',
        'birch',
        'jungle',
        'spruce',
        'crimson'
    ]
    wood_forms = ['log','planks','leaves','wood']
    wood_product_forms = ['stairs','slab','trapdoor','sign','pressure_plate','boat','door','fence','button']
    and_list = [wood_types, wood_forms]
    __create_or_append_group('woods', new_groups, item_ids, and_or_lists=and_list)
    and_list = [wood_types, wood_product_forms]
    __create_or_append_group('wood_products', new_groups, item_ids, and_or_lists=and_list, exact_matches=['barrel', 'chest','trapped_chest'])
    

    # tools
    tools_partials = ['pickaxe','shovel','_axe','hoe','fishing_rod', 'shears', 'flint_and_steel']
    __create_or_append_group('tools',new_groups, item_ids, partial_matches=tools_partials)
    
    # weapons
    weapons_partials = ['shield','sword','bow','arrow','trident']
    weapons_out = ['bowl']
    __create_or_append_group('weapons', new_groups, item_ids,partial_matches=weapons_partials, partial_filter_out=weapons_out)
    
    # armor
    armor_partials = ['leggings','helmet','chestplate','armor', 'boots']
    __create_or_append_group('armor',new_groups, item_ids, partial_matches=armor_partials,partial_filter_out=['armor_stand'])

    # Add back the minecraft: prefix
    for name in new_groups:
        new_groups[name] = ['minecraft:' + id for id in new_groups[name]]

    for name in new_groups:
        __update_tagged_blocks_for_group(name, new_groups)
    return new_groups

def __format_as_dict(groups, group_name_prefix=''):
    output_object = {'groups':[]}
    for name in groups:
            output_object['groups'].append({'group': group_name_prefix + name, 'values': groups[name]})
    return output_object

def get_item_tags_storage_dict():
    existing_groups = __read_existing_groups()

    all_groups = existing_groups
    new_groups = __build_custom_groups()

    groups_dict = __format_as_dict(all_groups, group_name_prefix='minecraft:')
    return groups_dict

def get_custom_item_tags_storage_dict(group_prefix=''):
    existing_groups = __read_existing_groups()
    all_groups = existing_groups
    new_groups = __build_custom_groups()

    groups_dict = __format_as_dict(all_groups, group_name_prefix='minecraft:')
    custom_groups_dict = __format_as_dict(new_groups, group_name_prefix=group_prefix)
    return custom_groups_dict