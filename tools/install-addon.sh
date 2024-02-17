#!/bin/bash

echo "Copying addon files to the destination directory..."

# Set the source directory
source_dir="$(dirname "$PWD")"
echo "Source directory: $source_dir"

# Set the destination directory
destination_dir="/mnt/c/Program Files (x86)/World of Warcraft/_classic_era_/Interface/AddOns/SOD_BISListTooltip"
echo "Destination directory: $destination_dir"

# Copy Lua and TOC files to the destination directory
cp "$source_dir"/*.lua "$destination_dir"
cp "$source_dir"/*.toc "$destination_dir"