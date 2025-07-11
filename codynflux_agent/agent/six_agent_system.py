# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""Six-Agent Coordination System - Main orchestration and integration."""

from typing import Dict, Any, Optional
import asyncio
import logging

from ..utils.config import Config
from ..utils.llm_basics import LLMMessage
from .multi_agent_base import (
    MultiAgentOrchestrator, MultiAgentCommunicationHub, AgentRole, AgentMessage, MessageType
)
from .commander_agent import CommanderAgent
from .observer_agent import ObserverAgent
from .analyst_agent import AnalystAgent
from .reproducer_agent import ReproducerAgent
from .executor_agent import ExecutorAgent
from .designer_agent import DesignerAgent
from .base import Agent


class SixAgentSystem:
    """
    Six-Agent Coordination System implementing the flowchart pattern:
    User Input → Commander → Observer → Analyst → Reproducer → Executor → Designer → Feedback Loop
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.communication_hub = MultiAgentCommunicationHub()
        self.orchestrator = MultiAgentOrchestrator(config)
        self.agents: Dict[AgentRole, Any] = {}
        self.is_initialized = False
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> bool:
        """Initialize all agents and the coordination system."""
        try:
            # Create all six agents
            self.agents[AgentRole.COMMANDER] = CommanderAgent(self.config, self.communication_hub)
            self.agents[AgentRole.OBSERVER] = ObserverAgent(self.config, self.communication_hub)
            self.agents[AgentRole.ANALYST] = AnalystAgent(self.config, self.communication_hub)
            self.agents[AgentRole.REPRODUCER] = ReproducerAgent(self.config, self.communication_hub)
            self.agents[AgentRole.EXECUTOR] = ExecutorAgent(self.config, self.communication_hub)
            self.agents[AgentRole.DESIGNER] = DesignerAgent(self.config, self.communication_hub)
            
            # Register agents with orchestrator
            for agent in self.agents.values():
                self.orchestrator.register_agent(agent)
            
            # Setup agent-specific configurations
            await self._configure_agents()
            
            self.is_initialized = True
            self.logger.info("Six-agent system initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize six-agent system: {e}")
            return False
    
    async def _configure_agents(self):
        """Configure agent-specific settings and capabilities."""
        # Configure Commander with coordination capabilities
        commander = self.agents[AgentRole.COMMANDER]
        commander.task = "System Coordination and Management"
        
        # Configure Observer with monitoring capabilities
        observer = self.agents[AgentRole.OBSERVER]
        observer.task = "System State Observation and Monitoring"
        
        # Configure Analyst with analysis capabilities
        analyst = self.agents[AgentRole.ANALYST]
        analyst.task = "Data Analysis and Pattern Recognition"
        
        # Configure Reproducer with testing capabilities
        reproducer = self.agents[AgentRole.REPRODUCER]
        reproducer.task = "Problem Reproduction and Verification"
        
        # Configure Executor with implementation capabilities
        executor = self.agents[AgentRole.EXECUTOR]
        executor.task = "Solution Implementation and Execution"
        
        # Configure Designer with optimization capabilities
        designer = self.agents[AgentRole.DESIGNER]
        designer.task = "System Design and Optimization"
    
    async def process_user_request(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a user request through the six-agent system.
        
        Args:
            user_input: The user's request or task
            context: Additional context and parameters
            
        Returns:
            The final result from the agent system
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            self.logger.info(f"Processing user request: {user_input[:100]}...")
            
            # Start the orchestrated task processing
            result = await self.orchestrator.start_task(user_input)
            
            self.logger.info("User request processing completed")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing user request: {e}")
            return f"Error processing request: {str(e)}"
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get the current status of all agents in the system."""
        status = {
            "system_initialized": self.is_initialized,
            "agents": {},
            "communication_hub": {
                "message_queue_size": len(self.communication_hub.message_queue),
                "message_history_size": len(self.communication_hub.message_history),
                "registered_agents": len(self.communication_hub.agent_states)
            },
            "orchestrator": {
                "is_running": self.orchestrator.is_running,
                "max_cycles": self.orchestrator.max_cycles
            }
        }
        
        # Get status of each agent
        for role, state in self.communication_hub.agent_states.items():
            status["agents"][role.value] = {
                "status": state.status.value,
                "current_task": state.current_task,
                "last_message_time": state.last_message.timestamp.isoformat() if state.last_message else None,
                "has_results": bool(state.results)
            }
        
        return status
    
    async def stop_system(self):
        """Stop the agent system gracefully."""
        self.logger.info("Stopping six-agent system...")
        self.orchestrator.stop()
        
        # Clear agent states
        for agent in self.agents.values():
            agent.update_status(agent.communication_hub.get_agent_status(agent.role))
        
        self.logger.info("Six-agent system stopped")


class SixAgentSystemBuilder:
    """Builder class for creating and configuring the Six-Agent System."""
    
    def __init__(self):
        self.config = None
        self.custom_agents = {}
        self.custom_configurations = {}
    
    def with_config(self, config: Config) -> 'SixAgentSystemBuilder':
        """Set the configuration for the system."""
        self.config = config
        return self
    
    def with_custom_agent(self, role: AgentRole, agent_class) -> 'SixAgentSystemBuilder':
        """Replace a default agent with a custom implementation."""
        self.custom_agents[role] = agent_class
        return self
    
    def with_agent_config(self, role: AgentRole, config: Dict[str, Any]) -> 'SixAgentSystemBuilder':
        """Add custom configuration for a specific agent."""
        self.custom_configurations[role] = config
        return self
    
    def build(self) -> SixAgentSystem:
        """Build and return the configured Six-Agent System."""
        if not self.config:
            raise ValueError("Config must be provided using with_config()")
        
        system = SixAgentSystem(self.config)
        
        # Apply custom agents if any
        for role, agent_class in self.custom_agents.items():
            system.agents[role] = agent_class(self.config, system.communication_hub)
        
        return system


# Integration with existing CodynfluxAgent
class SixAgentCodynfluxAgent(Agent):
    """
    Integration class that allows the Six-Agent System to work with existing CodynfluxAgent interface.
    """
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.six_agent_system = SixAgentSystem(config)
        self.system_initialized = False
    
    def setup_trajectory_recording(self, trajectory_path: str | None = None) -> str:
        """Set up trajectory recording for this agent.

        Args:
            trajectory_path: Path to save trajectory file. If None, generates default path.

        Returns:
            The path where trajectory will be saved.
        """
        from ..utils.trajectory_recorder import TrajectoryRecorder

        recorder = TrajectoryRecorder(trajectory_path)
        self._set_trajectory_recorder(recorder)

        return recorder.get_trajectory_path()
    
    async def initialize_system(self):
        """Initialize the six-agent system."""
        if not self.system_initialized:
            success = await self.six_agent_system.initialize()
            self.system_initialized = success
            return success
        return True
    
    def new_task(self, task: str, extra_args: Dict[str, str] | None = None, 
                 tool_names: list[str] | None = None):
        """Initialize a new task for the six-agent system."""
        self._task = task
        
        # Set up initial messages
        self._initial_messages = [
            LLMMessage(role="system", content=self.get_system_prompt()),
            LLMMessage(role="user", content=f"Process this task using six-agent coordination: {task}")
        ]
        
        # Store extra args for use during execution
        self._extra_args = extra_args or {}
        self._tool_names = tool_names
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the six-agent system."""
        return """You are coordinating a six-agent system for comprehensive task processing.

The system follows this workflow:
1. Commander (指揮官) - Receives user input and coordinates overall workflow
2. Observer (觀察者) - Gathers information and observes system state
3. Analyst (分析者) - Analyzes observations and identifies patterns
4. Reproducer (再現者) - Reproduces problems and creates test cases
5. Executor (執行者) - Implements solutions and executes fixes
6. Designer (設計者) - Designs improvements and optimizations

The agents work in sequence with feedback loops:
- Observer → Analyst → Reproducer → Executor
- Executor feedback → Commander → Designer (if improvements needed)
- Designer → Observer (for improvement validation)
- Commander provides final results to user

This systematic approach ensures thorough analysis, reliable reproduction, effective execution, and continuous improvement."""
    
    async def execute_task(self) -> 'AgentExecution':
        """Execute the task using the six-agent system."""
        from .agent_basics import AgentExecution, AgentState
        import time
        
        start_time = time.time()
        execution = AgentExecution(task=self._task, steps=[])
        
        try:
            # Initialize the system if needed
            if not await self.initialize_system():
                execution.final_result = "Failed to initialize six-agent system"
                execution.success = False
                return execution
            
            # Process the task through the six-agent system
            result = await self.six_agent_system.process_user_request(self._task, self._extra_args)
            
            execution.final_result = result
            execution.success = True
            
        except Exception as e:
            execution.final_result = f"Six-agent system error: {str(e)}"
            execution.success = False
        
        execution.execution_time = time.time() - start_time
        return execution
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get the current status of the six-agent system."""
        if self.system_initialized:
            return await self.six_agent_system.get_system_status()
        else:
            return {"system_initialized": False, "error": "System not initialized"}
    
    async def stop_system(self):
        """Stop the six-agent system."""
        if self.system_initialized:
            await self.six_agent_system.stop_system()


# Factory function for easy creation
def create_six_agent_system(config: Config, 
                           custom_agents: Optional[Dict[AgentRole, Any]] = None,
                           agent_configs: Optional[Dict[AgentRole, Dict[str, Any]]] = None) -> SixAgentSystem:
    """
    Factory function to create a configured Six-Agent System.
    
    Args:
        config: System configuration
        custom_agents: Optional custom agent implementations
        agent_configs: Optional agent-specific configurations
        
    Returns:
        Configured SixAgentSystem instance
    """
    builder = SixAgentSystemBuilder().with_config(config)
    
    if custom_agents:
        for role, agent_class in custom_agents.items():
            builder.with_custom_agent(role, agent_class)
    
    if agent_configs:
        for role, agent_config in agent_configs.items():
            builder.with_agent_config(role, agent_config)
    
    return builder.build()


# Export main classes for easy imports
__all__ = [
    'SixAgentSystem',
    'SixAgentSystemBuilder', 
    'SixAgentCodynfluxAgent',
    'create_six_agent_system'
]