# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""DTDD Test Planning and Writing Tool."""

import os
from datetime import datetime
from typing import Any, Dict

from .base import Tool, ToolCallArguments, ToolExecResult, ToolParameter


class DTDDTestPlanningTool(Tool):
    """Tool for planning and writing comprehensive tests in DTDD workflow."""

    def get_name(self) -> str:
        return "dtdd_test_planning"

    def get_description(self) -> str:
        return """Generate comprehensive test planning and test cases in DTDD workflow.
        
        This tool creates test plans that include:
        - Unit test planning and structure
        - Integration test design
        - Acceptance test standards and criteria
        - Performance test scenarios
        
        Use this as the fourth step in DTDD workflow after class diagrams to ensure code quality."""

    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="component_name",
                type="string",
                description="Name of the component or feature being tested",
                required=True
            ),
            ToolParameter(
                name="test_scope",
                type="string",
                description="Description of what needs to be tested (features, functions, classes)",
                required=True
            ),
            ToolParameter(
                name="acceptance_criteria",
                type="string",
                description="Acceptance criteria and success metrics",
                required=True
            ),
            ToolParameter(
                name="test_types",
                type="string",
                description="Types of tests needed: unit, integration, acceptance, performance",
                required=False
            ),
            ToolParameter(
                name="edge_cases",
                type="string",
                description="Edge cases and error conditions to test (optional)",
                required=False
            ),
            ToolParameter(
                name="performance_requirements",
                type="string",
                description="Performance requirements and benchmarks (optional)",
                required=False
            ),
            ToolParameter(
                name="output_file",
                type="string",
                description="Path where the test plan should be saved (default: docs/test_plan.md)",
                required=False
            ),
            ToolParameter(
                name="generate_test_code",
                type="boolean",
                description="Whether to generate sample test code templates",
                required=False
            )
        ]

    async def execute(self, arguments: ToolCallArguments) -> ToolExecResult:
        """Generate comprehensive test planning document."""
        try:
            component_name = arguments.get("component_name", "")
            test_scope = arguments.get("test_scope", "")
            test_types = arguments.get("test_types", "unit, integration")
            acceptance_criteria = arguments.get("acceptance_criteria", "")
            edge_cases = arguments.get("edge_cases", "")
            performance_requirements = arguments.get("performance_requirements", "")
            output_file = arguments.get("output_file", "docs/test_plan.md")
            generate_test_code = arguments.get("generate_test_code", True)

            # Create docs directory if it doesn't exist
            docs_dir = os.path.dirname(output_file)
            if docs_dir and not os.path.exists(docs_dir):
                os.makedirs(docs_dir, exist_ok=True)

            # Generate test plan content
            test_plan_content = self._generate_test_plan(
                component_name, test_scope, test_types, acceptance_criteria,
                edge_cases, performance_requirements, generate_test_code
            )

            # Check if file exists and append or create
            mode = 'a' if os.path.exists(output_file) else 'w'
            with open(output_file, mode, encoding='utf-8') as f:
                if mode == 'a':
                    f.write("\n\n---\n\n")
                f.write(test_plan_content)

            # Generate test code files if requested
            test_files_created = []
            if generate_test_code:
                test_files_created = self._generate_test_code_templates(component_name, test_types, test_scope)

            return ToolExecResult(
                output=f"Test plan for '{component_name}' added to: {output_file}" + 
                       (f"\nTest templates created: {', '.join(test_files_created)}" if test_files_created else "")
            )

        except Exception as e:
            return ToolExecResult(
                error=f"Failed to generate test plan: {str(e)}"
            )

    def _generate_test_plan(self, component_name: str, test_scope: str, test_types: str,
                          acceptance_criteria: str, edge_cases: str, performance_requirements: str,
                          generate_test_code: bool) -> str:
        """Generate the test plan content."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""# Test Plan: {component_name}

**Created Date:** {timestamp}  
**DTDD Phase:** 4 - Test Planning and Quality Assurance

## Component: {component_name}

### Test Scope
{test_scope}

### Test Types Required
{test_types}

## 1. Unit Testing Plan

### 1.1 Test Strategy
- Test individual functions/methods in isolation
- Mock external dependencies
- Achieve high code coverage (target: 90%+)
- Focus on business logic validation

### 1.2 Unit Test Cases

#### Positive Test Cases
- Test normal input scenarios
- Test expected behavior with valid data
- Verify return values and state changes

#### Negative Test Cases
- Test invalid input handling
- Test error conditions and exceptions
- Verify proper error messages and codes

#### Boundary Test Cases
- Test minimum and maximum values
- Test empty/null inputs
- Test edge cases in algorithms

{self._generate_edge_cases_section(edge_cases) if edge_cases else ""}

## 2. Integration Testing Plan

### 2.1 Integration Strategy
- Test component interactions
- Verify data flow between modules
- Test external service integrations
- Validate end-to-end workflows

### 2.2 Integration Test Scenarios
- API endpoint testing
- Database interaction testing
- External service communication
- Message queue/event handling

## 3. Acceptance Testing Plan

### 3.1 Acceptance Criteria
{acceptance_criteria}

### 3.2 User Story Validation
- Verify all user stories are implemented
- Test user workflows end-to-end
- Validate business rules and constraints
- Confirm UI/UX requirements

### 3.3 Acceptance Test Cases
| Test Case | Description | Expected Result | Status |
|-----------|-------------|-----------------|--------|
| AC-001 | Basic functionality | Should work as specified | ⏳ |
| AC-002 | Error handling | Should handle errors gracefully | ⏳ |
| AC-003 | Performance | Should meet performance criteria | ⏳ |

{self._generate_performance_section(performance_requirements) if performance_requirements else ""}

## 4. Test Environment Setup

### 4.1 Development Environment
- Local testing setup
- Test database configuration
- Mock services setup

### 4.2 CI/CD Pipeline
- Automated test execution
- Test reporting integration
- Code coverage tracking

### 4.3 Test Data Management
- Test data creation strategy
- Data cleanup procedures
- Test data versioning

## 5. Test Execution Strategy

### 5.1 Test Execution Order
1. Unit tests (fastest feedback)
2. Integration tests
3. Acceptance tests
4. Performance tests (if applicable)

### 5.2 Test Automation
- Automated unit and integration tests
- Manual acceptance testing initially
- Gradual automation of acceptance tests

### 5.3 Continuous Testing
- Run tests on every commit
- Nightly full test suite execution
- Performance baseline monitoring

## 6. Quality Metrics

### 6.1 Coverage Targets
- Unit test coverage: 90%+
- Integration test coverage: 80%+
- Critical path coverage: 100%

### 6.2 Quality Gates
- All tests must pass before deployment
- No critical or high severity bugs
- Performance requirements met

### 6.3 Success Criteria
- ✅ All acceptance criteria validated
- ✅ Test coverage targets achieved
- ✅ Performance benchmarks met
- ✅ Security tests passed

## 7. Risk Assessment

### 7.1 Testing Risks
- Incomplete test coverage
- Test environment instability
- Test data inconsistency
- Integration complexity

### 7.2 Mitigation Strategies
- Regular test review and updates
- Robust test environment management
- Comprehensive test data strategy
- Incremental integration approach

## 8. Test Deliverables

### 8.1 Documentation
- Test cases and procedures
- Test execution reports
- Coverage reports
- Performance test results

### 8.2 Code Artifacts
- Unit test suites
- Integration test scripts
- Test utilities and helpers
- Mock implementations

{self._generate_test_code_section() if generate_test_code else ""}

## 9. Timeline and Milestones

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Test Planning | 1-2 days | Test plan document |
| Unit Test Development | 3-5 days | Unit test suite |
| Integration Test Development | 2-3 days | Integration tests |
| Acceptance Test Execution | 1-2 days | Acceptance validation |
| Performance Testing | 1-2 days | Performance reports |

## 10. Next Steps

1. **Review test plan** with development team
2. **Set up test environment** and tooling
3. **Implement unit tests** alongside development
4. **Create integration tests** for component interactions
5. **Execute acceptance tests** with stakeholders
6. **Continuous improvement** based on test results

---

*This test plan follows DTDD (Document-Driven Development) methodology to ensure comprehensive quality assurance.*
"""

    def _generate_edge_cases_section(self, edge_cases: str) -> str:
        """Generate edge cases section."""
        return f"""
### 1.3 Edge Cases and Error Conditions
{edge_cases}

#### Common Edge Cases to Consider
- Empty/null input handling
- Boundary value testing
- Concurrent access scenarios
- Network failure conditions
- Memory/resource constraints
- Invalid data format handling
"""

    def _generate_performance_section(self, performance_requirements: str) -> str:
        """Generate performance testing section."""
        return f"""
## 4. Performance Testing Plan

### 4.1 Performance Requirements
{performance_requirements}

### 4.2 Performance Test Types
- **Load Testing**: Normal expected load
- **Stress Testing**: Beyond normal capacity
- **Spike Testing**: Sudden load increases
- **Volume Testing**: Large amounts of data

### 4.3 Performance Metrics
- Response time (95th percentile)
- Throughput (requests per second)
- Resource utilization (CPU, memory)
- Error rate under load

### 4.4 Performance Test Scenarios
| Scenario | Users | Duration | Success Criteria |
|----------|-------|----------|------------------|
| Normal Load | 100 | 10 min | <2s response time |
| Peak Load | 500 | 5 min | <5s response time |
| Stress Test | 1000 | 2 min | No system crash |
"""

    def _generate_test_code_section(self) -> str:
        """Generate test code templates section."""
        return f"""
## 11. Test Code Templates

### 11.1 Unit Test Template (Python/pytest)
```python
import pytest
from unittest.mock import Mock, patch
from your_module import YourClass

class TestYourClass:
    def setup_method(self):
        self.instance = YourClass()
    
    def test_basic_functionality(self):
        # Arrange
        input_data = "test_input"
        expected = "expected_output"
        
        # Act
        result = self.instance.method(input_data)
        
        # Assert
        assert result == expected
    
    def test_error_handling(self):
        with pytest.raises(ValueError):
            self.instance.method(None)
    
    @patch('your_module.external_dependency')
    def test_with_mock(self, mock_dependency):
        # Setup mock
        mock_dependency.return_value = "mocked_result"
        
        # Test
        result = self.instance.method_with_dependency()
        
        # Verify
        assert result == "expected_with_mock"
        mock_dependency.assert_called_once()
```

### 11.2 Integration Test Template
```python
import pytest
import requests
from unittest import TestCase

class TestAPIIntegration(TestCase):
    def setUp(self):
        self.base_url = "http://localhost:8000/api"
        # Setup test data
    
    def test_api_endpoint(self):
        response = requests.get(f"{self.base_url}/endpoint")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('expected_field', response.json())
    
    def test_end_to_end_workflow(self):
        # Test complete user workflow
        pass
```

### 11.3 Performance Test Template (locust)
```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 2)
    
    @task
    def test_endpoint(self):
        self.client.get("/api/endpoint")
    
    @task(3)  # 3x more frequent
    def test_heavy_endpoint(self):
        self.client.post("/api/heavy", json={"data": "test"})
```
"""

    def _generate_test_code_templates(self, component_name: str, test_types: str, test_scope: str) -> list:
        """Generate actual test code template files."""
        created_files = []
        
        # Create tests directory if it doesn't exist
        tests_dir = "tests"
        if not os.path.exists(tests_dir):
            os.makedirs(tests_dir, exist_ok=True)
        
        # Generate unit test template
        if "unit" in test_types.lower():
            unit_test_file = f"{tests_dir}/test_{component_name.lower().replace(' ', '_')}.py"
            unit_test_content = self._generate_unit_test_template(component_name, test_scope)
            
            with open(unit_test_file, 'w', encoding='utf-8') as f:
                f.write(unit_test_content)
            created_files.append(unit_test_file)
        
        # Generate integration test template
        if "integration" in test_types.lower():
            integration_test_file = f"{tests_dir}/test_{component_name.lower().replace(' ', '_')}_integration.py"
            integration_test_content = self._generate_integration_test_template(component_name, test_scope)
            
            with open(integration_test_file, 'w', encoding='utf-8') as f:
                f.write(integration_test_content)
            created_files.append(integration_test_file)
        
        return created_files

    def _generate_unit_test_template(self, component_name: str, test_scope: str) -> str:
        """Generate unit test template code."""
        class_name = component_name.replace(' ', '')
        
        return f'''# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""Unit tests for {component_name}."""

import pytest
from unittest.mock import Mock, patch

# TODO: Import your actual module
# from your_module import {class_name}


class Test{class_name}:
    """Test suite for {component_name}."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # TODO: Initialize your class instance
        # self.instance = {class_name}()
        pass
    
    def test_basic_functionality(self):
        """Test basic functionality of {component_name}."""
        # Arrange
        # TODO: Set up test data
        input_data = "test_input"
        expected = "expected_output"
        
        # Act
        # TODO: Call the method under test
        # result = self.instance.method(input_data)
        
        # Assert
        # TODO: Verify the result
        # assert result == expected
        pass
    
    def test_error_handling(self):
        """Test error handling in {component_name}."""
        # TODO: Test error conditions
        # with pytest.raises(ValueError):
        #     self.instance.method(None)
        pass
    
    def test_edge_cases(self):
        """Test edge cases for {component_name}."""
        # TODO: Test boundary conditions
        pass
    
    @patch('your_module.external_dependency')
    def test_with_mock(self, mock_dependency):
        """Test with mocked dependencies."""
        # Setup mock
        mock_dependency.return_value = "mocked_result"
        
        # TODO: Test with mock
        # result = self.instance.method_with_dependency()
        
        # Verify
        # assert result == "expected_with_mock"
        # mock_dependency.assert_called_once()
        pass

    def teardown_method(self):
        """Clean up after each test method."""
        # TODO: Clean up test data
        pass


# Test data fixtures
@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {{
        "test_field": "test_value"
    }}


@pytest.fixture
def mock_external_service():
    """Mock external service dependencies."""
    with patch('your_module.external_service') as mock:
        mock.return_value = Mock()
        yield mock
'''

    def _generate_integration_test_template(self, component_name: str, test_scope: str) -> str:
        """Generate integration test template code."""
        class_name = component_name.replace(' ', '')
        
        return f'''# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""Integration tests for {component_name}."""

import pytest
import requests
from unittest import TestCase

# TODO: Import your actual modules
# from your_module import {class_name}


class Test{class_name}Integration(TestCase):
    """Integration test suite for {component_name}."""
    
    def setUp(self):
        """Set up integration test environment."""
        # TODO: Setup test environment
        self.base_url = "http://localhost:8000/api"
        # Initialize test database, services, etc.
        pass
    
    def test_api_integration(self):
        """Test API integration for {component_name}."""
        # TODO: Test API endpoints
        # response = requests.get(f"{{self.base_url}}/endpoint")
        # self.assertEqual(response.status_code, 200)
        # self.assertIn('expected_field', response.json())
        pass
    
    def test_database_integration(self):
        """Test database integration."""
        # TODO: Test database operations
        pass
    
    def test_external_service_integration(self):
        """Test external service integration."""
        # TODO: Test external service calls
        pass
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # TODO: Test complete user workflow
        # 1. Create test data
        # 2. Execute workflow
        # 3. Verify results
        # 4. Clean up
        pass
    
    def test_error_scenarios(self):
        """Test error handling in integration scenarios."""
        # TODO: Test error conditions
        pass
    
    def tearDown(self):
        """Clean up after integration tests."""
        # TODO: Clean up test data, close connections
        pass


class Test{class_name}Performance:
    """Performance tests for {component_name}."""
    
    def test_response_time(self):
        """Test response time requirements."""
        # TODO: Implement performance tests
        pass
    
    def test_throughput(self):
        """Test throughput requirements."""
        # TODO: Test system throughput
        pass
    
    def test_load_handling(self):
        """Test system behavior under load."""
        # TODO: Implement load testing
        pass
'''