#!/usr/bin/env python3
import subprocess
import time
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

class CargoDaemon:
    def __init__(self, project_path: str, update_interval: int = 300):
        self.project_path = project_path
        self.update_interval = update_interval
        self.log_file = "logs/cargo_status.json"
        self.history_file = "logs/cargo_history.json"
        self.max_history = 100  # Keep last 100 check results
        
        # Create logs directory
        os.makedirs("logs", exist_ok=True)
        
        # Load history
        self.history = self.load_history()
    
    def load_history(self) -> List[Dict]:
        """Load check history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def run_cargo_check(self) -> Dict:
        """Run cargo check and capture output"""
        try:
            # First check if project path exists
            if not os.path.exists(self.project_path):
                return {
                    "timestamp": datetime.now().isoformat(),
                    "success": False,
                    "error": f"Project path does not exist: {self.project_path}"
                }
            
            # Check if it's a cargo project
            cargo_toml = os.path.join(self.project_path, "Cargo.toml")
            if not os.path.exists(cargo_toml):
                return {
                    "timestamp": datetime.now().isoformat(),
                    "success": False,
                    "error": f"No Cargo.toml found in {self.project_path}"
                }
            
            # Run cargo check
            result = subprocess.run(
                ["cargo", "check", "--message-format=json"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            # Parse JSON output
            messages = []
            errors = []
            warnings = []
            
            for line in result.stdout.splitlines():
                try:
                    msg = json.loads(line)
                    if msg.get("reason") == "compiler-message":
                        level = msg["message"]["level"]
                        if level == "error":
                            errors.append(msg["message"])
                        elif level == "warning":
                            warnings.append(msg["message"])
                        messages.append(msg["message"])
                except json.JSONDecodeError:
                    continue
            
            return {
                "timestamp": datetime.now().isoformat(),
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "error_count": len(errors),
                "warning_count": len(warnings),
                "messages": messages[:10],  # Keep only first 10 messages
                "stderr": result.stderr if result.stderr else None
            }
            
        except FileNotFoundError:
            return {
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": "Cargo not found. Please install Rust and Cargo."
            }
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
    
    def run_cargo_test(self) -> Dict:
        """Run cargo test and capture results"""
        try:
            result = subprocess.run(
                ["cargo", "test", "--", "--format=json"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            test_results = {
                "passed": 0,
                "failed": 0,
                "ignored": 0
            }
            
            # Parse test output
            for line in result.stdout.splitlines():
                if "test result:" in line:
                    # Extract test summary
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed;":
                            test_results["passed"] = int(parts[i-1])
                        elif part == "failed;":
                            test_results["failed"] = int(parts[i-1])
                        elif part == "ignored":
                            test_results["ignored"] = int(parts[i-1])
            
            return {
                "timestamp": datetime.now().isoformat(),
                "success": result.returncode == 0,
                "test_results": test_results,
                "stdout": result.stdout[-1000:],  # Last 1000 chars
                "stderr": result.stderr[-1000:] if result.stderr else None
            }
            
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
    
    def update_logs(self):
        """Update cargo logs"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running cargo check...")
        
        # Run checks
        check_status = self.run_cargo_check()
        test_status = self.run_cargo_test() if check_status["success"] else None
        
        # Combine results
        status = {
            "timestamp": datetime.now().isoformat(),
            "check": check_status,
            "test": test_status
        }
        
        # Save current status
        with open(self.log_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        # Add to history
        self.history.append(status)
        
        # Trim history if needed
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        # Save history
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
        
        # Print summary
        if check_status["success"]:
            print(f"✓ Cargo check passed")
            if test_status:
                tests = test_status.get("test_results", {})
                print(f"✓ Tests: {tests.get('passed', 0)} passed, {tests.get('failed', 0)} failed")
        else:
            print(f"✗ Cargo check failed: {check_status.get('error', 'Unknown error')}")
            if "error_count" in check_status:
                print(f"  Errors: {check_status['error_count']}, Warnings: {check_status['warning_count']}")
    
    def run(self):
        """Main daemon loop"""
        print(f"Starting Cargo daemon for: {self.project_path}")
        print(f"Update interval: {self.update_interval} seconds")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                self.update_logs()
                time.sleep(self.update_interval)
        except KeyboardInterrupt:
            print("\nStopping Cargo daemon...")
            sys.exit(0)

if __name__ == "__main__":
    # Get project path from command line or use current directory
    project_path = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    
    # Get update interval from command line or use default
    update_interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    
    daemon = CargoDaemon(project_path, update_interval)
    daemon.run()