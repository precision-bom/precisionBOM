# E2E Test Cases Documentation

This document describes all black-box end-to-end test cases for the BOM Agent Service API.

## Overview

These tests interact with the API endpoints as a black box, without knowledge of internal implementation. Tests are organized by functionality area.

## Prerequisites

- `OPENAI_API_KEY` environment variable must be set
- Python 3.11+
- Test dependencies installed: `uv sync --group dev`

## Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_health.py -v

# Run with output
uv run pytest tests/ -v -s
```

---

## Test Categories

### 1. Health & Utility Endpoints (`test_health.py`)

| ID | Test Name | Endpoint | Description | Expected Result |
|----|-----------|----------|-------------|-----------------|
| H1 | `test_h1_health_check_returns_200` | `GET /health` | Verify health check endpoint works | Returns `{"status": "healthy"}` with 200 |
| H2 | `test_h2_root_endpoint_returns_service_info` | `GET /` | Verify root endpoint returns API info | Returns service name, version, and endpoint list |
| H3 | `test_h3_models_endpoint_lists_available_models` | `GET /v1/models` | Verify models listing (OpenAI-compatible) | Returns list containing "bom-agent" model |

---

### 2. Projects CRUD (`test_projects_crud.py`)

| ID | Test Name | Endpoint | Description | Expected Result |
|----|-----------|----------|-------------|-----------------|
| P1 | `test_p1_create_project_with_bom_upload` | `POST /projects` | Create project by uploading BOM CSV | Returns project summary with ID and line item count |
| P2 | `test_p2_list_all_projects` | `GET /projects` | List all existing projects | Returns array of project summaries |
| P3 | `test_p3_list_projects_with_limit` | `GET /projects?limit=N` | List projects with pagination limit | Returns at most N projects |
| P4 | `test_p4_get_project_by_id` | `GET /projects/{id}` | Get full project details by ID | Returns project with context, line items, status, trace |
| P5 | `test_p5_get_project_trace` | `GET /projects/{id}/trace` | Get execution trace for project | Returns array of trace steps |
| P6 | `test_p6_delete_project` | `DELETE /projects/{id}` | Delete a project | Returns `{"deleted": "<id>"}` |
| P7 | `test_p7_get_deleted_project_returns_404` | `GET /projects/{id}` | Access deleted project | Returns 404 Not Found |

---

### 3. Upload and Process Flow (`test_upload_and_process.py`)

| ID | Test Name | Endpoint | Description | Expected Result |
|----|-----------|----------|-------------|-----------------|
| UP1 | `test_up1_upload_bom_and_process` | `POST /projects/upload-and-process` | Upload BOM and run full processing | Returns project ID with status |
| UP2 | `test_up2_process_creates_trace_entries` | `GET /projects/{id}/trace` | Verify processing creates trace | Trace contains processing steps |
| UP3 | `test_up3_line_items_have_status` | `GET /projects/{id}` | Verify line items have status after processing | All line items have status field |
| UP4 | `test_up4_reprocess_existing_project` | `POST /projects/{id}/process` | Re-process an existing project | Returns processing/started status |
| UP5 | `test_up5_upload_with_intake_file` | `POST /projects/upload-and-process` | Upload BOM with intake YAML | Project has context from intake file |
| UP6 | `test_up6_upload_minimal_bom` | `POST /projects/upload-and-process` | Process single-line BOM | Successfully processes with 1 line item |

**Note**: These tests involve actual LLM calls and may take longer to run.

---

### 4. Knowledge Base - Parts (`test_knowledge_parts.py`)

| ID | Test Name | Endpoint | Description | Expected Result |
|----|-----------|----------|-------------|-----------------|
| KP1 | `test_kp1_list_all_parts` | `GET /knowledge/parts` | List all parts in knowledge base | Returns array (may be empty) |
| KP2 | `test_kp2_list_parts_with_limit` | `GET /knowledge/parts?limit=N` | List parts with pagination | Returns at most N parts |
| KP3 | `test_kp3_get_part_by_mpn` | `GET /knowledge/parts/{mpn}` | Get specific part knowledge | Returns part with all knowledge fields |
| KP4 | `test_kp4_get_unknown_part_returns_404` | `GET /knowledge/parts/{mpn}` | Access non-existent part | Returns 404 Not Found |
| KP5 | `test_kp5_ban_a_part` | `POST /knowledge/parts/{mpn}/ban` | Ban a part from use | Returns `{"status": "banned", ...}` |
| KP6 | `test_kp6_verify_part_is_banned` | `GET /knowledge/parts/{mpn}` | Verify part shows banned | Part has `banned: true` |
| KP7 | `test_kp7_unban_a_part` | `POST /knowledge/parts/{mpn}/unban` | Remove ban from part | Part has `banned: false` |
| KP8 | `test_kp8_add_alternate_to_part` | `POST /knowledge/parts/{mpn}/alternates` | Add approved alternate | Returns success with alternate MPN |
| KP9 | `test_kp9_get_alternates_for_part` | `GET /knowledge/parts/{mpn}/alternates` | Get all approved alternates | Returns array of alternate MPNs |

---

### 5. Knowledge Base - Suppliers (`test_knowledge_suppliers.py`)

| ID | Test Name | Endpoint | Description | Expected Result |
|----|-----------|----------|-------------|-----------------|
| KS1 | `test_ks1_list_all_suppliers` | `GET /knowledge/suppliers` | List all suppliers | Returns array of supplier objects |
| KS2 | `test_ks2_get_supplier_by_id` | `GET /knowledge/suppliers/{id}` | Get specific supplier details | Returns supplier with all fields |
| KS3 | `test_ks3_get_unknown_supplier_returns_404` | `GET /knowledge/suppliers/{id}` | Access non-existent supplier | Returns 404 Not Found |
| KS4 | `test_ks4_create_new_supplier` | `POST /knowledge/suppliers` | Create new supplier | Returns `{"status": "created", ...}` |
| KS5 | `test_ks5_create_duplicate_supplier_fails` | `POST /knowledge/suppliers` | Create supplier with existing ID | Returns 400 Bad Request |
| KS6 | `test_ks6_set_supplier_trust_level` | `POST /knowledge/suppliers/{id}/trust` | Update supplier trust level | Trust level updated successfully |
| KS7 | `test_ks7_invalid_trust_level_fails` | `POST /knowledge/suppliers/{id}/trust` | Set invalid trust level | Returns 400 Bad Request |

---

### 6. Chat Completions (`test_chat_completions.py`)

| ID | Test Name | Endpoint | Description | Expected Result |
|----|-----------|----------|-------------|-----------------|
| C1 | `test_c1_basic_chat_completion` | `POST /v1/chat/completions` | Basic chat completion request | Returns OpenAI-format response |
| C2 | `test_c2_response_has_required_fields` | `POST /v1/chat/completions` | Verify response structure | Has id, choices, usage fields |
| C3 | `test_c3_chat_with_bom_question` | `POST /v1/chat/completions` | Ask BOM-related question | Returns relevant response content |
| C4 | `test_c4_chat_with_temperature_parameter` | `POST /v1/chat/completions` | Chat with temperature setting | Generates valid response |

**Note**: These tests require `OPENAI_API_KEY` and make actual LLM API calls.

---

### 7. Error Handling (`test_error_handling.py`)

| ID | Test Name | Endpoint | Description | Expected Result |
|----|-----------|----------|-------------|-----------------|
| E1 | `test_e1_invalid_project_id_format` | `GET /projects/{id}` | Invalid ID format | Returns 404 or 422 |
| E2 | `test_e2_non_existent_project` | `GET /projects/{uuid}` | Random UUID that doesn't exist | Returns 404 Not Found |
| E3 | `test_e3_missing_required_file_upload` | `POST /projects` | Missing bom_file | Returns 422 Validation Error |
| E4 | `test_e4_invalid_csv_format` | `POST /projects` | Malformed CSV content | Returns 400 or empty result |
| E5 | `test_e5_empty_csv_file` | `POST /projects` | CSV with only headers | Returns 400 Bad Request |
| E6 | `test_e6_invalid_ban_request_body` | `POST /knowledge/parts/{mpn}/ban` | Missing reason field | Returns 422 Validation Error |
| E7 | `test_e7_delete_non_existent_project` | `DELETE /projects/{uuid}` | Delete non-existent project | Returns 404 Not Found |
| E8 | `test_e8_invalid_supplier_type` | `POST /knowledge/suppliers` | Invalid supplier_type enum | Returns 400 Bad Request |
| E9 | `test_e9_get_trace_non_existent_project` | `GET /projects/{uuid}/trace` | Trace for non-existent project | Returns 404 Not Found |
| E10 | `test_e10_process_non_existent_project` | `POST /projects/{uuid}/process` | Process non-existent project | Returns 404 Not Found |

---

## Test Data

### Sample BOM CSV
```csv
Part Number,Description,Quantity,Manufacturer,MPN
R1,10K Resistor 0805 1%,100,Yageo,RC0805FR-0710KL
C1,100uF Electrolytic 25V,50,Panasonic,ECA-1EM101
U1,ATmega328P Microcontroller,10,Microchip,ATMEGA328P-PU
```

### Sample Intake YAML
```yaml
project:
  name: "Test Project"
  id: "TEST-001"
  owner: "test@example.com"

requirements:
  product_type: "consumer"
  quantity: 100
  deadline: "2026-06-01"
  budget_total: 5000.00

compliance:
  standards:
    - "RoHS"
  quality_class: "IPC Class 2"

sourcing_constraints:
  allow_brokers: false
  allow_alternates: true
  preferred_distributors:
    - "digikey"
    - "mouser"
  max_lead_time_days: 30
```

---

## Notes

- Tests use a separate test database directory (`data/test/`)
- Test databases are cleaned at the start of each test session
- Some tests create resources that are tracked for potential cleanup
- Chat completion tests make real API calls and may incur costs
- Processing tests may take longer due to LLM agent execution
