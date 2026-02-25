import subprocess
import os
import signal
import toml
import yaml
from typing import Optional

class AgentManager:
    def __init__(self, binary_path: str = "/app/bin/zeroclaw", config_dir: str = "/app/agents_config"):
        self.binary_path = binary_path
        self.config_dir = config_dir
        os.makedirs(self.config_dir, exist_ok=True)

    def _generate_config(self, agent_id: int, agent_name: str, system_prompt: str, config_data: dict):
        """Generate a ZeroClaw config.toml for a specific agent."""
        # This is a template that we'll fill with agent-specific info
        # In a real app, we'd pull Meta tokens from the config_data or DB
        config = {
            "runtime": {
                "default_provider": config_data.get("provider", "openai"),
                "default_model": config_data.get("model", "gpt-4o-mini"),
                "message_timeout_secs": 300
            },
            "api": {
                # API keys should be injected via environment variables
            },
            "channels_config": {
                "whatsapp": {
                    "access_token": config_data.get("whatsapp_token", ""),
                    "phone_number_id": config_data.get("whatsapp_phone_id", ""),
                    "verify_token": config_data.get("whatsapp_verify_token", "default_verify"),
                    "app_secret": config_data.get("whatsapp_app_secret", ""),
                    "allowed_numbers": config_data.get("allowed_numbers", [])
                }
            },
            "system": {
                "persona": system_prompt
            }
        }
        
        path = os.path.join(self.config_dir, f"agent_{agent_id}_config.toml")
        with open(path, "w") as f:
            toml.dump(config, f)
        return path

    def start_agent(self, agent_id: int, agent_name: str, system_prompt: str, config_data: dict) -> Optional[int]:
        """Start a ZeroClaw agent process and return its PID."""
        config_path = self._generate_config(agent_id, agent_name, system_prompt, config_data)
        
        # Build the command
        # zeroclaw --config <path> channel start whatsapp
        cmd = [
            self.binary_path,
            "--config", config_path,
            "channel", "start", "whatsapp"
        ]
        
        # Start as a background process
        try:
            # We use a log file to capture the agent's output for the "Intelligence Stream"
            log_path = os.path.join(self.config_dir, f"agent_{agent_id}.log")
            with open(log_path, "a") as log_file:
                process = subprocess.Popen(
                    cmd,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    preexec_fn=os.setsid # Create a new process group to allow killing sub-processes
                )
            return process.pid
        except Exception as e:
            print(f"Failed to start agent {agent_id}: {e}")
            return None

    def stop_agent(self, pid: int) -> bool:
        """Stop a running agent process."""
        try:
            # Kill the entire process group
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            return True
        except ProcessLookupError:
            return True # Already dead
        except Exception as e:
            print(f"Failed to stop agent with PID {pid}: {e}")
            return False

agent_manager = AgentManager()
