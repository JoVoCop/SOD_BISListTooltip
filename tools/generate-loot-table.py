#!/usr/bin/env python

import sys
import os
import json
from loguru import logger

CWD = os.path.dirname(__file__)

# Input
WOWHEAD_DATA_PATH = os.path.join(CWD, "../data/wowhead.json")

# Output
OUTPUT_FILENAME = os.path.join(CWD, "../WowheadLootTable.lua")

@logger.catch
def main():
    logger.info("Starting...")

    # Read WOWHEAD_DATA_PATH file as json
    logger.info(f"Reading wowhead data at {WOWHEAD_DATA_PATH}")
    with open(WOWHEAD_DATA_PATH, 'r') as f:
        wowhead_data = json.load(f)

    if wowhead_data is None:
        logger.error("Failed to read WOWHEAD_DATA_PATH")
        sys.exit(1)

    logger.info(f"Writing loot table to {OUTPUT_FILENAME}")    
    with open(OUTPUT_FILENAME, "w") as f:
        f.write("wowheadLootTable = {\n")

        # Iterate over each item in the list
        logger.info("Processing wowhead data")
        for itemkey, itemname in wowhead_data["items"].items():
            itemid, itemsuffixkey = itemkey.split("|")
            itembissuffixid = ""
            logger.info(f"Processing item {itemid} (SuffixID: {itemsuffixkey}) - {itemname}")


            sectionsText = "{"
            # Iterate over each page and generate a summary of where the item appears in each page
            for page in wowhead_data["pages"]:
                data_class = page["class"]
                data_spec = page["spec"]
                data_listname = page["list"]

                # iterate over each item in the "contents" key
                for item in page["contents"]:
                    data_item_name = item["ItemName"]
                    data_item_id = item["ItemID"]
                    data_item_suffix_key = item["ItemSuffixKey"]
                    data_item_bis_suffix_id = item["ItemBISSuffixID"]
                    data_item_rank = item["Rank"]
                    data_item_priority_text = item["PriorityText"]
                    data_item_priority_number = item["PriorityNumber"]
                    data_item_phase = item["Phase"]
                    data_item_source = item["Source"]

                    if itemid == data_item_id and itemsuffixkey == data_item_suffix_key:
                        logger.info(f"Found a match in page {data_listname}")
                        # We have a match
                        sectionsText = sectionsText + "{{[\"list\"] = \"{data_listname}\", [\"rank\"] = \"{data_item_rank}\", [\"class\"] = \"{data_class}\", [\"spec\"] = \"{data_spec}\", [\"priority_text\"] = \"{data_item_priority_text}\", [\"priority_number\"] = \"{data_item_priority_number}\", [\"phase\"] = \"{data_item_phase}\", [\"datasource\"] = \"Wowhead\"}},".format(
                            data_listname=data_listname,
                            data_item_rank=data_item_rank,
                            data_class=data_class,
                            data_spec=data_spec,
                            data_item_priority_text=data_item_priority_text,
                            data_item_priority_number=data_item_priority_number,
                            data_item_phase=data_item_phase
                        )

                        if itembissuffixid == "":
                            itembissuffixid = data_item_bis_suffix_id
                        elif itembissuffixid != data_item_bis_suffix_id:
                            logger.error(f"Item {itemid} has multiple BIS suffix IDs: {itembissuffixid} and {data_item_bis_suffix_id}")
                            sys.exit(1)

            sectionsText = sectionsText + "}"

            outputLine = "{{[\"itemid\"] = \"{itemid}\", [\"itemsuffixkey\"] = \"{itemsuffixkey}\", [\"itembissuffixid\"] = \"{itembissuffixid}\", [\"sections\"] = {sections}}},\n".format(
                itemid=itemid,
                itemsuffixkey=itemsuffixkey,
                itembissuffixid=itembissuffixid,
                sections=sectionsText
            )
            f.write(outputLine)    
        
        f.write("}\n")


    logger.info(f"Output written to {OUTPUT_FILENAME}")
    logger.info("Done")

if __name__ == "__main__":
    main()