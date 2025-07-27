#!/bin/bash

# OpenBB Session Change Log Generator
# Creates a change log file with timestamp for documenting session changes

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== OpenBB Session Change Log Generator ===${NC}"
echo ""

# Generate timestamp
TIMESTAMP=$(date '+%Y-%m-%d-%H-%M')
CHANGE_LOG_FILE="change_logs/change_log_${TIMESTAMP}.md"

echo -e "${BLUE}Creating change log file: ${YELLOW}${CHANGE_LOG_FILE}${NC}"
echo ""

# Create change_logs directory if it doesn't exist
mkdir -p change_logs

# Get git information
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
LAST_COMMIT=$(git log -1 --format="%h %s")
REPO_STATUS=$(git status --porcelain | wc -l)

# Interactive prompts for session information
echo -e "${YELLOW}Please provide information about this session:${NC}"
echo ""

read -p "Session focus/main objective: " SESSION_FOCUS
echo ""

read -p "Key accomplishments (separate with semicolons): " ACCOMPLISHMENTS
echo ""

read -p "Files modified (separate with semicolons, or press Enter to auto-detect): " FILES_MODIFIED
echo ""

read -p "Services status updates: " SERVICES_STATUS
echo ""

read -p "Any issues encountered: " ISSUES
echo ""

read -p "Next steps or recommendations: " NEXT_STEPS
echo ""

# Auto-detect modified files if not provided
if [ -z "$FILES_MODIFIED" ]; then
    echo -e "${BLUE}Auto-detecting modified files...${NC}"
    FILES_MODIFIED=$(git diff --name-only HEAD~1 2>/dev/null | tr '\n' ';' || echo "No recent changes detected")
fi

# Create the change log
cat > "$CHANGE_LOG_FILE" << EOF
# OpenBB Setup Session Change Log
**Date**: $(date '+%B %d, %Y - %I:%M %p')  
**Session Focus**: ${SESSION_FOCUS}

## Session Overview

This session focused on ${SESSION_FOCUS,,}.

## Key Accomplishments

EOF

# Parse and format accomplishments
IFS=';' read -ra ACCOMP_ARRAY <<< "$ACCOMPLISHMENTS"
for accomplishment in "${ACCOMP_ARRAY[@]}"; do
    if [ ! -z "$accomplishment" ]; then
        echo "### ✅ $(echo "$accomplishment" | sed 's/^[[:space:]]*//')" >> "$CHANGE_LOG_FILE"
        echo "" >> "$CHANGE_LOG_FILE"
    fi
done

cat >> "$CHANGE_LOG_FILE" << EOF

## Technical Changes Made

### Files Modified
EOF

# Parse and format modified files
IFS=';' read -ra FILES_ARRAY <<< "$FILES_MODIFIED"
for file in "${FILES_ARRAY[@]}"; do
    if [ ! -z "$file" ]; then
        echo "- \`$(echo "$file" | sed 's/^[[:space:]]*//')\`" >> "$CHANGE_LOG_FILE"
    fi
done

cat >> "$CHANGE_LOG_FILE" << EOF

### Git Repository Status
- **Branch**: ${CURRENT_BRANCH}
- **Last Commit**: ${LAST_COMMIT}
- **Uncommitted Changes**: $([ "$REPO_STATUS" -eq 0 ] && echo "None" || echo "${REPO_STATUS} files")
- **Repository**: $(git config --get remote.origin.url 2>/dev/null || echo "Local repository")

## Services Status

${SERVICES_STATUS}

## Environment Information

### OpenBB Configuration
- **Conda Environment**: \$(conda info --envs | grep '*' | awk '{print \$1}' 2>/dev/null || echo "Unknown")
- **Python Version**: \$(python --version 2>/dev/null || echo "Unknown")
- **OpenBB Installation**: \$(python -c "import openbb; print('✅ Installed')" 2>/dev/null || echo "⚠️ Not detected")

### System Information
- **OS**: \$(uname -s)
- **Working Directory**: \$(pwd)
- **Date**: $(date)

## Issues Encountered

${ISSUES:-"No major issues encountered during this session."}

## Quick Commands Reference

### Service Management
\`\`\`bash
# Start all services
./start_all.sh

# Start individual services
./start_jupyter.sh
./start_api.sh
./start_cli.sh

# Stop services
./stop_all.sh
\`\`\`

### Git Commands
\`\`\`bash
# Check status
git status

# Push changes
git push origin ${CURRENT_BRANCH}

# Pull updates from official OpenBB
git fetch upstream && git merge upstream/${CURRENT_BRANCH}
\`\`\`

## Session Outcome

$(if [ "$REPO_STATUS" -eq 0 ]; then
    echo "✅ All changes have been committed and the working directory is clean."
else
    echo "⚠️ There are ${REPO_STATUS} uncommitted changes in the working directory."
fi)

## Next Steps Recommendations

${NEXT_STEPS:-"Continue with regular OpenBB development and testing."}

---

**Session completed** - $(date '+%B %d, %Y at %I:%M %p')  
**Change log created by**: create_change_log.sh script
EOF

echo -e "${GREEN}✅ Change log created successfully!${NC}"
echo -e "   File: ${YELLOW}${CHANGE_LOG_FILE}${NC}"
echo -e "   Size: $(wc -l < "$CHANGE_LOG_FILE") lines"
echo ""

# Ask if user wants to commit the change log
if [ "$REPO_STATUS" -gt 0 ] || [ ! -f ".git/config" ]; then
    read -p "Would you like to commit this change log? (y/N): " COMMIT_LOG
    if [[ $COMMIT_LOG =~ ^[Yy]$ ]]; then
        git add "$CHANGE_LOG_FILE"
        git commit -m "Add session change log for $(date '+%Y-%m-%d')

Session focus: ${SESSION_FOCUS}

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
        echo -e "${GREEN}✅ Change log committed to git${NC}"
        
        read -p "Would you like to push to origin? (y/N): " PUSH_LOG
        if [[ $PUSH_LOG =~ ^[Yy]$ ]]; then
            git push origin "$CURRENT_BRANCH"
            echo -e "${GREEN}✅ Changes pushed to remote repository${NC}"
        fi
    fi
fi

echo ""
echo -e "${BLUE}Change log generation complete!${NC}"
echo -e "You can review the file with: ${YELLOW}cat ${CHANGE_LOG_FILE}${NC}"