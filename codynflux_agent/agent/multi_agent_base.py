# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""Multi-Agent system base classes for six-agent coordination pattern."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import asyncio
import uuid
from datetime import datetime

from ..utils.config import Config
from ..utils.llm_basics import LLMMessage, LLMResponse
from .base import Agent


class AgentRole(Enum):
    """Agent roles in the six-agent system."""
    COMMANDER = "commander"      # 指揮官
    OBSERVER = "observer"        # 觀察者
    ANALYST = "analyst"          # 分析者
    REPRODUCER = "reproducer"    # 再現者
    EXECUTOR = "executor"        # 執行者
    DESIGNER = "designer"        # 設計者


class MessageType(Enum):
    """Types of messages between agents."""
    TASK_ASSIGNMENT = "task_assignment"
    OBSERVATION = "observation"
    ANALYSIS = "analysis"
    REPRODUCTION = "reproduction"
    EXECUTION = "execution"
    DESIGN = "design"
    FEEDBACK = "feedback"
    STATUS_UPDATE = "status_update"


@dataclass
class AgentMessage:
    """Message structure for inter-agent communication."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_role: AgentRole = field(default=AgentRole.COMMANDER)
    receiver_role: Optional[AgentRole] = None
    message_type: MessageType = field(default=MessageType.STATUS_UPDATE)
    content: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    parent_message_id: Optional[str] = None


class AgentStatus(Enum):
    """Status of individual agents."""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentState:
    """State tracking for individual agents."""
    role: AgentRole
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    last_message: Optional[AgentMessage] = None
    results: Dict[str, Any] = field(default_factory=dict)


class MultiAgentCommunicationHub:
    """Central communication hub for agent coordination."""
    
    def __init__(self):
        self.message_queue: List[AgentMessage] = []
        self.agent_states: Dict[AgentRole, AgentState] = {}
        self.message_history: List[AgentMessage] = []
        
    def register_agent(self, role: AgentRole):
        """Register an agent with the hub."""
        self.agent_states[role] = AgentState(role=role)
    
    async def send_message(self, message: AgentMessage):
        """Send a message through the hub."""
        self.message_queue.append(message)
        self.message_history.append(message)
        
        # Update sender state
        if message.sender_role in self.agent_states:
            self.agent_states[message.sender_role].last_message = message
    
    async def get_messages_for_agent(self, role: AgentRole) -> List[AgentMessage]:
        """Get messages intended for a specific agent."""
        messages = [msg for msg in self.message_queue 
                   if msg.receiver_role == role or msg.receiver_role is None]
        # Remove processed messages
        self.message_queue = [msg for msg in self.message_queue 
                             if msg.receiver_role != role and msg.receiver_role is not None]
        return messages
    
    def update_agent_status(self, role: AgentRole, status: AgentStatus, task: Optional[str] = None):
        """Update agent status."""
        if role in self.agent_states:
            self.agent_states[role].status = status
            if task:
                self.agent_states[role].current_task = task
    
    def get_agent_status(self, role: AgentRole) -> Optional[AgentStatus]:
        """Get current status of an agent."""
        return self.agent_states.get(role, AgentState(role)).status


class MultiAgent(Agent):
    """Base class for agents in the multi-agent system."""
    
    def __init__(self, config: Config, role: AgentRole, communication_hub: MultiAgentCommunicationHub):
        super().__init__(config)
        self.role = role
        self.communication_hub = communication_hub
        self.communication_hub.register_agent(role)
        
    async def send_message(self, receiver: Optional[AgentRole], message_type: MessageType, 
                          content: str, data: Optional[Dict[str, Any]] = None):
        """Send a message to another agent."""
        message = AgentMessage(
            sender_role=self.role,
            receiver_role=receiver,
            message_type=message_type,
            content=content,
            data=data or {}
        )
        await self.communication_hub.send_message(message)
    
    async def receive_messages(self) -> List[AgentMessage]:
        """Receive messages from other agents."""
        return await self.communication_hub.get_messages_for_agent(self.role)
    
    def update_status(self, status: AgentStatus, task: Optional[str] = None):
        """Update this agent's status."""
        self.communication_hub.update_agent_status(self.role, status, task)
    
    @abstractmethod
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process an incoming message and optionally return a response."""
        pass
    
    @abstractmethod
    async def execute_autonomous_task(self) -> Optional[AgentMessage]:
        """Execute autonomous tasks when no messages are pending."""
        pass
    
    async def run_cycle(self) -> List[AgentMessage]:
        """Run one cycle of message processing and autonomous work."""
        responses = []
        
        # Process incoming messages
        messages = await self.receive_messages()
        for message in messages:
            response = await self.process_message(message)
            if response:
                responses.append(response)
        
        # Execute autonomous tasks if no messages
        if not messages:
            autonomous_response = await self.execute_autonomous_task()
            if autonomous_response:
                responses.append(autonomous_response)
        
        return responses


class MultiAgentOrchestrator:
    """Orchestrates the six-agent system according to the flowchart."""
    
    def __init__(self, config: Config):
        self.config = config
        self.communication_hub = MultiAgentCommunicationHub()
        self.agents: Dict[AgentRole, MultiAgent] = {}
        self.is_running = False
        self.max_cycles = 100
        
    def register_agent(self, agent: MultiAgent):
        """Register an agent with the orchestrator."""
        self.agents[agent.role] = agent
    
    async def start_task(self, user_input: str) -> str:
        """Start a new task with user input."""
        if AgentRole.COMMANDER not in self.agents:
            raise ValueError("Commander agent must be registered")
        
        # Send initial task to commander
        initial_message = AgentMessage(
            sender_role=AgentRole.COMMANDER,  # System message
            receiver_role=AgentRole.COMMANDER,
            message_type=MessageType.TASK_ASSIGNMENT,
            content=user_input
        )
        
        await self.communication_hub.send_message(initial_message)
        self.is_running = True
        
        # Run coordination loop
        return await self.coordination_loop()
    
    async def coordination_loop(self) -> str:
        """Main coordination loop following the flowchart pattern."""
        cycle_count = 0
        final_result = ""
        
        while self.is_running and cycle_count < self.max_cycles:
            cycle_count += 1
            
            # Run all agents in parallel
            tasks = []
            for agent in self.agents.values():
                tasks.append(agent.run_cycle())
            
            # Wait for all agents to complete their cycles
            agent_responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process responses and send them
            for agent_role, responses in zip(self.agents.keys(), agent_responses):
                if isinstance(responses, Exception):
                    print(f"Agent {agent_role.value} encountered error: {responses}")
                    continue
                
                for response in responses:
                    await self.communication_hub.send_message(response)
            
            # Check if task is completed
            commander_status = self.communication_hub.get_agent_status(AgentRole.COMMANDER)
            if commander_status == AgentStatus.COMPLETED:
                # Get final result from commander
                commander_state = self.communication_hub.agent_states.get(AgentRole.COMMANDER)
                if commander_state and "final_result" in commander_state.results:
                    final_result = commander_state.results["final_result"]
                self.is_running = False
                break
            
            # Prevent infinite loops
            await asyncio.sleep(0.1)
        
        if cycle_count >= self.max_cycles:
            final_result = "Task execution exceeded maximum cycles."
        
        return final_result
    
    def stop(self):
        """Stop the orchestrator."""
        self.is_running = False