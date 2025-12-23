# GitHub Repository Protection Setup

## 🔒 Protect Your Repository from Unauthorized Changes

This guide will help you set up proper branch protection and access controls.

---

## 1. Branch Protection Rules

### Protect `main` Branch

1. Go to your GitHub repository: https://github.com/J3r3my97/mini-aura
2. Click **Settings** → **Branches** (left sidebar)
3. Under "Branch protection rules", click **Add rule**

### Configure Protection Rules:

#### Branch Name Pattern:
```
main
```

#### Check These Boxes:

**Require a pull request before merging:**
- ✅ Require a pull request before merging
- ✅ Require approvals: **1** (minimum)
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ⬜ Require review from Code Owners (optional, but recommended)

**Require status checks to pass before merging:**
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging

**Other Settings:**
- ✅ Require conversation resolution before merging
- ✅ Require linear history (optional - prevents merge commits)
- ✅ Include administrators (applies rules to you too)
- ⬜ Allow force pushes (keep UNCHECKED)
- ⬜ Allow deletions (keep UNCHECKED)

#### Click **Create** or **Save changes**

---

## 2. Protect `pre-production` Branch (if using)

Repeat the same steps for your `pre-production` branch:

1. Click **Add rule** again
2. Branch name pattern: `pre-production`
3. Apply same settings as main

---

## 3. Repository Access Settings

### Review Collaborators:

1. Go to **Settings** → **Collaborators and teams**
2. Review who has access
3. Remove anyone you don't recognize
4. Set appropriate permission levels:
   - **Read:** Can view code only
   - **Triage:** Can manage issues/PRs
   - **Write:** Can push to non-protected branches
   - **Maintain:** Can manage repo settings
   - **Admin:** Full access (only you)

### Recommended Setup (Solo Project):
- **You:** Admin access
- **Trusted collaborators:** Write access
- **Others:** Remove or set to Read only

---

## 4. Enable Security Features

### Dependency Alerts:

1. Go to **Settings** → **Security & analysis**
2. Enable:
   - ✅ Dependency graph
   - ✅ Dependabot alerts
   - ✅ Dependabot security updates

### Secret Scanning:

- ✅ Secret scanning (auto-enabled for public repos)
- ✅ Push protection (prevents committing secrets)

---

## 5. Required Status Checks (Optional)

If you have CI/CD (GitHub Actions):

1. Go to **Actions** → **General**
2. Set "Fork pull request workflows from outside collaborators":
   - Select: **Require approval for first-time contributors**

---

## 6. Pull Request Template

Create a PR template to enforce standards:

`.github/PULL_REQUEST_TEMPLATE.md`:
```markdown
## Description
<!-- Describe your changes -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tested locally
- [ ] All tests pass
- [ ] No console errors

## Checklist
- [ ] Code follows project style
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
```

---

## 7. How It Works After Setup

### ❌ What's Blocked:

1. **Direct pushes to main** - No one (including you) can push directly
2. **Force pushes** - Prevented entirely
3. **Branch deletion** - Can't delete protected branches
4. **Unreviewed merges** - PRs need approval

### ✅ Proper Workflow:

1. Create feature branch: `git checkout -b feature/new-thing`
2. Make changes and commit
3. Push: `git push origin feature/new-thing`
4. Open Pull Request on GitHub
5. Review your own PR (if solo) or wait for review
6. Merge when approved and checks pass

---

## 8. Solo Developer Workflow

**If you're working alone but want protection:**

### Option A: Self-Review (Recommended)
1. Create PR from feature branch
2. Review your own code
3. Approve and merge

**Benefits:**
- Review your changes before merging
- Catch mistakes
- Clean git history
- Practice for future collaboration

### Option B: Bypass for Admin
- Uncheck "Include administrators" in branch protection
- You can push directly, others cannot
- Less safe but faster

---

## 9. Emergency Override

**If you need to bypass protection (emergency fix):**

1. Go to **Settings** → **Branches**
2. Edit the rule
3. Temporarily disable protection
4. Make your fix
5. **Re-enable protection immediately**

**Better approach:**
- Create emergency PR
- Self-approve quickly
- Merge
- Keeps audit trail

---

## 10. Verification Checklist

After setting up, verify:

- [ ] Try pushing directly to main → Should fail
- [ ] Create test PR → Should work
- [ ] Merge without approval → Should fail (if required reviews enabled)
- [ ] Approved PR merges → Should work
- [ ] Non-collaborators can't push → Correct
- [ ] CODEOWNERS file recognized

---

## 11. Current Access Status

Check who has access right now:

```bash
# If you have GitHub CLI installed:
gh repo collaborators

# Or check on GitHub:
# Settings → Collaborators and teams
```

Remove anyone you don't recognize!

---

## 12. Revoking Access

**If someone has unauthorized access:**

1. **Settings** → **Collaborators and teams**
2. Find the user
3. Click **Remove**
4. **Settings** → **Security & analysis** → **Secret scanning**
5. Review any exposed secrets
6. Rotate credentials if needed (Stripe keys, Firebase, etc.)

---

## 13. Fork Protection

**For public repositories:**

1. **Settings** → **Actions** → **General**
2. "Fork pull request workflows from outside collaborators"
3. Select: **Require approval for all outside collaborators**

This prevents:
- Malicious code running in your Actions
- Secret exfiltration
- Resource abuse

---

## 14. Deployment Protection

**For production deployments (Vercel):**

1. Vercel → Your Project → Settings → Git
2. **Production Branch:** `main`
3. **Preview Branches:** All other branches
4. Enable: "Require approval for deployments"

**For Cloud Build:**
- Triggers only run on specific branches (already configured in cloudbuild.yaml)

---

## Quick Setup Commands

```bash
# Create CODEOWNERS file (already done)
mkdir -p .github
cat > .github/CODEOWNERS << 'EOF'
* @J3r3my97
EOF

# Create PR template
cat > .github/PULL_REQUEST_TEMPLATE.md << 'EOF'
## Changes
<!-- Describe changes -->

## Testing
- [ ] Tested locally
- [ ] All tests pass

## Checklist
- [ ] Code reviewed
- [ ] Documentation updated
EOF

git add .github/
git commit -m "Add GitHub protection files"
git push
```

---

## Summary: Protection Levels

### 🟢 Minimal (Solo, casual):
- Branch protection on `main`
- No required reviews
- Can self-merge PRs

### 🟡 Recommended (Solo, serious):
- Branch protection on `main` and `pre-production`
- Required reviews: 1
- CODEOWNERS file
- Linear history
- Include administrators

### 🔴 Maximum (Team/Enterprise):
- All above +
- Required status checks
- 2+ required reviews
- Code owner review required
- No admin bypass
- Signed commits required

---

Choose your level based on your needs! For a production app like Mini-Aura, I recommend **🟡 Recommended** level.
