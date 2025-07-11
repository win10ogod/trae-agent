# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""DTDD Sequence Diagram Generation Tool."""

import os
from datetime import datetime
from typing import Any, Dict

from .base import Tool, ToolCallArguments, ToolExecResult, ToolParameter


class DTDDSequenceDiagramTool(Tool):
    """Tool for generating sequence diagrams to visualize program execution flow in DTDD workflow."""

    def get_name(self) -> str:
        return "dtdd_sequence_diagram"

    def get_description(self) -> str:
        return """Generate sequence diagrams to visualize program execution flow in DTDD workflow.
        
        This tool creates sequence diagrams that show:
        - System component interactions and sequence
        - Data flow and processing steps
        - Timing relationships and dependencies
        - Error handling flows
        
        Use this as the second step in DTDD workflow after PRD to design system interactions."""

    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="use_case_name",
                type="string",
                description="Name of the use case or user story being diagrammed",
                required=True
            ),
            ToolParameter(
                name="actors",
                type="string",
                description="List of actors/participants in the sequence (e.g., User, API, Database, Service)",
                required=True
            ),
            ToolParameter(
                name="main_flow",
                type="string",
                description="Description of the main flow of interactions step by step",
                required=True
            ),
            ToolParameter(
                name="alternative_flows",
                type="string",
                description="Alternative or error handling flows (optional)",
                required=False
            ),
            ToolParameter(
                name="output_file",
                type="string",
                description="Path where the sequence diagram should be saved (default: docs/sequence_diagrams.md)",
                required=False
            ),
            ToolParameter(
                name="diagram_format",
                type="string",
                description="Format for the diagram: 'mermaid' or 'plantuml'",
                required=False,
                enum=["mermaid", "plantuml"]
            )
        ]

    async def execute(self, arguments: ToolCallArguments) -> ToolExecResult:
        """Generate sequence diagrams for the specified use case."""
        try:
            use_case_name = arguments.get("use_case_name", "")
            actors = arguments.get("actors", "")
            main_flow = arguments.get("main_flow", "")
            alternative_flows = arguments.get("alternative_flows", "")
            output_file = arguments.get("output_file", "docs/sequence_diagrams.md")
            diagram_format = arguments.get("diagram_format", "mermaid")

            # Create docs directory if it doesn't exist
            docs_dir = os.path.dirname(output_file)
            if docs_dir and not os.path.exists(docs_dir):
                os.makedirs(docs_dir, exist_ok=True)

            # Generate sequence diagram content
            diagram_content = self._generate_sequence_diagram(
                use_case_name, actors, main_flow, alternative_flows, diagram_format
            )

            # Check if file exists and append or create
            mode = 'a' if os.path.exists(output_file) else 'w'
            with open(output_file, mode, encoding='utf-8') as f:
                if mode == 'a':
                    f.write("\n\n---\n\n")
                f.write(diagram_content)

            return ToolExecResult(
                output=f"Sequence diagram for '{use_case_name}' added to: {output_file}"
            )

        except Exception as e:
            return ToolExecResult(
                error=f"Failed to generate sequence diagram: {str(e)}"
            )

    def _generate_sequence_diagram(self, use_case_name: str, actors: str, main_flow: str, 
                                 alternative_flows: str, diagram_format: str) -> str:
        """Generate the sequence diagram content."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if diagram_format == "mermaid":
            return self._generate_mermaid_diagram(use_case_name, actors, main_flow, alternative_flows, timestamp)
        else:
            return self._generate_plantuml_diagram(use_case_name, actors, main_flow, alternative_flows, timestamp)

    def _generate_mermaid_diagram(self, use_case_name: str, actors: str, main_flow: str, 
                                alternative_flows: str, timestamp: str) -> str:
        """Generate Mermaid format sequence diagram."""
        
        # Parse actors
        actor_list = [actor.strip() for actor in actors.split(',')]
        
        # Generate participants
        participants = "\n".join([f"    participant {actor}" for actor in actor_list])
        
        # Generate basic flow interactions (this is a template - would need more sophisticated parsing)
        interactions = self._parse_flow_to_mermaid(main_flow, actor_list)
        
        return f"""# Sequence Diagram: {use_case_name}

**Created Date:** {timestamp}  
**DTDD Phase:** 2 - Program Execution Flow Design

## Use Case: {use_case_name}

### Actors/Participants
{', '.join(actor_list)}

### Main Flow Sequence Diagram

```mermaid
sequenceDiagram
{participants}
    
    Note over {actor_list[0]}: {use_case_name} - Main Flow
{interactions}
```

### Main Flow Description
{main_flow}

{self._generate_alternative_flows_section(alternative_flows) if alternative_flows else ""}

### Implementation Notes
- Ensure proper error handling at each interaction point
- Consider timeout and retry mechanisms for external service calls
- Implement logging for debugging and monitoring
- Add authentication/authorization checks where needed

### Next Steps
1. Validate sequence with stakeholders
2. Create class diagrams based on identified components
3. Plan detailed test cases for each interaction
"""

    def _generate_plantuml_diagram(self, use_case_name: str, actors: str, main_flow: str, 
                                 alternative_flows: str, timestamp: str) -> str:
        """Generate PlantUML format sequence diagram."""
        
        actor_list = [actor.strip() for actor in actors.split(',')]
        
        return f"""# Sequence Diagram: {use_case_name}

**Created Date:** {timestamp}  
**DTDD Phase:** 2 - Program Execution Flow Design

## Use Case: {use_case_name}

### Actors/Participants
{', '.join(actor_list)}

### Main Flow Sequence Diagram

```plantuml
@startuml {use_case_name.replace(' ', '_')}
title {use_case_name} - Main Flow

{chr(10).join([f'actor "{actor}" as {actor.replace(" ", "")}' for actor in actor_list])}

note over {actor_list[0].replace(" ", "")}: {use_case_name} starts

{self._parse_flow_to_plantuml(main_flow, actor_list)}

@enduml
```

### Main Flow Description
{main_flow}

{self._generate_alternative_flows_section(alternative_flows) if alternative_flows else ""}

### Implementation Notes
- Ensure proper error handling at each interaction point
- Consider timeout and retry mechanisms for external service calls
- Implement logging for debugging and monitoring
- Add authentication/authorization checks where needed

### Next Steps
1. Validate sequence with stakeholders
2. Create class diagrams based on identified components
3. Plan detailed test cases for each interaction
"""

    def _parse_flow_to_mermaid(self, flow_description: str, actors: list) -> str:
        """Parse flow description into Mermaid sequence interactions."""
        # This is a simplified parser - would need more sophisticated NLP in production
        lines = flow_description.split('\n')
        interactions = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line:
                # Try to identify actor patterns in the description
                for j, actor in enumerate(actors):
                    if actor.lower() in line.lower():
                        next_actor = actors[(j + 1) % len(actors)]
                        interactions.append(f"    {actor}->>{next_actor}: {line}")
                        break
                else:
                    # Default interaction
                    if len(actors) >= 2:
                        interactions.append(f"    {actors[0]}->>{actors[1]}: {line}")
        
        return "\n".join(interactions) if interactions else f"    {actors[0]}->>{actors[1] if len(actors) > 1 else actors[0]}: {flow_description}"

    def _parse_flow_to_plantuml(self, flow_description: str, actors: list) -> str:
        """Parse flow description into PlantUML sequence interactions."""
        lines = flow_description.split('\n')
        interactions = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line:
                for j, actor in enumerate(actors):
                    if actor.lower() in line.lower():
                        next_actor = actors[(j + 1) % len(actors)]
                        interactions.append(f'{actor.replace(" ", "")} -> {next_actor.replace(" ", "")}: {line}')
                        break
                else:
                    if len(actors) >= 2:
                        interactions.append(f'{actors[0].replace(" ", "")} -> {actors[1].replace(" ", "")}: {line}')
        
        return "\n".join(interactions) if interactions else f'{actors[0].replace(" ", "")} -> {actors[1].replace(" ", "") if len(actors) > 1 else actors[0].replace(" ", "")}: {flow_description}'

    def _generate_alternative_flows_section(self, alternative_flows: str) -> str:
        """Generate alternative flows section."""
        return f"""
### Alternative/Error Flows
{alternative_flows}

### Error Handling Considerations
- Input validation errors
- Network connectivity issues
- Service unavailability
- Authentication/authorization failures
- Data consistency errors
"""