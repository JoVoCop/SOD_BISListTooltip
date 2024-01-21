#!/usr/bin/env python

# Combines the last 4 *.md files from ./changelogs into a single curseforge.md.tmp file
# This output is used as the file changelog for curseforge


import sys
import os
import json
from loguru import logger

CWD = os.path.dirname(__file__)

# Input
CHANGELOGS_PATH = os.path.join(CWD, "../changelogs")

# Output
OUTPUT_FILENAME = os.path.join(CWD, "../curseforge.md.tmp")

@logger.catch
def main():
    logger.info("Starting...")

    # Read CHANGELOGS_PATH file as json
    logger.info(f"Reading changelog data at {CHANGELOGS_PATH}")
    with open(OUTPUT_FILENAME, "w") as f:
        # Iterate over each item in the list but only the last 4 in reverse order
        count = 0
        logger.info("Processing changelog data")
        for filename in sorted(os.listdir(CHANGELOGS_PATH), reverse=True)[:4]:
            count += 1
            logger.info(f"Processing changelog {filename}")
            with open(os.path.join(CHANGELOGS_PATH, filename), "r") as changelog:
                f.write(changelog.read())

                # If it's the last file, don't add a separator
                if count < 4:
                    f.write("\n\n---\n\n")

    logger.info("Done.")

if __name__ == "__main__":
    main()