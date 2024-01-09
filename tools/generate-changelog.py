#!/usr/bin/env python

# This script generates a chnagelog in markdown format comparing two json files from 
# data/wowhead.json.old (old) and data/wowhead.json (new)
# It will generate a file called wowhead-changelog.md in the root of the project
# Rather than just doing a plain diff, it will try to group the changes by contents.ItemName and page.list
# Only the changes under "pages.contents" will be compared, the other keys will be ignored

# Usage:
# python tools/generate-changelog.py <tag> <stub>
# tag: The tag to use for the changelog
# stub: If true, will generate a stub changelog with just the tag and date, no changes

import sys
import os
import json
from datetime import datetime
from loguru import logger
from deepdiff import DeepDiff
from pprint import pprint

CWD = os.path.dirname(__file__)

# Input
WOWHEAD_DATA_PATH_OLD = os.path.join(CWD, "../data/wowhead.json.old")
WOWHEAD_DATA_PATH_NEW = os.path.join(CWD, "../data/wowhead.json")

# Output
OUTPUT_FILENAME = os.path.join(CWD, "../changelog.md.tmp")

# Get tag from the first argument and optionally, get the 'stub' boolean from the second argument
if len(sys.argv) < 2:
    logger.error("No tag specified")
    sys.exit(1)
tag = sys.argv[1]
stub = False
if len(sys.argv) > 2:
    stub = sys.argv[2] == "true"

@logger.catch
def main():
    logger.info("Starting...")

    # Read WOWHEAD_DATA_PATH_OLD file as json
    logger.info(f"Reading wowhead data at {WOWHEAD_DATA_PATH_OLD}")
    with open(WOWHEAD_DATA_PATH_OLD, 'r') as f:
        wowhead_data_old = json.load(f)

    if wowhead_data_old is None:
        logger.error("Failed to read WOWHEAD_DATA_PATH_OLD")
        sys.exit(1)

    # Read WOWHEAD_DATA_PATH_NEW file as json
    logger.info(f"Reading wowhead data at {WOWHEAD_DATA_PATH_NEW}")
    with open(WOWHEAD_DATA_PATH_NEW, 'r') as f:
        wowhead_data_new = json.load(f)

    if wowhead_data_new is None:
        logger.error("Failed to read WOWHEAD_DATA_PATH_NEW")
        sys.exit(1)


    # Main diff logic

    differences = DeepDiff(wowhead_data_old, wowhead_data_new, ignore_order=True, view='tree')
    
    
    # Added items format:
    # Key: ItemName [ItemID]
    # Value: List of pages where the item appears
    added_items = {}

    # Removed items format:
    # Key: ItemName [ItemID]
    # Value: List of pages where the item was removed
    removed_items = {}

    # Changed items format:
    # Key: ItemName [ItemID]
    # Value: List of summary of changes
    changed_items = {}

    
    # Get added items if they exist
    if "iterable_item_added" in differences:
        for item_added in differences["iterable_item_added"]:
            item_name = item_added.t2["ItemName"]
            item_id = item_added.t2["ItemID"]
            item_priority_text = item_added.t2["PriorityText"]
            page = item_added.up.up.t2["list"]
            item_key = f"{item_name} (ItemID: `{item_id}`)"

            summary = f"{page} - Priority: `{item_priority_text}`"

            if item_key in added_items:
                added_items[item_key].append(summary)
            else:
                added_items[item_key] = [summary]

    # Get removed items if they exist
    if "iterable_item_removed" in differences:
        for item_removed in differences["iterable_item_removed"]:
            item_name = item_removed.t1["ItemName"]
            item_id = item_removed.t1["ItemID"]
            page = item_removed.up.up.t1["list"]
            item_key = f"{item_name} (ItemID: `{item_id}`)"

            if item_key in removed_items:
                removed_items[item_key].append(page)
            else:
                removed_items[item_key] = [page]

    # Get changed items if they exist
    if "values_changed" in differences:
        for item_changed in differences["values_changed"]:
            pprint(item_changed.up.t1)
            old_item_name = item_changed.up.t1["ItemName"]
            old_item_id = item_changed.up.t1["ItemID"]
            old_page = item_changed.up.up.up.t1["list"]
            print(old_page)
            changed_key = item_changed.path(output_format="list")[-1:]
            item_key = f"{old_item_name} (ItemID: `{old_item_id}`)"
            old_value = item_changed.t1
            new_value = item_changed.t2

            # Convert changed_key from list to string
            changed_key = "".join(changed_key)

            if changed_key[:2] == "['":
                changed_key = changed_key[2:] 
            if changed_key[-2:] == "']":
                changed_key = changed_key[:-2]
            

            # Ignore changes to PriorityText
            if changed_key == "PriorityText":
                continue

            # Summary in format "Page - Key: OldValue -> NewValue"
            summary = f"{old_page} - `{changed_key}: {old_value} -> {new_value}`"

            if item_key in changed_items:
                changed_items[item_key].append(summary)
            else:
                changed_items[item_key] = [summary]
            

            
    # Writing changelog
    logger.info(f"Writing changelog to {OUTPUT_FILENAME}")    
    with open(OUTPUT_FILENAME, "w") as f:
        # Today's date as YYYY-MM-DD
        f.write(f"## {tag} ({datetime.now().strftime('%Y-%m-%d')})\n\n")

        if stub:
            print("Stub changelog generated")
            sys.exit(0)

        # Added items
        if len(added_items) > 0:
            f.write("\n\n")
            f.write("### Additions\n\n")
            for item_name, additions in added_items.items():
                f.write(f"* {item_name}\n")
                for addition in additions:
                    f.write(f"  * {addition}\n")
        
        # Removed items
        if len(removed_items) > 0:
            f.write("\n\n")
            f.write("### Removals\n\n")
            for item_name, pages in removed_items.items():
                f.write(f"* {item_name}\n")
                f.write(f"  * Lists: {', '.join(pages)}\n")

        # Changed items
        if len(changed_items) > 0:
            f.write("\n\n")
            f.write("### Changes\n\n")
            for item_name, changes in changed_items.items():
                f.write(f"* {item_name}\n")
                for change in changes:
                    f.write(f"  * {change}\n")
        
        # Footer to indicate this was auto-generated
        f.write("\n\n")
        f.write("This changelog was automatically generated. Problems? Submit an issue in GitHub.\n")


if __name__ == "__main__":
    main()
