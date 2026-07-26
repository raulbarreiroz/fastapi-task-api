# QA Traceability Matrix - Level 1

> **Objective**: Ensure 100% functional coverage for the Task Manager API (Level 1).  
> **Current Status**: ✅ All planned scenarios are covered by automated tests.

## Coverage Summary
- **Total Scenarios**: 16
- **Automated Tests**: 16
- **Pass Rate**: 100% (All green)
- **Line Coverage**: 100% (`pytest tests/ -v --cov=app`)
- **Test isolation**: `clean_db` autouse fixture clears in-memory `fake_db` before/after each test

---

## Detailed Matrix

| Endpoint | Scenario | Input Example | Expected Result | Test Function | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **POST /tasks/** | Valid task (no URGENTE) | `{"title":"Comprar pan", "completed":true}` | 201, `completed=True` | `test_create_task_normal_completed` | ✅ |
| **POST /tasks/** | Title contains "URGENTE" (uppercase) | `{"title":"URGENTE: ...", "completed":true}` | 201, forced `completed=False` | `test_create_task_with_urgent_force_incomplete` | ✅ |
| **POST /tasks/** | Title contains "urgente" (lowercase) | `{"title":"urgente: ...", "completed":true}` | 201, forced `completed=False` | `test_urgent_case_insensitive` | ✅ |
| **POST /tasks/** | Title empty / only spaces | `{"title":"   "}` | 422 Validation Error | `test_create_task_empty_title` | ✅ |
| **POST /tasks/** | Title not a string | `{"title":123}` | 422 Validation Error | `test_create_task_not_string_title` | ✅ |
| **POST /tasks/** | Title > 100 chars | `{"title":"a"*101}` | 422 Validation Error | `test_create_task_title_too_long` | ✅ |
| **POST /tasks/** | Extra field in payload | `{"title":"X", "priority":"high"}` | 201, extra field ignored | `test_create_task_extra_field_ignored` | ✅ |
| **POST /tasks/** | `completed` as string `"true"` | `{"title":"X", "completed":"true"}` | 201, auto-casts to `True` | `test_create_task_completed_as_string` | ✅ |
| **POST /tasks/** | Missing `Authorization` header | (No headers) | 422 (FastAPI missing required param) | `test_create_task_missing_authorization_header` | ✅ |
| **POST /tasks/** | Invalid Bearer token | `Authorization: Bearer bad_token` | 401 Invalid token | `test_invalid_auth_token` | ✅ |
| **POST /tasks/** | Invalid auth scheme (no Bearer) | `Authorization: bad_token` | 401 Invalid auth scheme | `test_invalid_bearer_auth_token` | ✅ |
| **GET /tasks/** | List tasks (empty DB) | (No body) | 200, returns `[]` | `test_list_tasks_empty` | ✅ |
| **GET /tasks/{id}** | Existing task ID | Create then GET by returned id | 200, task object | `test_get_task` | ✅ |
| **GET /tasks/{id}** | Non-existing ID | `GET /tasks/999` | 404 Not Found | `test_get_task_not_found` | ✅ |
| **DELETE /tasks/** | Delete all tasks | Create one, then DELETE | 200, deleted list returned | `test_delete_all_tasks` | ✅ |
| **GET /health** | Health check | (No auth) | 200, `{"status":"ok","level":1}` | `test_health_endpoint` | ✅ |
| **Global** | Validation error format | Title too long | 422 with `{"detail","errors"}` | `test_create_task_title_too_long` | ✅ |

### Auth implementation note (Level 1)
Fake auth parses `Authorization` with `split(" ", 1)` and checks:
1. Scheme is `bearer` (case-insensitive)
2. Token contains the substring `"valid"`

External behavior of existing auth tests is unchanged after the refactor.

---

## Known Gaps (Next levels)
- Real PostgreSQL + transaction rollback fixtures (replace in-memory `fake_db`)
- Real JWT / `HTTPBearer` instead of fake token substring check
- Optional: explicit `GET /tasks/` with data scenario (currently covered indirectly via create + get flows)
- Optional: case-insensitive scheme test (`bearer valid_token_123`) if you want that branch documented as its own scenario

---

## How to Run

```bash
# Run all tests with coverage
pytest tests/ -v --cov=app --cov-report=term

# Generate HTML coverage report
pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html in your browser