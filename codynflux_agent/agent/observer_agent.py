# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""Observer Agent - Information gathering and system observation agent."""

from typing import Optional, Dict, Any, List
import os
import json

from ..utils.config import Config
from ..utils.llm_basics import LLMMessage
from .multi_agent_base import (
    MultiAgent, AgentRole, AgentMessage, MessageType, AgentStatus,
    MultiAgentCommunicationHub
)


class ObserverAgent(MultiAgent):
    """
    Observer Agent (觀察者) - Information gathering and system observation.
    
    Responsibilities:
    - Gather information from various sources
    - Monitor system state and environment
    - Collect data for analysis
    - Observe user interactions and system behavior
    - Feed observations to Analyst for processing
    """
    
    def __init__(self, config: Config, communication_hub: MultiAgentCommunicationHub):
        super().__init__(config, AgentRole.OBSERVER, communication_hub)
        self.observations = []
        self.observation_sources = []
        self.current_observation_task = None
        
    def new_task(self, task: str, extra_args: Dict[str, str] | None = None, 
                 tool_names: list[str] | None = None):
        """Initialize observation task."""
        self._task = task
        self.current_observation_task = {
            "task": task,
            "sources": [],
            "findings": [],
            "context": extra_args or {}
        }
        
        # Set up initial messages for LLM
        self._initial_messages = [
            LLMMessage(role="system", content=self.get_system_prompt()),
            LLMMessage(role="user", content=f"Begin observation for: {task}")
        ]
        
        self.update_status(AgentStatus.WORKING, "Gathering observations")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for Observer agent."""
        return """You are the Observer Agent (觀察者) in a six-agent coordination system.

Your primary responsibilities:
1. **Information Gathering**: Collect relevant data from multiple sources
2. **System Monitoring**: Observe current system state, files, processes, and environment
3. **Behavior Analysis**: Monitor user interactions and system responses
4. **Data Collection**: Gather comprehensive information for analysis
5. **Contextual Awareness**: Understand the environment and constraints

**Observation Strategies:**
- **File System Observation**: Examine project structure, code files, configuration files
- **Process Monitoring**: Check running processes, system status, resource usage
- **Error Tracking**: Identify error logs, exception traces, failure patterns
- **Dependency Analysis**: Observe library versions, package dependencies, environment setup
- **User Interaction Patterns**: Monitor how users interact with the system
- **Performance Metrics**: Collect timing, memory usage, and efficiency data

**Data Collection Techniques:**
- Read and analyze relevant files
- Execute diagnostic commands
- Monitor system outputs
- Track changes and modifications
- Document environmental conditions
- Capture current state snapshots

**Observation Reporting:**
- Provide structured, detailed observations
- Include quantitative and qualitative data
- Note patterns, anomalies, and important findings
- Maintain objectivity in reporting
- Prepare data for analytical processing

**Communication Guidelines:**
- Report findings clearly and systematically
- Include relevant context and metadata
- Highlight critical observations
- Provide actionable information for analysis
- Maintain comprehensive documentation

Be thorough, systematic, and objective in your observations."""
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming messages and perform observations."""
        
        if message.message_type == MessageType.TASK_ASSIGNMENT:
            return await self._handle_observation_request(message)
            
        elif message.message_type == MessageType.FEEDBACK:
            return await self._handle_feedback(message)
            
        return None
    
    async def _handle_observation_request(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle observation requests from Commander."""
        task_data = message.data
        is_improvement_cycle = task_data.get("is_improvement_cycle", False)
        
        if is_improvement_cycle:
            # This is a re-observation after design improvements
            return await self._observe_after_improvements(message)
        else:
            # Initial observation
            return await self._perform_initial_observation(message)
    
    async def _perform_initial_observation(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Perform initial observation of the system."""
        observations = await self._gather_system_observations(message.content)
        
        # Structure the observations
        observation_report = {
            "task": message.content,
            "observations": observations,
            "sources": self.observation_sources,
            "timestamp": self._get_timestamp(),
            "observation_type": "initial"
        }
        
        self.observations.append(observation_report)
        
        # Send observations to Commander for routing to Analyst
        return AgentMessage(
            sender_role=self.role,
            receiver_role=AgentRole.COMMANDER,
            message_type=MessageType.FEEDBACK,
            content=f"Completed initial observation. Found {len(observations)} key observations.",
            data=observation_report
        )
    
    async def _observe_after_improvements(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Observe system after design improvements have been applied."""
        improvements = message.data.get("design_improvements", [])
        
        # Perform focused observation on the improved areas
        observations = await self._observe_improvements(improvements, message.content)
        
        observation_report = {
            "task": message.content,
            "observations": observations,
            "improvements_evaluated": improvements,
            "sources": self.observation_sources,
            "timestamp": self._get_timestamp(),
            "observation_type": "post_improvement"
        }
        
        self.observations.append(observation_report)
        
        # Send improved observations back to Commander
        return AgentMessage(
            sender_role=self.role,
            receiver_role=AgentRole.COMMANDER,
            message_type=MessageType.FEEDBACK,
            content=f"Completed post-improvement observation. Evaluated {len(improvements)} improvements.",
            data=observation_report
        )
    
    async def _gather_system_observations(self, task: str) -> List[Dict[str, Any]]:
        """Gather comprehensive system observations."""
        observations = []
        
        # File system observations
        file_obs = await self._observe_file_system()
        observations.extend(file_obs)
        
        # Process observations
        process_obs = await self._observe_processes()
        observations.extend(process_obs)
        
        # Environment observations
        env_obs = await self._observe_environment()
        observations.extend(env_obs)
        
        # Error and log observations
        error_obs = await self._observe_errors_and_logs()
        observations.extend(error_obs)
        
        # Configuration observations
        config_obs = await self._observe_configuration()
        observations.extend(config_obs)
        
        return observations
    
    async def _observe_file_system(self) -> List[Dict[str, Any]]:
        """Observe file system structure and contents."""
        observations = []
        self.observation_sources.append("file_system")
        
        try:
            # Get current working directory
            cwd = os.getcwd()
            observations.append({
                "type": "file_system",
                "category": "working_directory",
                "value": cwd,
                "description": "Current working directory"
            })
            
            # List directory contents
            if os.path.exists(cwd):
                contents = os.listdir(cwd)
                observations.append({
                    "type": "file_system",
                    "category": "directory_contents",
                    "value": contents[:20],  # Limit to first 20 items
                    "description": f"Directory contents (showing first 20 of {len(contents)} items)"
                })
                
                # Look for important files
                important_files = [f for f in contents if f in [
                    'README.md', 'package.json', 'pyproject.toml', 'requirements.txt',
                    'Dockerfile', 'docker-compose.yml', '.env', 'config.py'
                ]]
                
                if important_files:
                    observations.append({
                        "type": "file_system",
                        "category": "important_files",
                        "value": important_files,
                        "description": "Important configuration and documentation files found"
                    })
                    
        except Exception as e:
            observations.append({
                "type": "file_system",
                "category": "error",
                "value": str(e),
                "description": "Error during file system observation"
            })
        
        return observations
    
    async def _observe_processes(self) -> List[Dict[str, Any]]:
        """Observe running processes and system status."""
        observations = []
        self.observation_sources.append("processes")
        
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            observations.append({
                "type": "process",
                "category": "cpu_usage",
                "value": cpu_percent,
                "description": "Current CPU usage percentage"
            })
            
            # Memory usage
            memory = psutil.virtual_memory()
            observations.append({
                "type": "process",
                "category": "memory_usage",
                "value": {
                    "percent": memory.percent,
                    "available_gb": round(memory.available / (1024**3), 2),
                    "total_gb": round(memory.total / (1024**3), 2)
                },
                "description": "Current memory usage statistics"
            })
            
        except ImportError:
            observations.append({
                "type": "process",
                "category": "psutil_unavailable",
                "value": "psutil not available",
                "description": "Process monitoring limited due to missing psutil"
            })
        except Exception as e:
            observations.append({
                "type": "process",
                "category": "error",
                "value": str(e),
                "description": "Error during process observation"
            })
        
        return observations
    
    async def _observe_environment(self) -> List[Dict[str, Any]]:
        """Observe environment variables and system configuration."""
        observations = []
        self.observation_sources.append("environment")
        
        try:
            # Python version
            import sys
            observations.append({
                "type": "environment",
                "category": "python_version",
                "value": sys.version,
                "description": "Python interpreter version"
            })
            
            # Platform information
            import platform
            observations.append({
                "type": "environment",
                "category": "platform",
                "value": {
                    "system": platform.system(),
                    "release": platform.release(),
                    "machine": platform.machine()
                },
                "description": "System platform information"
            })
            
            # Environment variables (filtered for security)
            important_env_vars = ['PATH', 'PYTHONPATH', 'HOME', 'USER', 'SHELL']
            env_data = {var: os.environ.get(var, 'Not set') for var in important_env_vars}
            observations.append({
                "type": "environment",
                "category": "environment_variables",
                "value": env_data,
                "description": "Important environment variables"
            })
            
        except Exception as e:
            observations.append({
                "type": "environment",
                "category": "error",
                "value": str(e),
                "description": "Error during environment observation"
            })
        
        return observations
    
    async def _observe_errors_and_logs(self) -> List[Dict[str, Any]]:
        """Observe error logs and system messages."""
        observations = []
        self.observation_sources.append("logs")
        
        # Look for common log files
        log_patterns = ['*.log', '*.err', 'error.txt', 'debug.txt']
        
        try:
            for pattern in log_patterns:
                # Simple file existence check (would need more sophisticated log parsing)
                if os.path.exists(pattern.replace('*', 'application')):
                    observations.append({
                        "type": "logs",
                        "category": "log_file_found",
                        "value": pattern,
                        "description": f"Log file matching pattern {pattern} found"
                    })
                    
        except Exception as e:
            observations.append({
                "type": "logs",
                "category": "error",
                "value": str(e),
                "description": "Error during log observation"
            })
        
        return observations
    
    async def _observe_configuration(self) -> List[Dict[str, Any]]:
        """Observe system and application configuration."""
        observations = []
        self.observation_sources.append("configuration")
        
        try:
            # Look for configuration files
            config_files = []
            for file in os.listdir('.'):
                if any(file.endswith(ext) for ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg']):
                    config_files.append(file)
            
            if config_files:
                observations.append({
                    "type": "configuration",
                    "category": "config_files",
                    "value": config_files,
                    "description": "Configuration files found in current directory"
                })
                
        except Exception as e:
            observations.append({
                "type": "configuration",
                "category": "error",
                "value": str(e),
                "description": "Error during configuration observation"
            })
        
        return observations
    
    async def _observe_improvements(self, improvements: List[Dict], task: str) -> List[Dict[str, Any]]:
        """Observe the effects of applied improvements."""
        observations = []
        
        for improvement in improvements:
            improvement_type = improvement.get("type", "unknown")
            target = improvement.get("target", "unknown")
            
            observations.append({
                "type": "improvement_validation",
                "category": f"{improvement_type}_validation",
                "value": improvement,
                "description": f"Validating {improvement_type} improvement on {target}"
            })
        
        # Re-run basic observations to see changes
        basic_obs = await self._gather_system_observations(task)
        observations.extend(basic_obs)
        
        return observations
    
    async def _handle_feedback(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle feedback from other agents."""
        # Observer typically doesn't need to respond to feedback,
        # but could use it to adjust observation strategies
        return None
    
    async def execute_autonomous_task(self) -> Optional[AgentMessage]:
        """Execute autonomous observation tasks."""
        # Continuously monitor for changes or anomalies
        if self.current_observation_task:
            # Could implement continuous monitoring here
            pass
        return None
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for observations."""
        from datetime import datetime
        return datetime.now().isoformat()