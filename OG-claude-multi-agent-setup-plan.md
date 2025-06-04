# Multi-Agent Claude Code Setup Plan

## Overview
This plan will help you replicate @DionysianAgent's setup: 12+ Claude 4 agents working autonomously with EigenCode integration, MCP servers, and coordination mechanisms for web development and general coding tasks.

## Prerequisites ✅
- [x] Claude Code Max account 
- [x] VS Code installed
- [ ] Rust/Cargo installed (for EigenCode and daemons)
- [ ] Node.js/npm (for some MCP servers)
- [ ] Git configured

## Phase 1: Core Infrastructure Setup

### 1.1 Install Rust and Cargo
```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Verify installation
rustc --version
cargo --version
```

### 1.2 Install Node.js (if not already installed)
```bash
# Using Node Version Manager (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install --lts
nvm use --lts
```

## Phase 2: MCP Server Setup

### 2.1 Install Claude Desktop (for MCP)
- Download from Anthropic's website
- This provides the MCP infrastructure needed

### 2.2 Set Up Required MCP Servers

#### A. Obsidian MCP Server
```bash
# Install Obsidian MCP server
npm install -g @anthropic/mcp-server-obsidian
```

#### B. Git/GitHub MCP Servers
```bash
# Install Git MCP server
npm install -g @anthropic/mcp-server-git
# Install GitHub MCP server  
npm install -g @anthropic/mcp-server-github
```

#### C. File System MCP Server
```bash
# For file operations
npm install -g @anthropic/mcp-server-filesystem
```

### 2.3 Configure MCP in Claude Desktop
Create/edit `~/.config/claude-desktop/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "obsidian": {
      "command": "mcp-server-obsidian",
      "args": ["--vault-path", "/path/to/your/obsidian/vault"]
    },
    "git": {
      "command": "mcp-server-git",
      "args": ["--repository", "/path/to/your/project"]
    },
    "github": {
      "command": "mcp-server-github",
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    },
    "filesystem": {
      "command": "mcp-server-filesystem",
      "args": ["--allowed-directory", "/path/to/your/projects"]
    }
  }
}
```

## Phase 3: EigenCode Setup

### 3.1 Research and Install EigenCode
```bash
# First, check if EigenCode is available via cargo
cargo search eigencode

# If available, install it:
cargo install eigencode

# If not available publicly, check:
# - Official EigenCode website/GitHub
# - Alternative: Build from source if open-sourced
```

### 3.2 Configure EigenCode
- Set up API keys for multiple AI providers
- Configure parallel coding settings
- Test basic functionality

## Phase 4: Core Scripts Development

### 4.1 Create Project Structure
```
multi-agent-claude/
├── scripts/
│   ├── start_session.py
│   ├── cargo_daemon.py
│   └── agent_coordinator.py
├── config/
│   ├── agents.json
│   ├── tasks.json
│   └── mcp_config.json
├── logs/
├── shared/
│   ├── todo_system.json
│   └── file_locks.json
└── context/
    ├── documentation/
    └── project_specs/
```

### 4.2 Start Session Script
Create `scripts/start_session.py`:
```python
#!/usr/bin/env python3
import json
import subprocess
import time
from typing import Dict, List

class AgentCoordinator:
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.active_agents = {}
        self.file_locks = {}
        self.todo_system = self.load_todo_system()
    
    def load_config(self, path: str) -> Dict:
        with open(path, 'r') as f:
            return json.load(f)
    
    def start_session(self, task_description: str):
        """Initialize multi-agent network"""
        print(f"Starting session for: {task_description}")
        
        # Load context from MCP servers
        self.load_context()
        
        # Setup MCP bridges
        self.setup_mcp_bridges()
        
        # Initialize EigenCode
        self.init_eigencode()
        
        # Start agents
        self.start_agents()
    
    def load_context(self):
        """Load context from various sources"""
        # Implementation for loading documentation, specs, etc.
        pass
    
    def setup_mcp_bridges(self):
        """Setup MCP bridges to tools"""
        # Implementation for MCP setup
        pass
    
    def init_eigencode(self):
        """Initialize EigenCode for parallel coding"""
        # Implementation for EigenCode initialization
        pass
    
    def start_agents(self):
        """Start multiple Claude agents"""
        for i in range(self.config['num_agents']):
            agent_id = f"agent_{i}"
            # Start agent process
            self.active_agents[agent_id] = self.spawn_agent(agent_id)
    
    def spawn_agent(self, agent_id: str):
        """Spawn individual Claude agent"""
        # Implementation for starting Claude Code sessions
        pass

if __name__ == "__main__":
    coordinator = AgentCoordinator("config/agents.json")
    coordinator.start_session("web_development_project")
```

### 4.3 Cargo Daemon Script
Create `scripts/cargo_daemon.py`:
```python
#!/usr/bin/env python3
import subprocess
import time
import json
from datetime import datetime

class CargoDaemon:
    def __init__(self, project_path: str, update_interval: int = 300):
        self.project_path = project_path
        self.update_interval = update_interval
        self.log_file = "logs/cargo_status.json"
    
    def run_cargo_check(self):
        """Run cargo check and capture output"""
        try:
            result = subprocess.run(
                ["cargo", "check", "--message-format=json"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            return {
                "timestamp": datetime.now().isoformat(),
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
    
    def update_logs(self):
        """Update cargo logs"""
        status = self.run_cargo_check()
        with open(self.log_file, 'w') as f:
            json.dump(status, f, indent=2)
        print(f"Updated cargo logs at {status['timestamp']}")
    
    def run(self):
        """Main daemon loop"""
        print(f"Starting Cargo daemon with {self.update_interval}s intervals")
        while True:
            self.update_logs()
            time.sleep(self.update_interval)

if __name__ == "__main__":
    daemon = CargoDaemon("/path/to/your/rust/project")
    daemon.run()
```

### 4.4 Task and File Lock Management
Create `scripts/task_manager.py`:
```python
#!/usr/bin/env python3
import json
import threading
import time
from typing import Dict, Set, Optional

class TaskManager:
    def __init__(self):
        self.todo_file = "shared/todo_system.json"
        self.locks_file = "shared/file_locks.json"
        self.claimed_tasks = {}
        self.file_locks = {}
        self.lock = threading.Lock()
    
    def claim_task(self, agent_id: str, task_id: str) -> bool:
        """Claim a task for an agent"""
        with self.lock:
            if task_id not in self.claimed_tasks:
                self.claimed_tasks[task_id] = agent_id
                self.save_claimed_tasks()
                return True
            return False
    
    def lock_file(self, agent_id: str, file_path: str) -> bool:
        """Lock a file for exclusive editing"""
        with self.lock:
            if file_path not in self.file_locks:
                self.file_locks[file_path] = agent_id
                self.save_file_locks()
                return True
            return False
    
    def release_file_lock(self, agent_id: str, file_path: str):
        """Release file lock"""
        with self.lock:
            if self.file_locks.get(file_path) == agent_id:
                del self.file_locks[file_path]
                self.save_file_locks()
    
    def save_claimed_tasks(self):
        with open(self.todo_file, 'w') as f:
            json.dump(self.claimed_tasks, f, indent=2)
    
    def save_file_locks(self):
        with open(self.locks_file, 'w') as f:
            json.dump(self.file_locks, f, indent=2)
```

## Phase 5: Configuration Files

### 5.1 Agent Configuration
Create `config/agents.json`:
```json
{
  "num_agents": 12,
  "agent_types": [
    {"id": "frontend", "count": 3, "specialization": "React/Vue/Angular"},
    {"id": "backend", "count": 3, "specialization": "Node.js/Python/Rust"},
    {"id": "database", "count": 2, "specialization": "MongoDB/PostgreSQL"},
    {"id": "testing", "count": 2, "specialization": "Unit/Integration tests"},
    {"id": "devops", "count": 2, "specialization": "Docker/CI-CD"}
  ],
  "claude_models": ["claude-sonnet-4", "claude-opus-4"],
  "max_concurrent_tasks": 5
}
```

### 5.2 Task Templates
Create `config/tasks.json`:
```json
{
  "web_development": {
    "frontend_tasks": [
      "Create React components",
      "Implement responsive design",
      "Add state management",
      "Optimize performance"
    ],
    "backend_tasks": [
      "Design API endpoints",
      "Implement authentication",
      "Database integration",
      "Add error handling"
    ],
    "general_tasks": [
      "Write documentation",
      "Create tests",
      "Code review",
      "Performance optimization"
    ]
  }
}
```

## Phase 6: Testing and Validation

### 6.1 Simple Test Setup
1. Create a test project structure
2. Run the start session script with 2-3 agents initially
3. Monitor agent coordination and file locking
4. Validate MCP server connections

### 6.2 Incremental Scaling
1. Start with 3 agents
2. Gradually increase to 6, then 9, then 12
3. Monitor performance and coordination at each step
4. Adjust timing and coordination parameters

## Phase 7: Optimization and Monitoring

### 7.1 Create Monitoring Dashboard
- Agent status tracking
- Task completion rates
- File lock conflicts
- Resource usage

### 7.2 Performance Tuning
- Adjust agent spawn timing
- Optimize context loading
- Fine-tune coordination mechanisms

## Security and Cost Considerations

### Security
- Store API keys securely using environment variables
- Implement proper access controls for file operations
- Monitor for unusual activity patterns

### Cost Management
- Set usage limits for Claude API calls
- Monitor monthly spending
- Implement circuit breakers for excessive usage

## Next Steps

1. **Phase 1-2**: Set up infrastructure and MCP servers
2. **Phase 3**: Research and install EigenCode
3. **Phase 4**: Develop core coordination scripts
4. **Phase 5**: Create configuration files
5. **Phase 6**: Test with small agent count
6. **Phase 7**: Scale up and optimize

## Troubleshooting Resources

- Anthropic's MCP documentation
- Claude Desktop configuration guides
- EigenCode documentation (when available)
- Rust/Cargo documentation for daemon setup

## Expected Challenges

1. **EigenCode availability**: May need to find alternatives or build from source
2. **MCP server compatibility**: May require version-specific configurations
3. **Agent coordination**: Complex timing and synchronization issues
4. **Resource management**: High CPU/memory usage with 12+ agents
5. **API rate limits**: Managing multiple concurrent Claude sessions

Start with Phase 1 and we can iterate on each component as you progress!