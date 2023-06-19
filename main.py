import requests, io, base64
from mojang import API
from nbt.nbt import TAG_List, TAG_Compound, NBTFile


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
    hypixel_api = "e11bb6a7-129a-488c-8d43-cccaea9ec763"

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

    item_ench_data = native_python_object["i"][index]["tag"]["ExtraAttributes"]["enchantments"]
    item_potato_count = native_python_object["i"][index]["tag"]["ExtraAttributes"]["hot_potato_count"]
    item_name = native_python_object["i"][index]["tag"]["display"]["Name"]

    return [item_ench_data, item_potato_count, item_name]

def convert_to_query(item_data):
    """
    Convert json format into list of enchantments for bazaar query
    """
    enchants = []
    for key, value in item_data.items():
        if key != "telekinesis":
            string = "ENCHANTMENT_" + key.upper() + "_" + str(value)
            enchants.append(string)
    return enchants

def get_enchant_prices(hypixel_json, data_to_bazaar):
    """
    Print enchants and their corresponding prioces.
    """
    ench_prices = {}
    for ench in data_to_bazaar:
        price_per_unit = 0 if len(hypixel_json["products"][ench]["sell_summary"]) == 0 else hypixel_json["products"][ench]["sell_summary"][0]["pricePerUnit"]
        ench_prices[ench] = price_per_unit
    return ench_prices

def print_out(lst, bazaar_json):
    """
    Print out the cost sum of the item nicely.
    """
    name = lst[2]
    potato_count = lst[1]
    ench_data = lst[0]

    data_to_bazaar = convert_to_query(ench_data)

    total = 0
    print("Name: ", name)
    for key, value in get_enchant_prices(bazaar_json, data_to_bazaar).items():
        print(key, "->", "{:,.2f}".format(value))
        total += value
    print("Sum: {:,.2f}".format(total))

    return 0

requestlink = str("https://api.hypixel.net/skyblock/bazaar")
bazaar_json = requests.get(requestlink).json()

index = 1
item_data = retrieve_item(index)

print_out(item_data, bazaar_json)