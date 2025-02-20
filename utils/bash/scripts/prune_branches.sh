#!/bin/bash

# Fetch the latest changes from the remote and prune deleted branches
git fetch --prune

# Get a list of local branches that have been merged into the current branch
merged_branches=$(git branch --merged | grep -v "\*" | grep -v "main")

# Loop through each merged branch
for branch in $merged_branches; do
    # Check if the branch exists on the remote
    if ! git show-ref --quiet --verify "refs/remotes/origin/$branch"; then
        # If the branch does not exist on the remote, ask for user confirmation before deleting it locally
        read -p "Do you want to delete the local branch '$branch'? (y/n): " confirm
        if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
            echo "Deleting local branch: $branch"
            git branch -d "$branch"
        else
            echo "Skipping deletion of local branch: $branch"
        fi
    fi
done

echo "Pruned branches have been processed."