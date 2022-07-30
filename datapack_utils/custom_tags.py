from os import name

from datapack_utils import resources

ALL_ITEM_IDS = [item['name'] for item in resources.get_items()]

def __update_tagged_blocks_for_group(name: str, tags_dict: dict) -> list:
    """Gets a list of blocks for the given group, expanding referenced groups"""
    additional = []
    for value in tags_dict[name]:
        if value in tags_dict:
            print(f'found nested tag: {value}')
            additional = additional + __update_tagged_blocks_for_group(value, tags_dict)
    tags_dict[name] = tags_dict[name] + additional
    return tags_dict[name]


def __contains_any_keyword(id: str, keywords: list) -> bool:
    """Returns whether any of the keywords in the list are a substring of the given string"""
    return any([keyword in id for keyword in keywords])


def string_matches_terms(string: str, and_list: list[list[str]]) -> bool:
    if not and_list:
        return False
    for or_list in and_list:
        if not any([keyword in string for keyword in or_list]):
            return False
    return True


def __create_or_append_group(name, tags_dict, all_items, partial_matches = [], and_or_lists = [], exact_matches = [], partial_filter_out = []) -> None:
    """Create a new block group by filtering the list of all blocks"""
    filtered = [id for id in all_items if __contains_any_keyword(id, partial_matches)]
    filtered = filtered + [id for id in all_items if string_matches_terms(id, and_or_lists)]
    filtered = filtered + [id for id in all_items if id in exact_matches]
    filtered = [id for id in filtered if not __contains_any_keyword(id, partial_filter_out)]
    if name not in tags_dict:
        tags_dict[name] = []
    
    tag_values = tags_dict[name]
    for id in filtered:
        if not id in tag_values:
            tag_values.append(id)
    tags_dict[name] = tag_values


def __build_custom_groups():
    new_tags = {}
    
    # mining
    mining_partials = ['ore', 'dirt', 'cobblestone']
    mining_types = ['cobblestone', 'andesite', 'diorite', 'granite', 'gravel', 'iron', 'gold','diamond','emerald','netherite','quartz','coal','flint','redstone', 'stone','blackstone', 'basalt', 'deepslate', 'copper', 'nether_brick', 'sandstone', 'red_sandstone']
    mining_forms = ['ingot','scrap', 'nugget']
    and_list = [mining_types, mining_forms]
    __create_or_append_group('mining', new_tags, ALL_ITEM_IDS, partial_matches=mining_partials, and_or_lists=and_list, exact_matches=mining_types)

    # mining_products
    mining_forms = ['block','stairs','slab','wall', 'bricks','smooth','cut']
    and_list = [mining_types, mining_forms]
    
    __create_or_append_group('mining_products', new_tags, ALL_ITEM_IDS, and_or_lists=and_list)
    __create_or_append_group('mining_products', new_tags, ALL_ITEM_IDS, and_or_lists=[['polished','chiseled'],mining_types])
    
    # plantables
    plantable_partials = [
        'sapling', 'seed', 'flower', 'bean','cactus', 'grass', 'fern', 'bush', 
        'stem, berries','tulip','rose', 'poppy', 'orchid','beetroot', 'kelp', 'lilac'
        ]
    plantable_whole = [
        'potato', 'sugar_cane','red_mushroom','brown_mushroom','azure_bluet','dandelion'
        ]
    partial_filter_out = ['baked', '_pot','soup', 'block']
    __create_or_append_group('plantables', new_tags, ALL_ITEM_IDS, partial_matches=plantable_partials, exact_matches=plantable_whole, partial_filter_out=partial_filter_out)

    # consumables
    consumables_partials = ['baked','apple', 'beef', 'chicken', 'cod', 'mutton','pork', 'stew', 'soup','melon','pumpkin', 'fish', 'pufferfish', 'salmon']
    consumables_wholes = ['wheat', 'rabbit','cooked_rabbit','bread','cookie','cake','egg']
    __create_or_append_group('consumables', new_tags, ALL_ITEM_IDS, partial_matches=consumables_partials, exact_matches=consumables_wholes, partial_filter_out=['seed','spawn', 'bucket','carved', 'fishing'])
    
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
    __create_or_append_group('woods', new_tags, ALL_ITEM_IDS, and_or_lists=and_list)
    and_list = [wood_types, wood_product_forms]
    __create_or_append_group('wood_products', new_tags, ALL_ITEM_IDS, and_or_lists=and_list, exact_matches=['barrel', 'chest','trapped_chest'])
    

    # tools
    tools_partials = ['pickaxe','shovel','_axe','hoe','fishing_rod', 'shears', 'flint_and_steel']
    __create_or_append_group('tools',new_tags, ALL_ITEM_IDS, partial_matches=tools_partials)
    
    # weapons
    weapons_partials = ['shield','sword','bow','arrow','trident']
    weapons_out = ['bowl']
    __create_or_append_group('weapons', new_tags, ALL_ITEM_IDS,partial_matches=weapons_partials, partial_filter_out=weapons_out)
    
    # armor
    armor_partials = ['leggings','helmet','chestplate','armor', 'boots']
    __create_or_append_group('armor',new_tags, ALL_ITEM_IDS, partial_matches=armor_partials,partial_filter_out=['armor_stand'])

    # Add back the minecraft: prefix
    for name in new_tags:
        new_tags[name] = ['minecraft:' + id for id in new_tags[name]]

    for name in new_tags:
        __update_tagged_blocks_for_group(name, new_tags)
    return new_tags

def get_custom_tags_dict(strip_namespace=False):
    new_tags = __build_custom_groups()
    if strip_namespace:
        for name in new_tags:
            new_tags[name] = [value[len('minecraft:'):] for value in new_tags[name]]
    return new_tags

def get_custom_tags(strip_namespace=False):
    new_tags_dict = get_custom_tags_dict(strip_namespace)
    new_tags_list = [{'name':key, 'values':value} for key,value in new_tags_dict.items()]
    return new_tags_list


def get_all_tags_dict():
    return resources.get_tags_dict() | get_custom_tags_dict()