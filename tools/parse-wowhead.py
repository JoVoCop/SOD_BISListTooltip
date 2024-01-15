#!/usr/bin/env python

import sys
import time
import os
import json
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from retry import retry


# Parses wowhead html and outputs a json file with the data. Should be updated to output a lua file instead later.

# Selenium binaries

CWD = os.path.dirname(__file__)
CHROMEDRIVER_PATH = os.path.join(CWD, "chrome/chromedriver-linux64/chromedriver")
CHROME_PATH = os.path.join(CWD, "chrome/chrome-linux64/chrome")

# WOWHEAD URLs
WOWHEAD_URLS = [
    # Druid
    {
        "class": "Druid",
        "spec": "Balance DPS",
        "list": "Druid Balance DPS",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/druid/balance/dps-bis-gear-pve-phase-1"
    },
    {
        "class": "Druid",
        "spec": "Feral DPS",
        "list": "Druid Feral DPS",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/druid/feral/dps-bis-gear-pve-phase-1"
    },
    {
        "class": "Druid",
        "spec": "Healer",
        "list": "Druid Healer",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/druid/healer-bis-gear-pve-phase-1"
    },
    {
        "class": "Druid",
        "spec": "Tank",
        "list": "Druid Tank",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/druid/tank-bis-gear-pve-phase-1"
    },
    
    # Hunter
    {
        "class": "Hunter",
        "spec": "DPS",
        "list": "Hunter DPS",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/hunter/dps-bis-gear-pve-phase-1"
    },
    
    # Mage
    {
        "class": "Mage",
        "spec": "DPS",
        "list": "Mage DPS",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/mage/dps-bis-gear-pve-phase-1"
    },
    {
        "class": "Mage",
        "spec": "Healer",
        "list": "Mage Healer",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/mage/healer-bis-gear-pve-phase-1"
    },
    
    # Paladin
    {
        "class": "Paladin",
        "spec": "DPS",
        "list": "Paladin DPS",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/paladin/dps-bis-gear-pve-phase-1"
    },
    {
        "class": "Paladin",
        "spec": "Healer",
        "list": "Paladin Healer",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/paladin/healer-bis-gear-pve-phase-1"
    },
    {
        "class": "Paladin",
        "spec": "Tank",
        "list": "Paladin Tank",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/paladin/tank-bis-gear-pve-phase-1",
        "custom_behaviors": {
            "suffix_from_column_text": True # The Paladin Tank list has a number of world drop items in a single row. These all have the same suffix. We need to use the text in the column to determine the suffix rather than from the item link.
        }
    },
    
    # Priest
    {
        "class": "Priest",
        "spec": "DPS",
        "list": "Priest DPS",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/priest/dps-bis-gear-pve-phase-1"
    },
    {
        "class": "Priest",
        "spec": "Healer",
        "list": "Priest Healer",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/priest/healer-bis-gear-pve-phase-1"
    },
    
    # Rogue
    {
        "class": "Rogue",
        "spec": "DPS",
        "list": "Rogue DPS",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/rogue/dps-bis-gear-pve-phase-1"
    },
    {
        "class": "Rogue",
        "spec": "Tank",
        "list": "Rogue Tank",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/rogue/tank-bis-gear-pve-phase-1"
    },
    
    # Shaman
    {
        "class": "Shaman",
        "spec": "Elemental DPS",
        "list": "Shaman Elemental DPS",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/shaman/elemental/dps-bis-gear-pve-phase-1"
    },
    {
        "class": "Shaman",
        "spec": "Enhancement DPS",
        "list": "Shaman Enhancement DPS",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/shaman/enhancement/dps-bis-gear-pve-phase-1"
    },
    {
        "class": "Shaman",
        "spec": "Healer",
        "list": "Shaman Healer",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/shaman/healer-bis-gear-pve-phase-1"
    },
    {
        "class": "Shaman",
        "spec": "Tank",
        "list": "Shaman Tank",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/shaman/tank-bis-gear-pve-phase-1"
    },
    
    # Warlock
    {
        "class": "Warlock",
        "spec": "DPS",
        "list": "Warlock DPS",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/warlock/dps-bis-gear-pve-phase-1"
    },
    {
        "class": "Warlock",
        "spec": "Tank",
        "list": "Warlock Tank",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/warlock/tank-bis-gear-pve-phase-1"
    },
    
    # Warrior
    {
        "class": "Warrior",
        "spec": "DPS",
        "list": "Warrior DPS",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/warrior/dps-bis-gear-pve-phase-1"
    },
    {
        "class": "Warrior",
        "spec": "Tank",
        "list": "Warrior Tank",
        "phase": "1",
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/warrior/tank-bis-gear-pve-phase-1"
    },
]
WOWHEAD_ITEM_URL_PREFIX = "https://classic.wowhead.com/item="

# WOWHEAD Image to Spec Mapping
WOWHEAD_IMAGE_TO_SPEC = {
    # Warlock DPS
    "spell_fire_burnout.gif": "Fire",
    "spell_shadow_shadowbolt.gif": "Shadow",

    # Warlock Tank
    "spell_fire_soulburn.gif": "Threat",
    "ability_warlock_demonicpower.gif": "Defensive"

}

# Allowed slots
WOW_SLOTS = [
    "head",
    "neck",
    "shoulders",
    "back",
    "chest",
    "wrist",
    "hands",
    "waist",
    "legs",
    "feet",
    "finger",
    "trinket",
    "main-hand",
    "two-hand",
    "off-hand",
    "one-hand",
    "ranged",
    "shield",
    "relic"
]

# Headings are inconsistent. This is a mapping of aliases to the correct heading
WOW_SLOT_ALIASES = {
    "cloak": "back",
    "shoulder": "shoulders",
    "wrists": "wrist",
    "glove": "hands",
    "gloves": "hands",
    "hand": "hands",
    "belt": "waist",
    "rings": "finger",
    "ring": "finger",
    "fingers": "finger",
    "trinkets": "trinket",
    "staves": "two-hand",
    "staff": "two-hand",
    "weapon": "two-hand",
    "two-handed": "two-hand",
    "duel-wield": "one-hand",
    "wand": "ranged",
    "wands": "ranged",
    "idol": "relic",
    "idols": "relic",
    "relics": "relic",
    "libram": "relic",
    "librams": "relic",
}

# Mapping file for english suffixes (ex: 'of the Whale) to their corresponding suffix ids as well as
# an internal 'key' which can be referenced in the lua file and work around localization issues
WOW_SUFFIX_MAPPING_FILE = os.path.join(CWD, "../data/wow-suffix-mapping.json")

# Output
OUTPUT_PATH = os.path.join(CWD, "../data/wowhead.json")

class Item:
    def __init__(self):
        self.name = None
        self.id = None
        self.source = None
        self.rank = None
        self.suffixkey = None
        self.prioritytext = None
        self.prioritynumber = None
        self.phase = None
        self.key = None
        self.slot = None

    def __str__(self):
        return f"{self.name} ({self.id})"

    def __repr__(self):
        return self.__str__()
    
    def get_name(self) -> str:
        return self.name
    
    def set_name(self, name: str) -> None:
        logger.debug(f"Setting name to \"{name}\"")
        self.name = name

    def get_id(self) -> str:
        return self.id
    
    def set_id(self, id: str) -> None:
        self.id = id

    def get_key(self) -> str:
        return self.key
    
    def set_key(self, key: str) -> None:
        logger.debug(f"Setting key to \"{key}\"")
        self.key = key

    def get_source(self) -> str:
        return self.source
    
    def set_source(self, source: str) -> None:
        self.source = source

    def get_rank(self) -> str:
        return self.rank
    
    def set_rank(self, rank: str) -> None:    
        self.rank = rank

    def get_suffixkey(self) -> str:
        return self.suffixkey
    
    def set_suffixkey(self, suffixkey: str) -> None:
        self.suffixkey = suffixkey

    def get_prioritytext(self) -> str:
        return self.prioritytext
    
    def set_prioritytext(self, prioritytext: str) -> None:
        self.prioritytext = prioritytext

    def get_prioritynumber(self) -> int:
        return self.prioritynumber
    
    def set_prioritynumber(self, prioritynumber: int) -> None:
        self.prioritynumber = prioritynumber

    def get_phase(self) -> str:
        return self.phase
    
    def set_phase(self, phase: str) -> None:
        self.phase = phase

    def get_slot(self) -> str:
        return self.slot
    
    def set_slot(self, slot: str) -> None:
        if slot not in WOW_SLOTS:
            if slot in WOW_SLOT_ALIASES:
                slot = WOW_SLOT_ALIASES[slot]
            else:
                raise Exception(f"Invalid slot {slot}")
        self.slot = slot

    def to_json(self) -> dict:
        return {
            "Rank": self.rank,
            "PriorityText": self.prioritytext,
            "PriorityNumber": self.prioritynumber,
            "Phase": self.phase,
            "ItemName": self.name,
            "ItemID": self.id,
            "ItemSuffixKey": self.suffixkey,
            "Source": self.source,
            "Slot": self.slot,
        }
    
    # static method to convert item column html to an Item object
    @staticmethod
    def from_column_html(item_browser: webdriver, item: "Item", link_num: int, column_html: str, column_text: str, links: list, wow_suffix_mapping: dict, custom_behaviors: dict) -> tuple["Item", str]:
        """
        Converts the html of a column to an Item object
        param item_browser: The selenium browser
        param item: The Item object to update
        param link_num: The link number to convert
        param column_html: The innerHtml of the column
        param column_text: The text of the column
        param links: The list of selenium links in the column
        param wow_suffix_mapping: The suffix mapping dictionary

        return: An Item object
        return: A string containing the reason for error
        """

        if item is None:
            item = Item()


        # Custom behaviors
        suffix_from_column_text = False
        if custom_behaviors is not None and "suffix_from_column_text" in custom_behaviors:
            logger.info("Using custom behavior suffix_from_column_text")
            suffix_from_column_text = custom_behaviors["suffix_from_column_text"]

        # Let's iterate over each item_link_data_testing["links"] and see if we print the following...
        # * Name of the item (link.text.strip())
        # * Any text between the link and the next link (link.tail.strip())
        # * The href (link.get_attribute("href"))
                
        # Iterate over item_link_data_testing["links"] using an index so we can get the next link
        for item_link_num in range(len(links)):
            if item_link_num != link_num:
                continue
            link = links[item_link_num]
            
            # Get the href
            href = link.get_attribute("href")

            logger.debug(f"Processing link {link.text.strip()}")
            if "item=" not in href:
                # Not an item link. We don't care about it
                return None, f"Skipping link {link.text.strip()} in because it is not an item link"

            # Get the text between the link and the next link
            text_between = ""
            if item_link_num == len(links) - 1:
                # Get html of the current link
                link_html = link.get_attribute("outerHTML")

                # Get all text after the link
                text_between = column_html.split(link_html)[1].strip()
            else:
                next_link = links[item_link_num + 1]

                # Get html of the current link
                link_html = link.get_attribute("outerHTML")
                # Get html of the next link
                next_link_html = next_link.get_attribute("outerHTML")
                # Get the text between the two links
                text_between = column_html.split(link_html)[1].split(next_link_html)[0].strip()
                

            logger.debug("Text between link and next link: " + text_between)
            if text_between == "":
                item_name = link.text.strip()
            else:

                # Remove any html tags from the text between
                # An html tag is defined as < followed by any number of characters that are not > followed by >
                import re
                text_between = re.sub(r"<[^>]*>", "", text_between)

                other_characters_to_remove = [
                    "/",
                    "&nbsp;"
                ]
                characters_to_remove_from_end = [
                    ","
                ]
                for character in other_characters_to_remove:
                    text_between = text_between.replace(character, "")

                # Remove whitespace
                text_between = text_between.strip()

                # Remove any characters from the end of the string
                for character in characters_to_remove_from_end:
                    if text_between.endswith(character):
                        text_between = text_between[:-1]
                
                # remove whitespace again
                text_between = text_between.strip()

                if text_between == "":
                    item_name = link.text.strip()
                else:
                    item_name = f"{link.text.strip()} {text_between}"

            # If there are double spaces, replace them with single spaces
            while "  " in item_name:
                logger.debug(f"Replacing double spaces in \"{item_name}\"")
                item_name = item_name.replace("  ", " ")

            
            logger.debug(f"href: {href}")

            # Get the item id
            item_id = href.split("item=")[1].split("/")[0]

            # If "&&" is in the link, it's probably rand or enchants. We can discard those.
            if "&&" in item_id:
                item_id = item_id.split("&&")[0]

            logger.debug(f"item_id: {item_id}")

            # Get the item name
            logger.debug(f"item_name: \"{item_name}\"")

            # Check if item_name contains any key from wow_suffix_mapping. Not using 'endswith' as some lists have inconsistent naming.
            #   For example, Rogue DPS lists "Cutthroat's Cape of the Tiger" as "Cutthroat's Cape of the Tiger +4/+4"
            # If it does, use the key as the suffix id
            # If it doesn't, use "" as the suffix id
            suffix_key = ""
            for key in wow_suffix_mapping:
                if suffix_from_column_text:
                    # Special way - match the suffix in the column text
                    if key.lower() in column_text.lower():
                        # We have a suspected suffix match. Let's hit the wowhead page for the item and confirm
                        if item_id_has_possible_suffixes(item_browser, item_id):
                            logger.debug(f"ItemID {item_id} has possible suffixes")
                        else:
                            logger.warning(f"ItemID {item_id} does not have possible suffixes. Skipping suffix match for {item_name} even though it contains {key}")
                            break
    
                        suffix_key = wow_suffix_mapping[key]["key"]
                        break
                else:
                    # Normal way - match the suffix in the item name
                    if key.lower() in item_name.lower():
                        # We have a suspected suffix match. Let's hit the wowhead page for the item and confirm
                        if item_id_has_possible_suffixes(item_browser, item_id):
                            logger.debug(f"ItemID {item_id} has possible suffixes")
                        else:
                            logger.warning(f"ItemID {item_id} does not have possible suffixes. Skipping suffix match for {item_name} even though it contains {key}")
                            break
                        
                        suffix_key = wow_suffix_mapping[key]["key"]
                        break


            item_key = f"{item_id}|{suffix_key}"
            item.set_key(item_key)
            item.set_id(item_id)
            item.set_name(item_name)
            item.set_suffixkey(suffix_key)
        
        return item, None
        
    

# Represents a single BIS page of data
class Page:
    def __init__(self, name: str, url: str, phase: str, spec: str, classname: str):
        self.name = name
        self.url = url
        self.phase = phase
        self.spec = spec
        self.classname = classname
        self.items = [] # List of Items
        self.item_keys = {} # Dictionary of itemid|suffixid to name.
        self.errors = []
        self.warnings = []


    def __str__(self):
        return f"{self.name} ({self.url})"

    def __repr__(self):
        return self.__str__()

    def add_item(self, item: Item) -> None:
        self.items.append(item)

    def get_items(self) -> list:
        return self.items
    
    def add_item_key(self, key: str, name: str) -> None:
        self.item_keys[key] = name
    
    def get_item_keys(self) -> dict:
        return self.item_keys

    def get_name(self):
        return self.name

    def get_url(self):
        return self.url
    
    def get_phase(self):
        return self.phase
    
    def get_classname(self):
        return self.classname
    
    def get_spec(self):
        return self.spec
    
    def add_error(self, error: str) -> None:
        self.errors.append(error)
    
    def get_errors(self):
        return self.errors
    
    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)
    
    def get_warnings(self):
        return self.warnings
    
    def get_item_json(self):
        output = []
        for item in self.items:
            output.append(item.to_json())
        return output

    

@retry(TimeoutException, tries=3)
def get_with_retry(driver, url):
    logger.debug(f"Getting {url}")
    driver.get(url)

def item_id_has_possible_suffixes(browser: webdriver, item_id: str) -> bool:
    """
    Returns True if the item id has possible suffixes. Returns False otherwise.
    
    A suffix is possible if the itemid page has an h2 tag with the text "Random Enchantments"

    param: browser: The selenium browser
    param: item_id: The item id to check

    return: True if the item id has possible suffixes. False otherwise.
    """

    # Get the item page
    item_url = f"{WOWHEAD_ITEM_URL_PREFIX}{item_id}"
    logger.debug(f"Getting {item_url}")
    get_with_retry(browser, item_url)

    # Get all h2 tags
    h2s = browser.find_elements(By.TAG_NAME, "h2")

    # Check if any of the h2 tags have the text "Random Enchantments"
    for h2 in h2s:
        if h2.text.strip() == "Random Enchantments":
            return True
    
    return False

def parse_wowhead_url(browser: webdriver, item_browser: webdriver, url: str, listname: str, phase: str, spec: str, classname: str, custom_behaviors: dict, wow_suffix_mapping: dict) -> Page:
    """
    Parses a wowhead url and returns a Page object with the following:
    - data (list of dictionaries)
        - Rank
        - ItemName
        - ItemID
        - Source
    - errors (list of strings)
    - warnings (list of strings)
    """

    # Get page
    logger.debug(f"Getting {url}")
    get_with_retry(browser, url)

    # Get data within id=guide-body
    logger.debug("Getting guide-body")
    guide_body = browser.find_element(By.ID, "guide-body")

    # Find all tables within guide_body
    logger.debug("Getting tables")
    tables = guide_body.find_elements(By.TAG_NAME, "table")

    page = Page(name=listname, url=url, phase=phase, spec=spec, classname=classname)

    # Iterate over tables and find the one with the correct columns
    # Correct columns are "Rank", "Item", and "Source" in that order in the first row
    logger.debug("Iterating over tables")
    for table in tables:
        # Find all rows in the table
        logger.debug("Getting rows")
        rows = table.find_elements(By.TAG_NAME, "tr")

        # Find the column names from the first row of each table
        columns = rows[0].find_elements(By.TAG_NAME, "td")
        column_names = []
        for column in columns:
            column_names.append(column.text.strip())

        if len(column_names) >= 3 and column_names[0] == "Rank" and column_names[1] == "Item" and column_names[2] == "Source":
            logger.info("Found a table with the correct columns")
        else:
            logger.info("Did not find a table with the correct columns")
            logger.info(f"Found columns {column_names}")
            continue

        

        # Determine slot by finding previous h3 tag with an id in (back, chest, head, neck, shoulders, waist, wrist, feet, finger, hands, legs, mainn-hand, off-hand, ranged, trinket)
        # Get the previous h3 tag
        item_slot = None
        previous_h3 = table.find_elements(By.XPATH, "preceding::h3")
        if len(previous_h3) > 0:
            previous_h3 = previous_h3[-1]
            logger.debug(f"Found previous h3 tag with text {previous_h3.text.strip()}")
            if previous_h3.get_attribute("id") is not None:
                logger.debug(f"Found previous h3 tag with id {previous_h3.get_attribute('id')}")

                # Get the id
                item_slot = str(previous_h3.get_attribute("id"))

                logger.info(f"Found slot {item_slot}")
        else:
            logger.error("Did not find previous h3 tag (item_slot)")
            raise Exception("Did not find previous h3 tag (item_slot)")
        
        

        # Find the data in each row
        row_current = 0
        row_count = len(rows) - 1
        for row in rows[1:]:
            row_current += 1

            # Get the number of Items per row - edge case but some rows have multiple items
            items_per_row = 0
            items_column_html = None
            item_links = []
            for i, column in enumerate(row.find_elements(By.TAG_NAME, "td")):
                column_name = column_names[i]
                if column_name == "Item":
                    item_links = column.find_elements(By.TAG_NAME, "a")
                    items_column_html = column.get_attribute("innerHTML")
                    if len(item_links) > 0:
                        items_per_row = len(item_links)
                        logger.debug(f"Found {items_per_row} items in row {row_current}")
                        break
            
            for itemanchornum in range(items_per_row):
                logger.info(f"-------------------------- Row: {row_current}, Anchor: {itemanchornum} --------------------------")
                logger.debug(f"Processing item {itemanchornum} in row {row_current}")

                item = Item()
                item.set_slot(item_slot)

                rank_found = False
                item_found = False
                source_found = False

                skip_row = False

                for i, column in enumerate(row.find_elements(By.TAG_NAME, "td")):
                    column_name = column_names[i]

                    if skip_row:
                        continue

                    
                    if column_name == "Rank":
                        rank_found = True

                        # Check if the column has a span with class="icontiny". If it does exist, get the background image from the style attribute. For the following example, we expect the output to be "spell_shadow_shadowbolt.gif":
                        # <span class="icontiny" style="background-image: url("https://wow.zamimg.com/images/wow/icons/tiny/spell_shadow_shadowbolt.gif");'></span>
                        
                        icons = column.find_elements(By.CLASS_NAME, "icontiny")
                        icon = None
                        if len(icons) > 0:
                            icon = icons[0]
                        if icon:
                            logger.debug(f"Found icon {icon.get_attribute('style')}")

                            icon_image = icon.get_attribute("style").split("url(\"")[1].split("\"")[0].split("/")[-1]

                            if icon_image in WOWHEAD_IMAGE_TO_SPEC:
                                item.set_rank(column.text.strip() + f" ({WOWHEAD_IMAGE_TO_SPEC[icon_image]})")
                            else:
                                page.add_error(f"Unknown icon image {icon_image}")
                                item.set_rank(column.text.strip() + f" ({icon_image})")
                        else:
                            item.set_rank(column.text.strip())

                        # Log the row number as "Priority"
                        item.set_prioritytext(f"{row_current}/{row_count}") # For example, 1/10
                        item.set_prioritynumber(row_current) # For example, 1. Useful for ordering the items for presentation
                        item.set_phase(phase)
                    elif column_name == "Item":
                        if item_found:
                            # Don't process item in a single row
                            logger.debug(f"Skipping item {item.get_name()} because item was already found")
                            continue

                        item, reason = Item.from_column_html(item_browser, item, itemanchornum, items_column_html, column.text.strip(), item_links, wow_suffix_mapping, custom_behaviors)
                        if item is None:
                            logger.warning(reason)
                            page.add_warning(reason)
                            skip_row = True
                            continue

                        item_found = True

                        logger.info(f"Found item {item.get_name()} with id {item.get_id()} and suffix key {item.get_suffixkey()}")
                        page.add_item_key(item.get_key(), item.get_name())
                    elif column_name == "Source":
                        source_found = True
                        if items_per_row > 1:
                            # If there are multiple items in the row,  just specify "multiple"
                            item.set_source("Multiple")
                        else:
                            item.set_source(column.text.strip())
                    elif column_name == "Location":
                        # Warrior sheets. Append to source
                        if items_per_row > 1:
                            pass
                        elif item.get_source() is not None:
                            item.set_source(f"{item.get_source()} ({column.text.strip()})")
                    else:
                        logger.warning(f"Unknown column name {column_name}")
                        page.add_warning(f"Unknown column name {column_name}")
                        #raise Exception(f"Unknown column name {column_name}")
                    
                if skip_row:
                    logger.debug(f"Skipping row {row_current}")
                    continue

                # Confirm that all columns were found
                if not rank_found:
                    page.add_error(f"Did not find Rank column in row {row_current}")
                    logger.error(f"Did not find Rank column in row {row_current}")
                if not item_found:
                    page.add_error(f"Did not find Item column in row {row_current}")
                    logger.error(f"Did not find Item column in row {row_current}")
                if not source_found:
                    page.add_error(f"Did not find Source column in row {row_current}")
                    logger.error(f"Did not find Source column in row {row_current}")
                
                logger.debug(f"Adding row {row_current} to data")
                page.add_item(item)

    if len(page.get_items()) == 0:
        page.add_error("Did not find any data")
        logger.error("Did not find any data")
    
    return page

@logger.catch(onerror=lambda _: sys.exit(1)) # Catch all exceptions and exit with code 1
def main():
    # Read WOWHEAD_WARLOCK_DPS_BIS_URL
    # Parse each table that has a columns "Rank", "Item", and "Source"
    # Extract the Rank, Item, and Source into a list of dictionaries
    # Output the list of dictionaries as a json file

    # Check if the chromedriver exists
    if not os.path.exists(CHROMEDRIVER_PATH):
        logger.critical("Chromedriver does not exist at " + CHROMEDRIVER_PATH)
        sys.exit(1)

    # Check if the chrome binary exists
    if not os.path.exists(CHROME_PATH):
        logger.critical("Chrome does not exist at " + CHROME_PATH)
        sys.exit(1)

    # Confirm the mapping file exists
    if not os.path.exists(WOW_SUFFIX_MAPPING_FILE):
        logger.critical("Mapping file does not exist at " + WOW_SUFFIX_MAPPING_FILE)
        sys.exit(1)

    
    logger.info("Starting...")

    # Create a new Chrome session
    options = Options()
    options.add_argument("--headless") # Ensure GUI is off
    options.add_argument("--no-sandbox")

    # Set path to chrome/chromedriver as per your configuration
    options.binary_location = CHROME_PATH
    webdriver_service = Service(CHROMEDRIVER_PATH)

    # Read the mapping file as json into a dictionary
    wow_suffix_mapping = None
    with open(WOW_SUFFIX_MAPPING_FILE, "r") as f:
        wow_suffix_mapping = json.load(f)
    if wow_suffix_mapping is None:
        logger.critical("Failed to read mapping file")
        sys.exit(1)
    

    # Choose Chrome Browser
    browser = webdriver.Chrome(service=webdriver_service, options=options)
    browser.set_page_load_timeout(60)

    # Secondary browser for item pages
    item_browser = webdriver.Chrome(service=webdriver_service, options=options)
    item_browser.set_page_load_timeout(60)

    # Iterate over WOWHEAD_URLS
    pages = []
    errors = []
    warnings = []
    item_keys = {} # Dictionary of itemid|suffixid to item names
    for wowhead_url in WOWHEAD_URLS:
        logger.info(f"Processing {wowhead_url['list']} ({wowhead_url['url']})")
        custom_behaviors = None
        if "custom_behaviors" in wowhead_url:
            custom_behaviors = wowhead_url["custom_behaviors"]
        
        wowhead_page = parse_wowhead_url(browser=browser, item_browser=item_browser, url=wowhead_url["url"], listname=wowhead_url["list"], phase=wowhead_url["phase"], spec=wowhead_url["spec"], classname=wowhead_url["class"], custom_behaviors=custom_behaviors, wow_suffix_mapping=wow_suffix_mapping)
        if len(wowhead_page.get_errors()) > 0:
            logger.error("Errors:")
            for error in wowhead_page.get_errors():
                logger.error(error)
                errors.append(error)
        if len(wowhead_page.get_warnings()) > 0:
            logger.warning("Warnings:")
            for warning in wowhead_page.get_warnings():
                logger.warning(warning)
                warnings.append(warning)
        if len(wowhead_page.get_items()) > 0:
            logger.success(f"We have {len(wowhead_page.get_items())} rows of data for {wowhead_page.get_name()}")
            page = {
                "class": wowhead_page.get_classname(),
                "spec": wowhead_page.get_spec(),
                "list": wowhead_page.get_name(),
                "contents": wowhead_page.get_item_json()
            }
            pages.append(page)
            item_keys.update(wowhead_page.get_item_keys())



    # Summarize data
    output = {
        "items": item_keys,
        "pages": pages
    }
    # logger.debug(json.dumps(output, indent=4))

    # Write to file
    logger.info(f"Writing to {OUTPUT_PATH}")
    with open(OUTPUT_PATH, "w") as f:
        f.write(json.dumps(output, indent=4))



    # Close browser
    browser.quit()

    if len(errors) > 0:
        logger.error(f"Found {len(errors)} errors")
        for error in errors:
            logger.error(error)
        sys.exit(1)
    if len(warnings) > 0:
        logger.warning(f"Found {len(warnings)} warnings")
        for warning in warnings:
            logger.warning(warning)
    if len(errors) == 0 and len(warnings) == 0:
        logger.success("No errors or warnings")

    sys.exit(0)
    

if __name__ == "__main__":
    main()
