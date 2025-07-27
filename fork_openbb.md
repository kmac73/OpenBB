# Fork OpenBB Repository Guide

## Overview

This guide helps you create your own fork of the OpenBB repository to maintain custom setup scripts and configurations without affecting the official OpenBB repository.

## Why Fork?

✅ **Complete Control** - Your own repository with your customizations  
✅ **No Accidental Pushes** - Can't accidentally contribute to official OpenBB  
✅ **Stay Updated** - Can still pull updates from upstream when needed  
✅ **Preserve Work** - Your setup scripts and configurations are safely stored  
✅ **Team Sharing** - Others can clone your customized version  

## Step-by-Step Forking Process

### 1. Fork on GitHub (Web Interface)

1. **Navigate to the Official Repository**:
   - Go to: **https://github.com/OpenBB-finance/OpenBB**

2. **Create the Fork**:
   - Click the **"Fork"** button (top right corner)
   - Choose your GitHub account as the destination
   - Optionally customize the repository name (default: `OpenBB`)
   - Click **"Create fork"**

3. **Result**:
   - Creates: `https://github.com/YOUR_USERNAME/OpenBB`
   - You now have your own copy of the entire OpenBB repository

### 2. Update Local Repository Remote Configuration

Once you've created the fork, update your local repository to point to your fork:

```bash
# Navigate to your local OpenBB directory
cd /path/to/your/OpenBB

# Update origin to point to your fork (replace YOUR_USERNAME)
git remote set-url origin https://github.com/YOUR_USERNAME/OpenBB.git

# Verify the change
git remote -v
# Should show:
# origin    https://github.com/YOUR_USERNAME/OpenBB.git (fetch)
# origin    https://github.com/YOUR_USERNAME/OpenBB.git (push)

# Add the original OpenBB repo as 'upstream' for future updates
git remote add upstream https://github.com/OpenBB-finance/OpenBB.git

# Verify both remotes are configured
git remote -v
# Should show:
# origin     https://github.com/YOUR_USERNAME/OpenBB.git (fetch)
# origin     https://github.com/YOUR_USERNAME/OpenBB.git (push)
# upstream   https://github.com/OpenBB-finance/OpenBB.git (fetch)
# upstream   https://github.com/OpenBB-finance/OpenBB.git (push)
```

### 3. Push Your Custom Changes to Your Fork

Push your existing branches with custom setup scripts:

```bash
# Push your develop branch (contains setup scripts and documentation)
git checkout develop
git push origin develop

# Push your alfa-class branch (your working branch)
git checkout alfa-class
git push origin alfa-class

# Push any other custom branches you've created
git push origin --all
```

### 4. Verify Your Fork Setup

Check that everything is working correctly:

```bash
# View your repository status
git status

# Check branch tracking
git branch -vv

# Verify your fork is accessible
curl -s https://api.github.com/repos/YOUR_USERNAME/OpenBB | grep -E '"name"|"full_name"|"private"'
```

## Daily Workflow with Your Fork

### Working on Your Custom Features

```bash
# Make changes to your setup scripts or configurations
# ... edit files ...

# Commit changes
git add .
git commit -m "Update custom setup configurations"

# Push to your fork (safe - won't affect official OpenBB)
git push origin develop
```

### Getting Updates from Official OpenBB

Periodically sync with the official repository to get latest features and fixes:

```bash
# Fetch updates from official OpenBB repository
git fetch upstream

# Switch to your develop branch
git checkout develop

# Merge official updates into your branch
git merge upstream/develop

# Push updated branch to your fork
git push origin develop
```

### Handling Merge Conflicts

If there are conflicts between official updates and your customizations:

```bash
# During merge, Git will show conflicts
git status

# Edit conflicted files to resolve conflicts
# Look for conflict markers: <<<<<<< ======= >>>>>>>

# After resolving conflicts
git add .
git commit -m "Resolve merge conflicts with upstream updates"
git push origin develop
```

## Repository Structure After Fork

```
Your Local Repository:
├── origin (remote) → https://github.com/YOUR_USERNAME/OpenBB.git
├── upstream (remote) → https://github.com/OpenBB-finance/OpenBB.git
├── develop (branch) → Your customized development branch  
├── alfa-class (branch) → Your working branch
└── main (branch) → Synced with official releases
```

## Custom Files in Your Fork

Your fork will contain your custom setup files:

- `install_openbb.sh` - Custom installation script
- `start_all.sh` - Service startup script
- `start_jupyter.sh` - Jupyter Lab startup script
- `start_api.sh` - API server startup script  
- `start_cli.sh` - CLI startup script
- `SETUP_INSTRUCTIONS.md` - Complete setup documentation
- `change_logs/` - Session change logs
- `fork_openbb.md` - This guide

## Sharing Your Fork

Others can use your customized OpenBB setup by cloning your fork:

```bash
# Others can clone your fork directly
git clone https://github.com/YOUR_USERNAME/OpenBB.git
cd OpenBB

# They get all your custom setup scripts immediately
./install_openbb.sh 1
./start_all.sh
```

## Advanced: Contributing Back to Official OpenBB

If you create improvements that would benefit everyone:

```bash
# Create a clean branch for contribution
git checkout upstream/develop
git checkout -b feature/my-improvement

# Make your changes (without your personal customizations)
# ... edit files ...

# Commit and push to your fork
git commit -m "Add useful feature for everyone"
git push origin feature/my-improvement

# Create Pull Request from your fork to official OpenBB
# Go to GitHub and create PR from your feature branch
```

## Troubleshooting

### Problem: Can't Push to Origin
```bash
# Check remote configuration
git remote -v

# Ensure you're pushing to your fork, not official repo
git remote set-url origin https://github.com/YOUR_USERNAME/OpenBB.git
```

### Problem: Merge Conflicts with Upstream
```bash
# See conflicted files
git status

# Reset to clean state if needed
git merge --abort
git reset --hard HEAD
```

### Problem: Lost Custom Changes
```bash
# Find your commits
git log --oneline --graph

# Create backup branch
git checkout -b backup-my-changes
git push origin backup-my-changes
```

## Security Considerations

🔒 **API Keys**: Never commit API keys to public repositories
- Keep API keys in local config files only
- Use environment variables for sensitive data
- Add API key files to `.gitignore`

🔒 **Private Fork**: Consider making your fork private if it contains:
- Custom business logic
- Proprietary configurations
- Internal API endpoints

## Next Steps

1. **Create your fork** on GitHub
2. **Update remote configuration** with your fork URL
3. **Push your custom branches** to your fork
4. **Test the setup** by cloning your fork in a new directory
5. **Document any additional customizations** in your fork's README

---

## Session State Information (For Continuation)

### Current Repository Status
- **Current Branch**: `develop` 
- **Local Git User**: `kmm <mcnamark73@gmail.com>`
- **Repository Location**: `/mnt/c/Users/kevin/git/OpenBB`
- **Original Remote**: `https://github.com/OpenBB-finance/OpenBB.git`

### Branches with Custom Changes
1. **`develop` branch**: Contains 2 commits ahead of origin/develop
   - `f1b84a12a70`: OpenBB Platform setup scripts and documentation
   - `a8cdaa54d51`: Change log documentation
   
2. **`alfa-class` branch**: Working branch with same commits

### Custom Files Created (Ready to Fork)
```
/mnt/c/Users/kevin/git/OpenBB/
├── install_openbb.sh              # Installation script (alfa-class-env support)
├── start_all.sh                   # Combined service startup
├── start_jupyter.sh               # Jupyter Lab startup (alfa-class-env)
├── start_api.sh                   # API server startup (alfa-class-env)
├── start_cli.sh                   # CLI startup (alfa-class-env)
├── SETUP_INSTRUCTIONS.md          # Complete setup documentation
├── change_logs/change_log_2025-07-27-08-32.md  # Session documentation
└── fork_openbb.md                 # This forking guide
```

### API Keys Configuration
- **Location**: `~/.openbb_platform/user_settings.json`
- **Configured Keys**: FMP, FRED, Alpha Vantage
- **Placeholder Keys**: Polygon, Quandl, Twelve Data

### OpenBB Services Status
- **Environment**: `alfa-class-env` conda environment
- **Jupyter Lab**: ✅ Running at http://localhost:8888
- **API Server**: ⚠️ Partial startup issues (Jupyter functional)
- **Installation**: ✅ Development mode completed

### Key Session Accomplishments
1. ✅ Modified all startup scripts to use `alfa-class-env`
2. ✅ Added command-line argument support to installation script
3. ✅ Created comprehensive setup documentation with API guidance
4. ✅ Configured API keys for FMP, FRED, and Alpha Vantage
5. ✅ Successfully restarted services with new configuration
6. ✅ Committed all changes to local `develop` branch
7. ✅ Created detailed change log and forking guide

### Immediate Next Steps for Fork Process
When you return to continue:

1. **Verify Current State**:
   ```bash
   cd /mnt/c/Users/kevin/git/OpenBB
   git status
   git branch -v
   git remote -v
   ```

2. **Create Fork on GitHub**:
   - Visit: https://github.com/OpenBB-finance/OpenBB
   - Click "Fork" button
   - Note your fork URL: `https://github.com/YOUR_USERNAME/OpenBB`

3. **Update Local Repository**:
   ```bash
   # Replace YOUR_USERNAME with your actual GitHub username
   git remote set-url origin https://github.com/YOUR_USERNAME/OpenBB.git
   git remote add upstream https://github.com/OpenBB-finance/OpenBB.git
   ```

4. **Push Custom Branches**:
   ```bash
   git push origin develop
   git push origin alfa-class
   ```

### Important Notes for Session Continuation
- All your custom setup work is preserved in local commits
- The fork process will not lose any of your customizations
- Your API keys are safely stored in `~/.openbb_platform/user_settings.json`
- Services can be restarted with `./stop_all.sh && ./start_all.sh`

### Files to Review When Returning
- `change_logs/change_log_2025-07-27-08-32.md` - Complete session documentation
- `SETUP_INSTRUCTIONS.md` - Updated setup guide with API recommendations
- This file (`fork_openbb.md`) - Forking process guide

---

**Your fork is now independent from the official OpenBB repository while still allowing you to receive updates and maintain your customizations!**

## Quick Reference Commands

```bash
# Fork setup (one-time)
git remote set-url origin https://github.com/YOUR_USERNAME/OpenBB.git
git remote add upstream https://github.com/OpenBB-finance/OpenBB.git

# Daily workflow
git push origin develop                    # Push your changes
git fetch upstream && git merge upstream/develop  # Get updates

# Verification
git remote -v                             # Check remotes
git branch -vv                            # Check tracking branches
```