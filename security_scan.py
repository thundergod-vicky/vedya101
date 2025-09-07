#!/usr/bin/env python3
"""
Security scanner for VEDYA project
Scans for hardcoded secrets, API keys, and sensitive data
"""

import os
import re
import sys
from pathlib import Path

# Secret patterns to detect
SECRET_PATTERNS = {
    'openai_key': r'sk-proj-[a-zA-Z0-9]{48,}',
    'openai_admin_key': r'sk-admin-[a-zA-Z0-9]{48,}',
    'aws_access_key': r'AKIA[0-9A-Z]{16}',
    'aws_secret_key': r'[A-Za-z0-9/+=]{40}',
    'clerk_key': r'(pk|sk)_test_[a-zA-Z0-9]{26,}',
    'jwt_token': r'eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
    'supabase_url': r'https://[a-z0-9]{20}\.supabase\.co',
    'postgres_url': r'postgres://[^:]+:[^@]+@[^/]+',
}

# Files to ignore
IGNORE_PATTERNS = [
    r'\.git/',
    r'node_modules/',
    r'__pycache__/',
    r'venv/',
    r'\.venv/',
    r'\.env/',
    r'\.next/',
    r'\.vercel/',
    r'dist/',
    r'build/',
    r'\.env$',  # We expect .env to have secrets
    r'\.env\.example$',
    r'security_scan\.py$',
    r'\.log$',
    r'\.pyc$',
    r'package-lock\.json$',
    r'yarn\.lock$',
    r'\.nft\.json$',  # Next.js build artifacts
    r'prerender-manifest\.json$',
    r'required-server-files\.json$',
]

def should_ignore_file(filepath):
    """Check if file should be ignored"""
    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, str(filepath)):
            return True
    return False

def scan_file(filepath):
    """Scan a single file for secrets"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        found_secrets = []
        for secret_type, pattern in SECRET_PATTERNS.items():
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                # Find line number
                line_num = content[:match.start()].count('\n') + 1
                found_secrets.append({
                    'type': secret_type,
                    'line': line_num,
                    'match': match.group()[:20] + '...' if len(match.group()) > 20 else match.group()
                })
        
        return found_secrets
    except Exception as e:
        print(f"Error scanning {filepath}: {e}")
        return []

def main():
    """Main scanner function"""
    project_root = Path.cwd()
    print(f"🔍 Scanning VEDYA project for hardcoded secrets...")
    print(f"📁 Project root: {project_root}")
    print()
    
    total_files = 0
    files_with_secrets = 0
    all_secrets = []
    
    # Scan all files
    for root, dirs, files in os.walk(project_root):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if not any(re.search(p, f"{root}/{d}") for p in IGNORE_PATTERNS)]
        
        for file in files:
            filepath = Path(root) / file
            
            if should_ignore_file(filepath):
                continue
                
            # Only scan text files
            if filepath.suffix in ['.py', '.js', '.ts', '.tsx', '.jsx', '.json', '.md', '.txt', '.yml', '.yaml', '.toml']:
                total_files += 1
                secrets = scan_file(filepath)
                
                if secrets:
                    files_with_secrets += 1
                    print(f"❌ {filepath}")
                    for secret in secrets:
                        print(f"   Line {secret['line']}: {secret['type']} - {secret['match']}")
                        all_secrets.append({
                            'file': str(filepath),
                            'type': secret['type'],
                            'line': secret['line']
                        })
                    print()
    
    # Summary
    print("=" * 60)
    print(f"📊 SCAN SUMMARY")
    print(f"Files scanned: {total_files}")
    print(f"Files with secrets: {files_with_secrets}")
    print(f"Total secrets found: {len(all_secrets)}")
    
    if all_secrets:
        print("\n🚨 SECURITY ISSUES FOUND!")
        print("📋 Actions needed:")
        print("1. Remove hardcoded secrets from source code")
        print("2. Use environment variables instead")
        print("3. Add files with secrets to .gitignore")
        print("4. Rotate any exposed credentials")
        
        # Group by type
        by_type = {}
        for secret in all_secrets:
            if secret['type'] not in by_type:
                by_type[secret['type']] = 0
            by_type[secret['type']] += 1
        
        print(f"\n📈 Secrets by type:")
        for secret_type, count in by_type.items():
            print(f"   {secret_type}: {count}")
        
        return 1
    else:
        print("\n✅ No hardcoded secrets found in tracked files!")
        print("💡 Remember to:")
        print("   - Keep .env files out of version control")
        print("   - Use environment variables for all secrets")
        print("   - Regularly rotate API keys")
        return 0

if __name__ == "__main__":
    sys.exit(main())
