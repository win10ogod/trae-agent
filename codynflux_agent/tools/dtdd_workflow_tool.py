# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""DTDD Workflow Orchestrator Tool."""

import os
from datetime import datetime
from typing import Any, Dict, List

from .base import Tool, ToolCallArguments, ToolExecResult, ToolParameter


class DTDDWorkflowTool(Tool):
    """Tool for orchestrating the complete DTDD (Document-Driven Development) workflow."""

    def get_name(self) -> str:
        return "dtdd_workflow"

    def get_description(self) -> str:
        return """Orchestrate the complete DTDD (Document-Driven Development) workflow.
        
        This tool guides through all DTDD phases:
        1. PRD (Product Requirements Document) - Detailed requirements and technical documentation
        2. Sequence Diagrams - Program execution flow visualization
        3. Class Diagrams - Program structure and relationship planning  
        4. Test Planning - Comprehensive test strategy and implementation
        
        Use this tool to execute the full DTDD workflow for systematic development approach."""

    def get_parameters(self) -> list[ToolParameter]:
        """Get the tool parameters."""
        return [
            ToolParameter(
                name="project_name",
                type="string",
                description="Name of the project or feature being developed",
                required=True
            ),
            ToolParameter(
                name="requirements",
                type="string", 
                description="Detailed description of what needs to be built",
                required=True
            ),
            ToolParameter(
                name="workflow_phases",
                type="string",
                description="Phases to execute: 'all', 'prd', 'sequence', 'class', 'test' (comma-separated)",
                required=False
            ),
            ToolParameter(
                name="output_directory",
                type="string",
                description="Directory to save all DTDD documents",
                required=False
            ),
            ToolParameter(
                name="interactive_mode",
                type="boolean",
                description="Whether to prompt for detailed inputs for each phase",
                required=False
            )
        ]

    async def execute(self, arguments: ToolCallArguments) -> ToolExecResult:
        """Execute the DTDD workflow phases."""
        try:
            project_name = arguments.get("project_name", "")
            requirements = arguments.get("requirements", "")
            workflow_phases = arguments.get("workflow_phases", "all")
            output_directory = arguments.get("output_directory", "docs/dtdd")
            interactive_mode = arguments.get("interactive_mode", False)

            # Create output directory
            if not os.path.exists(output_directory):
                os.makedirs(output_directory, exist_ok=True)

            # Parse phases to execute
            if workflow_phases.lower() == "all":
                phases = ["prd", "sequence", "class", "test"]
            else:
                phases = [phase.strip().lower() for phase in workflow_phases.split(",")]

            # Execute workflow phases
            results = []
            execution_summary = self._create_workflow_summary(project_name, phases, output_directory)
            
            for phase in phases:
                if phase == "prd":
                    result = await self._execute_prd_phase(project_name, requirements, output_directory)
                elif phase == "sequence":
                    result = await self._execute_sequence_phase(project_name, requirements, output_directory)
                elif phase == "class":
                    result = await self._execute_class_phase(project_name, requirements, output_directory)
                elif phase == "test":
                    result = await self._execute_test_phase(project_name, requirements, output_directory)
                else:
                    result = f"Unknown phase: {phase}"
                
                results.append(f"{phase.upper()}: {result}")

            # Create summary document
            summary_file = os.path.join(output_directory, "DTDD_Workflow_Summary.md")
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(execution_summary)

            return ToolExecResult(
                output=f"DTDD workflow completed for '{project_name}'. Documents saved to: {output_directory}\n" + 
                       "\n".join(results)
            )

        except Exception as e:
            return ToolExecResult(
                error=f"Failed to execute DTDD workflow: {str(e)}"
            )

    def _create_workflow_summary(self, project_name: str, phases: List[str], output_directory: str) -> str:
        """Create a summary document for the DTDD workflow execution."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""# DTDD Workflow Summary: {project_name}

**Created Date:** {timestamp}  
**Workflow Type:** Document-Driven Development (DTDD)  
**Output Directory:** {output_directory}

---

## DTDD Methodology Overview

DTDD (Document-Driven Development) is a systematic approach that emphasizes comprehensive documentation before implementation. This methodology ensures:

- **Risk Reduction**: Identify potential issues early through detailed planning
- **Improved Efficiency**: Clear roadmap reduces rework and confusion
- **Quality Assurance**: Comprehensive testing strategy ensures reliable software
- **Team Collaboration**: Standardized documentation facilitates communication
- **Maintainability**: Detailed documentation aids future development

---

## Workflow Phases Executed

{self._generate_phases_checklist(phases)}

---

## Project Structure

The following documents have been generated as part of the DTDD workflow:

```
{output_directory}/
├── PRD.md                          # Product Requirements Document
├── sequence_diagrams.md            # System Flow Visualization
├── class_diagrams.md              # Code Structure Planning
├── test_plan.md                   # Quality Assurance Strategy
├── DTDD_Workflow_Summary.md       # This summary document
└── implementation_guidelines.md    # Next steps for development
```

---

## Document Dependencies

```mermaid
graph TD
    A[PRD - Requirements] --> B[Sequence Diagrams - Flow Design]
    B --> C[Class Diagrams - Structure Planning]
    C --> D[Test Planning - Quality Assurance]
    D --> E[Implementation - Code Development]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#ffebee
```

---

## Quality Gates

Each phase includes specific quality checkpoints:

### ✅ Phase 1: PRD (Product Requirements Document)
- [ ] Requirements are clear and measurable
- [ ] Technical architecture is well-defined
- [ ] Constraints and limitations are documented
- [ ] Success criteria are established

### ✅ Phase 2: Sequence Diagrams
- [ ] System interactions are visualized
- [ ] Data flow is clearly defined
- [ ] Error handling flows are documented
- [ ] Timing and dependencies are clear

### ✅ Phase 3: Class Diagrams
- [ ] Class responsibilities are well-defined
- [ ] Relationships are properly modeled
- [ ] Design patterns are appropriately applied
- [ ] Code structure follows best practices

### ✅ Phase 4: Test Planning
- [ ] Test coverage is comprehensive
- [ ] Test types are appropriate for requirements
- [ ] Acceptance criteria are testable
- [ ] Performance requirements are defined

---

## Implementation Roadmap

### Immediate Next Steps
1. **Review Documentation**: Validate all generated documents with stakeholders
2. **Setup Environment**: Prepare development and testing environments
3. **Begin Implementation**: Start coding following the documented structure
4. **Iterative Testing**: Implement tests alongside development

### Development Guidelines
- Follow the class structure defined in class diagrams
- Implement interfaces before concrete classes
- Write tests before or alongside implementation (TDD)
- Regularly validate against acceptance criteria

### Success Metrics
- All acceptance criteria met
- Test coverage targets achieved
- Performance benchmarks satisfied
- Documentation kept up-to-date

---

## Continuous Improvement

### Documentation Updates
- Review and update documents as requirements evolve
- Track changes and maintain version control
- Ensure team alignment on any modifications

### Process Refinement
- Gather feedback on DTDD process effectiveness
- Identify areas for improvement in future projects
- Share lessons learned with the team

---

## Tools and Resources

### Diagram Viewing
- **Mermaid**: Use GitHub, GitLab, or Mermaid Live Editor
- **PlantUML**: Use PlantUML online server or IDE plugins

### Documentation Management
- Version control all documents alongside code
- Use markdown for easy editing and viewing
- Maintain document templates for future projects

---

*This workflow summary was generated using DTDD methodology to ensure systematic and quality-driven development.*
"""

    def _generate_phases_checklist(self, phases: List[str]) -> str:
        """Generate a checklist of executed phases."""
        all_phases = {
            "prd": "✅ **Phase 1: PRD** - Product Requirements Document generated",
            "sequence": "✅ **Phase 2: Sequence Diagrams** - Program flow visualization created", 
            "class": "✅ **Phase 3: Class Diagrams** - Code structure planning completed",
            "test": "✅ **Phase 4: Test Planning** - Quality assurance strategy developed"
        }
        
        checklist = []
        for phase_key, description in all_phases.items():
            if phase_key in phases:
                checklist.append(description)
            else:
                checklist.append(description.replace("✅", "⏸️").replace(" generated", " (skipped)").replace(" created", " (skipped)").replace(" completed", " (skipped)").replace(" developed", " (skipped)"))
        
        return "\n".join(checklist)

    async def _execute_prd_phase(self, project_name: str, requirements: str, output_directory: str) -> str:
        """Execute PRD generation phase."""
        try:
            # Import the PRD tool
            from .dtdd_prd_tool import DTDDPRDTool
            
            prd_tool = DTDDPRDTool()
            result = await prd_tool.execute({
                "project_name": project_name,
                "requirements_description": requirements,
                "target_audience": "Development team and stakeholders",
                "technical_stack": "To be determined based on requirements",
                "constraints": "Budget, timeline, and technical constraints to be defined",
                "output_file": os.path.join(output_directory, "PRD.md")
            })
            
            return "PRD document generated successfully" if result.output else f"PRD generation failed: {result.error}"
        except Exception as e:
            return f"PRD phase error: {str(e)}"

    async def _execute_sequence_phase(self, project_name: str, requirements: str, output_directory: str) -> str:
        """Execute sequence diagram generation phase."""
        try:
            from .dtdd_sequence_diagram_tool import DTDDSequenceDiagramTool
            
            sequence_tool = DTDDSequenceDiagramTool()
            result = await sequence_tool.execute({
                "use_case_name": f"{project_name} Main Flow",
                "actors": "User, System, Database, External Service",
                "main_flow": f"Based on requirements: {requirements[:200]}...",
                "alternative_flows": "Error handling and edge cases to be defined",
                "output_file": os.path.join(output_directory, "sequence_diagrams.md")
            })
            
            return "Sequence diagrams generated successfully" if result.output else f"Sequence diagram generation failed: {result.error}"
        except Exception as e:
            return f"Sequence phase error: {str(e)}"

    async def _execute_class_phase(self, project_name: str, requirements: str, output_directory: str) -> str:
        """Execute class diagram generation phase."""
        try:
            from .dtdd_class_diagram_tool import DTDDClassDiagramTool
            
            class_tool = DTDDClassDiagramTool()
            result = await class_tool.execute({
                "module_name": project_name,
                "classes_description": f"Based on requirements: {requirements}",
                "relationships": "Class relationships to be defined based on system design",
                "interfaces": "Interfaces and contracts to be specified",
                "design_patterns": "Appropriate design patterns to be selected",
                "output_file": os.path.join(output_directory, "class_diagrams.md")
            })
            
            return "Class diagrams generated successfully" if result.output else f"Class diagram generation failed: {result.error}"
        except Exception as e:
            return f"Class phase error: {str(e)}"

    async def _execute_test_phase(self, project_name: str, requirements: str, output_directory: str) -> str:
        """Execute test planning phase."""
        try:
            from .dtdd_test_planning_tool import DTDDTestPlanningTool
            
            test_tool = DTDDTestPlanningTool()
            result = await test_tool.execute({
                "component_name": project_name,
                "test_scope": f"Testing scope based on: {requirements}",
                "test_types": "unit, integration, acceptance",
                "acceptance_criteria": "Acceptance criteria to be derived from requirements",
                "edge_cases": "Edge cases and error conditions to be identified",
                "performance_requirements": "Performance benchmarks to be defined",
                "output_file": os.path.join(output_directory, "test_plan.md"),
                "generate_test_code": True
            })
            
            return "Test planning completed successfully" if result.output else f"Test planning failed: {result.error}"
        except Exception as e:
            return f"Test phase error: {str(e)}"