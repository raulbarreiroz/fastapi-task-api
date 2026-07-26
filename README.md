# FastAPI Task Manager API

## Overview 
This is a backend portfolio project built with FastAPI.
It is designed to replace the LocalStorage logic of an existing frontend task manager, moving data persistence to the server

## Tech Stack (Level 1)
- Python 3.11+
- FastAPI 
- Pydantic v2 (with custom validators)
- Uvicorn
- Pytest + HTTPX

## Level 1 Features (MVP)
- [x] In-memory task (simulating a database)
- [x] Pydantic models: 'TaskCreate' (input) and 'TaskResponse' (output).
- [x] Input sanitization: Auto-trims spaces from title and description
- [x] Business rule: Tasks with "URGENTE" in the title are forced to 'completed=False' (ensure user attention)
- [x] Fake JWT authentication dependency (Bearer token)
- [x] Global exception handler for validation errors
- [x] Unit tests covering creation, validation, and authentication
- [x] Auto-generated OpenAPI docs at '/docs'

## Setup & Run
```bash
python -m venv venv
source venv/bin/activate # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
# run tests
pytest tests/ -v --cov=app
```
