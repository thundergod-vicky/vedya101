#!/usr/bin/env python3
"""
cleanup.py
Utility script to remove testing files and consolidate the codebase.
"""

import os
import sys
import glob
import shutil
from datetime import datetime

# Files to clean up
TEMP_TEST_FILES = [
    "model_access_check.js",
    "compare_openai_keys.js",
    "model_check_result.json",
    "model_test_report.txt",
    "model_test_results.json",
    "diagnose_openai_key.py",
    "comprehensive_model_test.py", 
    "quick_model_test.py",
    "test_models.py",
    "test_openai.py",
    "test_openai_new.py",
    "test_openai_models.py",
    "demo_agents.py",
    "demo_langgraph.py",
    "terminal_chat.py",
    "final_test.py"
]

# Testing and verification files that can be moved to a tests folder
TEST_FILES = [
    "test_ai_planning.py",
    "test_ai_planning_dict.py",
    "test_clerk_flow.py",
    "test_conversational_chat.py",
    "test_email.py",
    "test_langgraph_quick.py",
    "test_planning_agent.py",
    "test_api.py",
    "validate_langgraph.py",
    "verify_ses_emails.py",
    "verify_supabase.py"
]

def create_backup_folder():
    """Create a timestamped backup folder."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"cleanup_backup_{timestamp}"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    return backup_dir

def backup_and_remove_files(file_list, backup_dir):
    """Backup files to backup folder and remove from main directory."""
    removed = []
    not_found = []

    for filename in file_list:
        if os.path.exists(filename):
            shutil.copy2(filename, os.path.join(backup_dir, filename))
            os.remove(filename)
            removed.append(filename)
        else:
            not_found.append(filename)

    return removed, not_found

def organize_test_files(file_list, backup_dir):
    """Move test files to tests folder, backing up first."""
    tests_dir = "tests"
    if not os.path.exists(tests_dir):
        os.makedirs(tests_dir)
    
    moved = []
    not_found = []

    for filename in file_list:
        if os.path.exists(filename):
            # Backup first
            shutil.copy2(filename, os.path.join(backup_dir, filename))
            
            # Move to tests folder
            shutil.copy2(filename, os.path.join(tests_dir, filename))
            os.remove(filename)
            moved.append(filename)
        else:
            not_found.append(filename)

    return tests_dir, moved, not_found

def main():
    print("VEDYA Project Cleanup")
    print("=====================")
    
    # Ask for confirmation
    confirm = input("This will move test files to a 'tests' folder and remove temporary files.\nA backup will be created. Continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    # Create backup folder
    backup_dir = create_backup_folder()
    print(f"Created backup directory: {backup_dir}")
    
    # Remove temporary test files
    removed, not_found = backup_and_remove_files(TEMP_TEST_FILES, backup_dir)
    print(f"\nRemoved {len(removed)} temporary files:")
    for f in removed:
        print(f"  - {f}")
    
    if not_found:
        print(f"\nNot found ({len(not_found)} files):")
        for f in not_found:
            print(f"  - {f}")
    
    # Organize test files into tests folder
    tests_dir, moved, not_found = organize_test_files(TEST_FILES, backup_dir)
    print(f"\nMoved {len(moved)} test files to {tests_dir}/:")
    for f in moved:
        print(f"  - {f}")
    
    if not_found:
        print(f"\nTest files not found ({len(not_found)} files):")
        for f in not_found:
            print(f"  - {f}")
    
    print(f"\nAll files backed up to: {backup_dir}")
    print("\nCleanup complete!")

if __name__ == "__main__":
    main()
