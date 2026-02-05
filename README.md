## GitSage

GitSage provides two core capabilities on top of GitHub repositories:

- **Repository Q&A**: Ask natural-language questions about any GitHub repo and get answers grounded purely in the indexed source and docs.
- **Repository Documentation Generator**: Generate structured, human-readable documentation (overview, architecture, setup, features, API reference) from a repo.

The backend is built with **FastAPI**, **ChromaDB**, and **Groq LLaMA**, and the frontend is a **React + Vite** SPA.

---

### 1. Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- A Groq API key
- A GitHub Personal Access Token (PAT) with read access to public repos

Create a `.env` file in `backend/` with:

```bash
GROQ_API_KEY=your_groq_api_key
GITHUB_PAT=your_github_pat
```

---

### 2. Backend Setup & Run

From the project root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

Key endpoints:

- `POST /ingest` – body: `{ "repo_url": "https://github.com/user/repo" }`
- `POST /ask` – body: `{ "repo_url": "...", "question": "..." }`
- `POST /generate-docs` – body: `{ "repo_url": "..." }`

Embeddings are stored persistently in `backend/vectorstore/chroma_db/`. Re‑ingesting the same repo at the same GitHub version will **skip** re‑embedding to keep ingestion fast.

---

### 3. Frontend Setup & Run

From the project root:

```bash
cd frontend
npm install
npm run dev
```

The app expects the backend at `http://127.0.0.1:8000` (configured in `src/api/gitsage.ts`).

Main pages:

- `Home` – entry and description
- `QA` – repository Q&A interface
- `Docs` – documentation generation UI
- `Compare` – compare docs/Q&A across repos

---

### 4. Architecture Overview

- `backend/main.py` – FastAPI app and HTTP routes (no business logic).
- `backend/repo_ingestion/` – GitHub API–based ingestion, filtering, cleaning, and chunking.
- `backend/embeddings/` – Routing and embedding for text/code; models are loaded once and reused.
- `backend/vectorstore/` – ChromaDB client and collections (code, text, repo index for caching).
- `backend/retrieval/` – Dual-space retriever over code and text embeddings.
- `backend/qa/` – Q&A orchestration, retrieval + prompting, and mode-specific behavior.
- `backend/docs/` – Documentation generator built on top of the same retrieval layer.
- `backend/llm/` – Groq LLaMA client with context truncation and deterministic generation settings.

---

### 5. Notes for Production

- Run the backend behind a process manager (e.g. systemd, supervisor, or Docker + orchestration).
- Configure FastAPI/uvicorn logging via environment variables or a logging config file if you need structured logs.
- Ensure `GROQ_API_KEY` and `GITHUB_PAT` are provided through your secret manager (not hard‑coded).
- Point `API_BASE` in `frontend/src/api/gitsage.ts` to your deployed backend URL.

