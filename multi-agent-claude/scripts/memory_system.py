#!/usr/bin/env python3
import json
import os
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional

class MemorySystem:
    """Shared memory system for multi-agent coordination"""
    
    def __init__(self):
        self.memory_dir = "shared/memory"
        self.context_file = "shared/memory/context.json"
        self.knowledge_base = "shared/memory/knowledge_base.json"
        self.agent_states = "shared/memory/agent_states.json"
        self.project_state = "shared/memory/project_state.json"
        self.lock = threading.Lock()
        
        # Create memory directory
        os.makedirs(self.memory_dir, exist_ok=True)
        
        # Initialize memory structures
        self.initialize_memory()
    
    def initialize_memory(self):
        """Initialize memory structures if they don't exist"""
        # Context memory - stores current project context
        if not os.path.exists(self.context_file):
            self.save_json(self.context_file, {
                "project_type": None,
                "current_phase": None,
                "tech_stack": [],
                "dependencies": {},
                "file_structure": {},
                "last_updated": datetime.now().isoformat()
            })
        
        # Knowledge base - stores learned patterns and solutions
        if not os.path.exists(self.knowledge_base):
            self.save_json(self.knowledge_base, {
                "patterns": {},
                "solutions": {},
                "errors_encountered": {},
                "best_practices": {}
            })
        
        # Agent states - tracks what each agent knows/is doing
        if not os.path.exists(self.agent_states):
            self.save_json(self.agent_states, {})
        
        # Project state - overall project progress
        if not os.path.exists(self.project_state):
            self.save_json(self.project_state, {
                "completed_tasks": [],
                "current_tasks": [],
                "pending_tasks": [],
                "blockers": [],
                "decisions_made": []
            })
    
    def save_json(self, filepath: str, data: Dict):
        """Thread-safe JSON save"""
        with self.lock:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
    
    def load_json(self, filepath: str) -> Dict:
        """Thread-safe JSON load"""
        with self.lock:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
            return {}
    
    def update_context(self, updates: Dict):
        """Update project context"""
        context = self.load_json(self.context_file)
        context.update(updates)
        context["last_updated"] = datetime.now().isoformat()
        self.save_json(self.context_file, context)
    
    def add_knowledge(self, category: str, key: str, value: Any):
        """Add to knowledge base"""
        kb = self.load_json(self.knowledge_base)
        if category not in kb:
            kb[category] = {}
        kb[category][key] = value
        self.save_json(self.knowledge_base, kb)
    
    def update_agent_state(self, agent_id: str, state: Dict):
        """Update individual agent state"""
        states = self.load_json(self.agent_states)
        states[agent_id] = {
            **state,
            "last_active": datetime.now().isoformat()
        }
        self.save_json(self.agent_states, states)
    
    def get_agent_state(self, agent_id: str) -> Optional[Dict]:
        """Get agent state"""
        states = self.load_json(self.agent_states)
        return states.get(agent_id)
    
    def update_project_state(self, updates: Dict):
        """Update overall project state"""
        state = self.load_json(self.project_state)
        for key, value in updates.items():
            if key in state:
                if isinstance(state[key], list):
                    if isinstance(value, list):
                        state[key].extend(value)
                    else:
                        state[key].append(value)
                else:
                    state[key] = value
        self.save_json(self.project_state, state)
    
    def get_full_context(self) -> Dict:
        """Get complete context for new agents"""
        return {
            "context": self.load_json(self.context_file),
            "knowledge_base": self.load_json(self.knowledge_base),
            "project_state": self.load_json(self.project_state),
            "active_agents": list(self.load_json(self.agent_states).keys())
        }
    
    def log_decision(self, agent_id: str, decision: str, reasoning: str):
        """Log important decisions made by agents"""
        state = self.load_json(self.project_state)
        state["decisions_made"].append({
            "agent_id": agent_id,
            "decision": decision,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat()
        })
        self.save_json(self.project_state, state)
    
    def get_relevant_knowledge(self, task_type: str) -> Dict:
        """Get knowledge relevant to a specific task"""
        kb = self.load_json(self.knowledge_base)
        relevant = {}
        
        # Simple relevance matching - can be enhanced
        for category, items in kb.items():
            if task_type.lower() in category.lower():
                relevant[category] = items
            else:
                # Check individual items
                relevant_items = {}
                for key, value in items.items():
                    if task_type.lower() in key.lower():
                        relevant_items[key] = value
                if relevant_items:
                    relevant[category] = relevant_items
        
        return relevant

if __name__ == "__main__":
    # Test the memory system
    memory = MemorySystem()
    
    # Test context update
    memory.update_context({
        "project_type": "web_development",
        "tech_stack": ["Eleventy", "Node.js", "CSS"]
    })
    
    # Test knowledge addition
    memory.add_knowledge("patterns", "eleventy_blog", {
        "structure": "src/blog/*.md",
        "frontmatter": ["title", "date", "author", "excerpt", "tags"]
    })
    
    # Test agent state
    memory.update_agent_state("agent_1", {
        "current_task": "implement_feature",
        "files_editing": ["src/index.njk"],
        "knowledge_gained": ["eleventy_structure"]
    })
    
    print("Memory system initialized and tested!")
    print("\nFull context:")
    print(json.dumps(memory.get_full_context(), indent=2))