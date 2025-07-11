# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""Agent module for Codynflux Agent."""

from .base import Agent
from .codynflux_agent import CodynfluxAgent

# Multi-agent system components
from .multi_agent_base import (
    MultiAgent, AgentRole, AgentMessage, MessageType, AgentStatus,
    MultiAgentCommunicationHub, MultiAgentOrchestrator
)
from .commander_agent import CommanderAgent
from .observer_agent import ObserverAgent
from .analyst_agent import AnalystAgent
from .reproducer_agent import ReproducerAgent
from .executor_agent import ExecutorAgent
from .designer_agent import DesignerAgent
from .six_agent_system import (
    SixAgentSystem, SixAgentSystemBuilder, SixAgentCodynfluxAgent, create_six_agent_system
)

__all__ = [
    # Base agents
    "Agent", 
    "CodynfluxAgent",
    
    # Multi-agent system base
    "MultiAgent", 
    "AgentRole", 
    "AgentMessage", 
    "MessageType", 
    "AgentStatus",
    "MultiAgentCommunicationHub", 
    "MultiAgentOrchestrator",
    
    # Individual specialist agents
    "CommanderAgent",
    "ObserverAgent", 
    "AnalystAgent",
    "ReproducerAgent",
    "ExecutorAgent",
    "DesignerAgent",
    
    # Six-agent system
    "SixAgentSystem",
    "SixAgentSystemBuilder", 
    "SixAgentCodynfluxAgent",
    "create_six_agent_system"
]
