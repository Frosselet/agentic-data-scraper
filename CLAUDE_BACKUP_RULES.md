# 🚨 CRITICAL BACKUP AND VERSIONING RULES

## MANDATORY RULES - ALWAYS VISIBLE IN CONTEXT

### 📋 Before ANY File Modifications:
1. **ALWAYS create a backup copy** with timestamp: `filename_backup_YYYY-MM-DD-HH-MM.ext`
2. **ALWAYS check for existing git status** and commit current state if valuable
3. **ALWAYS read the full file first** to understand current state
4. **NEVER make destructive changes** without explicit user confirmation

### 🔄 During Development Sessions:
1. **Commit progress every 30 minutes** or after major milestones
2. **Use descriptive commit messages** with what was accomplished
3. **Tag important states** for easy recovery
4. **Save intermediate working versions** before major refactoring

### 📁 File Management:
1. **Create versioned copies** for significant iterations: `file_v1.ext`, `file_v2.ext`
2. **Keep original file structure** - don't reorganize without permission
3. **Document all changes** in commit messages or change logs
4. **Test functionality** after each modification

### 🆘 Recovery Procedures:
1. **Check git history** first: `git log --oneline`
2. **Look for Jupyter checkpoints** in `.ipynb_checkpoints/`
3. **Check for backup files** with timestamps
4. **Use `git stash` and `git reset`** for recent changes
5. **Ask user for guidance** if recovery options are unclear

### ❌ NEVER DO:
- Overwrite files without backups
- Delete content without confirming it exists elsewhere
- Make assumptions about what the user wants to keep
- Proceed with destructive operations if unsure

### ✅ ALWAYS DO:
- Explain what will be modified before doing it
- Show the user what was found/recovered
- Ask for confirmation on significant changes
- Commit valuable progress immediately
- Keep detailed logs of what was done

---
**This file should remain visible and be consulted before ANY file operations.**