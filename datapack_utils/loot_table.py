from . import resources
from copy import deepcopy

SHULKER_TEMPLATE = {
    "type": "minecraft:block",
    "pools": [
        {
            "rolls": 1,
            "entries": [
                {
                    "type": "minecraft:alternatives",
                    "children": [
                        {
                            "type": "minecraft:dynamic",
                            "name": "minecraft:contents",
                            # "functions": [],
                            "conditions": [
                                {
                                    "condition": "minecraft:match_tool",
                                    "predicate": {
                                        "nbt": "{drop_contents:true}"
                                    }
                                }
                            ]
                        },
                        {
                            "type": "minecraft:item",
                            "name": "minecraft:pink_shulker_box",
                            "functions": [
                                {
                                    "function": "minecraft:copy_name",
                                    "source": "block_entity"
                                },
                                {
                                    "function": "minecraft:copy_nbt",
                                    "source": "block_entity",
                                    "ops": [
                                        {
                                            "source": "Lock",
                                            "target": "BlockEntityTag.Lock",
                                            "op": "replace"
                                        },
                                        {
                                            "source": "LootTable",
                                            "target": "BlockEntityTag.LootTable",
                                            "op": "replace"
                                        },
                                        {
                                            "source": "LootTableSeed",
                                            "target": "BlockEntityTag.LootTableSeed",
                                            "op": "replace"
                                        }
                                    ]
                                },
                                {
                                    "function": "minecraft:set_contents",
                                    "type": "minecraft:shulker_box",
                                    "entries": [
                                        {
                                            "type": "minecraft:dynamic",
                                            "name": "minecraft:contents"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}

def get_custom_shulker_loot_table(color='pink', functions=None):
    custom_shulker_loot = deepcopy(SHULKER_TEMPLATE)
    custom_shulker_loot['pools'][0]['entries'][0]['children'][1]['name'] = f'minecraft:{color}_shulker_box'
    if functions is not None:
        custom_shulker_loot['pools'][0]['entries'][0]['children'][0]['functions'] = functions
    return custom_shulker_loot

def get_id_assigning_shulker_loot_table():
    item_template = {
        "function": "minecraft:set_nbt",
        "tag": "{dt:{id:0}}",
        "conditions": [
            {
                "condition": "minecraft:match_tool",
                "predicate": {
                    "items": [
                        "minecraft:air"
                    ]
                }
            }
        ]
    }
    item_entries = []
    for item in resources.get_items():
        if item['name'] != 'air':
            item_entry = deepcopy(item_template)
            item_entry['tag'] = f"{{dt:{{id:{item['id']}, stackSize:{item['stackSize']}}}}}"
            item_entry['conditions'][0]['predicate']['items'][0] = f"minecraft:{item['name']}"
            item_entries.append(item_entry)

    return get_custom_shulker_loot_table(color='pink',functions=item_entries)
