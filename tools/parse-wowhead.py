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
        "url": "https://www.wowhead.com/classic/guide/season-of-discovery/classes/paladin/tank-bis-gear-pve-phase-1"
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

# WOWHEAD Image to Spec Mapping
WOWHEAD_IMAGE_TO_SPEC = {
    # Warlock DPS
    "spell_fire_burnout.gif": "Fire",
    "spell_shadow_shadowbolt.gif": "Shadow",

    # Warlock Tank
    "spell_fire_soulburn.gif": "Threat",
    "ability_warlock_demonicpower.gif": "Defensive"

}

# Mapping file for english suffixes (ex: 'of the Whale) to their corresponding suffix ids as well as
# an internal 'key' which can be referenced in the lua file and work around localization issues
WOW_SUFFIX_MAPPING_FILE = os.path.join(CWD, "../data/wow-suffix-mapping.json")

# Output
OUTPUT_PATH = os.path.join(CWD, "../data/wowhead.json")

@retry(TimeoutException, tries=3)
def get_with_retry(driver, url):
    logger.debug(f"Getting {url}")
    driver.get(url)

def parse_wowhead_url(browser: webdriver, url: str, listname: str, phase: str, wow_suffix_mapping: dict) -> dict:
    """
    Parses a wowhead url and returns a dictionary with the following:
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

    # Iterate over tables and find the one with the correct columns
    # Correct columns are "Rank", "Item", and "Source" in that order in the first row
    data = []
    errors = []
    warnings = []
    items = {} # Dictionary of itemid|suffixid to name.
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

        # Find the data in each row
        row_current = 0
        row_count = len(rows) - 1
        for row in rows[1:]:
            row_current += 1

            # Get the number of Items per row - edge case but some rows have multiple items
            items_per_row = 0
            for i, column in enumerate(row.find_elements(By.TAG_NAME, "td")):
                column_name = column_names[i]
                if column_name == "Item":
                    item_links = column.find_elements(By.TAG_NAME, "a")
                    if len(item_links) > 0:
                        items_per_row = len(item_links)
                        logger.debug(f"Found {items_per_row} items in row {row_current}")
                        break

            
            for itemanchornum in range(items_per_row):
                logger.debug(f"Processing item {itemanchornum} in row {row_current}")

                row_data = {}
                
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

                            # Exceptions due to formatting issues on Wowhead :(
                            if listname == "Paladin DPS":
                                # Shoulders are misformatted for first row. Instead of the rank, the item is listed
                                if column.text.strip() == "Sentry's Shoulderguards":
                                    logger.warning("Processing exception for Paladin DPS: Sentry's Shoulderguards")
                                    row_data["Rank"] = "Best"
                                    row_data["ItemName"] = "Sentry's Shoulderguards"
                                    row_data["ItemID"] = "15531"
                                    row_data["ItemSuffixKey"] = ""
                                    
                                    items["15531|"] = "Sentry's Shoulderguards"
                                    row_data["PriorityText"] = f"{row_current}/{row_count}" # For example, 1/10
                                    row_data["PriorityNumber"] = row_current # For example, 1. Useful for ordering the items for presentation
                                    row_data["Phase"] = "1"
                                    item_found = True # Mark item as found so we don't process the rest of the row
                                    continue

                            icon_image = icon.get_attribute("style").split("url(\"")[1].split("\"")[0].split("/")[-1]

                            if icon_image in WOWHEAD_IMAGE_TO_SPEC:
                                row_data["Rank"] = column.text.strip() + f" ({WOWHEAD_IMAGE_TO_SPEC[icon_image]})"
                            else:
                                errors.append(f"Unknown icon image {icon_image}")
                                row_data["Rank"] = column.text.strip() + f" ({icon_image})"
                        else:
                            row_data["Rank"] = column.text.strip()

                        # Log the row number as "Priority"
                        row_data["PriorityText"] = f"{row_current}/{row_count}" # For example, 1/10
                        row_data["PriorityNumber"] = row_current # For example, 1. Useful for ordering the items for presentation

                        # Log the phase as "Phase"
                        row_data["Phase"] = phase

                    elif column_name == "Item":
                        item_name = column.text.strip()
                        if item_found:
                            # Don't process multiple items in a single row
                            logger.debug(f"Skipping item {item_name} because item was already found")
                            continue
                        item_found = True

                        # If column name is 'Item', get the item name from the text and the item id from the href
                        # For item id, we uise regex to extract the numbers after item= and between slashes. For example, "https://www.wowhead.com/classic/item=211842/rakkamars-tattered-thinking-cap" results in 211842

                        
                        item_links = column.find_elements(By.TAG_NAME, "a")
                        if len(item_links) > 0:
                            item_link = item_links[itemanchornum].get_attribute("href")
                            if "item=" in item_link:
                                item_id = item_link.split("item=")[1].split("/")[0]
                            else:
                                logger.warning(f"Did not find item id for {item_name} in {listname} (link number: {itemanchornum}))")
                                warnings.append(f"Did not find item id for {item_name} in {listname} (link number: {itemanchornum}))")
                                skip_row = True
                                continue

                            # If "&&" is in the link, it's probably rand or enchants. We can discard those.
                            if "&&" in item_id:
                                item_id = item_id.split("&&")[0]

                        else:
                            logger.warning(f"Did not find item link for {item_name} in {listname}")
                            warnings.append(f"Did not find item link for {item_name} in {listname}")
                            skip_row = True
                            continue

                        # If item_name contains a line break, take current itemanchornum iteration number
                        if "\n" in item_name:
                            item_name = item_name.split("\n")[itemanchornum]



                        row_data["ItemName"] = item_name
                        row_data["ItemID"] = item_id

                        # Check if item_name contains any key from wow_suffix_mapping. Not using 'endswith' as some lists have inconsistent naming.
                        #   For example, Rogue DPS lists "Cutthroat's Cape of the Tiger" as "Cutthroat's Cape of the Tiger +4/+4"
                        # If it does, use the key as the suffix id
                        # If it doesn't, use "" as the suffix id
                        suffix_key = ""
                        for key in wow_suffix_mapping:
                            if key in item_name:
                                suffix_key = wow_suffix_mapping[key]["key"]
                                break
                        row_data["ItemSuffixKey"] = suffix_key
                        items_key = f"{item_id}|{suffix_key}"
                        items[items_key] = item_name

                        logger.info(f"Found item: {item_name} with id {item_id}")
                    elif column_name == "Source":
                        source_found = True
                        if items_per_row > 1:
                            # If there are multiple items in the row,  just specify "multiple"
                            row_data["Source"] = "Multiple"
                        else:
                            row_data["Source"] = column.text.strip()
                    elif column_name == "Location":
                        # Warrior sheets. Append to source
                        if items_per_row > 1:
                            pass
                        elif "Source" in row_data:
                            row_data["Source"] += f" ({column.text.strip()})"
                    else:
                        logger.warning(f"Unknown column name {column_name}")
                        warnings.append(f"Unknown column name {column_name}")
                        #raise Exception(f"Unknown column name {column_name}")
                    
                if skip_row:
                    logger.debug(f"Skipping row {row_current}")
                    continue

                # Confirm that all columns were found
                if not rank_found:
                    errors.append(f"Did not find Rank column in row {row_current}")
                    logger.error(f"Did not find Rank column in row {row_current}")
                if not item_found:
                    errors.append(f"Did not find Item column in row {row_current}")
                    logger.error(f"Did not find Item column in row {row_current}")
                if not source_found:
                    errors.append(f"Did not find Source column in row {row_current}")
                    logger.error(f"Did not find Source column in row {row_current}")
                
                logger.debug(f"Adding row {row_current} to data")
                data.append(row_data)

    if len(data) == 0:
        errors.append("Did not find any data")
        logger.error("Did not find any data")
    
    return {
        "data": data,
        "items": items,
        "errors": errors,
        "warnings": warnings
    }

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
    # Iterate over WOWHEAD_URLS
    pages = []
    errors = []
    warnings = []
    items = {} # Dictionary of itemid|suffixid to item names
    for wowhead_url in WOWHEAD_URLS:
        logger.info(f"Processing {wowhead_url['list']} ({wowhead_url['url']})")
        
        parse_response = parse_wowhead_url(browser=browser, url=wowhead_url["url"], listname=wowhead_url["list"], phase=wowhead_url["phase"], wow_suffix_mapping=wow_suffix_mapping)
        if len(parse_response["errors"]) > 0:
            logger.error("Errors:")
            for error in parse_response["errors"]:
                logger.error(error)
                errors.append(error)
        if len(parse_response["warnings"]) > 0:
            logger.warning("Warnings:")
            for warning in parse_response["warnings"]:
                logger.warning(warning)
                warnings.append(warning)
        if len(parse_response["data"]) > 0:
            logger.success(f"We have {len(parse_response['data'])} rows of data for {wowhead_url['list']}")
            page = {
                "class": wowhead_url["class"],
                "spec": wowhead_url["spec"],
                "list": wowhead_url["list"],
                "contents": parse_response["data"]
            }
            pages.append(page)
            items.update(parse_response["items"])



    # Summarize data
    output = {
        "items": items,
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
