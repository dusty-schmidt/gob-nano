# GOB Git Workflow & Automated Versioning System

## Overview

This document describes the comprehensive git workflow and automated versioning system designed to prevent conflicts when multiple workers are contributing to the GOB project. The system includes:

- **Conflict-free automated versioning**
- **Branch naming conventions**
- **Git hooks for validation**
- **Lock-based version management**
- **Comprehensive documentation**

## Key Components

### 1. Automated Version Bump Script (`auto_version_bump_auto.sh`)

**Features:**
- Non-interactive automated version bumping
- Lock-based conflict prevention
- Branch-specific version tagging
- Retry mechanism for concurrent access
- Stale lock detection and cleanup

**Usage:**
```bash
# Bump patch version (default)
./scripts/auto_version_bump_auto.sh

# Bump specific version type
./scripts/auto_version_bump_auto.sh major
./scripts/auto_version_bump_auto.sh minor
./scripts/auto_version_bump_auto.sh patch

# Specify branch (defaults to current)
./scripts/auto_version_bump_auto.sh patch main
```

**Conflict Prevention:**
- Uses file-based locking (`.version_lock` directory)
- Waits up to 10 seconds with retries
- Automatically removes stale locks
- Prevents duplicate version numbers

### 2. Git Hooks System (`git_hooks_installer.sh`)

**Pre-commit Hook:**
- Validates branch naming conventions
- Checks version consistency across files
- Prevents commits with version mismatches

**Post-merge Hook:**
- Automatically bumps version after main branch merges
- Ensures version increments are tracked

**Pre-push Hook:**
- Checks for version locks
- Prevents pushing during version updates
- Waits for active version operations to complete

**Post-commit Hook:**
- Displays current version after commits
- Provides immediate feedback on version state

### 3. Enhanced Version Manager (`version_manager.sh`)

**New Commands:**
```bash
# Get current version
./scripts/version_manager.sh get

# Set specific version
./scripts/version_manager.sh set 0.3.0

# Auto-increment patch version
./scripts/version_manager.sh bump

# Sync version files (fix mismatches)
./scripts/version_manager.sh sync

# Show version history
./scripts/version_manager.sh history
```

## Branch Naming Conventions

**Valid Branch Patterns:**
- `main` / `master` - Production releases
- `develop` - Development integration
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Critical fixes
- `micro-task-*` - Micro-task specific branches
- `release/*` - Release preparation

**Examples:**
- `feature/enhanced-versioning`
- `bugfix/version-sync-issue`
- `micro-task-8-main-logging`
- `release/v0.3.0`

## Workflow Examples

### Standard Development Workflow

1. **Create feature branch:**
```bash
git checkout -b feature/my-new-feature
```

2. **Make changes and commit:**
```bash
git add .
git commit -m "feat: Add new feature"
```

3. **Auto-bump version:**
```bash
./scripts/auto_version_bump_auto.sh patch
```

4. **Push and create PR:**
```bash
git push origin feature/my-new-feature
# Create PR via GitHub/GitLab interface
```

### Concurrent Worker Scenario

**Worker A:**
```bash
# Working on micro-task-7
./scripts/auto_version_bump_auto.sh patch
# Version bumped to 0.2.3
```

**Worker B (simultaneous):**
```bash
# Working on micro-task-8
./scripts/auto_version_bump_auto.sh patch
# Automatically waits for Worker A to complete
# Version bumped to 0.2.4
```

### Version Conflict Resolution

**Problem:** Version mismatch between VERSION file and version.py

**Solution:**
```bash
./scripts/version_manager.sh sync
```

**Problem:** Pre-commit hook blocks due to version inconsistency

**Solution:**
```bash
# Bypass hook temporarily (only if sure)
git commit --no-verify -m "fix: Update feature"

# Or fix the root cause
./scripts/version_manager.sh sync
git add VERSION src/gob/version.py
git commit -m "fix: Sync version files"
```

## Automated CI/CD Integration

### GitHub Actions Example
```yaml
name: Auto Version Bump
on:
  push:
    branches: [main]

jobs:
  version-bump:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Auto bump version
        run: |
          chmod +x scripts/auto_version_bump_auto.sh
          ./scripts/auto_version_bump_auto.sh patch
      - name: Push changes
        run: |
          git push origin main
          git push origin --tags
```

### Jenkins Pipeline Example
```groovy
pipeline {
    agent any
    stages {
        stage('Version Bump') {
            steps {
                sh 'chmod +x scripts/auto_version_bump_auto.sh'
                sh './scripts/auto_version_bump_auto.sh patch'
            }
        }
    }
    post {
        always {
            sh 'git push origin main'
            sh 'git push origin --tags'
        }
    }
}
```

## Troubleshooting

### Common Issues

**1. Version lock stuck:**
```bash
# Remove stale lock
rm -rf .version_lock

# Or use force (carefully)
./scripts/auto_version_bump_auto.sh patch --force
```

**2. Git hooks not working:**
```bash
# Reinstall hooks
./scripts/git_hooks_installer.sh

# Or manually remove and reinstall
rm -rf .git/hooks
./scripts/git_hooks_installer.sh
```

**3. Branch naming validation failure:**
```bash
# Rename branch to follow convention
git branch -m feature/my-new-feature
git branch -m micro-task-123-description
```

**4. Version already exists:**
```bash
# Check existing tags
git tag | grep "^v0.2.4$"

# Skip tag creation
git commit --no-verify -m "fix: Update without version bump"
```

### Best Practices

1. **Always use automated version bumping** for consistency
2. **Install git hooks** on all development machines
3. **Follow branch naming conventions** strictly
4. **Resolve version conflicts immediately** using sync
5. **Test version bumps** in feature branches first
6. **Document version changes** in commit messages
7. **Use branch-specific tags** for non-main branches

## Migration from Manual Versioning

### For Existing Projects

1. **Install the new system:**
```bash
./scripts/git_hooks_installer.sh
chmod +x scripts/auto_version_bump_auto.sh
chmod +x scripts/version_manager.sh
```

2. **Update existing version files:**
```bash
./scripts/version_manager.sh sync
```

3. **Test the new workflow:**
```bash
./scripts/auto_version_bump_auto.sh patch
```

4. **Update CI/CD pipelines** to use automated scripts

### Backward Compatibility

The system maintains backward compatibility:
- Existing VERSION files are preserved
- Manual version management still works
- Git hooks are optional (but recommended)
- All existing git workflows continue to function

## Advanced Configuration

### Custom Version Lock Timeout
```bash
# Set custom timeout (in seconds)
export VERSION_LOCK_TIMEOUT=60
./scripts/auto_version_bump_auto.sh patch
```

### Custom Retry Settings
```bash
# Set custom retry parameters
export MAX_RETRIES=10
export RETRY_DELAY=5
./scripts/auto_version_bump_auto.sh patch
```

### Branch-Specific Versioning
```bash
# Different version schemes for different branches
./scripts/auto_version_bump_auto.sh patch feature/experimental
./scripts/auto_version_bump_auto.sh minor release/v1.0
```

## Monitoring and Logging

### Version History
```bash
# View complete version history
./scripts/version_manager.sh history

# Check current version
./scripts/version_manager.sh get
```

### Git Log Filtering
```bash
# Show version-related commits
git log --oneline --grep="release\|version\|bump"

# Show recent version tags
git tag --sort=-version:refname | head -10
```

### Conflict Detection
```bash
# Check for version conflicts
git diff HEAD~1 HEAD -- VERSION src/gob/version.py

# Monitor lock file
ls -la .version_lock 2>/dev/null || echo "No lock active"
```

This comprehensive workflow system ensures that multiple workers can contribute to the GOB project without version conflicts, while maintaining a clean and automated versioning process.