# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains two distinct projects:

1. **Eleventy Website** (`/Websites/Tempate-Base-Website/`) - A static site generator project for a contractor/construction company
2. **Multi-Agent Claude System** (`/multi-agent-claude/`) - A coordination framework for running multiple Claude agents in parallel

## Essential Commands

### Eleventy Website Project
```bash
# Navigate to website directory
cd Websites/Tempate-Base-Website/

# Install dependencies
npm install

# Start development server (http://localhost:8080)
npm start

# Build static site (outputs to _site/)
npm run build
```

### Multi-Agent System
```bash
# Navigate to multi-agent directory
cd multi-agent-claude/

# Run initial setup
./setup.sh

# Install Rust if needed
./multi-agent-setup/install-rust.sh

# Test the setup
./test_setup.py

# Start agent coordinator
python3 scripts/start_session.py

# Run cargo daemon for Rust projects
python3 scripts/cargo_daemon.py /path/to/rust/project 300
```

## High-Level Architecture

### Eleventy Website Architecture
- **Static Site Generation**: Eleventy transforms Nunjucks templates and Markdown into static HTML
- **Blog System**: Automatically generates posts from Markdown files in `src/blog/` with specific frontmatter
- **Template Structure**: Nunjucks templates in `src/_includes/` provide layouts (base.njk, post.njk)
- **Deployment**: Pre-configured for Netlify with build settings in `netlify.toml`
- **Styling**: Single CSS file at `src/css/style.css` using CSS custom properties

### Multi-Agent System Architecture
- **Coordinator Pattern**: `start_session.py` manages multiple Claude agents with task distribution
- **Task Management**: `task_manager.py` prevents conflicts with file locking and task claiming
- **Agent Types**: 12 agents specialized in frontend, backend, database, testing, and DevOps
- **MCP Integration**: Connects to Model Context Protocol servers for enhanced capabilities
- **Shared State**: Todo system and file locks stored in `shared/` directory
- **Monitoring**: Cargo daemon provides continuous Rust project health checks

### Key Integration Points
- **File Locking**: Prevents multiple agents from editing same files simultaneously
- **Task Claims**: Timestamp-based system ensures only one agent works on each task
- **Shared Todo**: Centralized task tracking across all agents
- **MCP Servers**: Provide access to Obsidian docs, Git operations, and file system

## Working with Blog Posts

When creating blog posts in the Eleventy site:
1. Place Markdown files in `Websites/Tempate-Base-Website/src/blog/`
2. Use filename format: `YYYY-MM-DD-slug-name.md`
3. Include required frontmatter:
   ```yaml
   ---
   layout: post.njk
   title: "Post Title"
   date: 2024-03-01
   author: "Author Name"
   excerpt: "Brief description"
   tags: ["tag1", "tag2"]
   ---
   ```

## Testing and Validation

The repository currently has no configured test commands. When implementing tests:
- For the Eleventy site: Consider adding HTML validation and link checking
- For the multi-agent system: Test coordination scripts with `test_setup.py`

## Important Notes

- The git status shows many files have been moved from root to `Websites/Tempate-Base-Website/`
- No linting commands are currently configured - ask user for lint commands if needed
- The multi-agent system requires Rust/Cargo for full functionality
- MCP servers may require additional setup and API tokens