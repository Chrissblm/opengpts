#!/bin/bash

# Exit script if any command fails
set -e

# Ensure we're in the repository directory (optional, uncomment and set the path if needed)
# cd /path/to/your/repo
cd /Users/christophersmith/Documents/Repos/opengpts

# Step 1: Update nextgen/f-copy with the latest changes from fork/f-main
echo "Updating nextgen/f-copy with the latest from fork/f-main..."
git fetch origin # Assuming 'origin' points to your main repo where nextgen/f-copy is located
git checkout nextgen/f-copy
git pull fork f-main # Assuming 'fork' is the remote name for fork/f-main

# Step 2: Rebase nextgen/dev with






# Sync nextgen/f-copy with fork/f-main
echo "Syncing nextgen/f-copy with fork/f-main..."
git checkout nextgen/f-copy
git pull origin fork/f-main

# Ensure origin/main is the latest and update nextgen/f-copy
echo "Updating nextgen/f-copy with the latest from origin/main..."
git fetch origin main:main
git merge origin/main

# Pull and rebase nextgen/dev into nextgen/f-copy
echo "Rebasing nextgen/dev into nextgen/f-copy..."
git checkout nextgen/dev
git pull --rebase origin nextgen/f-copy

# Make sure nextgen/dev is the latest version
echo "Updating nextgen/dev with the latest changes..."
git push origin nextgen/dev

echo "Process completed successfully."


