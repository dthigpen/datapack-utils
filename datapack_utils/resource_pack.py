import json

import minecraft_data

def build_font_lang_file():
    translations = {}
    for item in minecraft_data.get_items_with_chars():
        translations[f'minecraft:{item["name"]}'] = f'{item["char"]}'

    with open('en_us.json','w') as f:
        json.dump(translations, f, indent=4)

def build_font_provider_file():
    providers = []
    for item in minecraft_data.get_items_with_chars():
        
        providers.append({
            "type": "bitmap",
            "file": f"minecraft:items/{item['name']}.png",
            "ascent": 8,
            "height": 10,
            "chars": [item['char']]
        })
        # providers[-1]['chars'][0] = "\\" + providers[-1]['chars'][0]

    with open('items.json','w') as f:
        json.dump({"providers":providers}, f, indent=4)
        

if __name__ == "__main__":
    build_font_provider_file()
    build_font_lang_file()