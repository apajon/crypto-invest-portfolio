#!/usr/bin/env bash

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 [patch|minor|major] [--push] [--dry-run]"
    exit 1
fi

LEVEL=$1
PUSH_FLAG=""
DRY_RUN_FLAG=""

# Options
for arg in "$@"; do
    case "$arg" in
        --push) PUSH_FLAG="--push" ;;
        --dry-run) DRY_RUN_FLAG="--dry-run" ;;
    esac
done

# Récupère la version courante
CURRENT=$(tbump current-version)
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

# Calcule la nouvelle version
case "$LEVEL" in
    patch) PATCH=$((PATCH+1)) ;;
    minor) MINOR=$((MINOR+1)); PATCH=0 ;;
    major) MAJOR=$((MAJOR+1)); MINOR=0; PATCH=0 ;;
    *) echo "Level must be patch, minor, or major"; exit 1 ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo "Bumping from $CURRENT to $NEW_VERSION..."

# Appelle tbump
tbump "$NEW_VERSION" $PUSH_FLAG $DRY_RUN_FLAG
