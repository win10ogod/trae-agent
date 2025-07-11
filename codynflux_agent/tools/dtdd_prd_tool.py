# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""DTDD PRD (Product Requirements Document) Generation Tool."""

import os
from datetime import datetime
from typing import Any, Dict

from .base import Tool, ToolCallArguments, ToolExecResult, ToolParameter


class DTDDPRDTool(Tool):
    """Tool for generating Product Requirements Document (PRD) in DTDD workflow."""

    def get_name(self) -> str:
        return "dtdd_prd_generator"

    def get_description(self) -> str:
        return """Generate a comprehensive Product Requirements Document (PRD) for DTDD workflow.
        
        This tool creates a detailed PRD that includes:
        - Product functional requirements
        - Technical architecture planning
        - System design concepts
        - Technology selection decisions
        
        Use this as the first step in DTDD workflow to establish clear requirements and technical documentation."""

    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="project_name",
                type="string",
                description="Name of the project or feature being developed",
                required=True
            ),
            ToolParameter(
                name="requirements_description",
                type="string",
                description="Detailed description of the requirements and what needs to be built",
                required=True
            ),
            ToolParameter(
                name="target_audience",
                type="string",
                description="Target users or audience for this feature/project",
                required=True
            ),
            ToolParameter(
                name="technical_stack",
                type="string",
                description="Preferred or existing technical stack (languages, frameworks, tools)",
                required=True
            ),
            ToolParameter(
                name="constraints",
                type="string",
                description="Any constraints, limitations, or specific requirements (performance, security, etc.)",
                required=False
            ),
            ToolParameter(
                name="output_file",
                type="string",
                description="Path where the PRD document should be saved (default: docs/PRD.md)",
                required=False
            )
        ]

    async def execute(self, arguments: ToolCallArguments) -> ToolExecResult:
        """Generate a comprehensive PRD document."""
        try:
            project_name = arguments.get("project_name", "")
            requirements_description = arguments.get("requirements_description", "")
            target_audience = arguments.get("target_audience", "")
            technical_stack = arguments.get("technical_stack", "")
            constraints = arguments.get("constraints", "No specific constraints mentioned")
            output_file = arguments.get("output_file", "docs/PRD.md")

            # Create docs directory if it doesn't exist
            docs_dir = os.path.dirname(output_file)
            if docs_dir and not os.path.exists(docs_dir):
                os.makedirs(docs_dir, exist_ok=True)

            # Generate PRD content
            prd_content = self._generate_prd_content(
                project_name, requirements_description, target_audience, 
                technical_stack, constraints
            )

            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(prd_content)

            return ToolExecResult(
                output=f"PRD document successfully generated at: {output_file}"
            )

        except Exception as e:
            return ToolExecResult(
                error=f"Failed to generate PRD: {str(e)}"
            )

    def _generate_prd_content(self, project_name: str, requirements_description: str, 
                             target_audience: str, technical_stack: str, constraints: str) -> str:
        """Generate the actual PRD content."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""# Product Requirements Document (PRD)
# {project_name}

**Created Date:** {timestamp}  
**Document Version:** 1.0  
**DTDD Phase:** 1 - Requirements & Technical Documentation

---

## 1. Executive Summary

### Project Overview
{requirements_description}

### Target Audience
{target_audience}

---

## 2. Product Functional Requirements

### 2.1 Core Features
<!-- Detail the main functionalities that need to be implemented -->

### 2.2 User Stories
<!-- Define user stories in the format: As a [user], I want [goal] so that [benefit] -->

### 2.3 Acceptance Criteria
<!-- Define clear criteria for when each feature is considered complete -->

---

## 3. Technical Architecture Planning

### 3.1 Technology Stack
{technical_stack}

### 3.2 System Architecture Overview
<!-- High-level system architecture description -->

### 3.3 Data Architecture
<!-- Database design, data flow, and storage requirements -->

### 3.4 API Design
<!-- API endpoints, request/response formats, authentication -->

---

## 4. System Design Concepts

### 4.1 Design Patterns
<!-- Recommended design patterns for this project -->

### 4.2 Scalability Considerations
<!-- How the system will handle growth and increased load -->

### 4.3 Security Requirements
<!-- Security measures, authentication, authorization, data protection -->

### 4.4 Performance Requirements
<!-- Response times, throughput, resource utilization targets -->

---

## 5. Technology Selection Decisions

### 5.1 Framework Selection
<!-- Rationale for chosen frameworks and libraries -->

### 5.2 Database Technology
<!-- Database selection reasoning -->

### 5.3 Infrastructure Decisions
<!-- Deployment, hosting, CI/CD considerations -->

### 5.4 Third-party Integrations
<!-- External services and APIs to be integrated -->

---

## 6. Constraints and Limitations

### 6.1 Technical Constraints
{constraints}

### 6.2 Business Constraints
<!-- Budget, timeline, resource limitations -->

### 6.3 Regulatory Requirements
<!-- Compliance requirements, legal considerations -->

---

## 7. Risk Assessment

### 7.1 Technical Risks
<!-- Potential technical challenges and mitigation strategies -->

### 7.2 Project Risks
<!-- Timeline, resource, scope risks -->

---

## 8. Success Metrics

### 8.1 Key Performance Indicators (KPIs)
<!-- Measurable metrics to evaluate project success -->

### 8.2 Quality Metrics
<!-- Code quality, test coverage, performance benchmarks -->

---

## 9. Timeline and Milestones

### 9.1 Development Phases
<!-- Break down the project into manageable phases -->

### 9.2 Key Milestones
<!-- Important checkpoints and deliverables -->

---

## 10. Next Steps (DTDD Workflow)

1. **Sequence Diagram Creation** - Design system interaction flows
2. **Class Diagram Planning** - Define program structure and relationships  
3. **Test Planning** - Design comprehensive testing strategy
4. **Implementation** - Begin coding based on documented requirements

---

## Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | | | |
| Technical Lead | | | |
| Project Manager | | | |

---

*This document was generated using DTDD (Document-Driven Development) methodology to ensure comprehensive planning before implementation.*
"""