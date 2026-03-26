# ToDo App (FastAPI + SQLite)

A simple full-stack ToDo application with:

- a FastAPI backend
- a SQLite database
- a lightweight HTML/CSS/JS frontend served by the same app

## Features

- Create todos
- View todos in custom display order
- Mark todos as complete/incomplete
- Delete todos

## Tech Stack

- Python
- FastAPI
- Uvicorn
- SQLite (`sqlite3` from Python standard library)
- Jinja2 templates + vanilla JavaScript frontend

## Project Structure

```text
ToDo/
├─ app/
│  ├─ main.py          # FastAPI app + routes
│  ├─ db.py            # SQLite connection + schema setup
│  ├─ todos_store.py   # SQL operations and ordering logic
│  └─ schemas.py       # Pydantic request/response models
├─ templates/
│  └─ index.html
├─ static/
│  ├─ app.js
│  └─ style.css
├─ requirements.txt
└─ environment.yml
```

## Getting Started

### 1) Clone the repository

```bash
git clone https://github.com/vikrawar/ToDo.git
cd ToDo
```

### 2) Install dependencies

#### Option A: pip + virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Option B: Conda

```bash
conda env create -f environment.yml
conda activate todo-fastapi
```

### 3) Run the app

```bash
uvicorn app.main:app --reload
```

- App UI: `http://127.0.0.1:8000/`
- API docs (Swagger): `http://127.0.0.1:8000/docs`

## API Endpoints


| Method   | Endpoint               | Description              |
| -------- | ---------------------- | ------------------------ |
| `GET`    | `/api/todos`           | List all todos           |
| `POST`   | `/api/todos`           | Create a todo            |
| `PATCH`  | `/api/todos/{todo_id}` | Update completion status |
| `DELETE` | `/api/todos/{todo_id}` | Delete a todo            |


### Notes

- Database file is created at `data/todos.db`.
- `POST /api/todos` trims whitespace and rejects empty titles.
- Missing todo IDs return `404`.

