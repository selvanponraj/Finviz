#!/bin/bash

# Get current date
DATE=$(date +%Y-%m-%d)

# Run the scanner and save to file
OUTPUT_FILE="Results/3% UP/finviz_daily-3up_${DATE}.txt"
python 3%UP.py > "${OUTPUT_FILE}"

echo "Finviz scan results saved to: ${OUTPUT_FILE}"

# Git operations
git add "${OUTPUT_FILE}"
git commit -m "Add Finviz results for ${DATE}"
git push

echo "Results pushed to git successfully!"
