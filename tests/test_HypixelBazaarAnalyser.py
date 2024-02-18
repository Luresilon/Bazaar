import pytest, sys
sys.path.insert(0, ".")
from src.HypixelBazaarAnalyser import HypixelBazaarAnalyser

@pytest.fixture
def analyzer():
    return HypixelBazaarAnalyser()

# Fixture to provide sample data for testing
@pytest.fixture
def sample_data():
    return {
        "products": {
            "ENCHANTED_ENDER_PEARL": {
                "recipe": {
                    "A1": "",
                    "A2": "ENDER_PEARL:4",
                    "A3": "",
                    "B1": "ENDER_PEARL:4",
                    "B2": "ENDER_PEARL:4",
                    "B3": "ENDER_PEARL:4",
                    "C1": "",
                    "C2": "ENDER_PEARL:4",
                    "C3": ""
                },
                "buy_summary":[
                    {"amount":75,"pricePerUnit":179.8,"orders":1}],
                "quick_status": {
                    "buyPrice": 10,
                    "sellPrice": 20,
                    "buyVolume": 15
                }
            },
            "ENDER_PEARL": {
                "recipe": {
                    "A1": "",
                    "A2": "ENDER_PEARL:1",
                    "A3": "",
                    "B1": "ENDER_PEARL:1",
                    "B2": "ENDER_PEARL:1",
                    "B3": "ENDER_PEARL:1",
                    "C1": "",
                    "C2": "ENDER_PEARL:1",
                    "C3": ""
                },
                "buy_summary":[
                    {"amount":75,"pricePerUnit":179.8,"orders":1}]
                ,
                "quick_status": {
                    "buyPrice": 15,
                    "sellPrice": 25,
                    "buyVolume": 15
                }
            }
        }
    }

# Test cases for HypixelBazaarAnalyser class
class TestHypixelBazaarAnalyser:
    
    # Test connect_to_server method
    def test_connect_to_server(self, analyzer):
        bazaar_api = "https://api.hypixel.net/skyblock/bazaar"
        data = analyzer.connect_to_server(bazaar_api)
        assert isinstance(data, dict)
        assert "products" in data
    
    # Test get_recipe_set method
    def test_get_recipe_set(self, analyzer):
        sample_product_data = {
            "recipe": {
                "A1": "item1:32",
                "A2": "item2:32"
            }
        }
        materials_set = analyzer.get_recipe_set(sample_product_data)
        assert isinstance(materials_set, set)
        assert "item1" in materials_set
        assert "item2" in materials_set
    
    # Test is_product_available method
    def test_is_product_available(self, analyzer, sample_data):
        product = "ENCHANTED_ENDER_PEARL"
        product_data = sample_data["products"]["ENCHANTED_ENDER_PEARL"]
        assert analyzer.is_product_available(product, product_data, sample_data) == True
    
    # Test calculate_recipe_cost method
    def test_calculate_recipe_cost(self, analyzer, sample_data):
        product_data = sample_data["products"]["ENCHANTED_ENDER_PEARL"]
        recipe_cost = analyzer.calculate_recipe_cost(product_data, sample_data, "buyPrice")
        assert isinstance(recipe_cost, float)
        assert recipe_cost == 20 * 15  # Assuming quantities are integers
    
    # Test print_top_products method
    def test_print_top_products(self, analyzer, capsys):
        profit_json = {
            "item1": {
                "product_name": "item1",
                "product_profit": 100,
                "recipe_cost": 50,
                "buy_volume": 200
            },
            "item2": {
                "product_name": "item2",
                "product_profit": 150,
                "recipe_cost": 75,
                "buy_volume": 300
            }
        }
        analyzer.print_top_products(profit_json, top_n=2)
        captured = capsys.readouterr()
        assert "Product Name" in captured.out
        assert "item1" in captured.out
        assert "item2" in captured.out

    # Test json_dump method
    def test_json_dump(self, analyzer, sample_data):
        current_bazaar_prices = sample_data
        recipes = sample_data["products"]
        insta_buy = True
        insta_sell = False
        min_buy_volume = 0
        result = analyzer.json_dump(current_bazaar_prices, recipes, insta_buy, insta_sell, min_buy_volume, analyzer)
        assert isinstance(result, dict)
        assert len(result) == 2  # Assuming both items are available