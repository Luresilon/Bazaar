import json
import requests
from time import sleep

class HypixelBazaarAnalyser:
    def __init__(self):
        pass

    def connect_to_server(self, bazaar_api: str) -> dict:
        """
        Connect to the Hypixel Bazaar API.

        Args:
        - bazaar_api (str): The URL of the Hypixel Bazaar API.

        Returns:
        - dict: The JSON response containing bazaar data.
        """
        response = requests.get(bazaar_api)

        if response.status_code != 200:
            print("[INFO] There was an error connecting to the server.")
            sleep(1)
            print("[INFO] Try again later.")
            exit()
        else:
            print("[INFO] Connecting to the server... ")
            sleep(1)
            print("[INFO] Connections successful.")
            return response.json()

    def get_recipe_set(self, product_data: dict) -> dict:
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

    def is_product_available(self, product: str, product_data: dict, bazaar_json: dict) -> dict:
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

    def calculate_recipe_cost(self, product_data: dict, bazaar_json: dict, buy_price: str) -> float:
        """
        Calculate the cost of a product's recipe.

        Args:
        - product_data (dict): Data of the product including recipe information.
        - bazaar_json (dict): JSON data from the bazaar API.
        - buy_price (str): Price of a material within the recipe.

        Returns:
        - float: The total cost of the product's recipe.
        """
        total = 0
        for material in product_data['recipe'].values():
            if material != "":
                item, quantity = material.split(':')
                total += float(bazaar_json["products"][item]["quick_status"][buy_price]) * float(quantity)
        return total

    def print_top_products(self, profit_json: dict, top_n: int=10):
        """
        Print top N products sorted by profit in descending order.

        Args:
        - profit_json (dict): Dictionary containing product profit information.
        - top_n (int): Number of top products to print (default is 10).
        """
        print(f"\n{'Product Name:':_<34}{'Product Profit:':_<30}{'Recipe Price:':_<30}{'Product Buy Volume:':_<26}")

        count = 0
        for entry in profit_json.values():
            print(f"{str(count + 1) + '.':<4}{entry.get('product_name', '_') :_<30}{entry.get('product_profit', '_') :_<30,.2f}{entry.get('recipe_cost', '_') :_<30,.2f}{entry.get('buy_volume', '_') :_<26}")
            count += 1
            if count == top_n:
                break

    def json_dump(self, current_bazaar_prices: dict, recipes: dict, insta_buy: bool, insta_sell: bool, min_buy_volume: int, analyzer) -> dict:
        """
        Generate JSON data for products with calculated profits.

        Args:
        - current_bazaar_prices (dict): JSON data containing current prices in the bazaar. Keys represent product names and values contain information about the products, including their prices.
        - recipes (dict): JSON data containing recipes for various products. Keys represent product names and values contain recipe information for each product.
        - analyzer (HypixelBazaarAnalyzer): An instance of the HypixelBazaarAnalyzer class (or any other analyzer class) containing methods to analyze the data.

        Returns:
        - dict: A dictionary containing product information, including product name, profit, price, recipe cost, and recipe details. The dictionary is sorted based on product profit in descending order.
        """
        #If we insta sell the product, then use the price of sellPrice, otherwise use buyPrice
        sell_price = 'sellPrice' if insta_sell else 'buyPrice'
        buy_price = 'buyPrice' if insta_buy else 'sellPrice'


        items = {}
        for product, product_data in recipes.items():
            if analyzer.is_product_available(product, product_data, current_bazaar_prices):
                buy_volume = current_bazaar_prices["products"][product]["quick_status"]["buyVolume"]
                if(buy_volume < min_buy_volume): continue
                product_price = 0 if len(current_bazaar_prices["products"][product]["buy_summary"]) == 0 else float(current_bazaar_prices["products"][product]["quick_status"][sell_price])
                product_recipe_cost = analyzer.calculate_recipe_cost(product_data, current_bazaar_prices, buy_price)

                processed_items = {
                    'product_name' : product,
                    'product_profit' : product_price - product_recipe_cost,
                    'product_price' : product_price,
                    'recipe_cost' : product_recipe_cost,
                    'recipe' : product_data['recipe'],
                    'buy_volume' : buy_volume
                    }

                items[product] = processed_items

        sorted_items = dict(sorted(items.items(), key=lambda item: item[1]['product_profit'], reverse=True))
        return sorted_items

def main():
    analyzer = HypixelBazaarAnalyser()
    HYPIXEL_BAZAAR_API = "https://api.hypixel.net/skyblock/bazaar"
    HYPIXEL_RECIPES_JSON = "db\InternalNameMappings.json"

    current_bazar_prices = analyzer.connect_to_server(HYPIXEL_BAZAAR_API)
    recipes = json.load(open(HYPIXEL_RECIPES_JSON, 'r', encoding='utf-8'))

    #Change parameters here:
    #_____________________________________________#
    num_of_products = 10
    insta_buy = True
    insta_sell = False
    min_buy_volume = 0
    #_____________________________________________#
    
    print("_" * 120)
    print("[INFO] CURRENT CONFIGURATIONS:")
    print(f"[INFO] Recipe: {'INSTA-BUY' if insta_buy == True else 'NORM-BUY'}")
    print(f"[INFO] Product: {'INSTA-SELL' if insta_sell == True else 'NORM-SELL'}")
    print(f"[INFO] Num of Entries: {num_of_products}")
    print(f"[INFO] Minimum Buy Volume: {min_buy_volume}")
    print("_" * 120)

    items = analyzer.json_dump(current_bazar_prices, recipes, insta_buy, insta_sell, min_buy_volume, analyzer)
    analyzer.print_top_products(items, num_of_products) #can add num_of_products for how many entries you want (10 by default)

if __name__ == "__main__":
    main()