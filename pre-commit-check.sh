#!/bin/bash
# Pre-commit security check for NVIDIA Earnings Analyzer
# Run this before committing to ensure no sensitive data is included

echo "🔒 Running pre-commit security check..."

# Check if security check script exists and run it
if [ -f "security_check.py" ]; then
    python security_check.py
    exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo ""
        echo "🚨 COMMIT BLOCKED: Security issues found!"
        echo "   Please resolve the issues above before committing."
        echo ""
        echo "💡 Quick fixes:"
        echo "   - Ensure .env files are not staged: git reset HEAD *.env"
        echo "   - Check .gitignore includes all sensitive files"
        echo "   - Run: python security_check.py"
        echo ""
        exit 1
    fi
else
    echo "⚠️  security_check.py not found, skipping automated checks"
    echo "   Please manually verify no sensitive data is being committed"
fi

echo "✅ Security check passed!"
exit 0
