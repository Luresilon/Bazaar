# Hypixel Skyblock Market Analyser

Welcome this repo contains two programs designed to assist players of Hypixel Skyblock with various tasks related to the Hypixel Bazaar.

## Overview

This repository houses two distinct programs:

1. **Item Appraisal Tool**: This tool helps users appraise items in their inventory or from the Hypixel Bazaar. It provides valuable information such as item enchantments, hot potato count, and estimated market value.

2. **Bazaar Deal Finder**: This program assists users in finding the best buy and sell deals on the Hypixel Bazaar. By analyzing current market data, it identifies profitable opportunities for buying low and selling high.

## Installation

To use the programs in this repository, follow these steps:

1. Clone the repository to your local machine:

    ```bash
    git clone https://github.com/Luresilon/Bazaar.git
    ```

2. Navigate to the cloned directory:

    ```bash
    cd Bazaar
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Item Appraisal Tool

Before running the script:
 1. Sign up for Hypixel Developer and link it to your account.
 2. Create and retrieve a Development Key.
 3. Open ```HypixelItemAppraiser.py``` with the IDE of your choice and edit:
     - ```Line 163: username``` to your username.
     - ```Line 164: hypixel_developer_key``` to your development key.  
     - ```Line 165: item_index``` to the slot of the item you want appraised.
 4. On Skyblock make sure your API settings are available by:
     - Open Skyblock Menu
     - Go to Settings.
     - Go to API Settings and enable Inventory API.

To run the script:

 1. Go to ```src``` folder:
    ```bash
    cd src
    ```
 2. Run ```HypixelItemAppraiser.py```:
    ```bash
    python HypixelAppraiserItem.py
    ```

## Hypixel Bazaar Trader

To configure, open ```HypixelBazaarAnalyser.py``` and change the following variables from line ```151 - 154``` (or you can leave the default configurations):
 - ```num_of_products = 10```
 - ```insta_buy = True```
 - ```insta_sell = False```
 - ```min_buy_volume = 0```

To run the script:
1. Go to ```src``` folder:
    ```bash
    cd src
    ```
 2. Run ```HypixelItemAppraiser.py```:
    ```bash
    python HypixelBazaarAnalyser.py
    ```

## Feature Improvements
 1. Add a user-friendly GUI for altering configurations.
 2. Implement log history of items apprraised and/or best bazaar trades.
 3. Larger unit test coverage and integration testing.

## Tests

To run the tests:

 1. Run tests (in bazaar folder):
    ```bash
    pytest
    ```

## Disclaimer
Both scripts heavily depend on the uptime of Hypixel API.