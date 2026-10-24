# CLAUDE.md

## What this is

**Spotify Stats** — a chatbot web app that answers natural-language questions about a user's Spotify streaming history ("What was my most-streamed Bruno Mars song in 2019?"). Users upload the JSON export from Spotify's privacy page; the backend loads it into SQLite, has an LLM translate each question into SQL, runs it, then has the LLM phrase the result as a friendly reply.

## Layout

```
backend/                 Flask API (Python)
  app.py                 Routes: GET /check-database, POST /upload, POST /query
  config.py              DB_PATH and UPLOAD_FOLDER, anchored to backend/
  services/
    process_files.py     Validates uploaded JSON and inserts rows into the `streams` table
    query_handler.py     prompt -> SQL (OpenAI) -> execute -> natural-language answer (OpenAI)
  requirements.txt
  .env.example
frontend/                Create React App (React 19)
  src/App.js             All state + API calls (check DB, upload, query)
  src/components/        Presentational components, each with a co-located .css file
  .env.example
```

## Running locally

Backend (Python 3.10+):

```bash
cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

```bash
cd backend && cp .env.example .env   # then fill in OPENAI_API_KEY and SECRET_KEY; FLASK_DEBUG=1 for auto-reload
```

```bash
cd backend && python app.py   # serves on http://127.0.0.1:5000
```

Frontend:

```bash
cd frontend && npm install && npm start   # http://localhost:3000
```

The frontend reads `REACT_APP_BACKEND_URL`, defaulting to `http://127.0.0.1:5000`.

There are no automated tests yet. Adding frontend tests means installing `@testing-library/react` and `@testing-library/jest-dom` (CRA's `npm test` picks up `src/setupTests.js` automatically).

## How the data flows

1. On load, the frontend calls `/check-database`; the chat input stays disabled until the `streams` table has rows.
2. `/upload` saves files to `backend/uploads/`, then `process_json_files` validates every entry has all 15 required keys and inserts rows (entries with no track/artist/album, i.e. podcasts, are skipped). Any validation error deletes `database.db` entirely.
3. `/query` calls `handle_user_prompt`, which returns `{query, results, chatbot_response}` or `{error}`. The frontend only displays `chatbot_response`.

## Conventions and gotchas

- **The `streams` schema is defined twice**: the `CREATE TABLE` in `services/process_files.py` and the schema text inside the prompt in `services/query_handler.py`. Change both together.
- Always use `config.DB_PATH` / `config.UPLOAD_FOLDER`; never hard-code `"database.db"` or relative paths (they break when the app is launched from another directory).
- Backend imports are relative to `backend/` (`from services.x import ...`, `from config import ...`), so run Python from inside `backend/`.
- The model name (`gpt-3.5-turbo`) is hard-coded in `query_handler.py` (twice) and shown in `frontend/src/components/Header.js`; keep them in sync.
- Errors in `query_handler.py` are signalled by returning strings containing `"Error"`/`"Database error"` rather than raising; `handle_user_prompt` checks for those substrings.
- Uploads append to the existing table: re-uploading the same files double-counts streams.
- New React components go in `frontend/src/components/` as `Name.js` + `Name.css`; keep state in `App.js`.
- `database.db`, `uploads/` and `.env` contain the user's personal listening data or secrets and are git-ignored; never commit them.

## Security guardrails (keep these intact)

- LLM-generated SQL runs in `execute_sql_query` on a **read-only** SQLite connection (`mode=ro`) with an authorizer that only permits SELECT/READ/FUNCTION/RECURSIVE actions, so writes, `ATTACH` and `PRAGMA` are denied. Never run model output on the read-write connection used by `process_files.py`.
- Uploaded filenames go through `werkzeug.utils.secure_filename` before being joined into a path.
- CORS only allows the origins in `CORS_ORIGINS` (default `http://localhost:3000`); add the deployed frontend's origin there rather than using `*`.
- Debug mode is off by default; set `FLASK_DEBUG=1` in `backend/.env` for local development only.
