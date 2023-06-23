import json, requests
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
    return json.load(open(json_file))

def recipe_set(product_data):
    recipe = product_data["recipe"]
    print(recipe)
    materials_set = {
        material.split(':')[0] for material in recipe.values() if material.split(':')[0] != ''
    }
    return materials_set

def is_it_in_yet(product, product_data, bazaar_json):
    # print("no")
    if 'recipe' in product_data and product in bazaar_json["products"]:
        # print("yes")
        recipe = product_data["recipe"]
        materials_set = recipe_set(product_data)
        if all(material in bazaar_json["products"] for material in materials_set):
            print("Yes")
            return True
    return False

def main():
    hypixel_bazaar_api = "https://api.hypixel.net/skyblock/bazaar"
    hypixel_recipes_json = "InternalNameMappings.json"

    bazaar_json = connection_info(hypixel_bazaar_api)
    product_names = get_names(bazaar_json)
    recipes = read_json(hypixel_recipes_json)
    
    num = 0
    for product, product_data in recipes.items():
        if is_it_in_yet(product, product_data, bazaar_json):
            print("It is working")
        else:
            print("It is not")

main()