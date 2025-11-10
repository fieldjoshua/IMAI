#!/bin/bash

# PR Creation Helper Script
# Validates branch, tests, trackers, and creates PR with proper versioning

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== IMAI PR Creation Helper ===${NC}\n"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) not installed${NC}"
    echo "   Install with: brew install gh"
    echo "   Or create PR manually via GitHub web interface"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ Not authenticated with GitHub${NC}"
    echo "   Run: gh auth login"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)

if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
    echo -e "${RED}❌ Cannot create PR from main/master branch${NC}"
    echo "   Create a feature branch first: git checkout -b feat/feature-name"
    exit 1
fi

# Validate branch name format
if ! echo "$CURRENT_BRANCH" | grep -qE '^(feat|fix|test|docs|refactor|chore|style|perf|ci|build)/'; then
    echo -e "${YELLOW}⚠️  Branch name doesn't follow convention (feat/, fix/, test/, docs/, etc.)${NC}"
    read -p "   Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}⚠️  Uncommitted changes detected${NC}"
    git status --short
    read -p "   Commit changes first? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   Please commit your changes first, then run this script again"
        exit 1
    else
        exit 1
    fi
fi

# Check if branch is pushed
if ! git rev-parse --abbrev-ref --symbolic-full-name @{u} &> /dev/null; then
    echo -e "${YELLOW}⚠️  Branch not pushed to remote${NC}"
    read -p "   Push branch now? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push -u origin "$CURRENT_BRANCH"
    else
        echo "   Please push your branch first"
        exit 1
    fi
fi

# Run tests
echo -e "${GREEN}Running tests...${NC}"
if ! python -m pytest tests/ -v --tb=short 2>/dev/null || [ ! -d "tests" ] || [ -z "$(find tests -name '*.py' 2>/dev/null)" ]; then
    echo -e "${YELLOW}⚠️  No tests found or tests failed${NC}"
    echo "   Per guardrails, tests should pass before creating PR"
    read -p "   Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✅ Tests passed${NC}"
fi

# Check tracker updates
echo -e "${GREEN}Checking tracker updates...${NC}"
REQUIREMENTS_CHANGED=$(git diff main...HEAD --name-only | grep -E 'requirements\.txt' || true)
TRACKERS_CHANGED=$(git diff main...HEAD --name-only | grep -E 'trackers/.*\.md' || true)

if [ -n "$REQUIREMENTS_CHANGED" ] && [ -z "$TRACKERS_CHANGED" ]; then
    echo -e "${YELLOW}⚠️  requirements.txt changed but trackers/dependencies.md not updated${NC}"
    read -p "   Update trackers/dependencies.md now? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}   Please update trackers/dependencies.md before creating PR${NC}"
        exit 1
    fi
fi

# Determine PR number (try to get from existing PRs or use 01)
PR_NUMBER="01"
EXISTING_PR=$(gh pr list --head "$CURRENT_BRANCH" --json number --jq '.[0].number' 2>/dev/null || true)
if [ -n "$EXISTING_PR" ]; then
    PR_NUMBER=$(printf "%02d" "$EXISTING_PR")
    echo -e "${BLUE}Found existing PR #${PR_NUMBER}${NC}"
fi

# Get PR phase name from branch or prompt
PHASE_NAME=$(echo "$CURRENT_BRANCH" | sed 's|^[^/]*/||' | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')
read -p "PR Phase Name [$PHASE_NAME]: " INPUT_PHASE
PHASE_NAME=${INPUT_PHASE:-$PHASE_NAME}

# Determine version (check if PR exists)
VERSION="(a)"
if [ -n "$EXISTING_PR" ]; then
    # Get current version from PR title
    CURRENT_TITLE=$(gh pr view "$EXISTING_PR" --json title --jq -r '.title' 2>/dev/null || true)
    if echo "$CURRENT_TITLE" | grep -qE '\([a-z]\)'; then
        CURRENT_VERSION=$(echo "$CURRENT_TITLE" | grep -oE '\([a-z]\)' | tr -d '()')
        NEXT_LETTER=$(echo "$CURRENT_VERSION" | tr 'a-z' 'b-z' | head -c 1)
        VERSION="($NEXT_LETTER)"
    elif echo "$CURRENT_TITLE" | grep -qE '-v[0-9]+'; then
        CURRENT_VERSION=$(echo "$CURRENT_TITLE" | grep -oE '-v[0-9]+' | grep -oE '[0-9]+')
        NEXT_VERSION=$((CURRENT_VERSION + 1))
        VERSION="-v${NEXT_VERSION}"
    fi
fi

PR_TITLE="PR #${PR_NUMBER}${VERSION} — ${PHASE_NAME}"

echo -e "\n${BLUE}PR Details:${NC}"
echo "  Title: $PR_TITLE"
echo "  Branch: $CURRENT_BRANCH"
echo "  Version: $VERSION"

# Create or update PR
if [ -n "$EXISTING_PR" ]; then
    echo -e "\n${GREEN}Updating existing PR...${NC}"
    gh pr edit "$EXISTING_PR" --title "$PR_TITLE" --body-file .github/pull_request_template.md
    echo -e "${GREEN}✅ PR updated${NC}"
    echo -e "${BLUE}View PR: $(gh pr view "$EXISTING_PR" --json url --jq -r '.url')${NC}"
else
    echo -e "\n${GREEN}Creating new PR...${NC}"
    gh pr create --title "$PR_TITLE" --body-file .github/pull_request_template.md --base main
    echo -e "${GREEN}✅ PR created${NC}"
    echo -e "${BLUE}View PR: $(gh pr list --head "$CURRENT_BRANCH" --json url --jq -r '.[0].url')${NC}"
fi

echo -e "\n${GREEN}Next steps:${NC}"
echo "  1. Update PR description with version history"
echo "  2. Complete mandatory updates checklist"
echo "  3. Wait for CI checks to pass"
echo "  4. Address any feedback and update version if needed"

