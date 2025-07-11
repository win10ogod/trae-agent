# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""CodynfluxAgent for software engineering tasks."""

import asyncio
import os
import subprocess
from typing import override

from ..tools import tools_registry
from ..tools.base import Tool, ToolExecutor, ToolResult
from ..utils.config import Config
from ..utils.llm_basics import LLMMessage, LLMResponse
from .agent_basics import AgentError, AgentExecution
from .base import Agent

CodynfluxAgentToolNames = [
    "str_replace_based_edit_tool",
    "sequentialthinking", 
    "json_edit_tool",
    "task_done",
    "bash",
]

# DTDD-specific tool configuration
DTDDAgentToolNames = [
    "dtdd_workflow",
    "dtdd_prd_generator",
    "dtdd_sequence_diagram", 
    "dtdd_class_diagram",
    "dtdd_test_planning",
    "str_replace_based_edit_tool",
    "sequentialthinking",
    "bash",
    "task_done",
]


class CodynfluxAgent(Agent):
    """Codynflux Agent specialized for software engineering tasks."""

    def __init__(self, config: Config):
        self.project_path: str = ""
        self.base_commit: str | None = None
        self.must_patch: str = "false"
        self.patch_path: str | None = None
        self.dtdd_mode: bool = False  # DTDD workflow mode
        super().__init__(config)

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

    @override
    def new_task(
        self,
        task: str,
        extra_args: dict[str, str] | None = None,
        tool_names: list[str] | None = None,
    ):
        """Create a new task."""
        self._task: str = task

        # Check for DTDD mode
        if extra_args and extra_args.get("dtdd_mode") == "true":
            self.dtdd_mode = True

        if tool_names is None:
            tool_names = DTDDAgentToolNames if self.dtdd_mode else CodynfluxAgentToolNames

        # Get the model provider from the LLM client
        provider = self._llm_client.provider.value
        self._tools: list[Tool] = [
            tools_registry[tool_name](model_provider=provider) for tool_name in tool_names
        ]
        self._tool_caller: ToolExecutor = ToolExecutor(self._tools)

        self._initial_messages: list[LLMMessage] = []
        self._initial_messages.append(LLMMessage(role="system", content=self.get_system_prompt()))

        user_message = ""
        if not extra_args:
            raise AgentError("Project path and issue information are required.")
        if "project_path" not in extra_args:
            raise AgentError("Project path is required")

        self.project_path = extra_args.get("project_path", "")
        user_message += f"[Project root path]:\n{self.project_path}\n\n"

        if "issue" in extra_args:
            user_message += f"[Problem statement]: We're currently solving the following issue within our repository. Here's the issue text:\n{extra_args['issue']}\n"
        optional_attrs_to_set = ["base_commit", "must_patch", "patch_path"]
        for attr in optional_attrs_to_set:
            if attr in extra_args:
                setattr(self, attr, extra_args[attr])

        self._initial_messages.append(LLMMessage(role="user", content=user_message))

        # If trajectory recorder is set, start recording
        if self._trajectory_recorder:
            self._trajectory_recorder.start_recording(
                task=task,
                provider=self._llm_client.provider.value,
                model=self._model_parameters.model,
                max_steps=self._max_steps,
            )

    @override
    async def execute_task(self) -> AgentExecution:
        """Execute the task and finalize trajectory recording."""
        console_task = asyncio.create_task(self._cli_console.start()) if self._cli_console else None
        execution = await super().execute_task()
        if self._cli_console and console_task and not console_task.done():
            await console_task

        # Finalize trajectory recording if recorder is available
        if self._trajectory_recorder:
            self._trajectory_recorder.finalize_recording(
                success=execution.success, final_result=execution.final_result
            )

        if self.patch_path is not None:
            with open(self.patch_path, "w") as patch_f:
                patch_f.write(self.get_git_diff())

        return execution

    def get_system_prompt(self) -> str:
        """Get the system prompt for CodynfluxAgent."""
        if self.dtdd_mode:
            return self._get_dtdd_system_prompt()
        else:
            return self._get_standard_system_prompt()

    def _get_dtdd_system_prompt(self) -> str:
        """Get the DTDD (Document-Driven Development) system prompt."""
        return """You are an expert AI software engineering agent specialized in DTDD (Document-Driven Development) methodology.

All file system operations must use relative paths from the project root directory provided in the user's message. Do not assume you are in a `/repo` or `/workspace` directory. Always use the provided `[Project root path]` as your current working directory.

**DTDD METHODOLOGY OVERVIEW:**
DTDD (Document-Driven Development) is a systematic approach that emphasizes comprehensive documentation before implementation. This ensures risk reduction, improved efficiency, quality assurance, team collaboration, and maintainability.

**PRIMARY WORKFLOW - DTDD 4-Phase Approach:**

## Phase 1: PRD (Product Requirements Document)
Use the `dtdd_prd_generator` tool to create:
- Detailed product functional requirements
- Technical architecture planning
- System design concepts  
- Technology selection decisions
- Clear acceptance criteria

## Phase 2: Sequence Diagrams
Use the `dtdd_sequence_diagram` tool to visualize:
- System component interactions and sequence
- Data flow and processing steps
- Timing relationships and dependencies
- Error handling flows

## Phase 3: Class Diagrams  
Use the `dtdd_class_diagram` tool to plan:
- Class structure design
- Object relationships and associations
- Inheritance and composition relationships
- Interface definitions and implementations

## Phase 4: Test Planning
Use the `dtdd_test_planning` tool to ensure:
- Unit test planning and structure
- Integration test design
- Acceptance test standards
- Performance test scenarios

**WORKFLOW EXECUTION:**

1. **Requirements Analysis**: Understand the user's request and break it down into clear requirements
2. **Use dtdd_workflow Tool**: For comprehensive projects, use the `dtdd_workflow` tool to execute all phases automatically
3. **Individual Phase Tools**: For specific documentation needs, use individual DTDD tools
4. **Implementation**: Only after documentation is complete, proceed with actual coding
5. **Validation**: Ensure implementation matches the documented design

**TOOL USAGE PRIORITY:**
- Start with `dtdd_workflow` for new features/projects
- Use individual DTDD tools for specific documentation updates
- Use `sequential_thinking` for complex analysis
- Use standard tools (edit, bash) only after documentation phase

**QUALITY GATES:**
- Each phase must be completed before moving to the next
- Documentation must be reviewed and validated
- Implementation must follow documented design
- Tests must cover all documented requirements

Follow this methodology rigorously to ensure systematic, quality-driven development that reduces risks and improves maintainability."""

    def _get_standard_system_prompt(self) -> str:
        """Get the standard system prompt for regular development tasks."""
        return """You are an expert AI software engineering agent.

All file system operations must use relative paths from the project root directory provided in the user's message. Do not assume you are in a `/repo` or `/workspace` directory. Always use the provided `[Project root path]` as your current working directory.

Your primary goal is to resolve a given GitHub issue by navigating the provided codebase, identifying the root cause of the bug, implementing a robust fix, and ensuring your changes are safe and well-tested.

Follow these steps methodically:

1.  Understand the Problem:
    - Begin by carefully reading the user's problem description to fully grasp the issue.
    - Identify the core components and expected behavior.

2.  Explore and Locate:
    - Use the available tools to explore the codebase.
    - Locate the most relevant files (source code, tests, examples) related to the bug report.

3.  Reproduce the Bug (Crucial Step):
    - Before making any changes, you **must** create a script or a test case that reliably reproduces the bug. This will be your baseline for verification.
    - Analyze the output of your reproduction script to confirm your understanding of the bug's manifestation.

4.  Debug and Diagnose:
    - Inspect the relevant code sections you identified.
    - If necessary, create debugging scripts with print statements or use other methods to trace the execution flow and pinpoint the exact root cause of the bug.

5.  Develop and Implement a Fix:
    - Once you have identified the root cause, develop a precise and targeted code modification to fix it.
    - Use the provided file editing tools to apply your patch. Aim for minimal, clean changes.

6.  Verify and Test Rigorously:
    - Verify the Fix: Run your initial reproduction script to confirm that the bug is resolved.
    - Prevent Regressions: Execute the existing test suite for the modified files and related components to ensure your fix has not introduced any new bugs.
    - Write New Tests: Create new, specific test cases (e.g., using `pytest`) that cover the original bug scenario. This is essential to prevent the bug from recurring in the future. Add these tests to the codebase.
    - Consider Edge Cases: Think about and test potential edge cases related to your changes.

7.  Summarize Your Work:
    - Conclude your trajectory with a clear and concise summary. Explain the nature of the bug, the logic of your fix, and the steps you took to verify its correctness and safety.

**Guiding Principle:** Act like a senior software engineer. Prioritize correctness, safety, and high-quality, test-driven development.

# GUIDE FOR HOW TO USE "sequential_thinking" TOOL:
- Your thinking should be thorough and so it's fine if it's very long. Set total_thoughts to at least 5, but setting it up to 25 is fine as well. You'll need more total thoughts when you are considering multiple possible solutions or root causes for an issue.
- Use this tool as much as you find necessary to improve the quality of your answers.
- You can run bash commands (like tests, a reproduction script, or 'grep'/'find' to find relevant context) in between thoughts.
- The sequential_thinking tool can help you break down complex problems, analyze issues step-by-step, and ensure a thorough approach to problem-solving.
- Don't hesitate to use it multiple times throughout your thought process to enhance the depth and accuracy of your solutions.

If you are sure the issue has been solved, you should call the `task_done` to finish the task."""

    @override
    def reflect_on_result(self, tool_results: list[ToolResult]) -> str | None:
        return None

    def get_git_diff(self) -> str:
        """Get the git diff of the project."""
        pwd = os.getcwd()
        if not os.path.isdir(self.project_path):
            return ""
        os.chdir(self.project_path)
        try:
            if not self.base_commit:
                stdout = subprocess.check_output(["git", "--no-pager", "diff"]).decode()
            else:
                stdout = subprocess.check_output(
                    ["git", "--no-pager", "diff", self.base_commit, "HEAD"]
                ).decode()
        except (subprocess.CalledProcessError, FileNotFoundError):
            stdout = ""
        finally:
            os.chdir(pwd)
        return stdout

    # Copyright (c) 2024 paul-gauthier
    # SPDX-License-Identifier: Apache-2.0
    # Original remove_patches_to_tests function was released under Apache-2.0 License, with the full license text
    # available at https://github.com/Aider-AI/aider-swe-bench/blob/6e98cd6c3b2cbcba12976d6ae1b07f847480cb74/LICENSE.txt
    # Original function is at https://github.com/Aider-AI/aider-swe-bench/blob/6e98cd6c3b2cbcba12976d6ae1b07f847480cb74/tests.py#L45

    def remove_patches_to_tests(self, model_patch: str) -> str:
        """
        Remove any changes to the tests directory from the provided patch.
        This is to ensure that the model_patch does not disturb the repo's
        tests when doing acceptance testing with the `test_patch`.
        """
        lines = model_patch.splitlines(keepends=True)
        filtered_lines: list[str] = []
        test_patterns = ["/test/", "/tests/", "/testing/", "test_", "tox.ini"]
        is_tests = False

        for line in lines:
            if line.startswith("diff --git a/"):
                target_path = line.split()[-1]
                is_tests = target_path.startswith("b/") and any(
                    p in target_path for p in test_patterns
                )

            if not is_tests:
                filtered_lines.append(line)

        return "".join(filtered_lines)

    @override
    def llm_indicates_task_completed(self, llm_response: LLMResponse) -> bool:
        """Check if the LLM indicates that the task is completed."""
        if llm_response.tool_calls is None:
            return False
        return any(tool_call.name == "task_done" for tool_call in llm_response.tool_calls)

    @override
    def _is_task_completed(self, llm_response: LLMResponse) -> bool:
        """Enhanced task completion detection."""
        if self.must_patch == "true":
            model_patch = self.get_git_diff()
            patch = self.remove_patches_to_tests(model_patch)
            if not patch.strip():
                return False

        return True

    @override
    def task_incomplete_message(self) -> str:
        """Return a message indicating that the task is incomplete."""
        return "ERROR! Your Patch is empty. Please provide a patch that fixes the problem."
