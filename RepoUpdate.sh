# Using the Script
# Save the script into a file, for example,  RepoUpdate.sh
# Make the script executable: chmod +x RepoUpdate.sh
# Run the script: ./RepoUpdate.sh


#!/bin/bash

# Define remote URLs
ORIGIN="https://github.com/Chrissblm/chat-with-your-data-solution-accelerator_PRIVATE.git" #where we update too
AZURE_ORIGIN_URL="https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator.git"  #where we update from

# Define branches
SOURCE_BRANCH="main"  # Branch to copy changes from
TARGET_BRANCH="main-azurepull"  # Branch to reset to upstream and then apply changes

get_repo_root() {
    git rev-parse --show-toplevel
}

# Define the base directory for the repository
# Uncomment the next line and specify the path if you want to set it manually
# REPO_DIR="/Users/christophersmith/Documents/Repos/chat-with-your-data-solution-accelerator_PRIVATE"
# Otherwise, dynamically find the repository root
REPO_DIR=${REPO_DIR:-$(get_repo_root)}

# Files to copy - adjust these as per your requirement
declare -a FILES_TO_COPY=(
    # ".devcontainer/azuredevcontainer.json"
    # ".devcontainer/devcontainer.dockerfile"
    # ".devcontainer/devcontainer.json"
    # ".env.dev"
    # ".gitignore"
    # ".vscode/settings.json"
    # "RepoUpdate.sh"
    # "Update_repo_from_AzureSample.sh"
    # "azure-pipelines-webappadmin.yml"
    # "azure-pipelines-webappmain.yml"
    # "changes.patch"
    "code/admin/Admin.py"
    "code/admin/images/ngpAI_150Clr.png"
    # "code/admin/pages/00_GPT.py"
    # "code/admin/pages/01_Ingest_Data.py"
    # "code/admin/pages/03_Delete_Data.py"
    # "code/admin/pages/05_Analysis.py"
    # "code/admin/temp_db.sqlite"
    # "code/requirements.txt"
    # "code/utilities/GPT/GPT_helper.py"
    # "code/utilities/GPT/__init__.py"
    # "code/utilities/GPT/token_counter.py"
    # "code/utilities/helpers/EnvHelper.py"
    # "code/utilities/helpers/LLMHelper.py"
    # "code/utilities/tools/SQLPrompt.py"
    # "code/utilities/tools/analyze.py"
)


# Function to reset TARGET_BRANCH to upstream/main
reset_to_upstream_main() {
    pushd "${REPO_DIR}"
    
    # Check if main_rebase exists locally
    if ! git rev-parse --verify "${TARGET_BRANCH}"; then
        echo "${TARGET_BRANCH} does not exist locally. Checking remote..."
        
        # Check if main_rebase exists on the remote and track it
        if git ls-remote --heads origin "${TARGET_BRANCH}" | grep -q "${TARGET_BRANCH}"; then
            echo "${TARGET_BRANCH} found on remote. Setting up local tracking..."
            git checkout -b "${TARGET_BRANCH}" "origin/${TARGET_BRANCH}"
        else
            echo "${TARGET_BRANCH} does not exist on the remote. Exiting..."
            return 1
        fi
    else
        git checkout "${TARGET_BRANCH}"
    fi

    git fetch upstream
    git reset --hard upstream/main
    echo "Reset ${TARGET_BRANCH} to upstream/main"
    git push --force origin "${TARGET_BRANCH}"
    echo "Pushed ${TARGET_BRANCH} to origin"
    popd
}


# Function to copy each file
copy_files() {
    # Checkout to the target branch
    git checkout $TARGET_BRANCH

    for file in "${FILES_TO_COPY[@]}"; do
        # Checkout the specific file from the source branch
        git checkout $SOURCE_BRANCH -- $file
        echo "Copied ${file}"
    done
}

# Function to create and apply a patch
create_and_apply_patch() {
    pushd "${REPO_DIR}"
    git diff upstream/main..HEAD > changes.patch
    echo "Created changes.patch"
    git apply changes.patch
    echo "Applied changes.patch"
    popd
}

# Function to add, commit, and push changes
commit_and_push() {
    pushd "${REPO_DIR}"
    git add .
    git commit -m "Applied changes from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"
    git push origin "${TARGET_BRANCH}"
    popd
}

# Execute the functions
reset_to_upstream_main
copy_files
create_and_apply_patch
commit_and_push


echo "Script execution completed."
