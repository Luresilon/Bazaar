import requests
import re
from mojang import API
from nbt.nbt import NBTFile, TAG_List, TAG_Compound
from io import BytesIO
import base64


class HypixelBazaarData:
    def __init__(self):
        self.hypixel_api_key = "0000"  # Insert your Hypixel API key here
        self.bazaar_api_url = "https://api.hypixel.net/skyblock/bazaar"
        self.hypixel_profile_url = "https://api.hypixel.net/skyblock/profiles"
        self.api = API()

    def get_player_data(self, username: str) -> dict:

        """
        Retrieve player data from the Hypixel API.

        Args:
            username (str): The Minecraft username of the player.

        Returns:
            dict: The player's data.
        """

        uuid = self.api.get_uuid(username)
        request_link = f"{self.hypixel_profile_url}?key={self.hypixel_api_key}&uuid={uuid}"
        player_data = requests.get(request_link).json()
        return player_data

    def decode_nbt(self, raw: str) -> NBTFile:
        
        """
        Decode a gzipped and base64 decoded string to an NBT object.

        Args:
            raw (str): The raw NBT data.

        Returns:
            NBTFile: The NBT object.
        """
        return NBTFile(fileobj=BytesIO(base64.b64decode(raw)))

    def unpack_nbt(self, tag: NBTFile) -> dict:
        
        """
        Unpack an NBT tag into a native Python data structure.

        Args:
            tag (NBT tag): The NBT tag.

        Returns:
            dict: The unpacked data structure. (can be any)
        """

        if isinstance(tag, TAG_List):
            return [self.unpack_nbt(i) for i in tag.tags]
        elif isinstance(tag, TAG_Compound):
            return {i.name: self.unpack_nbt(i) for i in tag.tags}
        else:
            return tag.value

    def retrieve_item_data(self, username: str, index: int) -> dict:
        
        """
        Retrieve data for an item from the player's inventory.

        Args:
            username (str): The Minecraft username of the player.
            index (int): The index of the item in the player's inventory.

        Returns:
            dict: The item data.
        """

        player_data = self.get_player_data(username)

        nbt_data = player_data["profiles"][1]["members"]["3e230fba3f5e448bacc7bafd4ef5b44a"]["inv_contents"]["data"]
        nbt_object = self.decode_nbt(nbt_data)
        native_python_object = self.unpack_nbt(nbt_object)
        print(native_python_object)

        item_ench_data = None if "enchantments" not in native_python_object["i"][index]["tag"]["ExtraAttributes"] else native_python_object["i"][index]["tag"]["ExtraAttributes"]["enchantments"]
        item_potato_count = 0 if "hot_potato_count" not in native_python_object["i"][index]["tag"]["ExtraAttributes"] else native_python_object["i"][index]["tag"]["ExtraAttributes"]["hot_potato_count"]
        item_name = native_python_object["i"][index]["tag"]["display"]["Name"]

        return [item_ench_data, item_potato_count, item_name]

    def convert_to_enchant_query(self, item_data: dict) -> list:
        """
        Convert item enchantments to a list of enchantment queries for the bazaar.
        Note: Avoid untrackable legacy enchantment 'Telekenesis'

        Args:
            item_data (dict): The item data containing enchantments.

        Returns:
            list: A list of enchantment queries.
        """

        enchantments = []
        for key, value in item_data.items():
            if key != "telekinesis":
                enchantment_query = f"ENCHANTMENT_{key.upper()}_{value}"
                enchantments.append(enchantment_query)
        return enchantments

    def get_enchantment_prices(self, bazaar_json: dict, enchantment_queries: list) -> dict:
        """
        Retrieve prices for enchantments from the bazaar data.

        Args:
            bazaar_json (dict): The bazaar data.
            enchantment_queries (list): A list of enchantment queries.

        Returns:
            dict: A dictionary containing enchantment prices.
        """

        enchantment_prices = {}
        for query in enchantment_queries:
            if query in bazaar_json["products"]:
                buy_summary = bazaar_json["products"][query].get("buy_summary", [])
                if buy_summary:
                    price_per_unit = buy_summary[0]["pricePerUnit"]
                    enchantment_prices[query] = price_per_unit
        return enchantment_prices

    def print_item_costs(self, item_data: dict, bazaar_json: dict):
        """
        Print the cost of an item including enchantments and hot potato books.

        Args:
            item_data (dict): The item data.
            bazaar_json (dict): The bazaar data.
        """

        name = re.sub('§\d+', '', item_data[2])
        hot_potato_count = item_data[1]
        enchantment_data = item_data[0]

        hot_potato_price = hot_potato_count * bazaar_json["products"]["HOT_POTATO_BOOK"]["sell_summary"][0]["pricePerUnit"]

        enchantment_queries = self.convert_to_enchant_query(enchantment_data)
        enchantment_prices = self.get_enchantment_prices(bazaar_json, enchantment_queries)
        sorted_enchantment_prices = sorted(enchantment_prices.items(), key=lambda x: x[1], reverse=True)

        total_enchantment_cost = sum(enchantment_prices.values())

        print(f"{'-'*40}\n{name}\n{'-'*40}")
        for enchantment, price in sorted_enchantment_prices:
            print(f"{enchantment:<30}{'->':^5}{price:<10,.2f}")

        print(f"\n{'Enchantment Cost(s):':<20}{'Total:':^5}{total_enchantment_cost:<10,.2f}")
        print(f"{'Hot Potato(s) Cost:':<20}{'Total:':^5}{hot_potato_price:<10,.2f}")
        print(f"\n{'Grand Total:':<20}{'Total:':^5}{total_enchantment_cost + hot_potato_price:<10,.2f}")


def main():
    bazaar_data = HypixelBazaarData()
    bazaar_json = requests.get(bazaar_data.bazaar_api_url).json()
    item_data = bazaar_data.retrieve_item_data("Tigropod", 0)
    bazaar_data.print_item_costs(item_data, bazaar_json)


if __name__ == "__main__":
    main()