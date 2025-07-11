# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""DTDD Class Diagram Planning Tool."""

import os
from datetime import datetime
from typing import Any, Dict

from .base import Tool, ToolCallArguments, ToolExecResult, ToolParameter


class DTDDClassDiagramTool(Tool):
    """Tool for planning program architecture and class relationships in DTDD workflow."""

    def get_name(self) -> str:
        return "dtdd_class_diagram"

    def get_description(self) -> str:
        return """Generate class diagrams to plan program architecture and relationships in DTDD workflow.
        
        This tool creates class diagrams that show:
        - Class structure design
        - Object relationships and associations
        - Inheritance and composition relationships
        - Interface definitions and implementations
        
        Use this as the third step in DTDD workflow after sequence diagrams to plan code structure."""

    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="module_name",
                type="string",
                description="Name of the module or component being designed",
                required=True
            ),
            ToolParameter(
                name="classes_description",
                type="string",
                description="Description of the main classes needed and their responsibilities",
                required=True
            ),
            ToolParameter(
                name="relationships",
                type="string",
                description="Description of relationships between classes (inheritance, composition, association)",
                required=True
            ),
            ToolParameter(
                name="interfaces",
                type="string",
                description="Interface definitions and contracts (optional)",
                required=False
            ),
            ToolParameter(
                name="design_patterns",
                type="string",
                description="Design patterns to be used (optional)",
                required=False
            ),
            ToolParameter(
                name="output_file",
                type="string",
                description="Path where the class diagram should be saved (default: docs/class_diagrams.md)",
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
        """Generate class diagrams for the specified module."""
        try:
            module_name = arguments.get("module_name", "")
            classes_description = arguments.get("classes_description", "")
            relationships = arguments.get("relationships", "")
            interfaces = arguments.get("interfaces", "")
            design_patterns = arguments.get("design_patterns", "")
            output_file = arguments.get("output_file", "docs/class_diagrams.md")
            diagram_format = arguments.get("diagram_format", "mermaid")

            # Create docs directory if it doesn't exist
            docs_dir = os.path.dirname(output_file)
            if docs_dir and not os.path.exists(docs_dir):
                os.makedirs(docs_dir, exist_ok=True)

            # Generate class diagram content
            diagram_content = self._generate_class_diagram(
                module_name, classes_description, relationships, interfaces, 
                design_patterns, diagram_format
            )

            # Check if file exists and append or create
            mode = 'a' if os.path.exists(output_file) else 'w'
            with open(output_file, mode, encoding='utf-8') as f:
                if mode == 'a':
                    f.write("\n\n---\n\n")
                f.write(diagram_content)

            return ToolExecResult(
                output=f"Class diagram for '{module_name}' added to: {output_file}"
            )

        except Exception as e:
            return ToolExecResult(
                error=f"Failed to generate class diagram: {str(e)}"
            )

    def _generate_class_diagram(self, module_name: str, classes_description: str, 
                              relationships: str, interfaces: str, design_patterns: str, 
                              diagram_format: str) -> str:
        """Generate the class diagram content."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if diagram_format == "mermaid":
            return self._generate_mermaid_class_diagram(
                module_name, classes_description, relationships, interfaces, 
                design_patterns, timestamp
            )
        else:
            return self._generate_plantuml_class_diagram(
                module_name, classes_description, relationships, interfaces, 
                design_patterns, timestamp
            )

    def _generate_mermaid_class_diagram(self, module_name: str, classes_description: str,
                                      relationships: str, interfaces: str, design_patterns: str,
                                      timestamp: str) -> str:
        """Generate Mermaid format class diagram."""
        
        # Parse class descriptions to extract class names
        classes = self._extract_classes_from_description(classes_description)
        
        # Generate class definitions
        class_definitions = self._generate_mermaid_classes(classes, classes_description)
        
        # Generate relationships
        relationship_definitions = self._generate_mermaid_relationships(relationships)
        
        return f"""# Class Diagram: {module_name}

**Created Date:** {timestamp}  
**DTDD Phase:** 3 - Program Structure and Relationship Planning

## Module: {module_name}

### Class Responsibilities
{classes_description}

### Class Diagram

```mermaid
classDiagram
{class_definitions}
{relationship_definitions}
```

### Relationships Description
{relationships}

{self._generate_interfaces_section(interfaces) if interfaces else ""}

{self._generate_design_patterns_section(design_patterns) if design_patterns else ""}

### Implementation Guidelines

#### Class Structure
- Follow Single Responsibility Principle
- Implement proper encapsulation with private/protected methods
- Use type hints for better code documentation
- Add proper docstrings for all public methods

#### Relationship Implementation
- Use composition over inheritance where possible
- Implement proper dependency injection
- Define clear interfaces/contracts
- Consider using abstract base classes for shared behavior

#### Code Quality
- Follow naming conventions (PEP 8 for Python)
- Implement proper error handling
- Add logging where appropriate
- Consider thread safety if needed

### Next Steps
1. Review class design with team
2. Create detailed test planning for each class
3. Begin implementation following the planned structure
4. Implement interfaces first, then concrete classes
"""

    def _generate_plantuml_class_diagram(self, module_name: str, classes_description: str,
                                       relationships: str, interfaces: str, design_patterns: str,
                                       timestamp: str) -> str:
        """Generate PlantUML format class diagram."""
        
        classes = self._extract_classes_from_description(classes_description)
        
        return f"""# Class Diagram: {module_name}

**Created Date:** {timestamp}  
**DTDD Phase:** 3 - Program Structure and Relationship Planning

## Module: {module_name}

### Class Responsibilities
{classes_description}

### Class Diagram

```plantuml
@startuml {module_name.replace(' ', '_')}_Classes
title {module_name} - Class Structure

{self._generate_plantuml_classes(classes, classes_description)}

{self._generate_plantuml_relationships(relationships)}

@enduml
```

### Relationships Description
{relationships}

{self._generate_interfaces_section(interfaces) if interfaces else ""}

{self._generate_design_patterns_section(design_patterns) if design_patterns else ""}

### Implementation Guidelines

#### Class Structure
- Follow Single Responsibility Principle
- Implement proper encapsulation with private/protected methods
- Use type hints for better code documentation
- Add proper docstrings for all public methods

#### Relationship Implementation
- Use composition over inheritance where possible
- Implement proper dependency injection
- Define clear interfaces/contracts
- Consider using abstract base classes for shared behavior

### Next Steps
1. Review class design with team
2. Create detailed test planning for each class
3. Begin implementation following the planned structure
4. Implement interfaces first, then concrete classes
"""

    def _extract_classes_from_description(self, description: str) -> list:
        """Extract potential class names from description."""
        # Simple extraction - look for capitalized words that might be class names
        import re
        words = re.findall(r'\b[A-Z][a-zA-Z]*\b', description)
        # Filter common words that aren't likely class names
        common_words = {'The', 'This', 'That', 'It', 'A', 'An', 'Each', 'All', 'Some', 'Any', 'When', 'Where', 'How', 'Why', 'What', 'Which'}
        classes = [word for word in words if word not in common_words]
        # Remove duplicates while preserving order
        return list(dict.fromkeys(classes))

    def _generate_mermaid_classes(self, classes: list, description: str) -> str:
        """Generate Mermaid class definitions."""
        if not classes:
            return "    class DefaultClass{\n        +method()\n    }"
        
        class_defs = []
        for class_name in classes[:5]:  # Limit to first 5 classes
            class_defs.append(f"""    class {class_name}{{
        -private_field: type
        +public_method(): type
        +get_property(): type
        +set_property(value: type)
    }}""")
        
        return "\n\n".join(class_defs)

    def _generate_mermaid_relationships(self, relationships: str) -> str:
        """Generate Mermaid relationship definitions."""
        if not relationships.strip():
            return ""
        
        # Simple relationship parsing
        lines = relationships.split('\n')
        relationship_defs = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Look for common relationship keywords
                if 'inherit' in line.lower() or 'extends' in line.lower():
                    relationship_defs.append("    Parent <|-- Child")
                elif 'compose' in line.lower() or 'has' in line.lower():
                    relationship_defs.append("    Container *-- Component")
                elif 'associate' in line.lower() or 'uses' in line.lower():
                    relationship_defs.append("    ClassA --> ClassB")
                elif 'implement' in line.lower():
                    relationship_defs.append("    Interface <|.. Implementation")
        
        return "\n" + "\n".join(relationship_defs) if relationship_defs else ""

    def _generate_plantuml_classes(self, classes: list, description: str) -> str:
        """Generate PlantUML class definitions."""
        if not classes:
            return "class DefaultClass {\n  +method()\n}"
        
        class_defs = []
        for class_name in classes[:5]:  # Limit to first 5 classes
            class_defs.append(f"""class {class_name} {{
  -private_field: type
  +public_method(): type
  +get_property(): type
  +set_property(value: type)
}}""")
        
        return "\n\n".join(class_defs)

    def _generate_plantuml_relationships(self, relationships: str) -> str:
        """Generate PlantUML relationship definitions."""
        if not relationships.strip():
            return ""
        
        lines = relationships.split('\n')
        relationship_defs = []
        
        for line in lines:
            line = line.strip()
            if line:
                if 'inherit' in line.lower() or 'extends' in line.lower():
                    relationship_defs.append("Parent <|-- Child")
                elif 'compose' in line.lower() or 'has' in line.lower():
                    relationship_defs.append("Container *-- Component")
                elif 'associate' in line.lower() or 'uses' in line.lower():
                    relationship_defs.append("ClassA --> ClassB")
                elif 'implement' in line.lower():
                    relationship_defs.append("Interface <|.. Implementation")
        
        return "\n" + "\n".join(relationship_defs) if relationship_defs else ""

    def _generate_interfaces_section(self, interfaces: str) -> str:
        """Generate interfaces section."""
        return f"""
### Interface Definitions
{interfaces}

#### Interface Design Principles
- Define clear contracts and method signatures
- Keep interfaces focused and cohesive
- Use abstract base classes where appropriate
- Document expected behavior and constraints
"""

    def _generate_design_patterns_section(self, design_patterns: str) -> str:
        """Generate design patterns section."""
        return f"""
### Design Patterns
{design_patterns}

#### Pattern Implementation Guidelines
- Choose patterns that solve real problems
- Don't over-engineer with unnecessary patterns
- Document why each pattern was chosen
- Ensure patterns are implemented correctly
"""