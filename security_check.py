#!/usr/bin/env python3
"""
Security Verification Script for NVIDIA Earnings Analyzer
Run this script to verify your security setup before committing to git.
"""

import os
import sys
import glob
from pathlib import Path

def check_security():
    """Check for common security issues"""
    issues = []
    warnings = []
    
    print("🔍 Security Verification for NVIDIA Earnings Analyzer")
    print("=" * 60)
    
    # Check 1: .env files protection
    print("1. Checking .env files...")
    env_files = glob.glob("**/.env", recursive=True)
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"   ✅ Found .env file: {env_file}")
            # Check if it contains real API keys
            with open(env_file, 'r') as f:
                content = f.read()
                if 'sk-proj-' in content or 'sk-' in content:
                    if 'your_api_key_here' not in content and 'your_openai_api_key_here' not in content:
                        warnings.append(f"⚠️  Real API key detected in {env_file}")
    
    # Check 2: .gitignore exists
    print("2. Checking .gitignore protection...")
    if os.path.exists('.gitignore'):
        print("   ✅ Root .gitignore exists")
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
            required_patterns = ['.env', '__pycache__', 'cache/', '*.db']
            for pattern in required_patterns:
                if pattern in gitignore_content:
                    print(f"   ✅ {pattern} is protected")
                else:
                    issues.append(f"❌ {pattern} not found in .gitignore")
    else:
        issues.append("❌ Root .gitignore file missing")
    
    # Check 3: Sensitive files in git
    print("3. Checking for sensitive files in git...")
    try:
        import subprocess
        result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
        if result.returncode == 0:
            tracked_files = result.stdout.strip().split('\n')
            sensitive_patterns = ['.env', '.key', '__pycache__', 'cache/', 'node_modules/']
            for file in tracked_files:
                if file:  # Skip empty lines
                    for pattern in sensitive_patterns:
                        if pattern in file:
                            issues.append(f"❌ Sensitive file tracked in git: {file}")
            if not any(pattern in file for file in tracked_files for pattern in sensitive_patterns):
                print("   ✅ No sensitive files found in git")
        else:
            warnings.append("⚠️  Not a git repository or git not available")
    except Exception as e:
        warnings.append(f"⚠️  Could not check git status: {e}")
    
    # Check 4: API key configuration
    print("4. Checking API key configuration...")
    backend_env = "backend_lite/.env"
    if os.path.exists(backend_env):
        print(f"   ✅ Backend .env file exists")
        with open(backend_env, 'r') as f:
            content = f.read()
            if 'OPENAI_API_KEY=' in content:
                if 'your_openai_api_key_here' in content or 'your_api_key_here' in content:
                    warnings.append("⚠️  OpenAI API key not configured (using placeholder)")
                elif 'sk-' in content:
                    print("   ✅ OpenAI API key appears to be configured")
                else:
                    warnings.append("⚠️  OpenAI API key format looks unusual")
            else:
                issues.append("❌ OPENAI_API_KEY not found in backend .env")
    else:
        issues.append(f"❌ Backend .env file missing: {backend_env}")
    
    # Check 5: Cache directories
    print("5. Checking cache directories...")
    cache_dirs = ['cache', 'backend_lite/cache', 'backend_lite/model_cache']
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            print(f"   ℹ️  Cache directory exists: {cache_dir}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SECURITY VERIFICATION SUMMARY")
    print("=" * 60)
    
    if issues:
        print("🚨 CRITICAL ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
        print("\n   ⚠️  DO NOT COMMIT until these issues are resolved!")
        return False
    
    if warnings:
        print("⚠️  WARNINGS:")
        for warning in warnings:
            print(f"   {warning}")
        print("\n   💡 Review these warnings before committing.")
    
    if not issues and not warnings:
        print("✅ ALL SECURITY CHECKS PASSED!")
        print("   🚀 Safe to commit to git!")
    elif not issues:
        print("✅ NO CRITICAL ISSUES FOUND")
        print("   🚀 Generally safe to commit (review warnings)")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = check_security()
    sys.exit(0 if success else 1)
