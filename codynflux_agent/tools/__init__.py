# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""Tools module for Codynflux Agent."""

from typing import Type

from .base import Tool, ToolCall, ToolExecutor, ToolResult
from .bash_tool import BashTool
from .edit_tool import TextEditorTool
from .json_edit_tool import JSONEditTool
from .sequential_thinking_tool import SequentialThinkingTool
from .dtdd_prd_tool import DTDDPRDTool
from .dtdd_sequence_diagram_tool import DTDDSequenceDiagramTool
from .dtdd_class_diagram_tool import DTDDClassDiagramTool
from .dtdd_test_planning_tool import DTDDTestPlanningTool
from .dtdd_workflow_tool import DTDDWorkflowTool
from .task_done_tool import TaskDoneTool

__all__ = [
    "Tool",
    "ToolResult",
    "ToolCall",
    "ToolExecutor",
    "BashTool",
    "TextEditorTool",
    "JSONEditTool",
    "SequentialThinkingTool",
    "TaskDoneTool",
    "DTDDPRDTool",
    "DTDDSequenceDiagramTool", 
    "DTDDClassDiagramTool",
    "DTDDTestPlanningTool",
    "DTDDWorkflowTool",
]

tools_registry: dict[str, Type[Tool]] = {
    "bash": BashTool,
    "str_replace_based_edit_tool": TextEditorTool,
    "json_edit_tool": JSONEditTool,
    "sequentialthinking": SequentialThinkingTool,
    "task_done": TaskDoneTool,
    "dtdd_prd_generator": DTDDPRDTool,
    "dtdd_sequence_diagram": DTDDSequenceDiagramTool,
    "dtdd_class_diagram": DTDDClassDiagramTool,
    "dtdd_test_planning": DTDDTestPlanningTool,
    "dtdd_workflow": DTDDWorkflowTool,
}
