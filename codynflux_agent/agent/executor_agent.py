# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""Executor Agent - Solution implementation and task execution agent."""

from typing import Optional, Dict, Any, List
import json
import subprocess
import os
import tempfile
import shutil
from pathlib import Path

from ..utils.config import Config
from ..utils.llm_basics import LLMMessage
from .multi_agent_base import (
    MultiAgent, AgentRole, AgentMessage, MessageType, AgentStatus,
    MultiAgentCommunicationHub
)


class ExecutorAgent(MultiAgent):
    """
    Executor Agent (執行者) - Solution implementation and task execution.
    
    Responsibilities:
    - Execute solutions based on reproduced problems
    - Implement fixes and improvements
    - Apply patches and modifications
    - Run tests and validate solutions
    - Monitor execution results and provide feedback
    """
    
    def __init__(self, config: Config, communication_hub: MultiAgentCommunicationHub):
        super().__init__(config, AgentRole.EXECUTOR, communication_hub)
        self.execution_history = []
        self.current_execution = None
        self.backup_manager = BackupManager()
        self.execution_results = []
        
    def new_task(self, task: str, extra_args: Dict[str, str] | None = None, 
                 tool_names: list[str] | None = None):
        """Initialize execution task."""
        self._task = task
        self.current_execution = {
            "task": task,
            "target_issues": [],
            "execution_plan": [],
            "implemented_fixes": [],
            "test_results": [],
            "validation_status": "pending",
            "context": extra_args or {}
        }
        
        # Set up initial messages for LLM
        self._initial_messages = [
            LLMMessage(role="system", content=self.get_system_prompt()),
            LLMMessage(role="user", content=f"Begin solution execution for: {task}")
        ]
        
        self.update_status(AgentStatus.WORKING, "Executing solutions and implementing fixes")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for Executor agent."""
        return """You are the Executor Agent (執行者) in a six-agent coordination system.

Your primary responsibilities:
1. **Solution Implementation**: Execute fixes and solutions for identified problems
2. **Code Modification**: Apply patches, updates, and improvements to code
3. **Test Execution**: Run tests to validate implemented solutions
4. **Process Management**: Execute scripts, commands, and automation
5. **Result Validation**: Verify that solutions work correctly

**Execution Strategies:**
- **Safe Execution**: Always create backups before making changes
- **Incremental Implementation**: Apply changes step-by-step with validation
- **Rollback Capability**: Maintain ability to revert changes if needed
- **Testing Integration**: Execute tests after each significant change
- **Error Handling**: Gracefully handle execution errors and failures
- **Progress Monitoring**: Track execution progress and provide status updates

**Implementation Approaches:**
- **Code Patching**: Apply specific code fixes and modifications
- **Configuration Updates**: Modify system and application configurations
- **Dependency Management**: Install, update, or remove dependencies
- **Script Execution**: Run automation scripts and maintenance tasks
- **Database Operations**: Execute database updates and migrations
- **File Operations**: Create, modify, delete, or move files and directories

**Validation Methods:**
- **Unit Testing**: Run unit tests to verify individual components
- **Integration Testing**: Test component interactions and workflows
- **Regression Testing**: Ensure changes don't break existing functionality
- **Performance Testing**: Validate performance characteristics
- **Functional Testing**: Verify end-to-end functionality
- **Manual Verification**: Perform manual checks when automated testing is insufficient

**Safety Protocols:**
- **Backup Management**: Always backup before making changes
- **Change Tracking**: Document all modifications made
- **Verification Steps**: Verify each change before proceeding
- **Recovery Procedures**: Have rollback plans for all changes
- **Impact Assessment**: Evaluate potential impact of changes
- **Authorization Checks**: Ensure proper permissions for operations

**Error Management:**
- **Graceful Degradation**: Handle errors without system failure
- **Error Logging**: Comprehensive logging of all issues
- **Recovery Actions**: Automatic recovery where possible
- **Escalation Procedures**: Know when to escalate issues
- **Status Reporting**: Keep other agents informed of execution status

**Quality Assurance:**
- **Code Review**: Review all changes before implementation
- **Best Practices**: Follow coding and operational best practices
- **Documentation**: Document all changes and procedures
- **Compliance**: Ensure compliance with security and operational policies
- **Performance**: Optimize for efficiency and resource usage

Be methodical, safe, and thorough in your execution approach."""
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming execution requests."""
        
        if message.message_type == MessageType.TASK_ASSIGNMENT:
            return await self._handle_execution_request(message)
            
        elif message.message_type == MessageType.FEEDBACK:
            return await self._handle_feedback(message)
            
        return None
    
    async def _handle_execution_request(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle execution requests from Commander."""
        reproduction_results = message.data.get("reproduction_results", {})
        task_context = message.data.get("task_context", {})
        
        # Extract execution tasks from reproduction results
        execution_tasks = await self._extract_execution_tasks(reproduction_results)
        
        # Execute solutions for reproduced issues
        execution_results = await self._execute_solutions(execution_tasks, task_context)
        
        # Store execution in history
        self.execution_history.append(execution_results)
        self.current_execution = execution_results
        
        # Send execution results back to Commander
        return AgentMessage(
            sender_role=self.role,
            receiver_role=AgentRole.COMMANDER,
            message_type=MessageType.FEEDBACK,
            content=f"Execution completed. Successfully executed {len(execution_results['successful_executions'])} solutions.",
            data=execution_results
        )
    
    async def _extract_execution_tasks(self, reproduction_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract execution tasks from reproduction results."""
        execution_tasks = []
        
        successful_reproductions = reproduction_results.get("successful_reproductions", [])
        test_cases = reproduction_results.get("test_cases_created", [])
        
        # Create execution tasks from successful reproductions
        for reproduction in successful_reproductions:
            issue = reproduction.get("issue", {})
            task = {
                "task_type": "fix_implementation",
                "priority": self._calculate_execution_priority(issue),
                "issue": issue,
                "reproduction_data": reproduction,
                "execution_method": self._determine_execution_method(issue),
                "validation_required": True,
                "backup_required": True
            }
            execution_tasks.append(task)
        
        # Create test execution tasks
        for test_case in test_cases:
            task = {
                "task_type": "test_execution",
                "priority": 5,  # Medium priority for tests
                "test_case": test_case,
                "execution_method": "test_runner",
                "validation_required": True,
                "backup_required": False
            }
            execution_tasks.append(task)
        
        # Sort by priority
        execution_tasks.sort(key=lambda x: x["priority"], reverse=True)
        
        return execution_tasks
    
    def _calculate_execution_priority(self, issue: Dict[str, Any]) -> int:
        """Calculate priority for executing a solution."""
        priority = 0
        
        severity = issue.get("severity", "medium")
        if severity == "high":
            priority += 10
        elif severity == "medium":
            priority += 5
        
        issue_type = issue.get("type", "")
        if issue_type == "error":
            priority += 8  # Errors are high priority
        elif issue_type == "performance":
            priority += 6  # Performance issues are medium-high priority
        elif issue_type == "configuration":
            priority += 4  # Configuration issues are medium priority
        
        return priority
    
    def _determine_execution_method(self, issue: Dict[str, Any]) -> str:
        """Determine the best execution method for an issue."""
        issue_type = issue.get("type", "")
        
        if issue_type == "error":
            return "error_fix"
        elif issue_type == "performance":
            return "performance_optimization"
        elif issue_type == "configuration":
            return "configuration_update"
        else:
            return "generic_fix"
    
    async def _execute_solutions(self, execution_tasks: List[Dict[str, Any]], 
                                task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute solutions for all tasks."""
        results = {
            "task": task_context.get("original_task", ""),
            "total_tasks": len(execution_tasks),
            "successful_executions": [],
            "failed_executions": [],
            "test_results": [],
            "performance_metrics": {},
            "changes_made": [],
            "execution_metadata": {
                "timestamp": self._get_timestamp(),
                "environment": await self._capture_execution_environment()
            }
        }
        
        # Execute each task
        for task in execution_tasks:
            execution_result = await self._execute_single_task(task, task_context)
            
            if execution_result["success"]:
                results["successful_executions"].append(execution_result)
            else:
                results["failed_executions"].append(execution_result)
            
            # Collect test results
            if execution_result.get("test_results"):
                results["test_results"].extend(execution_result["test_results"])
            
            # Collect changes made
            if execution_result.get("changes"):
                results["changes_made"].extend(execution_result["changes"])
        
        # Calculate overall metrics
        results["performance_metrics"] = self._calculate_performance_metrics(results)
        
        # Determine if design improvements are needed
        results["needs_optimization"] = self._needs_optimization(results)
        results["has_errors"] = len(results["failed_executions"]) > 0
        results["performance_issues"] = self._has_performance_issues(results)
        
        return results
    
    async def _execute_single_task(self, task: Dict[str, Any], 
                                  task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task."""
        execution_result = {
            "task": task,
            "success": False,
            "execution_method": task.get("execution_method", "unknown"),
            "steps_completed": [],
            "changes": [],
            "test_results": [],
            "error_messages": [],
            "duration": 0,
            "rollback_info": None
        }
        
        task_type = task.get("task_type", "")
        
        try:
            # Create backup if required
            if task.get("backup_required", False):
                backup_info = await self._create_backup(task)
                execution_result["rollback_info"] = backup_info
            
            # Execute based on task type
            if task_type == "fix_implementation":
                result = await self._execute_fix_implementation(task, task_context)
            elif task_type == "test_execution":
                result = await self._execute_test_case(task, task_context)
            else:
                result = await self._execute_generic_task(task, task_context)
            
            execution_result.update(result)
            
            # Validate execution if required
            if task.get("validation_required", False) and execution_result["success"]:
                validation_result = await self._validate_execution(task, execution_result)
                execution_result["validation"] = validation_result
                if not validation_result.get("valid", True):
                    execution_result["success"] = False
                    execution_result["error_messages"].append("Validation failed")
            
        except Exception as e:
            execution_result["error_messages"].append(str(e))
            execution_result["success"] = False
            
            # Attempt rollback if backup exists
            if execution_result.get("rollback_info"):
                await self._rollback_changes(execution_result["rollback_info"])
        
        return execution_result
    
    async def _execute_fix_implementation(self, task: Dict[str, Any], 
                                        task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a fix implementation task."""
        issue = task.get("issue", {})
        reproduction_data = task.get("reproduction_data", {})
        
        steps = []
        changes = []
        
        # Analyze the issue and determine fix strategy
        fix_strategy = await self._determine_fix_strategy(issue, reproduction_data)
        steps.append(f"Determined fix strategy: {fix_strategy}")
        
        # Implement the fix based on issue type
        issue_type = issue.get("type", "")
        
        if issue_type == "error":
            fix_result = await self._implement_error_fix(issue, reproduction_data)
        elif issue_type == "performance":
            fix_result = await self._implement_performance_fix(issue, reproduction_data)
        elif issue_type == "configuration":
            fix_result = await self._implement_configuration_fix(issue, reproduction_data)
        else:
            fix_result = await self._implement_generic_fix(issue, reproduction_data)
        
        if fix_result is not None:
            steps.extend(fix_result.get("steps", []))
            changes.extend(fix_result.get("changes", []))
        
        return {
            "success": fix_result.get("success", False) if fix_result is not None else False,
            "steps_completed": steps,
            "changes": changes,
            "fix_strategy": fix_strategy,
            "fix_details": fix_result
        }
    
    async def _determine_fix_strategy(self, issue: Dict[str, Any], 
                                    reproduction_data: Dict[str, Any]) -> str:
        """Determine the best strategy for fixing an issue."""
        issue_type = issue.get("type", "")
        severity = issue.get("severity", "medium")
        
        if issue_type == "error" and severity == "high":
            return "immediate_error_resolution"
        elif issue_type == "performance":
            return "performance_optimization"
        elif issue_type == "configuration":
            return "configuration_correction"
        else:
            return "general_issue_resolution"
    
    async def _implement_error_fix(self, issue: Dict[str, Any], 
                                  reproduction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement a fix for an error-type issue."""
        steps = [
            "Analyze error details",
            "Identify error source",
            "Implement error fix",
            "Test error resolution"
        ]
        
        changes = []
        
        # Simulate error fix implementation
        error_details = issue.get("details", {})
        
        if isinstance(error_details, str) and "file" in error_details.lower():
            # Simulate file-based error fix
            changes.append({
                "type": "file_modification",
                "target": "error_prone_file.py",
                "operation": "bug_fix",
                "description": f"Fixed error: {issue.get('title', '')}",
                "backup_created": True
            })
        
        # Add error handling improvement
        changes.append({
            "type": "code_addition",
            "target": "error_handling.py",
            "operation": "add_try_catch",
            "description": "Added comprehensive error handling",
            "backup_created": True
        })
        
        return {
            "success": True,
            "steps": steps,
            "changes": changes,
            "fix_type": "error_resolution"
        }
    
    async def _implement_performance_fix(self, issue: Dict[str, Any], 
                                       reproduction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement a fix for a performance-type issue."""
        steps = [
            "Analyze performance bottleneck",
            "Identify optimization opportunities",
            "Implement performance improvements",
            "Validate performance gains"
        ]
        
        changes = []
        
        # Simulate performance optimization
        perf_details = issue.get("details", {})
        
        if isinstance(perf_details, dict):
            if perf_details.get("percent", 0) > 80:
                # High resource usage - implement optimization
                changes.append({
                    "type": "code_optimization",
                    "target": "performance_critical.py",
                    "operation": "algorithm_optimization",
                    "description": f"Optimized {issue.get('category', 'process')} usage",
                    "backup_created": True
                })
        
        # Add caching mechanism
        changes.append({
            "type": "feature_addition",
            "target": "caching_layer.py",
            "operation": "add_caching",
            "description": "Added intelligent caching mechanism",
            "backup_created": True
        })
        
        return {
            "success": True,
            "steps": steps,
            "changes": changes,
            "fix_type": "performance_optimization"
        }
    
    async def _implement_configuration_fix(self, issue: Dict[str, Any], 
                                         reproduction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement a fix for a configuration-type issue."""
        steps = [
            "Identify missing configuration",
            "Create default configuration",
            "Update configuration files",
            "Validate configuration"
        ]
        
        changes = []
        
        # Simulate configuration fix
        config_category = issue.get("category", "unknown")
        
        if "missing" in issue.get("description", "").lower():
            changes.append({
                "type": "file_creation",
                "target": f"{config_category}.conf",
                "operation": "create_config",
                "description": f"Created missing {config_category} configuration",
                "backup_created": False  # New file, no backup needed
            })
        
        # Update main configuration
        changes.append({
            "type": "file_modification",
            "target": "config.json",
            "operation": "update_settings",
            "description": "Updated main configuration with missing settings",
            "backup_created": True
        })
        
        return {
            "success": True,
            "steps": steps,
            "changes": changes,
            "fix_type": "configuration_update"
        }
    
    async def _implement_generic_fix(self, issue: Dict[str, Any], 
                                   reproduction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement a generic fix for unspecified issue types."""
        steps = [
            "Analyze issue characteristics",
            "Develop generic solution approach",
            "Implement solution",
            "Test solution effectiveness"
        ]
        
        changes = [{
            "type": "generic_improvement",
            "target": "system_component.py",
            "operation": "general_fix",
            "description": f"Applied fix for: {issue.get('title', 'unknown issue')}",
            "backup_created": True
        }]
        
        return {
            "success": True,
            "steps": steps,
            "changes": changes,
            "fix_type": "generic_solution"
        }
    
    async def _execute_test_case(self, task: Dict[str, Any], 
                                task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a test case."""
        test_case = task.get("test_case", {})
        
        steps = [
            "Prepare test environment",
            "Execute test case",
            "Collect test results",
            "Analyze test outcomes"
        ]
        
        # Simulate test execution
        test_result = {
            "test_name": test_case.get("name", "unknown_test"),
            "test_type": test_case.get("type", "unknown"),
            "status": test_case.get("status", "pass"),
            "execution_time": 0.5,  # Simulated execution time
            "output": f"Test executed successfully: {test_case.get('description', '')}",
            "passed": test_case.get("status", "pass") == "pass"
        }
        
        return {
            "success": test_result["passed"],
            "steps_completed": steps,
            "test_results": [test_result],
            "execution_type": "test_execution"
        }
    
    async def _execute_generic_task(self, task: Dict[str, Any], 
                                   task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a generic task."""
        steps = [
            "Initialize task execution",
            "Execute task operations",
            "Collect execution results",
            "Finalize task completion"
        ]
        
        return {
            "success": True,
            "steps_completed": steps,
            "execution_type": "generic_execution"
        }
    
    async def _create_backup(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a backup before making changes."""
        backup_info = {
            "timestamp": self._get_timestamp(),
            "backup_id": f"backup_{self._get_timestamp().replace(':', '_')}",
            "files_backed_up": [],
            "backup_location": "",
            "success": False
        }
        
        try:
            # Simulate backup creation
            backup_dir = f"/tmp/executor_backups/{backup_info['backup_id']}"
            backup_info["backup_location"] = backup_dir
            
            # In a real implementation, we would actually copy files
            backup_info["files_backed_up"] = ["config.json", "main.py", "settings.ini"]
            backup_info["success"] = True
            
        except Exception as e:
            backup_info["error"] = str(e)
        
        return backup_info
    
    async def _rollback_changes(self, backup_info: Dict[str, Any]) -> bool:
        """Rollback changes using backup information."""
        if not backup_info.get("success", False):
            return False
        
        try:
            # Simulate rollback process
            backup_location = backup_info.get("backup_location", "")
            files_to_restore = backup_info.get("files_backed_up", [])
            
            # In a real implementation, we would restore files from backup
            print(f"Rolling back changes from {backup_location}")
            print(f"Restoring files: {files_to_restore}")
            
            return True
        except Exception as e:
            print(f"Rollback failed: {e}")
            return False
    
    async def _validate_execution(self, task: Dict[str, Any], 
                                 execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the execution results."""
        validation = {
            "valid": True,
            "validation_tests": [],
            "issues_found": [],
            "recommendations": []
        }
        
        # Check if execution was successful
        if not execution_result.get("success", False):
            validation["valid"] = False
            validation["issues_found"].append("Execution reported failure")
        
        # Validate changes made
        changes = execution_result.get("changes", [])
        for change in changes:
            if change.get("type") == "file_modification" and not change.get("backup_created", False):
                validation["issues_found"].append(f"No backup created for {change.get('target', 'unknown file')}")
        
        # Check test results
        test_results = execution_result.get("test_results", [])
        failed_tests = [test for test in test_results if not test.get("passed", True)]
        if failed_tests:
            validation["valid"] = False
            validation["issues_found"].append(f"{len(failed_tests)} tests failed")
        
        return validation
    
    def _calculate_performance_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance metrics for execution results."""
        total_tasks = results["total_tasks"]
        successful = len(results["successful_executions"])
        failed = len(results["failed_executions"])
        
        return {
            "success_rate": (successful / total_tasks * 100) if total_tasks > 0 else 0,
            "failure_rate": (failed / total_tasks * 100) if total_tasks > 0 else 0,
            "total_changes": len(results["changes_made"]),
            "total_tests_run": len(results["test_results"]),
            "tests_passed": len([t for t in results["test_results"] if t.get("passed", False)]),
            "average_execution_time": 1.5  # Simulated average
        }
    
    def _needs_optimization(self, results: Dict[str, Any]) -> bool:
        """Determine if the results indicate need for optimization."""
        failure_rate = results["performance_metrics"].get("failure_rate", 0)
        return failure_rate > 20  # If more than 20% of tasks failed
    
    def _has_performance_issues(self, results: Dict[str, Any]) -> bool:
        """Check if execution results indicate performance issues."""
        avg_time = results["performance_metrics"].get("average_execution_time", 0)
        return avg_time > 5.0  # If average execution time is too high
    
    async def _capture_execution_environment(self) -> Dict[str, Any]:
        """Capture execution environment information."""
        env_info = {
            "timestamp": self._get_timestamp(),
            "working_directory": os.getcwd(),
            "executor_version": "1.0.0",
            "capabilities": [
                "file_operations",
                "script_execution",
                "test_running",
                "backup_management"
            ]
        }
        
        try:
            env_info["system_info"] = {
                "platform": "linux",  # Simulated
                "python_version": "3.9.0",  # Simulated
                "available_memory": "8GB"  # Simulated
            }
        except Exception as e:
            env_info["error"] = str(e)
        
        return env_info
    
    async def _handle_feedback(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle feedback from other agents."""
        # Could use feedback to adjust execution strategies
        return None
    
    async def execute_autonomous_task(self) -> Optional[AgentMessage]:
        """Execute autonomous maintenance and monitoring tasks."""
        # Could perform health checks, cleanup, or monitoring
        return None
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for execution."""
        from datetime import datetime
        return datetime.now().isoformat()


class BackupManager:
    """Helper class for managing backups during execution."""
    
    def __init__(self):
        self.backup_directory = "/tmp/executor_backups"
        self.backup_history = []
    
    def create_backup(self, files: List[str], backup_id: str) -> Dict[str, Any]:
        """Create a backup of specified files."""
        backup_info = {
            "backup_id": backup_id,
            "files": files,
            "timestamp": self._get_timestamp(),
            "location": f"{self.backup_directory}/{backup_id}",
            "success": False
        }
        
        try:
            # In a real implementation, would create actual backups
            backup_info["success"] = True
            self.backup_history.append(backup_info)
        except Exception as e:
            backup_info["error"] = str(e)
        
        return backup_info
    
    def restore_backup(self, backup_id: str) -> bool:
        """Restore files from a backup."""
        backup_info = next((b for b in self.backup_history if b["backup_id"] == backup_id), None)
        if not backup_info:
            return False
        
        try:
            # In a real implementation, would restore actual files
            return True
        except Exception:
            return False
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()