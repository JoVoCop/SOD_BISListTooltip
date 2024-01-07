#!/usr/bin/env python

# This script converts the suffix mapping file to a lua table.

import sys
import os
import json
from loguru import logger

INPUT_FILE = "../data/wow-suffix-mapping.json"
OUTPUT_FILE = "../SuffixMapping.lua"

@logger.catch(onerror=lambda _: sys.exit(1)) # Catch all exceptions and exit with code 1
def main():
    logger.info("Starting...")

    logger.info(f"Reading suffix mapping data at {INPUT_FILE}")
    with open(INPUT_FILE, "r") as f:
        suffix_mapping = json.load(f)

    if suffix_mapping is None:
        logger.error("Failed to read suffix mapping file")
        sys.exit(1)

    logger.info(f"Writing suffix mapping to {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w") as f:
        f.write("suffixMapping = {\n")
        for suffix, value in suffix_mapping.items():
            logger.info(f"Processing {suffix} = {value}")
            numbers = value["values"]
            key = value["key"]
            for number in numbers:
                f.write("{{[\"suffixid\"] = \"{0}\", [\"suffixkey\"] = \"{1}\"}},\n".format(number, key))
        f.write("}\n")

    logger.info(f"Successfully converted {INPUT_FILE} to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()