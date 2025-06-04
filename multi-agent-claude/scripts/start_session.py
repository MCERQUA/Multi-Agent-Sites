#!/usr/bin/env python3
import json
import subprocess
import time
import os
import sys
import threading
from typing import Dict, List, Optional
from datetime import datetime
from task_manager import TaskManager
from memory_system import MemorySystem

class AgentCoordinator:
    def __init__(self, config_path: str):
        self.log_file = "logs/coordinator.log"
        self.active_agents = {}
        self.task_manager = TaskManager()
        self.memory_system = MemorySystem()
        self.running = False
        self.config = self.load_config(config_path)
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp and level"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        with open(self.log_file, 'a') as f:
            f.write(log_message + "\n")
    
    def load_config(self, path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(path, 'r') as f:
                config = json.load(f)
                self.log(f"Loaded configuration from {path}")
                return config
        except FileNotFoundError:
            self.log(f"Config file not found: {path}", "WARNING")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            "num_agents": 3,
            "agent_types": [
                {"id": "general", "count": 3, "specialization": "General development"}
            ],
            "claude_models": ["claude-3-opus-20240229"],
            "max_concurrent_tasks": 3,
            "coordination": {
                "task_assignment_strategy": "load_balanced",
                "conflict_resolution": "timestamp_based",
                "communication_interval": 60,
                "health_check_interval": 300
            }
        }
    
    def start_session(self, task_description: str):
        """Initialize multi-agent network with coordination"""
        self.log(f"=== Starting Multi-Agent Session ===")
        self.log(f"Task: {task_description}")
        self.log(f"Agents: {self.config['num_agents']}")
        
        # Update memory with session info
        self.memory_system.update_context({
            "session_start": datetime.now().isoformat(),
            "main_task": task_description,
            "num_agents": self.config['num_agents'],
            "agent_types": self.config['agent_types']
        })
        
        # Create initial task breakdown
        self.create_initial_tasks(task_description)
        
        # Initialize infrastructure
        self.setup_infrastructure()
        
        # Start agents
        self.start_agents()
        
        # Start coordination loop
        self.running = True
        self.coordinate_agents()
    
    def create_initial_tasks(self, description: str):
        """Break down main task into subtasks based on agent specializations"""
        self.log("Creating initial task breakdown...")
        
        # Analyze task to determine subtasks
        subtasks = self.analyze_and_breakdown_task(description)
        
        # Add tasks to shared todo system
        todo_data = self.task_manager.load_json(self.task_manager.todo_file)
        if "tasks" not in todo_data:
            todo_data["tasks"] = []
        
        for task in subtasks:
            todo_data["tasks"].append({
                "id": f"task_{len(todo_data['tasks']) + 1}",
                "description": task["description"],
                "type": task["type"],
                "priority": task["priority"],
                "status": "pending",
                "assigned_to": None,
                "created_at": datetime.now().isoformat()
            })
        
        self.task_manager.save_json(self.task_manager.todo_file, todo_data)
        self.log(f"Created {len(subtasks)} initial tasks")
    
    def analyze_and_breakdown_task(self, description: str) -> List[Dict]:
        """Intelligently break down task based on description"""
        subtasks = []
        
        # Detect project type and create appropriate tasks
        description_lower = description.lower()
        
        # Common initial tasks
        subtasks.append({
            "description": "Analyze project requirements and existing codebase",
            "type": "analysis",
            "priority": "high"
        })
        
        # Web development tasks
        if any(word in description_lower for word in ["web", "website", "frontend", "eleventy"]):
            subtasks.extend([
                {"description": "Set up development environment", "type": "setup", "priority": "high"},
                {"description": "Design component architecture", "type": "frontend", "priority": "medium"},
                {"description": "Implement responsive UI components", "type": "frontend", "priority": "medium"},
                {"description": "Configure build and deployment", "type": "devops", "priority": "low"}
            ])
        
        # Backend tasks
        if any(word in description_lower for word in ["api", "backend", "server", "database"]):
            subtasks.extend([
                {"description": "Design API endpoints", "type": "backend", "priority": "high"},
                {"description": "Set up database schema", "type": "backend", "priority": "high"},
                {"description": "Implement authentication", "type": "backend", "priority": "medium"}
            ])
        
        # Testing tasks
        if any(word in description_lower for word in ["test", "quality", "robust"]):
            subtasks.append({
                "description": "Create comprehensive test suite",
                "type": "testing",
                "priority": "medium"
            })
        
        return subtasks
    
    def setup_infrastructure(self):
        """Setup MCP servers and other infrastructure"""
        self.log("Setting up infrastructure...")
        
        # Check MCP servers
        self.check_mcp_servers()
        
        # Initialize EigenCode if available
        self.check_eigencode()
        
        # Load existing project context
        context = self.memory_system.get_full_context()
        self.log(f"Loaded context with {len(context['active_agents'])} previously active agents")
    
    def check_mcp_servers(self):
        """Check availability of MCP servers"""
        mcp_config = self.load_json("config/mcp_config.json")
        
        for server_name, server_config in mcp_config.get("mcpServers", {}).items():
            if server_config.get("enabled", False):
                # Check if server command exists
                command = server_config.get("command", "")
                try:
                    result = subprocess.run(["which", command], capture_output=True, text=True)
                    if result.returncode == 0:
                        self.log(f"✓ MCP server '{server_name}' available")
                    else:
                        self.log(f"✗ MCP server '{server_name}' not found", "WARNING")
                except Exception as e:
                    self.log(f"Error checking MCP server '{server_name}': {e}", "ERROR")
    
    def check_eigencode(self):
        """Check for EigenCode availability"""
        try:
            result = subprocess.run(["eigencode", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"✓ EigenCode available: {result.stdout.strip()}")
                self.memory_system.update_context({"eigencode_available": True})
            else:
                self.log("✗ EigenCode not found", "WARNING")
                self.memory_system.update_context({"eigencode_available": False})
        except FileNotFoundError:
            self.log("✗ EigenCode not installed", "WARNING")
            self.memory_system.update_context({"eigencode_available": False})
    
    def start_agents(self):
        """Initialize agent pool"""
        self.log("Initializing agent pool...")
        
        agent_count = 0
        for agent_type in self.config["agent_types"]:
            for i in range(agent_type["count"]):
                agent_id = f"{agent_type['id']}_agent_{i}"
                self.active_agents[agent_id] = {
                    "id": agent_id,
                    "type": agent_type["id"],
                    "specialization": agent_type["specialization"],
                    "status": "idle",
                    "current_task": None,
                    "tasks_completed": 0,
                    "started_at": datetime.now().isoformat()
                }
                
                # Update memory with agent state
                self.memory_system.update_agent_state(agent_id, {
                    "type": agent_type["id"],
                    "specialization": agent_type["specialization"],
                    "status": "idle"
                })
                
                agent_count += 1
                self.log(f"Initialized {agent_id} ({agent_type['specialization']})")
        
        self.log(f"Agent pool ready with {agent_count} agents")
    
    def coordinate_agents(self):
        """Main coordination loop"""
        self.log("Starting coordination loop...")
        
        # Start monitoring threads
        monitor_thread = threading.Thread(target=self.monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Start task assignment thread
        assignment_thread = threading.Thread(target=self.task_assignment_loop)
        assignment_thread.daemon = True
        assignment_thread.start()
        
        try:
            while self.running:
                # Main coordination logic
                time.sleep(1)
                
                # Check for user input
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    line = sys.stdin.readline().strip()
                    if line.lower() == 'quit':
                        self.log("Shutdown requested by user")
                        self.shutdown()
                    elif line.lower() == 'status':
                        self.print_status()
        except KeyboardInterrupt:
            self.log("Interrupted by user")
            self.shutdown()
        except Exception as e:
            self.log(f"Coordination error: {e}", "ERROR")
            self.shutdown()
    
    def monitor_loop(self):
        """Monitor agent health and progress"""
        while self.running:
            try:
                # Check agent health
                for agent_id, agent in self.active_agents.items():
                    if agent["status"] == "working" and agent["current_task"]:
                        # Check if task is still valid
                        if not self.task_manager.is_task_claimed(agent["current_task"]):
                            self.log(f"Task {agent['current_task']} no longer claimed by {agent_id}", "WARNING")
                            agent["status"] = "idle"
                            agent["current_task"] = None
                
                # Log periodic status
                if int(time.time()) % 60 == 0:  # Every minute
                    self.log_status_summary()
                
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                self.log(f"Monitor error: {e}", "ERROR")
    
    def task_assignment_loop(self):
        """Assign tasks to idle agents"""
        while self.running:
            try:
                # Get pending tasks
                todo_data = self.task_manager.load_json(self.task_manager.todo_file)
                pending_tasks = [t for t in todo_data.get("tasks", []) if t["status"] == "pending"]
                
                # Get idle agents
                idle_agents = [a for a in self.active_agents.values() if a["status"] == "idle"]
                
                # Assign tasks based on strategy
                if pending_tasks and idle_agents:
                    self.assign_tasks(pending_tasks, idle_agents)
                
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                self.log(f"Assignment error: {e}", "ERROR")
    
    def assign_tasks(self, tasks: List[Dict], agents: List[Dict]):
        """Intelligently assign tasks to agents"""
        strategy = self.config.get("coordination", {}).get("task_assignment_strategy", "load_balanced")
        
        for task in tasks:
            if not agents:
                break
                
            # Find best agent for task
            best_agent = self.find_best_agent_for_task(task, agents)
            
            if best_agent:
                # Try to claim task
                if self.task_manager.claim_task(best_agent["id"], task["id"]):
                    best_agent["status"] = "working"
                    best_agent["current_task"] = task["id"]
                    
                    # Update task status
                    task["status"] = "in_progress"
                    task["assigned_to"] = best_agent["id"]
                    
                    # Update memory
                    self.memory_system.update_agent_state(best_agent["id"], {
                        "status": "working",
                        "current_task": task["id"],
                        "task_description": task["description"]
                    })
                    
                    self.log(f"Assigned task '{task['description']}' to {best_agent['id']}")
                    
                    # Remove agent from idle list
                    agents.remove(best_agent)
    
    def find_best_agent_for_task(self, task: Dict, agents: List[Dict]) -> Optional[Dict]:
        """Find the most suitable agent for a task"""
        task_type = task.get("type", "general")
        
        # First, try to find specialist
        for agent in agents:
            if agent["type"] == task_type:
                return agent
        
        # Then, try general agents
        for agent in agents:
            if agent["type"] == "general":
                return agent
        
        # Finally, any agent
        return agents[0] if agents else None
    
    def log_status_summary(self):
        """Log current system status"""
        todo_data = self.task_manager.load_json(self.task_manager.todo_file)
        tasks = todo_data.get("tasks", [])
        
        status_counts = {
            "pending": len([t for t in tasks if t["status"] == "pending"]),
            "in_progress": len([t for t in tasks if t["status"] == "in_progress"]),
            "completed": len([t for t in tasks if t["status"] == "completed"])
        }
        
        agent_status = {
            "idle": len([a for a in self.active_agents.values() if a["status"] == "idle"]),
            "working": len([a for a in self.active_agents.values() if a["status"] == "working"])
        }
        
        self.log(f"Status - Tasks: {status_counts} | Agents: {agent_status}")
    
    def print_status(self):
        """Print detailed status"""
        print("\n=== Multi-Agent System Status ===")
        print(f"Agents: {len(self.active_agents)}")
        for agent_id, agent in self.active_agents.items():
            print(f"  {agent_id}: {agent['status']} - Task: {agent['current_task'] or 'None'}")
        
        todo_data = self.task_manager.load_json(self.task_manager.todo_file)
        tasks = todo_data.get("tasks", [])
        print(f"\nTasks: {len(tasks)}")
        for task in tasks:
            print(f"  {task['id']}: {task['status']} - {task['description'][:50]}...")
        print()
    
    def shutdown(self):
        """Gracefully shutdown the system"""
        self.log("Shutting down coordinator...")
        self.running = False
        
        # Save final state
        self.memory_system.update_context({
            "session_end": datetime.now().isoformat(),
            "agents_final_state": self.active_agents
        })
        
        # Release all locks
        for agent_id, agent in self.active_agents.items():
            if agent["current_task"]:
                self.task_manager.release_task(agent_id, agent["current_task"])
        
        self.log("Coordinator shutdown complete")
    
    def load_json(self, filepath: str) -> Dict:
        """Load JSON file safely"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.log(f"Error loading {filepath}: {e}", "ERROR")
            return {}

if __name__ == "__main__":
    import select
    
    # Ensure directories exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("shared", exist_ok=True)
    os.makedirs("shared/memory", exist_ok=True)
    
    # Check if config path is provided
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/agents.json"
    
    # Create coordinator
    coordinator = AgentCoordinator(config_path)
    
    # Get task description
    if len(sys.argv) > 2:
        task_description = sys.argv[2]
    else:
        task_description = input("Enter task description: ")
    
    # Start session
    coordinator.start_session(task_description)