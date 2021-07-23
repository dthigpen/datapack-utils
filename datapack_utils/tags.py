from . import resources

CRAFTING_NAMESPACE = 'dt.crafting:'
INV_SORT_NAMESPACE = 'dt.inv_sort:'
item_ids = resources.get_items(strip_prefix=True)

def update_tagged_blocks_for_group(name: str, groups: dict) -> list:
    """Gets a list of blocks for the given group, expanding referenced groups"""
    additional = []
    prefix = "#minecraft:"
    for value in groups[name]:
        if value.find(prefix) == 0:
            sub_key = value[len(prefix):]
            if sub_key in groups:
                additional = additional + update_tagged_blocks_for_group(value[len(prefix):], groups)
            else:
                print('tag not found:', sub_key, 'in group:', name)
    groups[name] = [value for value in groups[name] if value.find(prefix) == -1]
    groups[name] = groups[name] + additional
    return groups[name]

def read_existing_groups() -> dict:
    """Reads builtin JSON tag files as a dictionary"""
    groups = {}
    for tag_path, tag_dict in resources.get_item_tags():
        group_name = tag_path.stem
        groups[group_name] = tag_dict['values']
    
    for name in groups:
        update_tagged_blocks_for_group(name, groups)
    return groups


def contains_keyword(id: str, keywords: list) -> bool:
    """Returns whether any of the keywords in the list are a substring of the given string"""
    return any([keyword in id for keyword in keywords])


def create_group(name, groups, all_items, partial_matches = [], exact_matches = [], partial_filter_out = []) -> None:
    """Create a new block group by filtering the list of all blocks"""
    filtered = [id for id in all_items if contains_keyword(id, partial_matches)]
    filtered = filtered + [id for id in all_items if id in exact_matches]
    filtered = [id for id in filtered if not contains_keyword(id, partial_filter_out)]
    deduplicated = []
    for id in filtered:
        if not id in deduplicated:
            deduplicated.append(id)
    groups[name] = deduplicated

def build_id_variants(start_list: list, end_list: list) -> list:
    """Build a list of strings by combining each element in two lists with an underscore"""
    variants = []
    for start in start_list:
        for end in end_list:
            joiner = '_' if len(start) > 0 and len(end) > 0 else ''
            variants.append(start + joiner + end)
    return variants

def build_custom_groups():
    new_groups = {}
    
    # mining group
    mining_partials = ['ore']
    mining_exact = ['cobblestone', 'andesite', 'diorite']
    
    mining_types = ['cobblestone', 'andesite', 'diorite', 'granite', 'gravel', 'iron', 'gold','diamond','emerald','netherite','quartz','coal','redstone']
    mining_forms = ['block','ingot','scrap','']
    mining_exact = build_id_variants(mining_types, mining_forms)
    
    create_group('mining', new_groups, item_ids, exact_matches=mining_exact)

    # Plantables
    plantable_partials = [
        'sapling', 'seed', 'flower', 'bean','cactus', 'grass', 'fern', 'bush', 
        'stem, berries','tulip','rose', 'poppy', 'orchid','beetroot', 'kelp', 'lilac'
        ]
    plantable_whole = [
        'potato', 'sugar_cane','red_mushroom','brown_mushroom','azure_bluet','dandelion'
        ]
    create_group('plantables', new_groups, item_ids, plantable_partials, plantable_whole, ['baked', '_pot','soup', 'block'])
    
    # Consumables
    consumables_partials = ['baked','apple', 'beef', 'chicken', 'cod', 'mutton','pork', 'stew', 'soup','melon','pumpkin']
    consumables_wholes = ['wheat', 'rabbit','cooked_rabbit','bread','cookie','cake']
    create_group('consumables', new_groups, item_ids, consumables_partials, consumables_wholes,['seed','spawn', 'bucket','carved'])
    


    wood_types = [
        'dark_oak',
        'oak',
        'acacia',
        'birch',
        'jungle',
        'spruce'
    ]
    wood_forms = ['log','planks','leaves','wood']
    wood_product_forms = ['stairs','slab','trapdoor','sign','pressure_plate','boat','door','fence']
    woods_partials = build_id_variants(wood_types, wood_forms)
    wood_product_partials = build_id_variants(wood_types, wood_product_forms)
    create_group('woods', new_groups, item_ids, woods_partials)
    create_group('wood_products', new_groups, item_ids, wood_product_partials)

    # tools
    tools_partials = ['pickaxe','shovel','_axe','hoe','fishing_rod']
    create_group('tools',new_groups, item_ids, tools_partials)
    # weapons
    weapons_partials = ['shield','sword','bow','arrow','trident']
    weapons_out = ['bowl']
    create_group('weapons', new_groups, item_ids,weapons_partials,[], weapons_out)
    
    # Add back the minecraft: prefix
    for name in new_groups:
        new_groups[name] = ['minecraft:' + id for id in new_groups[name]]

    for name in new_groups:
        update_tagged_blocks_for_group(name, new_groups)
    return new_groups

def format_as_dict(groups, group_name_prefix=''):
    output_object = {'groups':[]}
    for name in groups:
            output_object['groups'].append({'group': group_name_prefix + name, 'values': groups[name]})
    return output_object

def get_item_tags_storage_dict():
    existing_groups = read_existing_groups()

    # all_groups = {**existing_groups, **new_groups}
    all_groups = existing_groups
    new_groups = build_custom_groups()

    groups_dict = format_as_dict(all_groups, group_name_prefix='minecraft:')
    return groups_dict

def get_custom_item_tags_storage_dict():
    existing_groups = read_existing_groups()
    all_groups = existing_groups
    new_groups = build_custom_groups()

    groups_dict = format_as_dict(all_groups, group_name_prefix='minecraft:')
    custom_groups_dict = format_as_dict(new_groups, group_name_prefix='minecraft:')
    return custom_groups_dict