import json
import requests
from time import sleep

class HypixelBazaarAnalyzer:
    def __init__(self):
        pass

    def connect_to_server(self, bazaar_api):
        """
        Connect to the Hypixel Bazaar API.

        Args:
        - bazaar_api (str): The URL of the Hypixel Bazaar API.

        Returns:
        - dict: The JSON response containing bazaar data.
        """
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

    def get_recipe_set(self, product_data):
        """
        Extract unique materials from a product's recipe.

        Args:
        - product_data (dict): Data of the product including recipe information.

        Returns:
        - set: Set of unique materials in the recipe.
        """
        recipe = product_data["recipe"]
        materials_set = {
            material.split(':')[0] for material in recipe.values() if isinstance(material, str) and material.split(':')[0] != ''
        }
        return materials_set

    def is_product_available(self, product, product_data, bazaar_json):
        """
        Check if all materials required for a product are available in the bazaar.

        Args:
        - product (str): Name of the product.
        - product_data (dict): Data of the product including recipe information.
        - bazaar_json (dict): JSON data from the bazaar API.

        Returns:
        - bool: True if the product is available, False otherwise.
        """
        if 'recipe' in product_data and product in bazaar_json["products"]:
            materials_set = self.get_recipe_set(product_data)
            if all(material in bazaar_json["products"] for material in materials_set):
                return True
        return False

    def calculate_recipe_cost(self, product_data, bazaar_json):
        """
        Calculate the cost of a product's recipe.

        Args:
        - product_data (dict): Data of the product including recipe information.
        - bazaar_json (dict): JSON data from the bazaar API.

        Returns:
        - float: The total cost of the product's recipe.
        """
        total = 0
        for material in product_data['recipe'].values():
            if material != "":
                item, quantity = material.split(':')
                total += float(bazaar_json["products"][item]["buy_summary"][0]["pricePerUnit"]) * float(quantity)
        return total

    def print_top_products(self, profit_json, top_n=10):
        """
        Print top N products sorted by profit in descending order.

        Args:
        - profit_json (dict): Dictionary containing product profit information.
        - top_n (int): Number of top products to print (default is 10).
        """
        print(f"\n{'Product Name:':_<30}{'Product Profit:':_<30}{'Recipe Price:':_<30}{'Buy Volume:':_<15}")

        count = 0
        for entry in profit_json.values():
            print(f"{entry.get('product_name', '_') :_<30}{entry.get('product_profit', '_') :_<30,.2f}{entry.get('recipe_cost', '_') :_<30,.2f}{entry.get('buy_volume', '_') :_<15}")
            count += 1
            if count == top_n:
                break

    def json_dump(self, current_bazaar_prices: dict, recipes: dict, analyzer) -> dict:
        """
        Generate JSON data for products with calculated profits.

        Args:
        - current_bazaar_prices (dict): JSON data containing current prices in the bazaar. Keys represent product names and values contain information about the products, including their prices.
        - recipes (dict): JSON data containing recipes for various products. Keys represent product names and values contain recipe information for each product.
        - analyzer (HypixelBazaarAnalyzer): An instance of the HypixelBazaarAnalyzer class (or any other analyzer class) containing methods to analyze the data.

        Returns:
        - dict: A dictionary containing product information, including product name, profit, price, recipe cost, and recipe details. The dictionary is sorted based on product profit in descending order.
        """

        items = {}
        for product, product_data in recipes.items():
            if analyzer.is_product_available(product, product_data, current_bazaar_prices):
                product_price = 0 if len(current_bazaar_prices["products"][product]["buy_summary"]) == 0 else float(current_bazaar_prices["products"][product]["quick_status"]["sellPrice"])
                product_recipe_cost = analyzer.calculate_recipe_cost(product_data, current_bazaar_prices)

                processed_items = {
                    'product_name' : product,
                    'product_profit' : product_price - product_recipe_cost,
                    'product_price' : product_price,
                    'recipe_cost' : product_recipe_cost,
                    'recipe' : product_data['recipe'],
                    'buy_volume' : current_bazaar_prices["products"][product]["quick_status"]["buyMovingWeek"]
                    }

                items[product] = processed_items

        sorted_items = dict(sorted(items.items(), key=lambda item: item[1]['product_profit'], reverse=True))
        return sorted_items

def main():
    analyzer = HypixelBazaarAnalyzer()
    HYPIXEL_BAZAAR_API = "https://api.hypixel.net/skyblock/bazaar"
    HYPIXEL_RECIPES_JSON = "InternalNameMappings.json"
    top_n = 10

    current_bazar_prices = analyzer.connect_to_server(HYPIXEL_BAZAAR_API)
    recipes = json.load(open(HYPIXEL_RECIPES_JSON, 'r', encoding='utf-8'))

    items = analyzer.json_dump(current_bazar_prices, recipes, analyzer)
    print(f"{'_':_<90}\n[INFO] CURRENT CONFIGURATIONS:\n[INFO] Recipe: INSTA-BUY\n[INFO] Product: NORMAL-SELL\n[INFO] Num of Entries: {top_n}\n{'_':_<90}")
    analyzer.print_top_products(items, top_n) #can add top_n for how many entries you want (10 by default)

if __name__ == "__main__":
    main()