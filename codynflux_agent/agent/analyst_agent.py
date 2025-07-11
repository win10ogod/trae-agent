# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""Analyst Agent - Data analysis and pattern recognition agent."""

from typing import Optional, Dict, Any, List
import json
import re

from ..utils.config import Config
from ..utils.llm_basics import LLMMessage
from .multi_agent_base import (
    MultiAgent, AgentRole, AgentMessage, MessageType, AgentStatus,
    MultiAgentCommunicationHub
)


class AnalystAgent(MultiAgent):
    """
    Analyst Agent (分析者) - Data analysis and pattern recognition.
    
    Responsibilities:
    - Analyze observations from Observer agent
    - Identify patterns, trends, and anomalies
    - Diagnose problems and root causes
    - Generate insights and recommendations
    - Prepare analysis for Reproducer agent
    """
    
    def __init__(self, config: Config, communication_hub: MultiAgentCommunicationHub):
        super().__init__(config, AgentRole.ANALYST, communication_hub)
        self.analysis_history = []
        self.current_analysis = None
        self.identified_patterns = []
        
    def new_task(self, task: str, extra_args: Dict[str, str] | None = None, 
                 tool_names: list[str] | None = None):
        """Initialize analysis task."""
        self._task = task
        self.current_analysis = {
            "task": task,
            "observations": [],
            "patterns": [],
            "insights": [],
            "recommendations": [],
            "root_causes": [],
            "context": extra_args or {}
        }
        
        # Set up initial messages for LLM
        self._initial_messages = [
            LLMMessage(role="system", content=self.get_system_prompt()),
            LLMMessage(role="user", content=f"Begin analysis for: {task}")
        ]
        
        self.update_status(AgentStatus.WORKING, "Analyzing data and patterns")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for Analyst agent."""
        return """You are the Analyst Agent (分析者) in a six-agent coordination system.

Your primary responsibilities:
1. **Data Analysis**: Process observations and extract meaningful insights
2. **Pattern Recognition**: Identify trends, correlations, and anomalies in data
3. **Root Cause Analysis**: Diagnose underlying problems and their sources
4. **Problem Classification**: Categorize issues by type, severity, and impact
5. **Recommendation Generation**: Propose solutions and next steps

**Analysis Methodologies:**
- **Statistical Analysis**: Quantitative data processing and trend analysis
- **Logical Reasoning**: Systematic problem decomposition and inference
- **Pattern Matching**: Recognition of known issue patterns and signatures
- **Risk Assessment**: Evaluation of potential impacts and failure modes
- **Dependency Analysis**: Understanding relationships and connections
- **Performance Analysis**: Efficiency, bottleneck, and optimization opportunities

**Analysis Categories:**
- **Error Analysis**: Bug identification, exception patterns, failure modes
- **Performance Analysis**: Speed, memory, resource utilization issues
- **Security Analysis**: Vulnerability assessment, threat identification
- **Usability Analysis**: User experience issues, interaction problems
- **Code Quality Analysis**: Maintainability, complexity, best practices
- **System Architecture Analysis**: Design flaws, scalability concerns

**Analysis Process:**
1. **Data Examination**: Review all observations systematically
2. **Pattern Detection**: Identify recurring themes and anomalies
3. **Hypothesis Formation**: Develop theories about causes and relationships
4. **Evidence Evaluation**: Assess strength and reliability of findings
5. **Conclusion Drawing**: Synthesize insights into actionable recommendations
6. **Priority Assignment**: Rank issues by importance and urgency

**Reporting Standards:**
- Provide clear, structured analysis reports
- Include confidence levels for findings
- Highlight critical issues requiring immediate attention
- Suggest specific, actionable next steps
- Document analytical reasoning and methodology

Be thorough, logical, and evidence-based in your analysis."""
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming analysis requests."""
        
        if message.message_type == MessageType.TASK_ASSIGNMENT:
            return await self._handle_analysis_request(message)
            
        elif message.message_type == MessageType.FEEDBACK:
            return await self._handle_feedback(message)
            
        return None
    
    async def _handle_analysis_request(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle analysis requests from Commander."""
        observer_results = message.data.get("observer_results", {})
        task_context = message.data.get("task_context", {})
        
        # Perform comprehensive analysis
        analysis_results = await self._analyze_observations(observer_results, task_context)
        
        # Store analysis in history
        self.analysis_history.append(analysis_results)
        self.current_analysis = analysis_results
        
        # Send analysis results back to Commander
        return AgentMessage(
            sender_role=self.role,
            receiver_role=AgentRole.COMMANDER,
            message_type=MessageType.FEEDBACK,
            content=f"Analysis completed. Identified {len(analysis_results['findings'])} key findings.",
            data=analysis_results
        )
    
    async def _analyze_observations(self, observer_results: Dict[str, Any], 
                                  task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze observations from Observer agent."""
        observations = observer_results.get("observations", [])
        
        analysis_results = {
            "task": task_context.get("original_task", ""),
            "observation_summary": self._summarize_observations(observations),
            "findings": [],
            "patterns": [],
            "root_causes": [],
            "recommendations": [],
            "priority_issues": [],
            "confidence_scores": {},
            "analysis_metadata": {
                "observation_count": len(observations),
                "analysis_timestamp": self._get_timestamp(),
                "observation_sources": observer_results.get("sources", [])
            }
        }
        
        # Perform different types of analysis
        findings = await self._identify_findings(observations)
        patterns = await self._detect_patterns(observations)
        root_causes = await self._analyze_root_causes(findings, patterns)
        recommendations = await self._generate_recommendations(findings, root_causes)
        
        analysis_results.update({
            "findings": findings,
            "patterns": patterns,
            "root_causes": root_causes,
            "recommendations": recommendations,
            "priority_issues": self._prioritize_issues(findings, root_causes)
        })
        
        return analysis_results
    
    def _summarize_observations(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize the key aspects of observations."""
        summary = {
            "total_observations": len(observations),
            "observation_types": {},
            "categories": {},
            "error_count": 0,
            "warning_count": 0
        }
        
        for obs in observations:
            obs_type = obs.get("type", "unknown")
            category = obs.get("category", "unknown")
            
            # Count observation types
            summary["observation_types"][obs_type] = summary["observation_types"].get(obs_type, 0) + 1
            
            # Count categories
            summary["categories"][category] = summary["categories"].get(category, 0) + 1
            
            # Count errors and warnings
            if "error" in str(obs.get("value", "")).lower():
                summary["error_count"] += 1
            elif "warning" in str(obs.get("value", "")).lower():
                summary["warning_count"] += 1
        
        return summary
    
    async def _identify_findings(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify key findings from observations."""
        findings = []
        
        for obs in observations:
            finding = await self._analyze_single_observation(obs)
            if finding:
                findings.append(finding)
        
        # Add aggregate findings
        aggregate_findings = await self._identify_aggregate_findings(observations)
        findings.extend(aggregate_findings)
        
        return findings
    
    async def _analyze_single_observation(self, observation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze a single observation for findings."""
        obs_type = observation.get("type", "")
        category = observation.get("category", "")
        value = observation.get("value", "")
        description = observation.get("description", "")
        
        finding = None
        
        # Error analysis
        if category == "error" or "error" in str(value).lower():
            finding = {
                "type": "error",
                "severity": "high",
                "title": f"Error detected in {obs_type}",
                "description": description,
                "details": value,
                "category": category,
                "requires_attention": True
            }
        
        # Performance analysis
        elif obs_type == "process" and "usage" in category:
            if isinstance(value, dict) and "percent" in value:
                usage_percent = value.get("percent", 0)
                if usage_percent > 80:
                    finding = {
                        "type": "performance",
                        "severity": "medium",
                        "title": f"High {category.replace('_', ' ')}",
                        "description": f"{category} at {usage_percent}%",
                        "details": value,
                        "category": category,
                        "requires_attention": True
                    }
            elif isinstance(value, (int, float)) and value > 80:
                finding = {
                    "type": "performance",
                    "severity": "medium",
                    "title": f"High {category.replace('_', ' ')}",
                    "description": f"{category} at {value}%",
                    "details": value,
                    "category": category,
                    "requires_attention": True
                }
        
        # Configuration analysis
        elif obs_type == "configuration":
            if not value or (isinstance(value, list) and len(value) == 0):
                finding = {
                    "type": "configuration",
                    "severity": "low",
                    "title": f"Missing {category}",
                    "description": description,
                    "details": "No configuration found",
                    "category": category,
                    "requires_attention": False
                }
        
        return finding
    
    async def _identify_aggregate_findings(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify findings from aggregate observation patterns."""
        findings = []
        
        # Count observation types
        type_counts = {}
        error_count = 0
        
        for obs in observations:
            obs_type = obs.get("type", "unknown")
            type_counts[obs_type] = type_counts.get(obs_type, 0) + 1
            
            if obs.get("category") == "error":
                error_count += 1
        
        # Multiple errors finding
        if error_count > 3:
            findings.append({
                "type": "system",
                "severity": "high",
                "title": "Multiple system errors detected",
                "description": f"Found {error_count} errors across different system components",
                "details": {"error_count": error_count},
                "category": "system_health",
                "requires_attention": True
            })
        
        # Data completeness finding
        if len(type_counts) < 3:
            findings.append({
                "type": "data",
                "severity": "medium",
                "title": "Limited observation coverage",
                "description": f"Only {len(type_counts)} observation types collected",
                "details": {"types": list(type_counts.keys())},
                "category": "data_quality",
                "requires_attention": False
            })
        
        return findings
    
    async def _detect_patterns(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect patterns in observations."""
        patterns = []
        
        # Group observations by type and category
        grouped_obs = {}
        for obs in observations:
            key = f"{obs.get('type', 'unknown')}:{obs.get('category', 'unknown')}"
            if key not in grouped_obs:
                grouped_obs[key] = []
            grouped_obs[key].append(obs)
        
        # Analyze patterns in each group
        for group_key, group_obs in grouped_obs.items():
            if len(group_obs) > 1:
                pattern = await self._analyze_observation_group(group_key, group_obs)
                if pattern:
                    patterns.append(pattern)
        
        # Cross-group pattern analysis
        cross_patterns = await self._analyze_cross_group_patterns(grouped_obs)
        patterns.extend(cross_patterns)
        
        return patterns
    
    async def _analyze_observation_group(self, group_key: str, observations: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analyze patterns within a group of similar observations."""
        if len(observations) <= 1:
            return None
        
        pattern_type, category = group_key.split(":", 1)
        
        return {
            "pattern_type": "repetition",
            "category": category,
            "observation_type": pattern_type,
            "count": len(observations),
            "description": f"Multiple {category} observations in {pattern_type}",
            "significance": "medium" if len(observations) > 2 else "low",
            "details": {
                "group_key": group_key,
                "observation_count": len(observations)
            }
        }
    
    async def _analyze_cross_group_patterns(self, grouped_obs: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Analyze patterns across different observation groups."""
        patterns = []
        
        # Error correlation pattern
        error_groups = [key for key in grouped_obs.keys() if "error" in key.lower()]
        if len(error_groups) > 1:
            patterns.append({
                "pattern_type": "error_correlation",
                "category": "system_health",
                "observation_type": "cross_system",
                "count": len(error_groups),
                "description": f"Errors detected across {len(error_groups)} different system components",
                "significance": "high",
                "details": {
                    "error_groups": error_groups,
                    "correlation_strength": "medium"
                }
            })
        
        return patterns
    
    async def _analyze_root_causes(self, findings: List[Dict[str, Any]], 
                                 patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze potential root causes based on findings and patterns."""
        root_causes = []
        
        # High-severity findings analysis
        high_severity_findings = [f for f in findings if f.get("severity") == "high"]
        for finding in high_severity_findings:
            root_cause = await self._identify_root_cause(finding, patterns)
            if root_cause:
                root_causes.append(root_cause)
        
        # Pattern-based root cause analysis
        for pattern in patterns:
            if pattern.get("significance") == "high":
                root_cause = await self._identify_pattern_root_cause(pattern, findings)
                if root_cause:
                    root_causes.append(root_cause)
        
        return root_causes
    
    async def _identify_root_cause(self, finding: Dict[str, Any], 
                                 patterns: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Identify root cause for a specific finding."""
        finding_type = finding.get("type", "")
        finding_category = finding.get("category", "")
        
        root_cause = {
            "finding_id": finding.get("title", ""),
            "probable_cause": "",
            "confidence": 0.0,
            "evidence": [],
            "impact": finding.get("severity", "unknown"),
            "actionable_steps": []
        }
        
        # Error-based root cause analysis
        if finding_type == "error":
            root_cause.update({
                "probable_cause": "System component failure or misconfiguration",
                "confidence": 0.7,
                "evidence": [finding.get("description", "")],
                "actionable_steps": [
                    "Examine error logs for detailed information",
                    "Check system configuration",
                    "Verify component dependencies"
                ]
            })
        
        # Performance-based root cause analysis
        elif finding_type == "performance":
            root_cause.update({
                "probable_cause": "Resource contention or inefficient processes",
                "confidence": 0.6,
                "evidence": [f"High {finding_category}: {finding.get('details', '')}"],
                "actionable_steps": [
                    "Identify resource-intensive processes",
                    "Optimize system resource allocation",
                    "Consider scaling resources"
                ]
            })
        
        # Configuration-based root cause analysis
        elif finding_type == "configuration":
            root_cause.update({
                "probable_cause": "Missing or incorrect configuration",
                "confidence": 0.5,
                "evidence": [finding.get("description", "")],
                "actionable_steps": [
                    "Review configuration requirements",
                    "Verify configuration file locations",
                    "Update missing configuration settings"
                ]
            })
        
        return root_cause if root_cause["confidence"] > 0.3 else None
    
    async def _identify_pattern_root_cause(self, pattern: Dict[str, Any], 
                                         findings: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Identify root cause based on detected patterns."""
        if pattern.get("pattern_type") == "error_correlation":
            return {
                "finding_id": "error_correlation_pattern",
                "probable_cause": "Systemic issue affecting multiple components",
                "confidence": 0.8,
                "evidence": [pattern.get("description", "")],
                "impact": "high",
                "actionable_steps": [
                    "Investigate common dependencies",
                    "Check system-wide configuration",
                    "Examine resource constraints"
                ]
            }
        
        return None
    
    async def _generate_recommendations(self, findings: List[Dict[str, Any]], 
                                      root_causes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Priority-based recommendations
        high_priority_findings = [f for f in findings if f.get("severity") == "high"]
        for finding in high_priority_findings:
            rec = await self._create_finding_recommendation(finding)
            if rec:
                recommendations.append(rec)
        
        # Root cause-based recommendations
        for root_cause in root_causes:
            rec = await self._create_root_cause_recommendation(root_cause)
            if rec:
                recommendations.append(rec)
        
        # General system recommendations
        general_recs = await self._create_general_recommendations(findings)
        recommendations.extend(general_recs)
        
        return recommendations
    
    async def _create_finding_recommendation(self, finding: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create recommendation for a specific finding."""
        return {
            "type": "finding_based",
            "priority": finding.get("severity", "medium"),
            "title": f"Address {finding.get('title', '')}",
            "description": f"Resolve {finding.get('type', '')} issue",
            "action_items": [
                f"Investigate {finding.get('category', '')} issue",
                "Implement appropriate fix",
                "Verify resolution"
            ],
            "target_finding": finding.get("title", ""),
            "estimated_effort": self._estimate_effort(finding)
        }
    
    async def _create_root_cause_recommendation(self, root_cause: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create recommendation for addressing a root cause."""
        return {
            "type": "root_cause_based",
            "priority": root_cause.get("impact", "medium"),
            "title": f"Address root cause: {root_cause.get('finding_id', '')}",
            "description": root_cause.get("probable_cause", ""),
            "action_items": root_cause.get("actionable_steps", []),
            "confidence": root_cause.get("confidence", 0.0),
            "estimated_effort": self._estimate_effort_for_root_cause(root_cause)
        }
    
    async def _create_general_recommendations(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create general system improvement recommendations."""
        recommendations = []
        
        # If many findings, recommend comprehensive review
        if len(findings) > 5:
            recommendations.append({
                "type": "general",
                "priority": "medium",
                "title": "Comprehensive system review",
                "description": f"Multiple issues detected ({len(findings)} findings)",
                "action_items": [
                    "Conduct systematic code review",
                    "Implement monitoring and alerting",
                    "Establish regular maintenance procedures"
                ],
                "estimated_effort": "high"
            })
        
        return recommendations
    
    def _prioritize_issues(self, findings: List[Dict[str, Any]], 
                          root_causes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize issues based on severity and impact."""
        priority_issues = []
        
        # High severity findings
        high_severity = [f for f in findings if f.get("severity") == "high"]
        priority_issues.extend(high_severity)
        
        # High confidence root causes
        high_confidence_causes = [rc for rc in root_causes if rc.get("confidence", 0) > 0.7]
        priority_issues.extend(high_confidence_causes)
        
        # Sort by severity/confidence
        priority_issues.sort(key=lambda x: (
            1 if x.get("severity") == "high" or x.get("impact") == "high" else 0,
            x.get("confidence", 0.5)
        ), reverse=True)
        
        return priority_issues[:5]  # Top 5 priority issues
    
    def _estimate_effort(self, finding: Dict[str, Any]) -> str:
        """Estimate effort required to address a finding."""
        severity = finding.get("severity", "medium")
        finding_type = finding.get("type", "")
        
        if severity == "high":
            return "high"
        elif finding_type == "configuration":
            return "low"
        else:
            return "medium"
    
    def _estimate_effort_for_root_cause(self, root_cause: Dict[str, Any]) -> str:
        """Estimate effort required to address a root cause."""
        confidence = root_cause.get("confidence", 0.0)
        impact = root_cause.get("impact", "medium")
        
        if impact == "high" and confidence > 0.7:
            return "high"
        elif confidence < 0.5:
            return "medium"  # Uncertain, may require investigation
        else:
            return "medium"
    
    async def _handle_feedback(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle feedback from other agents."""
        # Could use feedback to refine analysis methods
        return None
    
    async def execute_autonomous_task(self) -> Optional[AgentMessage]:
        """Execute autonomous analysis tasks."""
        # Could perform continuous analysis or refinement
        return None
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for analysis."""
        from datetime import datetime
        return datetime.now().isoformat()