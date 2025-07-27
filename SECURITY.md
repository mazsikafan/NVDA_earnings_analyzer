# 🔒 Security & Environment Setup Guide

## ⚠️ CRITICAL SECURITY NOTICE

This application uses sensitive API keys and credentials that **MUST NOT** be committed to version control.

## 🚨 Before First Commit

### 1. Verify .gitignore Protection
The root `.gitignore` file protects:
- `.env` files (containing API keys)
- Cache directories (`cache/`, `model_cache/`)
- Python bytecode (`__pycache__/`)
- Node.js dependencies (`node_modules/`)
- Database files (`*.db`, `*.sqlite`)
- IDE files (`.vscode/`, `.idea/`)

### 2. Set Up Environment Files

#### Backend Setup
```bash
cd backend_lite
cp .env.example .env
# Edit .env with your actual values:
# OPENAI_API_KEY=sk-proj-your-actual-key-here
```

#### Frontend Setup (if needed)
```bash
cd frontend
cp .env.example .env
# Add any frontend-specific environment variables
```

### 3. Verify No Sensitive Data in Git
```bash
# Check what's tracked
git ls-files | grep -E "\.env$|\.key|cache|__pycache__"

# Should return nothing - if it shows files, they need to be removed!
```

## 🔑 API Keys Required

### OpenAI API Key (Required)
- **Purpose**: Enhanced LLM-powered tone analysis and strategic messaging insights
- **Get Key**: https://platform.openai.com/api-keys
- **Cost**: Pay-per-use (typically $0.001-0.002 per analysis)
- **Storage**: Add to `backend_lite/.env` as `OPENAI_API_KEY=your-key-here`

## 🚫 Files That Should NEVER Be Committed

```bash
# Environment files
.env
.env.local
.env.production

# API keys in any format
*.key
api_keys.txt
secrets.json

# Cache and temporary data
cache/
__pycache__/
node_modules/
*.db
*.log

# IDE and OS files
.vscode/
.DS_Store
Thumbs.db
```

## ✅ Safe to Commit

```bash
# Example/template files
.env.example
config.example.json

# Source code
*.py
*.js
*.tsx
*.ts

# Documentation
*.md
requirements.txt
package.json
```

## 🛡️ Security Best Practices

1. **Never share .env files** via email, chat, or any communication channel
2. **Rotate API keys** regularly (monthly recommended)
3. **Use environment-specific keys** (dev, staging, production)
4. **Monitor API usage** in OpenAI dashboard for unexpected charges
5. **Use least-privilege access** - only grant necessary permissions

## 🔍 If Secrets Are Accidentally Committed

If you accidentally commit sensitive data:

1. **Immediately rotate all exposed keys**
2. **Remove from git history**:
   ```bash
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch path/to/sensitive/file' \
   --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push** (⚠️ be careful with shared repos):
   ```bash
   git push origin --force --all
   ```

## 📞 Need Help?

- Review the main README.md for setup instructions
- Check .env.example files for configuration templates
- Ensure all team members follow these security practices

---

**Remember**: When in doubt, don't commit. Security is everyone's responsibility! 🔒
