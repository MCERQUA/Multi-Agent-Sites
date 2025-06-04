#!/usr/bin/env python3
import json
import threading
import time
import os
from typing import Dict, Set, Optional, List
from datetime import datetime

class TaskManager:
    def __init__(self):
        self.todo_file = "shared/todo_system.json"
        self.locks_file = "shared/file_locks.json"
        self.claimed_tasks = {}
        self.file_locks = {}
        self.lock = threading.Lock()
        
        # Create shared directory if it doesn't exist
        os.makedirs("shared", exist_ok=True)
        
        # Load existing state
        self.load_state()
    
    def load_state(self):
        """Load existing task claims and file locks"""
        if os.path.exists(self.todo_file):
            with open(self.todo_file, 'r') as f:
                data = json.load(f)
                self.claimed_tasks = data.get("claimed_tasks", {})
        
        if os.path.exists(self.locks_file):
            with open(self.locks_file, 'r') as f:
                self.file_locks = json.load(f)
    
    def claim_task(self, agent_id: str, task_id: str) -> bool:
        """Claim a task for an agent"""
        with self.lock:
            if task_id not in self.claimed_tasks:
                self.claimed_tasks[task_id] = {
                    "agent_id": agent_id,
                    "claimed_at": datetime.now().isoformat()
                }
                self.save_claimed_tasks()
                print(f"Task {task_id} claimed by {agent_id}")
                return True
            else:
                print(f"Task {task_id} already claimed by {self.claimed_tasks[task_id]['agent_id']}")
                return False
    
    def release_task(self, agent_id: str, task_id: str):
        """Release a claimed task"""
        with self.lock:
            if task_id in self.claimed_tasks and self.claimed_tasks[task_id]["agent_id"] == agent_id:
                del self.claimed_tasks[task_id]
                self.save_claimed_tasks()
                print(f"Task {task_id} released by {agent_id}")
    
    def lock_file(self, agent_id: str, file_path: str) -> bool:
        """Lock a file for exclusive editing"""
        with self.lock:
            if file_path not in self.file_locks:
                self.file_locks[file_path] = {
                    "agent_id": agent_id,
                    "locked_at": datetime.now().isoformat()
                }
                self.save_file_locks()
                print(f"File {file_path} locked by {agent_id}")
                return True
            else:
                print(f"File {file_path} already locked by {self.file_locks[file_path]['agent_id']}")
                return False
    
    def release_file_lock(self, agent_id: str, file_path: str):
        """Release file lock"""
        with self.lock:
            if file_path in self.file_locks and self.file_locks[file_path]["agent_id"] == agent_id:
                del self.file_locks[file_path]
                self.save_file_locks()
                print(f"File {file_path} unlocked by {agent_id}")
    
    def get_available_tasks(self) -> List[str]:
        """Get list of unclaimed tasks"""
        # Load current todo system
        if os.path.exists(self.todo_file):
            with open(self.todo_file, 'r') as f:
                todo_data = json.load(f)
                all_tasks = [task["id"] for task in todo_data.get("tasks", [])]
                return [task_id for task_id in all_tasks if str(task_id) not in self.claimed_tasks]
        return []
    
    def get_locked_files(self) -> Dict[str, str]:
        """Get dictionary of locked files and their owners"""
        return {path: info["agent_id"] for path, info in self.file_locks.items()}
    
    def save_claimed_tasks(self):
        """Save claimed tasks to todo file"""
        todo_data = {"tasks": [], "claimed_tasks": self.claimed_tasks}
        
        # Load existing tasks if file exists
        if os.path.exists(self.todo_file):
            with open(self.todo_file, 'r') as f:
                existing = json.load(f)
                todo_data["tasks"] = existing.get("tasks", [])
        
        with open(self.todo_file, 'w') as f:
            json.dump(todo_data, f, indent=2)
    
    def save_file_locks(self):
        """Save file locks to file"""
        with open(self.locks_file, 'w') as f:
            json.dump(self.file_locks, f, indent=2)
    
    def cleanup_stale_locks(self, timeout_hours: int = 24):
        """Clean up locks older than timeout_hours"""
        current_time = datetime.now()
        stale_locks = []
        
        with self.lock:
            # Check file locks
            for file_path, lock_info in self.file_locks.items():
                lock_time = datetime.fromisoformat(lock_info["locked_at"])
                if (current_time - lock_time).total_seconds() > timeout_hours * 3600:
                    stale_locks.append(("file", file_path))
            
            # Check task claims
            for task_id, claim_info in self.claimed_tasks.items():
                claim_time = datetime.fromisoformat(claim_info["claimed_at"])
                if (current_time - claim_time).total_seconds() > timeout_hours * 3600:
                    stale_locks.append(("task", task_id))
            
            # Remove stale locks
            for lock_type, lock_id in stale_locks:
                if lock_type == "file":
                    print(f"Removing stale file lock: {lock_id}")
                    del self.file_locks[lock_id]
                else:
                    print(f"Removing stale task claim: {lock_id}")
                    del self.claimed_tasks[lock_id]
            
            if stale_locks:
                self.save_file_locks()
                self.save_claimed_tasks()
    
    def is_task_claimed(self, task_id: str) -> bool:
        """Check if a task is currently claimed"""
        return task_id in self.claimed_tasks
    
    def save_json(self, filepath: str, data: Dict):
        """Save JSON data to file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_json(self, filepath: str) -> Dict:
        """Load JSON data from file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}

# Example usage
if __name__ == "__main__":
    manager = TaskManager()
    
    # Example: Agent 1 claims a task
    if manager.claim_task("agent_1", "task_001"):
        print("Successfully claimed task_001")
    
    # Example: Agent 2 tries to claim same task
    if not manager.claim_task("agent_2", "task_001"):
        print("Could not claim task_001")
    
    # Example: Agent 1 locks a file
    if manager.lock_file("agent_1", "/path/to/file.py"):
        print("Successfully locked file.py")
    
    # Show available tasks
    print("\nAvailable tasks:", manager.get_available_tasks())
    
    # Show locked files
    print("Locked files:", manager.get_locked_files())
    
    # Clean up old locks
    manager.cleanup_stale_locks()