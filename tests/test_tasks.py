import pytest_asyncio
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.routers.tasks import fake_db
from app.config import settings


# ------------------------------------------------------------
# FIXTURE (Configuración compartida para todos los tests)
# ------------------------------------------------------------
@pytest_asyncio.fixture(scope="function")
async def client():
    """
    Create an asynchronous HTTP client for testing the API without the need to 
    start a real server (using ASGITransport).
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.fixture(autouse=True)
def clean_db():
    """
    Clean the fake database before and after each test.
    """
    fake_db.clear()   # 1) BEFORE the test
    yield             # ← test runs here
    fake_db.clear()   # 2) AFTER the test

# ------------------------------------------------------------
# CONSTANTES
# ------------------------------------------------------------
VALID_HEADERS = {"Authorization": "Bearer valid_token_123"}

# ------------------------------------------------------------
# TESTS DE HEALTH (GET /health)
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_health_endpoint(client):
    """GIVEN no authentication required
       WHEN calling GET /health
       THEN returns 200 with status ok and level 1."""
    # ACT
    response = await client.get(f"{settings.API_V1_PREFIX}/health/")
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["level"] == 1
    assert data["project"] == "Task Manager"

# ------------------------------------------------------------
# TESTS DE AUTENTICACIÓN
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_task_missing_authorization_header(client):
    """GIVEN no Authorization header
       WHEN calling POST /tasks/
       THEN FastAPI raises 422 because Header(...) is mandatory."""
    # ARRANGE (no headers)
    payload = {"title": "Sin token", "description": "Fallo seguro"}
    # ACT
    response = await client.post(f"{settings.API_V1_PREFIX}/tasks/", json=payload)  # Note: no headers
    # ASSERT
    # FastAPI lanza 422 por parámetro requerido en la dependencia (no 401)
    assert response.status_code == 422
    # Verifica que el error hable de 'authorization'
    errors = response.json().get("errors", [])
    assert any("authorization" in err["field"].lower() for err in errors)

@pytest.mark.asyncio
async def test_invalid_auth_token(client):
    """GIVEN invalid Bearer token (doesn't contain 'valid')
       WHEN calling POST /tasks/
       THEN 401 Unauthorized."""
    # ARRANGE
    payload = {"title": "Hack", "description": "Intento"}
    headers = {"Authorization": "Bearer bad_token"}
    # ACT
    response = await client.post(f"{settings.API_V1_PREFIX}/tasks/", json=payload, headers=headers)
    # ASSERT
    assert response.status_code == 401
    assert "Invalid token" in response.text

@pytest.mark.asyncio
async def test_invalid_bearer_auth_token(client):
    """GIVEN invalid bearer token (doesn't contain 'valid')
       WHEN calling POST /tasks/
       THEN 401 Unauthorized."""
    # ARRANGE
    payload = {"title": "Hack", "description": "Intento"}
    headers = {"Authorization": "bad_token"}
    # ACT
    response = await client.post(f"{settings.API_V1_PREFIX}/tasks/", json=payload, headers=headers)
    # ASSERT
    assert response.status_code == 401
    assert "Invalid auth scheme" in response.text

# ------------------------------------------------------------
# TESTS DE CREACIÓN (POST /tasks/)
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_task_with_urgent_force_incomplete(client):
    """GIVEN a task with 'URGENTE' in title and completed=True
       WHEN calling POST /tasks/
       THEN the business rule forces completed=False (override)."""
    # ARRANGE
    payload = {
        "title": "URGENTE: Revisar servidor",
        "description": "El servidor se está cayendo",
        "completed": True
    }
    # ACT
    response = await client.post(f"{settings.API_V1_PREFIX}/tasks/", json=payload, headers=VALID_HEADERS)
    # ASSERT
    assert response.status_code == 201
    data = response.json()
    assert data["completed"] is False
    assert "URGENTE" in data["title"]
    assert data["created_at"] is not None

@pytest.mark.asyncio
async def test_urgent_case_insensitive(client):
    """GIVEN task with 'urgente' in lowercase and completed=True
       WHEN calling POST /tasks/
       THEN the rule must trigger (since code uses .upper())."""
    # ARRANGE
    payload = {
        "title": "urgente: apagar fuego",
        "description": "Incendio en el servidor",
        "completed": True
    }
    # ACT
    response = await client.post(f"{settings.API_V1_PREFIX}/tasks/", json=payload, headers=VALID_HEADERS)
    # ASSERT
    assert response.status_code == 201
    assert response.json()["completed"] is False

@pytest.mark.asyncio
async def test_create_task_normal_completed(client):
    """GIVEN a normal task (no URGENTE) and completed=True
       WHEN calling POST /tasks/
       THEN completed remains True."""
    # ARRANGE
    payload = {
        "title": "Comprar pan",
        "description": "Ir a la panadería",
        "completed": True
    }
    # ACT
    response = await client.post(f"{settings.API_V1_PREFIX}/tasks/", json=payload, headers=VALID_HEADERS)
    # ASSERT
    assert response.status_code == 201
    assert response.json()["completed"] is True

@pytest.mark.asyncio
async def test_create_task_empty_title(client):
    """GIVEN title with only spaces
       WHEN calling POST /tasks/
       THEN 422 Validation Error is returned (trim validator fails min_length)."""
    # ARRANGE
    payload = {
        "title": "   ",
        "description": "Solo espacios"
    }
    # ACT
    response = await client.post(f"{settings.API_V1_PREFIX}/tasks/", json=payload, headers=VALID_HEADERS)
    # ASSERT
    assert response.status_code == 422
    errors = response.json()["errors"]
    assert any("title" in err["field"] for err in errors)

@pytest.mark.asyncio
async def test_create_task_not_string_title(client):
    """GIVEN title not a string
       WHEN calling POST /tasks/
       THEN 422 Validation Error is returned (title must be a string)."""
    # ARRANGE
    payload = {
        "title": 123,
        "description": "Solo espacios"
    }
    # ACT
    response = await client.post(f"{settings.API_V1_PREFIX}/tasks/", json=payload, headers=VALID_HEADERS)
    # ASSERT
    assert response.status_code == 422
    errors = response.json()["errors"]
    assert any("title" in err["field"] for err in errors)

@pytest.mark.asyncio
async def test_create_task_title_too_long(client):
    """GIVEN title with 101 characters
       WHEN calling POST /tasks/
       THEN 422 Validation Error (max_length=100)."""
    # ARRANGE
    payload = {
        "title": "a" * 101,
        "description": "Demasiado largo"
    }
    # ACT
    response = await client.post(f"{settings.API_V1_PREFIX}/tasks/", json=payload, headers=VALID_HEADERS)
    # ASSERT
    assert response.status_code == 422
    errors = response.json()["errors"]
    assert any("title" in err["field"] for err in errors)

@pytest.mark.asyncio
async def test_create_task_extra_field_ignored(client):
    """GIVEN payload with extra field 'priority'
       WHEN calling POST /tasks/
       THEN the request succeeds (201) and extra field is NOT in response."""
    # ARRANGE
    payload = {
        "title": "Tarea normal",
        "description": "Con campo extra",
        "completed": False,
        "priority": "high"  # Campo extra no definido en el schema
    }
    # ACT
    response = await client.post(f"{settings.API_V1_PREFIX}/tasks/", json=payload, headers=VALID_HEADERS)
    # ASSERT
    assert response.status_code == 201
    data = response.json()
    assert "priority" not in data  # Pydantic ignora extra fields por defecto
    assert data["title"] == "Tarea normal"

@pytest.mark.asyncio
async def test_create_task_completed_as_string(client):
    """GIVEN completed sent as string 'true'
       WHEN calling POST /tasks/
       THEN Pydantic auto-casts to boolean (should not throw 422)."""
    # ARRANGE
    payload = {
        "title": "Test tipado",
        "description": "Enviando string",
        "completed": "true"  # String en lugar de bool
    }
    # ACT
    response = await client.post(f"{settings.API_V1_PREFIX}/tasks/", json=payload, headers=VALID_HEADERS)
    # ASSERT
    assert response.status_code == 201
    # Pydantic v2 convierte "true" a True, y "false" a False.
    assert response.json()["completed"] is True

# ------------------------------------------------------------
# TESTS DE CONSULTA (GET /tasks/ y GET /tasks/{id})
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_tasks_empty(client):
    """GIVEN no tasks created yet
       WHEN calling GET /tasks/
       THEN returns 200 with an empty list."""
    # ACT
    response = await client.get(f"{settings.API_V1_PREFIX}/tasks/", headers=VALID_HEADERS)
    # ASSERT
    assert response.status_code == 200
    assert response.json() == []
    
@pytest.mark.asyncio
async def test_get_task(client):
    """GIVEN existing task ID
       WHEN calling GET /tasks/{id}
       THEN returns 200 with the task details."""
    # ARRANGE
    payload = {
        "title": "Comprar pan",
        "description": "Ir a la panadería",
        "completed": True
    }
    response = await client.post(f"{settings.API_V1_PREFIX}/tasks/", json=payload, headers=VALID_HEADERS)
    assert response.status_code == 201
    task_id = response.json()['id']
    # ACT
    response = await client.get(f"{settings.API_V1_PREFIX}/tasks/{task_id}", headers=VALID_HEADERS)
    # ASSERT
    assert response.status_code == 200
    assert response.json()['id'] == task_id

@pytest.mark.asyncio
async def test_get_task_not_found(client):
    """GIVEN non-existing task ID
       WHEN calling GET /tasks/{id}
       THEN 404 Not Found."""
    # ACT
    response = await client.get(f"{settings.API_V1_PREFIX}/tasks/999", headers=VALID_HEADERS)
    # ASSERT
    assert response.status_code == 404
    assert "Task not found" in response.text

# ------------------------------------------------------------
# TESTS DE ELIMINACIÓN TOTAL (DELETE /tasks/0)
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_delete_all_tasks(client):
    """GIVEN tasks created
       WHEN calling DELETE /tasks/
       THEN returns 200 with the list of all deleted tasks."""
    # ARRANGE
    payload = {
        "title": "Comprar pan",
        "description": "Ir a la panadería",
        "completed": True
    }
    response = await client.post(f"{settings.API_V1_PREFIX}/tasks/", json=payload, headers=VALID_HEADERS)
    assert response.status_code == 201
    # ACT
    response = await client.delete(f"{settings.API_V1_PREFIX}/tasks/", headers=VALID_HEADERS)
    # ASSERT
    assert response.status_code == 200