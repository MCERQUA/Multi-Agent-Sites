# Multi-Agent Claude System

A coordination framework for running multiple Claude Code agents in parallel with MCP server integration and task management.

## Overview

This system enables you to:
- Run 12+ Claude agents working autonomously
- Coordinate tasks and prevent file conflicts
- Integrate with MCP servers for enhanced capabilities
- Monitor Rust projects with cargo daemon
- Track progress through a shared todo system

## Quick Start

1. **Run the setup script:**
   ```bash
   ./setup.sh
   ```

2. **Install Rust (if needed):**
   ```bash
   ./multi-agent-setup/install-rust.sh
   ```

3. **Configure MCP servers:**
   - Edit `~/.config/claude-desktop/claude_desktop_config.json`
   - Use `config/mcp_config.json` as a template

4. **Test the setup:**
   ```bash
   ./test_setup.py
   ```

5. **Start a session:**
   ```bash
   python3 scripts/start_session.py
   ```

## Project Structure

```
multi-agent-claude/
├── scripts/              # Core coordination scripts
│   ├── start_session.py  # Main coordinator
│   ├── task_manager.py   # Task and file lock management
│   └── cargo_daemon.py   # Rust project monitoring
├── config/              # Configuration files
│   ├── agents.json      # Agent configuration
│   ├── tasks.json       # Task templates
│   └── mcp_config.json  # MCP server settings
├── logs/                # Log files
├── shared/              # Shared state files
└── context/             # Project documentation
```

## Configuration

### Agent Configuration (`config/agents.json`)

- `num_agents`: Total number of agents (default: 12)
- `agent_types`: Specializations (frontend, backend, database, etc.)
- `claude_models`: Models to use
- `max_concurrent_tasks`: Task limit per agent

### MCP Configuration (`config/mcp_config.json`)

Configure paths and tokens for:
- Obsidian vault integration
- Git repository access
- GitHub API access
- File system permissions

## Usage Examples

### Starting a Web Development Session

```bash
python3 scripts/start_session.py config/agents.json "Build a React dashboard with API backend"
```

### Running Cargo Daemon for Rust Projects

```bash
python3 scripts/cargo_daemon.py /path/to/rust/project 300
```

### Using Task Manager Standalone

```python
from scripts.task_manager import TaskManager

manager = TaskManager()
manager.claim_task("agent_1", "implement_auth")
manager.lock_file("agent_1", "src/auth.rs")
```

## Key Features

### Task Coordination
- Prevents multiple agents from working on same task
- Tracks task claims with timestamps
- Automatic cleanup of stale claims

### File Locking
- Prevents conflicting file edits
- Timestamp-based conflict resolution
- Automatic lock release on completion

### Cargo Integration
- Continuous `cargo check` monitoring
- Test result tracking
- Error and warning aggregation

### MCP Server Integration
- Obsidian for documentation access
- Git/GitHub for version control
- File system for project navigation

## Troubleshooting

### MCP Servers Not Found
The `@anthropic` namespace MCP servers may not be publicly available. Look for:
- `@modelcontextprotocol/*` packages
- Community MCP implementations
- Build from source if available

### Rust Not Installed
Run the provided install script:
```bash
./multi-agent-setup/install-rust.sh
source ~/.cargo/env
```

### EigenCode Not Available
EigenCode may not be publicly available. Alternatives:
- Check for community implementations
- Use the system without EigenCode (reduced parallel coding)
- Monitor for future releases

## Security Considerations

- Store API tokens in environment variables
- Review file system permissions in MCP config
- Monitor agent activity in logs
- Set appropriate resource limits

## Scaling Tips

1. Start with 2-3 agents for testing
2. Monitor resource usage (CPU, memory, API calls)
3. Gradually increase agent count
4. Adjust `update_interval` and `max_concurrent_tasks`
5. Use task complexity ratings for better distribution

## Future Enhancements

- [ ] Web dashboard for monitoring
- [ ] Advanced task dependency management
- [ ] Inter-agent communication protocol
- [ ] Automated test suite integration
- [ ] Cloud deployment support

## Contributing

Feel free to extend the system with:
- Additional MCP server integrations
- New agent specializations
- Enhanced coordination strategies
- Performance optimizations

## License

This coordination framework is provided as-is for educational and development purposes.