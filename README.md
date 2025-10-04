# Job Matcher Platform

FastAPI + PostgreSQL backend paired with a Next.js frontend to parse CVs, store structured candidates/jobs, and return ranked matches.

## Backend Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```
2. Configure PostgreSQL (or set `DATABASE_URL`) and initialise the schema:
   ```bash
   python -m backend.init_db
   ```
3. Run the API server:
   ```bash
   uvicorn backend.main:app --reload
   ```

## Running Tests

Automated tests use in-memory SQLite with the same SQLAlchemy models, so they run quickly without touching Postgres.

```bash
pytest
```

## API Highlights

- `GET /match/candidate/{candidate_id}` returns ranked job matches with per-job analytics, including semantic similarity scores when embeddings are enabled.
- `GET /match/candidate/{candidate_id}/skill-gap` aggregates the top missing skills across considered jobs and links curated learning resources.

## Frontend (Next.js)

Install dependencies and launch the dev server:
```bash
cd frontend
npm install
npm run dev
```

## Roadmap

- Enrich rule-based scoring with resume signals (tenure, seniority hints).
- Introduce pgvector-backed semantic search and hybrid ranking.
- Evolve skill-gap insights into actionable career recommendation endpoints.
- Connect the frontend upload flow to `/candidates/upload` and the matching results endpoint.

Set `EMBEDDING_BACKEND=sentence-transformer` to use a SentenceTransformer model (default `all-MiniLM-L6-v2`), or leave unset to fall back to a lightweight hashed embedding that keeps tests fast.

## Staging Environment Setup

To run the staging environment locally using Docker:

1. Ensure Docker and Docker Compose are installed on your system.
2. Copy the `.env.example` file to `.env` and update the values as needed.
3. Build and start the services:

   ```bash
   docker-compose up --build
   ```

4. Access the services:
   - Backend: [http://localhost:8000](http://localhost:8000)
   - Frontend: [http://localhost:3000](http://localhost:3000)

5. To stop the services:

   ```bash
   docker-compose down
   ```
