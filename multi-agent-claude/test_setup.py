#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.task_manager import TaskManager

print("Testing Task Manager...")
manager = TaskManager()

# Test task claiming
if manager.claim_task("test_agent", "test_task"):
    print("✓ Task claiming works")
    manager.release_task("test_agent", "test_task")
else:
    print("✗ Task claiming failed")

# Test file locking
if manager.lock_file("test_agent", "test_file.py"):
    print("✓ File locking works")
    manager.release_file_lock("test_agent", "test_file.py")
else:
    print("✗ File locking failed")

print("\nBasic setup test complete!")
