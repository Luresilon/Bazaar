import requests, io, base64, re
from mojang import API
from nbt.nbt import TAG_List, TAG_Compound, NBTFile

#{
# 'modifier': 'gentle', 
# 'id': 'ASPECT_OF_THE_END', 
# 'enchantments': {'knockback': 2}, 
# 'uuid': '1b58e677-db19-4197-a581-b26248e16f0c', 
# 'timestamp': '5/31/23 8:11 AM'
# }
#
#{
# 'hot_potato_count': 10, 
# 'gems': {'unlocked_slots': ['SAPPHIRE_0', 'SAPPHIRE_1'], 
# 'SAPPHIRE_0': {'uuid': '9b4bfa8e-820e-4cf4-a7b2-ab386b2584a5', 'quality': 'FLAWLESS'}, 
# 'SAPPHIRE_1': {'uuid': '5b77a002-259d-409a-bc60-63579d552ae5', 'quality': 'FLAWLESS'}}, 
# 'modifier': 'heroic', 
# 'id': 'RUNIC_STAFF', 
# 'boss_tier': 2, 
# 'enchantments': {'impaling': 3, 'luck': 6, 'smite': 6, 'looting': 4, 'scavenger': 4, 'ender_slayer': 6, 'experience': 3, 'vampirism': 6, 'cubism': 5, 'execute': 5, 'giant_killer': 6}, 
# 'uuid': '40660639-93cf-4286-8412-b63f5740f41e', 'timestamp': '6/14/23 7:21 AM'
# }


def decode_nbt(raw):
    """
    Decode a gziped and base64 decoded string to an NBT object
    """

    return NBTFile(fileobj=io.BytesIO(base64.b64decode(raw)))


def unpack_nbt(tag):
    """
    Unpack an NBT tag into a native Python data structure.
    Taken from https://github.com/twoolie/NBT/blob/master/examples/utilities.py
    """

    

    if isinstance(tag, TAG_List):
        return [unpack_nbt(i) for i in tag.tags]
    elif isinstance(tag, TAG_Compound):
        return dict((i.name, unpack_nbt(i)) for i in tag.tags)
    else:
        return tag.value

def get_json(user):
    """
    Retrieve Json format data of a player.
    """

    api = API()

    uuid = api.get_uuid(user)
    hypixel_api = "4057db46-1129-4054-a362-bce3fd866c41"

    request_link = str("https://api.hypixel.net/skyblock/profiles?key=" + hypixel_api + "&uuid=" + uuid)
    player_data = requests.get(request_link).json()

    return player_data

def retrieve_item(index):

    """
    Open API link and retrieve enchantments of the item on the first slot of the
    utility bar.

    TO DO: Add Optional for enchants or other
    """
    username = "Tigropod"
    player_data = get_json(username)

    nbt_data = player_data["profiles"][1]["members"]["3e230fba3f5e448bacc7bafd4ef5b44a"]["inv_contents"]["data"]

    nbt_object = decode_nbt(nbt_data)
    native_python_object = unpack_nbt(nbt_object)

    item_ench_data = None if "enchantments" not in native_python_object["i"][index]["tag"]["ExtraAttributes"] else native_python_object["i"][index]["tag"]["ExtraAttributes"]["enchantments"]
    item_potato_count = 0 if "hot_potato_count" not in native_python_object["i"][index]["tag"]["ExtraAttributes"] else native_python_object["i"][index]["tag"]["ExtraAttributes"]["hot_potato_count"]
    item_name = native_python_object["i"][index]["tag"]["display"]["Name"]

    return [item_ench_data, item_potato_count, item_name]

def convert_to_query(item_data):
    """
    Convert json format into list of enchantments for bazaar query
    """
    enchants = []
    print(item_data.items())
    for key, value in item_data.items():
        if key != "telekinesis":
            string = "ENCHANTMENT_" + key.upper() + "_" + str(value)
            enchants.append(string)
    return enchants

def get_enchant_prices(bazaar_json, data_to_bazaar):
    """
    Print enchants and their corresponding prioces.
    """
    ench_prices = {}
    for ench in data_to_bazaar:
        if len(bazaar_json["products"][ench]["buy_summary"]) != 0:
            price_per_unit = bazaar_json["products"][ench]["buy_summary"][0]["pricePerUnit"]
            ench_prices[ench] = price_per_unit
        else:
            continue
    return ench_prices

def print_out(lst, bazaar_json):
    """
    Print out the cost sum of the item nicely.

    Print format: ENCHNATMENT_IMPLAING_3   ->  1,122,503.30
    """
    name = re.sub('§\d+', '', lst[2])
    potato_count = lst[1]
    ench_data = lst[0]

    # print(potato_count)
    if potato_count <= 10:
        hot_potato_sum = potato_count * bazaar_json["products"]["HOT_POTATO_BOOK"]["sell_summary"][0]["pricePerUnit"]
    else:
        hot_potato_sum = 10 * bazaar_json["products"]["HOT_POTATO_BOOK"]["sell_summary"][0]["pricePerUnit"]
        hot_potato_sum = (potato_count - 10) * bazaar_json["products"]["FUMING_POTATO_BOOK"]["sell_summary"][0]["pricePerUnit"]


    if ench_data != None:
        data_to_bazaar = convert_to_query(ench_data)
        sorted_enchant_prices = sorted(get_enchant_prices(bazaar_json, data_to_bazaar).items(), key=lambda x: x[1], reverse=True)

        ench_total = 0
        print(f"{'-'*40}\n{name}\n{'-'*40}")
        
        for key, value in sorted_enchant_prices:
            print(f"{key : <30}{'->' : ^5}{value : <10,.2f}")
            ench_total += value
    else:
        ench_total = 0
        
    
    print(f"\n{'Enchants Sum:  ' : <20}{':' : ^5}{ench_total : <10,.2f}")
    print(f"{'Hot Potato Sum: ' : <20}{':' : ^5}{hot_potato_sum : <10,.2f}")
    print(f"\n{'Total: ' : <20}{':' : ^5}{ench_total + hot_potato_sum: <10,.2f}")


    return 0

requestlink = str("https://api.hypixel.net/skyblock/bazaar")

bazaar_json = requests.get(requestlink).json()

index = 3
item_data = retrieve_item(index)

print_out(item_data, bazaar_json)
# username = "Tigropod"
# player_data = get_json(username)
# nbt_data = player_data["profiles"][1]["members"]["3e230fba3f5e448bacc7bafd4ef5b44a"]["inv_contents"]["data"]

# nbt_object = decode_nbt(nbt_data)
# native_python_object = unpack_nbt(nbt_object)
# print(native_python_object["i"][index]["tag"]["ExtraAttributes"])