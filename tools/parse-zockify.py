#!/usr/bin/env python

import sys
import time
import os
import json
import re
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from retry import retry

# Selenium binaries

CWD = os.path.dirname(__file__)
CHROMEDRIVER_PATH = os.path.join(CWD, "chrome/chromedriver-linux64/chromedriver")
CHROME_PATH = os.path.join(CWD, "chrome/chrome-linux64/chrome")

ZOCKIFY_URLS = [
    # Druid
    {
        "class": "Druid",
        "spec": "Balance DPS",
        "list": "Druid Balance DPS",
        "url": "https://www.zockify.com/wowclassic/druid/balance/"
    },
    {
        "class": "Druid",
        "spec": "Feral DPS",
        "list": "Druid Feral DPS",
        "url": "https://www.zockify.com/wowclassic/druid/feral/"
    },
    {
        "class": "Druid",
        "spec": "Healer",
        "list": "Druid Healer",
        "phase": "1",
        "url": "https://www.zockify.com/wowclassic/druid/healer/"
    },
    {
        "class": "Druid",
        "spec": "Tank",
        "list": "Druid Tank",
        "phase": "1",
        "url": "https://www.zockify.com/wowclassic/druid/tank/"
    },
]

CURRENT_PHASE = "2"

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


# Mapping file for english suffixes (ex: 'of the Whale) to their corresponding suffix ids as well as
# an internal 'key' which can be referenced in the lua file and work around localization issues
WOW_SUFFIX_MAPPING_FILE = os.path.join(CWD, "../data/wow-suffix-mapping.json")

# Mapping file for english suffixes (ex: 'of the Whale) and their itemid to their corresponding bis suffix id
# We do this to reduce the number of requests we need to make
ITEM_BIS_SUFFIX_CACHE_FILE = os.path.join(CWD, "../data/item-bis-suffix-cache.json")
USE_ITEM_BIS_SUFFIX_CACHE = True

# Output
OUTPUT_PATH = os.path.join(CWD, "../data/zockify.json")

class SuffixNotFoundException(Exception):
    def __init__(self, item_id, suffix):
        self.message = f"Failed to find matching suffix for item {item_id} with suffix {suffix}"
        super().__init__(self.message)


class Item:
    def __init__(self):
        self.name = None
        self.id = None
        self.source = None
        self.rank = None
        self.suffixkey = None
        self.bissuffixid = None # The best possible roll for a given suffix. This is interpreted by this script and not defined explicitly in the wowhead data. This should be optionally displayed in the output.
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

    def get_bissuffixid(self) -> str:
        return self.bissuffixid
    
    def set_bissuffixid(self, bissuffixid: str) -> None:
        self.bissuffixid = bissuffixid
    
    def to_json(self) -> dict:
        return {
            "Rank": self.rank,
            "PriorityText": self.prioritytext,
            "PriorityNumber": self.prioritynumber,
            "Phase": self.phase,
            "ItemName": self.name,
            "ItemID": self.id,
            "ItemSuffixKey": self.suffixkey,
            "ItemBISSuffixID": self.bissuffixid,
            "Source": self.source,
            "Slot": self.slot,
        }
    
    @staticmethod
    def get_bis_suffix_id(item_browser: webdriver, wow_suffix_mapping: dict, item_bis_suffix_cache: dict, item_id: str, suffix: str) -> str:
        """
        Determines the best possible suffix id for this item and sets it in self.bissuffixid.

        param item_browser: The selenium browser
        param wow_suffix_mapping: The suffix mapping dictionary
        param item_bis_suffix_cache: The item bis suffix cache dictionary. Format: {"itemid": {"suffix": "suffixid"}}
        param item_id: The item id to check
        param suffix: The suffix to check (ex: 'of the Bear')

        return: None if the item id has no possible suffixes (i.e. missing the "Random Enchantments" h2 tag). Otherwise, the best possible suffix id.

        raises: SuffixNotFoundException if there are possible suffixes but the provided suffix is not one of them
        raises: Exception If there was an issue parsing the suffixes
        """

        found_matching_suffix = False
        best_attributes = []


        if USE_ITEM_BIS_SUFFIX_CACHE:
            # Check if the item id is in the cache
            if item_id in item_bis_suffix_cache:
                # Check if the suffix is in the cache
                if suffix in item_bis_suffix_cache[item_id]:
                    # We have a match. Return the suffix id
                    logger.info(f"Found matching suffix {suffix} for item {item_id} in cache")
                    return item_bis_suffix_cache[item_id][suffix]

        # Get the item page
        item_url = f"{WOWHEAD_ITEM_URL_PREFIX}{item_id}"
        logger.debug(f"Getting {item_url}")
        get_with_retry(item_browser, item_url)
        
        # Get h2 with the text "Random Enchantments"
        # Find the following <ul> and iterate over each <li>
        # Each <li> has a <div> with a <span> with the suffix name followed by <br> then the attributes
        # Example:
        # <h2>Random Enchantments</h2>
        # <div class="random-enchantments">
        #   <ul>
        #     <li>
        #         <div>
        #             <span class="q2">...of the Monkey</span>
        #             <small class="q0">(18.0% chance)</small><br>
        #             +(3 - 4) Agility , +(3 - 4) Stamina
        #         </div>
        #     </li>
        #   </ul>
        # </div>

        # Find the h2 with the text "Random Enchantments"

        # Get all h2 tags
        h2s = item_browser.find_elements(By.TAG_NAME, "h2")
        enchant_header = None

        # Check if any of the h2 tags have the text "Random Enchantments"
        for h2 in h2s:
            if h2.text.strip() == "Random Enchantments":
                enchant_header = h2
                break

        if enchant_header is None:
            logger.warning(f"Failed to find heading with text 'Random Enchantments' for item {item_id}. Returning None")
            return None
        
        # Find the next <ul> following the h2
        uls = enchant_header.find_elements(By.XPATH, "./following::ul")

        ul_count = 0
        for ul in uls:
            ul_count += 1
            # We never need to go above 2 uls
            if ul_count > 2:
                break
            logger.info(f"Processing ul {ul_count}")
            if ul is None:
                logger.error(f"Failed to find ul following 'Random Enchantments' heading for item {item_id}")
                # Raise exception
                raise Exception(f"Failed to find ul following 'Random Enchantments' heading for item {item_id}")
            
            # Iterate over each <li>
            lis = ul.find_elements(By.XPATH, "./li")
            if lis is None:
                logger.error(f"Failed to find li elements following ul for item {item_id}")
                # Raise exception
                raise Exception(f"Failed to find li elements following ul for item {item_id}")
            
            for li in lis:
                # Each <li> has a <div> with a <span> with the suffix name followed by <br> then the attributes
                # Example:
                # <li>
                #   <div>
                #       <span class="q2">...of the Monkey</span>
                #       <small class="q0">(18.0% chance)</small><br>
                #       +(3 - 4) Agility , +(3 - 4) Stamina
                #   </div>
                # </li>

                if found_matching_suffix:
                    # We already found the matching suffix. Skip the rest of the suffixes
                    continue

                # Find the <div>
                try:
                    div = li.find_element(By.XPATH, "./div")
                except NoSuchElementException:
                    logger.warning(f"Failed to find div following li for item {item_id} (ul: {ul_count})")
                    break

                if div is None:
                    logger.error(f"Failed to find div following li for item {item_id}")
                    # Raise exception
                    raise Exception(f"Failed to find div following li for item {item_id}")
                
                # Find the <span> with the suffix name
                span = div.find_element(By.XPATH, "./span")
                if span is None:
                    logger.error(f"Failed to find span following div for item {item_id}")
                    # Raise exception
                    raise Exception(f"Failed to find span following div for item {item_id}")
                
                # Get text after <br> in the div
                raw_attributes = div.text.split("\n")[1]
                suffix_name = span.text
                
                # Remove ... from suffix name if it starts with ...
                if suffix_name.startswith("..."):
                    suffix_name = suffix_name[3:]

                # Split raw_attributes by comma
                raw_attributes = raw_attributes.split(",")

                # Trim each attribute
                raw_attributes = [x.strip() for x in raw_attributes]

                # Check if the suffix_name matches the provided suffix
                if suffix_name.lower() != suffix.lower():
                    # Suffix name does not match. Skip this suffix
                    logger.debug(f"Skipping suffix {suffix_name} because it does not match {suffix}")
                    continue
                
                # Suffix name matches
                found_matching_suffix = True
                for raw_attribute in raw_attributes:
                    # Find the best roll for each attribute
                    best_suffix = get_best_suffix_roll(raw_attribute)
                    best_attributes.append(best_suffix)
                    
        if not found_matching_suffix:
            # We did not find a matching suffix. Raise exception
            logger.error(f"Failed to find matching suffix for item {item_id} with suffix {suffix}")
            raise SuffixNotFoundException(item_id, suffix)
        
        # We now have a list of best attributes. Let's find the best one from suffix_mapping

        # Example:
        #   suffix = "of the Monkey"
        #   attributes = ["+6 Agility", "+6 Stamina"]

        # Iterate over each suffix in the suffix_mapping and find the matching suffix
        for mapping_suffix_name in wow_suffix_mapping:
            if mapping_suffix_name.lower() == suffix.lower():

                # Example:
                #   mapping_suffix_name = "of the Monkey"

                logger.info(f"Found matching suffix {mapping_suffix_name} for item {item_id}")

                # Iterate over each "value_attributes" and find the matching attributes from best_attributes
                for mapping_attribute_id in wow_suffix_mapping[mapping_suffix_name]["value_attributes"]:
                    mapping_suffix_attributes = wow_suffix_mapping[mapping_suffix_name]["value_attributes"][mapping_attribute_id].split("|")

                    # Example:
                    #   mapping_attribute_id = "598"
                    #   mapping_suffix_attributes = ["+6 Agility", "+6 Stamina"]

                    # We need to find if all elements of "attributes" matches all elements of "mapping_suffix_attributes"
                    if set(best_attributes) == set(mapping_suffix_attributes):
                        logger.info(f"Found matching attributes {best_attributes} for suffix {mapping_suffix_name} for item {item_id} with attribute id {mapping_attribute_id}")

                        # Log this in cache
                        if item_id not in item_bis_suffix_cache:
                            item_bis_suffix_cache[item_id] = {}
                        item_bis_suffix_cache[item_id][suffix] = mapping_attribute_id

                        # We found a match. Return the suffix id
                        return mapping_attribute_id
        
        # We did not find a match. Raise exception
        logger.error(f"Failed to find matching suffix for item {item_id} with suffix {suffix}")
        raise SuffixNotFoundException(item_id, suffix)



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

def is_expected_attribute_pattern(attribute: str) -> bool:
    """
    Given an attribute, return True if it matches the expected pattern.

    Expected patterns:
    * +DIGIT TEXT
    * +DIGIT% TEXT
    """

    regex = re.compile(r"^\+(\d+)(%)? .+$")
    matches = regex.findall(attribute)
    if matches is not None and len(matches) > 0:
        return True
    return False

def get_best_suffix_roll(raw_attribute: str) -> str:
    """
    Given a raw attribute string, return the best roll.

    Example input: "+(3 - 4) Agility"
    Example output: "+4 Agility"
    """

    # Trim the leading and trailing spaces
    raw_attribute = raw_attribute.strip()

    # Confirm there is only one set of parentheses
    if raw_attribute.count("(") > 1 or raw_attribute.count(")") > 1:
        logger.error(f"Found raw attribute {raw_attribute} with more than one set of parentheses")
        raise Exception(f"Found raw attribute {raw_attribute} with more than one set of parentheses")
    
    # If there are no parentheses, return the raw attribute
    if raw_attribute.count("(") == 0 and raw_attribute.count(")") == 0:
        logger.debug(f"Found raw attribute {raw_attribute} with no parentheses")
        if is_expected_attribute_pattern(raw_attribute):
            logger.debug(f"Found expected attribute pattern for raw attribute {raw_attribute}")
            return raw_attribute
        else:
            logger.error(f"Found unexpected attribute pattern for raw attribute {raw_attribute}")
            raise Exception(f"Found unexpected attribute pattern for raw attribute {raw_attribute}")

    # Get all text between the parentheses
    open_paren_index = raw_attribute.find("(")
    close_paren_index = raw_attribute.find(")")
    raw_roll = raw_attribute[open_paren_index + 1:close_paren_index]
    logger.debug(f"Found raw roll {raw_roll} for raw attribute {raw_attribute}")

    # Get the last number in raw_roll
    # Example: raw_roll = "3 - 4"
    regex = re.compile(r"(\d+)")
    matches = regex.findall(raw_roll)
    if matches is None or len(matches) == 0:
        logger.error(f"Failed to find number in raw roll {raw_roll} for raw attribute {raw_attribute}")
        raise Exception(f"Failed to find number in raw roll {raw_roll} for raw attribute {raw_attribute}")
    
    # Get the last number
    roll = matches[-1]
    logger.debug(f"Found roll {roll} for raw roll {raw_roll} for raw attribute {raw_attribute}")

    # Replace the parantheses with the roll using open_paren_index and close_paren_index
    # Example: raw_attribute = "+(3 - 4) Agility" -> "+4 Agility"
    best_roll = raw_attribute[:open_paren_index] + roll + raw_attribute[close_paren_index + 1:]
    logger.debug(f"Found best roll {best_roll} for raw roll {raw_roll} for raw attribute {raw_attribute}")

    return best_roll

@retry(TimeoutException, tries=3)
def get_with_retry(driver, url):
    logger.debug(f"Getting {url}")
    driver.get(url)

def parse_zockify_url(browser: webdriver, item_browser: webdriver, url: str, listname: str, phase: str, spec: str, classname: str, custom_behaviors: dict, wow_suffix_mapping: dict, item_bis_suffix_cache: dict) -> Page:
    """
    Parses a zockify url and returns a Page object with the following:
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

    # Get h2 element with id starting with "sod-phase-{phase}-bis-list"
    logger.debug(f"Getting element with ID starting with sod-phase-{phase}-bis-list")
    phase_header = browser.find_element(By.XPATH, f"//h2[starts-with(@id, 'sod-phase-{phase}-bis-list')]")
    logger.debug(f"Found phase header with text {phase_header.text}")

    logger.debug("Finding ul following phase header")
    bis_ul = browser.find_element(By.XPATH, f"//h2[starts-with(@id, 'sod-phase-{phase}-bis-list')]/following-sibling::ul")

    
    # Find all li within bis_ul
    logger.debug("Getting li elements")
    elements = bis_ul.find_elements(By.TAG_NAME, "li")

    page = Page(name=listname, url=url, phase=phase, spec=spec, classname=classname)

    
    # Iterate over li elements - these are the slots
    logger.debug("Iterating over elements")
    for element in elements:
        # Elements are split by <br> tags. The first strong element is the slot name. The rest are items

        # get first strong element. This is the slot name
        logger.debug("Getting strong element")
        slot = element.find_element(By.TAG_NAME, "strong")
        slot_name = slot.text.lower()
        logger.info(f"Found slot {slot_name}")

        # Find each span containing the data-z-tooltip attribute. This indicates it's an item
        logger.debug("Getting span elements")
        spans = element.find_elements(By.XPATH, "./span[contains(@data-z-tooltip, 'classic')]")
        logger.debug(f"Found {len(spans)} spans (items)")

        # Iterate over spans
        item_count = len(spans)
        item_current = 0
        for span in spans:
            item_name = span.text.strip()

            logger.debug(f"Found span with text {span.text}")

            # Get the data-z-tooltip element
            item_id = None
            tooltip = span.get_attribute("data-z-tooltip")
            if tooltip is not None:
                # Get everything after the last slash in the tooltip
                item_id = tooltip.split("/")[-1]
                logger.debug(f"Found item id {item_id} in tooltip")
            
            if item_id is None:
                logger.error(f"Failed to find item id for item {item_name} in slot {slot_name}")
                page.add_error(f"Failed to find item id for item {item_name} in slot {slot_name}")
                continue

            logger.info(f"Found Item {item_name} ({item_id}) in slot {slot_name}")
            item_current += 1

            item = Item()
            item.set_slot(slot_name)
            item.set_name(item_name)
            item.set_id(item_id)
            item.set_rank(f"BIS") # Always BIS for Zockify. TODO: Parse spec images
            
            item.set_prioritytext(f"{item_current}/{item_count}") # For example, 1/3
            item.set_prioritynumber(item_current) # For example, 1. Useful for ordering the items for presentation
            item.set_phase(phase)
            item.set_source("TBD") # TODO: Parse source


            # NEXT: We have item parsing, we need to...
            # * get spec images parsed
            # * output to json
            # * Get 'of the' suffixes parsed
            # * Compare against wowhead parser to make sure we're not missing anything
        





    # Print the text of the h2
    
    sys.exit(1)




@logger.catch(onerror=lambda _: sys.exit(1)) # Catch all exceptions and exit with code 1
def main():
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

    # Confirm the suffix cache file exists
    if not os.path.exists(ITEM_BIS_SUFFIX_CACHE_FILE):
        logger.critical("Suffix cache file does not exist at " + ITEM_BIS_SUFFIX_CACHE_FILE)
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

    # Read the suffix cache file as json into a dictionary
    item_bis_suffix_cache = None
    with open(ITEM_BIS_SUFFIX_CACHE_FILE, "r") as f:
        item_bis_suffix_cache = json.load(f)
    if item_bis_suffix_cache is None:
        logger.critical("Failed to read suffix cache file")
        sys.exit(1)
    

    # Choose Chrome Browser
    browser = webdriver.Chrome(service=webdriver_service, options=options)
    browser.set_page_load_timeout(60)

    # Secondary browser for item pages
    item_browser = webdriver.Chrome(service=webdriver_service, options=options)
    item_browser.set_page_load_timeout(60)

    # Iterate over ZOCKIFY_URLS
    pages = []
    errors = []
    warnings = []
    item_keys = {} # Dictionary of itemid|suffixid to item names
    for zockify_url in ZOCKIFY_URLS:
        logger.info(f"Processing {zockify_url['list']} ({zockify_url['url']})")
        custom_behaviors = None
        if "custom_behaviors" in zockify_url:
            custom_behaviors = zockify_url["custom_behaviors"]
        
        zockify_page = parse_zockify_url(browser=browser, item_browser=item_browser, url=zockify_url["url"], listname=zockify_url["list"], phase=CURRENT_PHASE, spec=zockify_url["spec"], classname=zockify_url["class"], custom_behaviors=custom_behaviors, wow_suffix_mapping=wow_suffix_mapping, item_bis_suffix_cache=item_bis_suffix_cache)
        if len(zockify_page.get_errors()) > 0:
            logger.error("Errors:")
            for error in zockify_page.get_errors():
                logger.error(error)
                errors.append(error)
        if len(zockify_page.get_warnings()) > 0:
            logger.warning("Warnings:")
            for warning in zockify_page.get_warnings():
                logger.warning(warning)
                warnings.append(warning)
        if len(zockify_page.get_items()) > 0:
            logger.success(f"We have {len(zockify_page.get_items())} rows of data for {zockify_page.get_name()}")
            page = {
                "class": zockify_page.get_classname(),
                "spec": zockify_page.get_spec(),
                "list": zockify_page.get_name(),
                "contents": zockify_page.get_item_json()
            }
            pages.append(page)
            item_keys.update(zockify_page.get_item_keys())



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

    # Write cache back to file
    logger.info(f"Writing suffix cache to {ITEM_BIS_SUFFIX_CACHE_FILE}")
    with open(ITEM_BIS_SUFFIX_CACHE_FILE, "w") as f:
        f.write(json.dumps(item_bis_suffix_cache, indent=4))



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
