import json, requests, collections
from time import sleep

def connection_info(bazaar_api):
    response = requests.get(bazaar_api)

    if response.status_code != 200:
        print("There was an error connecting to the server.")
        sleep(1)
        print("Try again later.")
        exit()
    else:
        print("Connecting to the server... ")
        sleep(1)
        print("Connections successful.")
        return response.json()
    
def get_names(bazaar_json):
    return [product_name for product_name in bazaar_json["products"]]

def read_json(json_file):
    return json.load(open(json_file, 'r', encoding = 'utf-8'))

def recipe_set(product_data):
    recipe = product_data["recipe"]
    materials_set = {
        material.split(':')[0] for material in recipe.values() if isinstance(material, str) and material.split(':')[0] != ''
    }
    return materials_set

def is_it_in_yet(product, product_data, bazaar_json):
    if 'recipe' in product_data and product in bazaar_json["products"]:
        materials_set = recipe_set(product_data)
        if all(material in bazaar_json["products"] for material in materials_set):
            # print(materials_set)
            return True
    return False

def recipe_cost(product_data, bazaar_json):
    total = 0
    for material in product_data['recipe'].values():
        if material != "":
            item, quantity = material.split(':')
            total += float(bazaar_json["products"][item]["buy_summary"][0]["pricePerUnit"]) * float(quantity)
    return total

def print_output(item, amount):

    print(f"Product Name: {item[0]}\nProduct Profit: {item[1]["product_profit"]}")
    
    

def main():
    hypixel_bazaar_api = "https://api.hypixel.net/skyblock/bazaar"
    hypixel_recipes_json = "InternalNameMappings.json"

    bazaar_json = connection_info(hypixel_bazaar_api)
    product_names = get_names(bazaar_json)
    recipes = read_json(hypixel_recipes_json)
    
    items = {}
    num = 0
    for product, product_data in recipes.items():
        # print(product)
        if is_it_in_yet(product, product_data, bazaar_json):
            num += 1
            # print(product, "True", num)
            # print(product)
            # num += 1
            # print("n: ", num)
            # print(bazaar_json["products"][product])
            # null buy/sell order arrays cause list out of index because of "['buy_summary'][0]" "
            product_price = 0 if len(bazaar_json["products"][product]["buy_summary"]) == 0 else float(bazaar_json["products"][product]["buy_summary"][0]["pricePerUnit"])
            product_recipe_cost = recipe_cost(product_data, bazaar_json)

            processed_items = {
                'product_name' : product,
                'product_profit' : product_price - product_recipe_cost,
                'product_price' : product_price,
                'recipe_cost' : product_recipe_cost,
                'recipe' : product_data['recipe']
            }

            items[product] = processed_items
            # print(len(items))
            # od = collections.OrderedDict(sorted(items.items()))
    
        
            # print(f"Product: {product_price}")
            # print(f"Product Cost: {product_recipe_cost}")
            # print(f"Profift: {product_price - product_recipe_cost}")
    
    sorted_dict = dict(sorted(items.items(), key=lambda item: item[1]['product_profit'], reverse = True))
    for i in sorted_dict.items():
        print(i)

main()

# {
# 'name': 'Absolute Ender Pearl', 
# 'recipe': {
#   'A1': '', 
#   'A2': 'ENCHANTED_ENDER_PEARL:16', 
#   'A3': '', 
#   'B1': 'ENCHANTED_ENDER_PEARL:16', 
#   'B2': 'ENCHANTED_ENDER_PEARL:16', 
#   'B3': 'ENCHANTED_ENDER_PEARL:16', 
#   'C1': '', 
#   'C2': 'ENCHANTED_ENDER_PEARL:16', 
#   'C3': ''}, 
# 'wiki': 'https://wiki.hypixel.net/Absolute_Ender_Pearl', 
# 'base_rarity': 'RARE'
# }