# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""Commander Agent - Central coordination agent in the six-agent system."""

from typing import Optional, Dict, Any
import json

from ..utils.config import Config
from ..utils.llm_basics import LLMMessage
from .multi_agent_base import (
    MultiAgent, AgentRole, AgentMessage, MessageType, AgentStatus,
    MultiAgentCommunicationHub
)


class CommanderAgent(MultiAgent):
    """
    Commander Agent (指揮官) - Central coordination agent.
    
    Responsibilities:
    - Receive user input and distribute tasks
    - Coordinate workflow between other agents
    - Make strategic decisions based on feedback
    - Provide final results to users
    """
    
    def __init__(self, config: Config, communication_hub: MultiAgentCommunicationHub):
        super().__init__(config, AgentRole.COMMANDER, communication_hub)
        self.current_workflow_stage = "initial"
        self.task_context = {}
        self.feedback_history = []
        
    def new_task(self, task: str, extra_args: Dict[str, str] | None = None, 
                 tool_names: list[str] | None = None):
        """Initialize a new task for the multi-agent system."""
        self._task = task
        self.task_context = {
            "original_task": task,
            "extra_args": extra_args or {},
            "current_stage": "analysis",
            "completed_stages": [],
            "agent_results": {}
        }
        
        # Set up initial messages for LLM
        self._initial_messages = [
            LLMMessage(role="system", content=self.get_system_prompt()),
            LLMMessage(role="user", content=f"New task assignment: {task}")
        ]
        
        self.update_status(AgentStatus.WORKING, "Task coordination and planning")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for Commander agent."""
        return """You are the Commander Agent (指揮官) in a six-agent coordination system.

Your primary responsibilities:
1. **Task Distribution**: Analyze user requests and assign appropriate tasks to specialized agents
2. **Workflow Coordination**: Orchestrate the flow between Observer → Analyst → Reproducer → Executor
3. **Strategic Decision Making**: Make high-level decisions based on agent feedback
4. **Quality Assurance**: Ensure all stages are completed properly before moving to the next
5. **Final Integration**: Synthesize results from all agents into coherent user responses

**Agent Coordination Flow:**
1. Observer (觀察者): Receives information and observes the system state
2. Analyst (分析者): Analyzes observations and identifies patterns/issues  
3. Reproducer (再現者): Reproduces problems to verify understanding
4. Executor (執行者): Executes solutions and implements changes
5. Designer (設計者): Designs improvements and optimizations based on feedback

**Decision Making Guidelines:**
- Always ensure Observer has completed observation before sending to Analyst
- Verify Analyst has completed analysis before sending to Reproducer
- Confirm reproduction is successful before sending to Executor
- Monitor execution feedback and coordinate with Designer for improvements
- Make strategic decisions on whether to continue, retry, or escalate

**Communication Style:**
- Be clear and directive in task assignments
- Provide context and background for each agent
- Synthesize feedback from multiple agents
- Make decisions quickly but thoroughly

Coordinate effectively and ensure high-quality task completion."""
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming messages from other agents or user input."""
        
        if message.message_type == MessageType.TASK_ASSIGNMENT:
            # Initial task from user - start the workflow
            return await self._handle_initial_task(message)
            
        elif message.message_type == MessageType.FEEDBACK:
            # Feedback from other agents
            return await self._handle_agent_feedback(message)
            
        elif message.message_type == MessageType.STATUS_UPDATE:
            # Status updates from agents
            return await self._handle_status_update(message)
            
        return None
    
    async def _handle_initial_task(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle initial task assignment and start the workflow."""
        self.task_context["original_task"] = message.content
        self.current_workflow_stage = "observation"
        
        # Send task to Observer first
        response = AgentMessage(
            sender_role=self.role,
            receiver_role=AgentRole.OBSERVER,
            message_type=MessageType.TASK_ASSIGNMENT,
            content=f"Begin observation for task: {message.content}",
            data={
                "task_context": self.task_context,
                "priority": "high",
                "stage": "observation"
            }
        )
        
        return response
    
    async def _handle_agent_feedback(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle feedback from other agents and coordinate next steps."""
        self.feedback_history.append(message)
        sender_role = message.sender_role
        
        # Store agent results
        self.task_context["agent_results"][sender_role.value] = message.data
        
        # Determine next action based on sender and workflow stage
        if sender_role == AgentRole.OBSERVER and self.current_workflow_stage == "observation":
            return await self._transition_to_analysis(message)
            
        elif sender_role == AgentRole.ANALYST and self.current_workflow_stage == "analysis":
            return await self._transition_to_reproduction(message)
            
        elif sender_role == AgentRole.REPRODUCER and self.current_workflow_stage == "reproduction":
            return await self._transition_to_execution(message)
            
        elif sender_role == AgentRole.EXECUTOR and self.current_workflow_stage == "execution":
            return await self._handle_execution_completion(message)
            
        elif sender_role == AgentRole.DESIGNER:
            return await self._handle_design_feedback(message)
            
        return None
    
    async def _transition_to_analysis(self, observer_message: AgentMessage) -> Optional[AgentMessage]:
        """Transition from observation to analysis stage."""
        self.current_workflow_stage = "analysis"
        self.task_context["completed_stages"].append("observation")
        
        analysis_task = f"""Analyze the observations: {observer_message.content}
        
        Original task: {self.task_context['original_task']}
        Observer findings: {observer_message.data}
        
        Please provide detailed analysis of patterns, issues, and recommendations."""
        
        return AgentMessage(
            sender_role=self.role,
            receiver_role=AgentRole.ANALYST,
            message_type=MessageType.TASK_ASSIGNMENT,
            content=analysis_task,
            data={
                "observer_results": observer_message.data,
                "task_context": self.task_context
            }
        )
    
    async def _transition_to_reproduction(self, analyst_message: AgentMessage) -> Optional[AgentMessage]:
        """Transition from analysis to reproduction stage."""
        self.current_workflow_stage = "reproduction"
        self.task_context["completed_stages"].append("analysis")
        
        reproduction_task = f"""Reproduce the identified issues: {analyst_message.content}
        
        Analysis results: {analyst_message.data}
        
        Please reproduce the problem to verify our understanding and create test cases."""
        
        return AgentMessage(
            sender_role=self.role,
            receiver_role=AgentRole.REPRODUCER,
            message_type=MessageType.TASK_ASSIGNMENT,
            content=reproduction_task,
            data={
                "analysis_results": analyst_message.data,
                "task_context": self.task_context
            }
        )
    
    async def _transition_to_execution(self, reproducer_message: AgentMessage) -> Optional[AgentMessage]:
        """Transition from reproduction to execution stage."""
        self.current_workflow_stage = "execution"
        self.task_context["completed_stages"].append("reproduction")
        
        execution_task = f"""Execute the solution: {reproducer_message.content}
        
        Reproduction results: {reproducer_message.data}
        
        Please implement the fix and execute the necessary changes."""
        
        return AgentMessage(
            sender_role=self.role,
            receiver_role=AgentRole.EXECUTOR,
            message_type=MessageType.TASK_ASSIGNMENT,
            content=execution_task,
            data={
                "reproduction_results": reproducer_message.data,
                "task_context": self.task_context
            }
        )
    
    async def _handle_execution_completion(self, executor_message: AgentMessage) -> Optional[AgentMessage]:
        """Handle completion of execution and potentially involve Designer."""
        self.task_context["completed_stages"].append("execution")
        
        # Check if we need design improvements
        if self._needs_design_improvement(executor_message):
            return await self._request_design_improvement(executor_message)
        else:
            return await self._complete_task(executor_message)
    
    def _needs_design_improvement(self, executor_message: AgentMessage) -> bool:
        """Determine if design improvements are needed."""
        # Check execution results for indicators that design improvement is needed
        exec_data = executor_message.data
        return (
            exec_data.get("has_errors", False) or
            exec_data.get("performance_issues", False) or
            exec_data.get("needs_optimization", False)
        )
    
    async def _request_design_improvement(self, executor_message: AgentMessage) -> Optional[AgentMessage]:
        """Request design improvements from Designer agent."""
        self.current_workflow_stage = "design"
        
        design_task = f"""Design improvements based on execution results: {executor_message.content}
        
        Execution results: {executor_message.data}
        Full task context: {self.task_context}
        
        Please design optimizations and improvements."""
        
        return AgentMessage(
            sender_role=self.role,
            receiver_role=AgentRole.DESIGNER,
            message_type=MessageType.TASK_ASSIGNMENT,
            content=design_task,
            data={
                "execution_results": executor_message.data,
                "task_context": self.task_context
            }
        )
    
    async def _handle_design_feedback(self, design_message: AgentMessage) -> Optional[AgentMessage]:
        """Handle feedback from Designer and decide on next steps."""
        design_improvements = design_message.data.get("improvements", [])
        
        if design_improvements:
            # Send improvements back to Observer for re-evaluation
            self.current_workflow_stage = "observation"  # Restart cycle with improvements
            
            improvement_task = f"""Re-observe system with design improvements: {design_message.content}
            
            Design improvements: {design_improvements}
            Previous results: {self.task_context}
            
            Please observe the system after implementing suggested improvements."""
            
            return AgentMessage(
                sender_role=self.role,
                receiver_role=AgentRole.OBSERVER,
                message_type=MessageType.TASK_ASSIGNMENT,
                content=improvement_task,
                data={
                    "design_improvements": design_improvements,
                    "task_context": self.task_context,
                    "is_improvement_cycle": True
                }
            )
        else:
            return await self._complete_task(design_message)
    
    async def _complete_task(self, final_message: AgentMessage) -> Optional[AgentMessage]:
        """Complete the task and prepare final results."""
        self.current_workflow_stage = "completed"
        self.task_context["completed_stages"].append("final")
        
        # Synthesize final result
        final_result = self._synthesize_final_result()
        
        # Update status and store result
        self.update_status(AgentStatus.COMPLETED)
        self.communication_hub.agent_states[self.role].results["final_result"] = final_result
        
        return AgentMessage(
            sender_role=self.role,
            receiver_role=None,  # Broadcast to system
            message_type=MessageType.STATUS_UPDATE,
            content=final_result,
            data={
                "task_completed": True,
                "final_result": final_result,
                "task_context": self.task_context
            }
        )
    
    def _synthesize_final_result(self) -> str:
        """Synthesize final result from all agent outputs."""
        result_parts = []
        
        result_parts.append(f"Task: {self.task_context['original_task']}")
        result_parts.append(f"Completed stages: {', '.join(self.task_context['completed_stages'])}")
        
        # Add results from each agent
        agent_results = self.task_context.get("agent_results", {})
        for agent_name, result in agent_results.items():
            if result:
                result_parts.append(f"{agent_name.title()} Results: {result}")
        
        return "\n\n".join(result_parts)
    
    async def _handle_status_update(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle status updates from other agents."""
        # Log status update
        sender_status = message.data.get("status", "unknown")
        print(f"Status update from {message.sender_role.value}: {sender_status}")
        return None
    
    async def execute_autonomous_task(self) -> Optional[AgentMessage]:
        """Execute autonomous coordination tasks."""
        # Check if any agents need attention or if workflow is stalled
        if self.current_workflow_stage == "initial":
            return None  # Waiting for initial task
            
        # Monitor agent statuses and provide guidance if needed
        return await self._monitor_workflow_progress()
    
    async def _monitor_workflow_progress(self) -> Optional[AgentMessage]:
        """Monitor workflow progress and provide guidance if needed."""
        # This could include timeout handling, error recovery, etc.
        # For now, return None as autonomous monitoring
        return None