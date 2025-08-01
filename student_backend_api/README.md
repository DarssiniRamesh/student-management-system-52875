# Student Backend API

This directory contains the FastAPI backend for the Student Management System.

## Quick Start

1. **Install dependencies**:
    ```
    pip install -r requirements.txt
    ```

2. **Copy `.env.example` to `.env`** and fill in the required environment variables for your local or deployment environment.

> Make sure your `.env` file includes a line for the database:
> ```
> DATABASE_URL=sqlite:///./dev.db
> ```
> For production deployments, set `DATABASE_URL` to your actual database connection string (e.g., for PostgreSQL: `postgresql://user:password@host:port/dbname`). If not set and `ENV` is `production`, startup will error.

3. **Start the FastAPI server**:
    ```
    bash start_server.sh
    ```
    - To use a custom host/port:
    ```
    bash start_server.sh 0.0.0.0 3001
    ```

4. **Access OpenAPI docs** at [http://localhost:3001/docs](http://localhost:3001/docs)

5. **Verify Installation**:
    - To check for missing dependencies, run:
    ```bash
    pip check
    ```
    - To ensure all required files are present for startup:
    ```bash
    ls -l .env .env.example requirements.txt start_server.sh src/api/main.py
    ```
    - If any of these files are missing or `pip check` reports issues, resolve them before running the backend.

---

## Troubleshooting

- **Port 3001 already in use:** Stop other processes using the port or pick another port for the backend.
- **Missing `.env` or missing/invalid `SECRET_KEY`:** Ensure `.env` exists with all required variables. Critical for security and correct app launch.
- **Module or import errors:** Ensure you run `uvicorn` or scripts from within the `student_backend_api` directory.
- **Missing `fastapi` or dependencies:** Ensure you've run:
    ```
    pip install -r requirements.txt
    ```
    If you see `ModuleNotFoundError`, check requirements and reinstall all dependencies.
- **Database issues:** Check `DATABASE_URL` in `.env`. Defaults to local SQLite for development.

---

## Dev Notes

- Use `start_server.sh` to simplify local dev runs.
- Use `.env.example` as a reference for all required variables.
- For Docker/container use, bind to `0.0.0.0` and expose port `3001`.

>>>>>>> REPLACE
