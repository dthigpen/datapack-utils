from collections import namedtuple
from dataclasses import dataclass
from dataclasses import field
from string import Template
from typing import NamedTuple

#{"jformat":7,"jobject":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"font":null,"color":"dark_red","insertion":"","click_event_type":0,"click_event_value":"","hover_event_type":0,"hover_event_value":"","hover_event_object":{},"hover_event_children":[],"text":"Error: "},{"bold":true,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"font":null,"color":"none","insertion":"","click_event_type":0,"click_event_value":"","hover_event_type":0,"hover_event_value":"","hover_event_object":{},"hover_event_children":[],"text":"$pretty_name"},{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"font":null,"color":"none","insertion":"","click_event_type":0,"click_event_value":"","hover_event_type":0,"hover_event_value":"","hover_event_object":{},"hover_event_children":[],"text":" requires "},{"bold":true,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"font":null,"color":"none","insertion":"","click_event_type":0,"click_event_value":"","hover_event_type":0,"hover_event_value":"","hover_event_object":{},"hover_event_children":[],"text":"$dep_pretty_name "},{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"font":null,"color":"none","insertion":"","click_event_type":0,"click_event_value":"","hover_event_type":0,"hover_event_value":"","hover_event_object":{},"hover_event_children":[],"text":"$dep_major.$dep_minor"}],"command":"/tellraw @p %s","jtemplate":"tellraw"}
DEPENDENCY_NOT_FOUND_MSG = 'tellraw @p ["",{"text":"Error: ","color":"dark_red"},{"text":"$pretty_name","bold":true}," requires ",{"text":"$dep_pretty_name ","bold":true},"$dep_major.$dep_minor"]'
#{"jformat":7,"jobject":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"font":null,"color":"dark_red","insertion":"","click_event_type":0,"click_event_value":"","hover_event_type":0,"hover_event_value":"","hover_event_object":{},"hover_event_children":[],"text":"Error: "},{"bold":true,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"font":null,"color":"none","insertion":"","click_event_type":0,"click_event_value":"","hover_event_type":0,"hover_event_value":"","hover_event_object":{},"hover_event_children":[],"text":"$pretty_name"},{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"font":null,"color":"none","insertion":"","click_event_type":0,"click_event_value":"","hover_event_type":0,"hover_event_value":"","hover_event_object":{},"hover_event_children":[],"text":" expected "},{"bold":true,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"font":null,"color":"none","insertion":"","click_event_type":0,"click_event_value":"","hover_event_type":0,"hover_event_value":"","hover_event_object":{},"hover_event_children":[],"text":"$dep_pretty_name "},{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"font":null,"color":"none","insertion":"","click_event_type":0,"click_event_value":"","hover_event_type":0,"hover_event_value":"","hover_event_object":{},"hover_event_children":[],"text":"$dep_major.$dep_minor"},{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"font":null,"color":"none","insertion":"","click_event_type":0,"click_event_value":"","hover_event_type":0,"hover_event_value":"","hover_event_object":{},"hover_event_children":[],"text":" but found "},{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"font":null,"color":"none","insertion":"","click_event_type":0,"click_event_value":"","hover_event_type":0,"hover_event_value":"","hover_event_object":{},"hover_event_children":[],"score_name":"$$$$$dep_load_name.version.major","score_objective":"load.status","score_value":null},{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"font":null,"color":"none","insertion":"","click_event_type":0,"click_event_value":"","hover_event_type":0,"hover_event_value":"","hover_event_object":{},"hover_event_children":[],"text":"."},{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"font":null,"color":"none","insertion":"","click_event_type":0,"click_event_value":"","hover_event_type":0,"hover_event_value":"","hover_event_object":{},"hover_event_children":[],"score_name":"$$$$$dep_load_name.version.minor","score_objective":"load.status","score_value":null}],"command":"/tellraw @p %s","jtemplate":"tellraw"}
DEPENDENCY_WRONG_VERSION_MSG = 'tellraw @p ["",{"text":"Error: ","color":"dark_red"},{"text":"$pretty_name","bold":true}," expected ",{"text":"$dep_pretty_name ","bold":true},"$dep_major.$dep_minor"," but found ",{"score":{"name":"$$$dep_load_name.version.major","objective":"load.status"}},".",{"score":{"name":"$$$dep_load_name.version.minor","objective":"load.status"}}]'

dependency_template = Template(
        f'''# check for $dep_pretty_name datapack
execute unless score $$$dep_load_name load.status matches 1 run {DEPENDENCY_NOT_FOUND_MSG}
scoreboard players set $$dt.tmp.dep load.status 0
execute if score $$$dep_load_name.version.major load.status matches $dep_major if score $$$dep_load_name.version.minor load.status matches $dep_minor.. run scoreboard players set $$dt.tmp.dep load.status 1
execute if score $$$dep_load_name load.status matches 1 unless score $$dt.tmp.dep load.status matches 1 run {DEPENDENCY_WRONG_VERSION_MSG}
execute if score $$$dep_load_name load.status matches 1 unless score $$dt.tmp.dep load.status matches 1 run scoreboard players set $$$load_name load.status 0

''')



def coordinate_range(min_coord: tuple[int, int, int], max_coord: tuple[int, int, int]):
    for x in range(min_coord[0], max_coord[0] + 1):
        for y in range(min_coord[1], max_coord[1] + 1):
            for z in range(min_coord[2], max_coord[2] + 1):
                yield (x, y, z)



@dataclass
class Pack:

    @dataclass
    class Version:
        major: int
        minor: int
        patch: int = 0
    
    name: str
    load_name: str
    tick_function: str = None
    version: Version = None
    dependencies: list = field(default_factory=list)

    


def setup_versioning(pack_info: Pack):
    output = ''

    # If a version was specified output it
    
    if pack_info.version:
        output += f'''
scoreboard players set ${pack_info.load_name}.version.major load.status {pack_info.version.major}
scoreboard players set ${pack_info.load_name}.version.minor load.status {pack_info.version.minor}
scoreboard players set ${pack_info.load_name}.version.patch load.status {pack_info.version.patch}

'''
    output += f'scoreboard players set ${pack_info.load_name} load.status 1\n\n'

    for dep in pack_info.dependencies:
        output += dependency_template.substitute(
            pretty_name=pack_info.name, load_name=pack_info.load_name, dep_pretty_name=dep.name, dep_load_name=dep.load_name, dep_major=dep.version.major, dep_minor=dep.version.minor)
    
    if pack_info.dependencies:
        output += 'scoreboard players reset $dt.tmp.dep load.status\n'
    
    if pack_info.tick_function:
        output += '# Only tick if successfully loaded\n'
        output += f'schedule clear {pack_info.tick_function}\n'
        output += f'execute if score ${pack_info.load_name} load.status matches 1 run schedule function {pack_info.tick_function} 1t replace'
    return output