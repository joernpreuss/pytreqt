# Test Coverage Matrix

This document shows the traceability between requirements and test cases.

**Last updated**: 2025-09-23

## Coverage Summary

- **Total Requirements**: 34
- **Requirements with Tests**: 15
- **Requirements without Tests**: 19

**Coverage Percentage**: 44.1%

## Requirements Coverage

### BR-1.1: The system shall prevent requirement typos from going undetected
**Status**: ✅ **Tested**

**Test Cases**:
- `test_requirement_validation_invalid`
- `test_requirement_validation_valid`

### BR-1.2: The system shall ensure all business requirements have corresponding tests
**Status**: ❌ **Not Tested**

**Test Cases**: None
⚠️ *This requirement needs test coverage*

### BR-1.3: The system shall provide traceability between requirements and tests
**Status**: ✅ **Tested**

**Test Cases**:
- `test_traceability_matrix_generation`

### BR-2.1: The system shall integrate seamlessly with existing pytest workflows
**Status**: ✅ **Tested**

**Test Cases**:
- `test_pytest_plugin_integration`

### BR-2.2: The system shall provide immediate feedback during test execution
**Status**: ❌ **Not Tested**

**Test Cases**: None
⚠️ *This requirement needs test coverage*

### BR-2.3: The system shall support both CI/CD and local development environments
**Status**: ✅ **Tested**

**Test Cases**:
- `test_parallel_execution_compatibility`

### BR-3.1: The system shall be self-contained with minimal external dependencies
**Status**: ✅ **Tested**

**Test Cases**:
- `test_self_contained_operation`

### BR-3.2: The system shall support different project structures and requirements formats
**Status**: ❌ **Not Tested**

**Test Cases**: None
⚠️ *This requirement needs test coverage*

### BR-3.3: The system shall provide clear error messages for configuration issues
**Status**: ✅ **Tested**

**Test Cases**:
- `test_malformed_requirement_handling`

### BR-4.1: The system shall support custom requirement ID patterns via configuration
**Status**: ❌ **Not Tested**

**Test Cases**: None
⚠️ *This requirement needs test coverage*

### BR-4.2: The system shall allow custom output formats for reports
**Status**: ❌ **Not Tested**

**Test Cases**: None
⚠️ *This requirement needs test coverage*

### BR-4.3: The system shall enable integration with external documentation systems
**Status**: ❌ **Not Tested**

**Test Cases**: None
⚠️ *This requirement needs test coverage*

### FR-1.1: The system shall extract requirement IDs from test docstrings using the pattern `Requires: REQ-ID`
**Status**: ✅ **Tested**

**Test Cases**:
- `test_requirement_extraction_single`

### FR-1.2: The system shall support multiple requirement IDs per test (comma-separated)
**Status**: ✅ **Tested**

**Test Cases**:
- `test_requirement_extraction_multiple`

### FR-1.3: The system shall ignore malformed requirement references and report them as warnings
**Status**: ✅ **Tested**

**Test Cases**:
- `test_malformed_requirement_handling`

### FR-2.1: The system shall validate that all referenced requirement IDs exist in the REQUIREMENTS.md file
**Status**: ✅ **Tested**

**Test Cases**:
- `test_requirement_extraction_multiple`
- `test_requirement_validation_valid`

### FR-2.2: The system shall report invalid requirement references with test location
**Status**: ✅ **Tested**

**Test Cases**:
- `test_requirement_validation_invalid`

### FR-2.3: The system shall support requirement ID formats: FR-X.Y, BR-X.Y, NFR-X.Y
**Status**: ❌ **Not Tested**

**Test Cases**: None
⚠️ *This requirement needs test coverage*

### FR-3.1: The system shall generate coverage reports showing which requirements are tested
**Status**: ✅ **Tested**

**Test Cases**:
- `test_coverage_report_generation`

### FR-3.2: The system shall display test results with colorized status indicators (✓, ✗, ⊝)
**Status**: ❌ **Not Tested**

**Test Cases**: None
⚠️ *This requirement needs test coverage*

### FR-3.3: The system shall show untested requirements in coverage reports
**Status**: ❌ **Not Tested**

**Test Cases**: None
⚠️ *This requirement needs test coverage*

### FR-3.4: The system shall generate TEST_COVERAGE.md with traceability matrix
**Status**: ✅ **Tested**

**Test Cases**:
- `test_coverage_report_generation`
- `test_traceability_matrix_generation`

### FR-4.1: The system shall integrate with pytest as a plugin
**Status**: ✅ **Tested**

**Test Cases**:
- `test_pytest_plugin_integration`

### FR-4.2: The system shall collect requirements during test discovery phase
**Status**: ❌ **Not Tested**

**Test Cases**: None
⚠️ *This requirement needs test coverage*

### FR-4.3: The system shall work with parallel test execution (pytest-xdist)
**Status**: ✅ **Tested**

**Test Cases**:
- `test_parallel_execution_compatibility`

### FR-4.4: The system shall capture test results and map to requirements
**Status**: ❌ **Not Tested**

**Test Cases**: None
⚠️ *This requirement needs test coverage*

### FR-5.1: The system shall provide a `show` command to display coverage from last run
**Status**: ❌ **Not Tested**

**Test Cases**: None
⚠️ *This requirement needs test coverage*

### FR-5.2: The system shall provide a `coverage` command to generate detailed reports
**Status**: ❌ **Not Tested**

**Test Cases**: None
⚠️ *This requirement needs test coverage*

### FR-5.3: The system shall provide a `changes` command to detect affected tests
**Status**: ❌ **Not Tested**

**Test Cases**: None
⚠️ *This requirement needs test coverage*

### FR-5.4: The system shall provide a `stats` command to show coverage statistics
**Status**: ❌ **Not Tested**

**Test Cases**: None
⚠️ *This requirement needs test coverage*

### FR-6.1: The system shall cache coverage data in `.pytest_cache/requirements_coverage.json`
**Status**: ❌ **Not Tested**

**Test Cases**: None
⚠️ *This requirement needs test coverage*

### FR-6.2: The system shall include execution metadata (timestamp, command, environment)
**Status**: ❌ **Not Tested**

**Test Cases**: None
⚠️ *This requirement needs test coverage*

### FR-6.3: The system shall detect database type from environment variables
**Status**: ❌ **Not Tested**

**Test Cases**: None
⚠️ *This requirement needs test coverage*

### FR-6.4: The system shall preserve git state information in coverage data
**Status**: ❌ **Not Tested**

**Test Cases**: None
⚠️ *This requirement needs test coverage*

## Requirements Needing Tests

The following requirements have no test coverage:

- **BR-1.2**: The system shall ensure all business requirements have corresponding tests
- **BR-2.2**: The system shall provide immediate feedback during test execution
- **BR-3.2**: The system shall support different project structures and requirements formats
- **BR-4.1**: The system shall support custom requirement ID patterns via configuration
- **BR-4.2**: The system shall allow custom output formats for reports
- **BR-4.3**: The system shall enable integration with external documentation systems
- **FR-2.3**: The system shall support requirement ID formats: FR-X.Y, BR-X.Y, NFR-X.Y
- **FR-3.2**: The system shall display test results with colorized status indicators (✓, ✗, ⊝)
- **FR-3.3**: The system shall show untested requirements in coverage reports
- **FR-4.2**: The system shall collect requirements during test discovery phase
- **FR-4.4**: The system shall capture test results and map to requirements
- **FR-5.1**: The system shall provide a `show` command to display coverage from last run
- **FR-5.2**: The system shall provide a `coverage` command to generate detailed reports
- **FR-5.3**: The system shall provide a `changes` command to detect affected tests
- **FR-5.4**: The system shall provide a `stats` command to show coverage statistics
- **FR-6.1**: The system shall cache coverage data in `.pytest_cache/requirements_coverage.json`
- **FR-6.2**: The system shall include execution metadata (timestamp, command, environment)
- **FR-6.3**: The system shall detect database type from environment variables
- **FR-6.4**: The system shall preserve git state information in coverage data

## Test Statistics

- **Total Test Cases with Requirements**: 18
- **Unique Requirements Tested**: 15
- **Average Tests per Requirement**: 1.2

---

*This file is auto-generated by pytreqt*
*To update, run: `pytreqt coverage`*
