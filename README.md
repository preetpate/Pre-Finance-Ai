# Pre-Finance AI

> Offline AI-powered document intelligence platform — no paid APIs, no cloud, complete privacy.

![Pre-Finance AI](https://img.shields.io/badge/Stack-FastAPI%20%7C%20SQLite%20%7C%20Ollama%20%7C%20FAISS-8B5CF6?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## What it does

Upload PDF, DOCX, or TXT documents. Ask questions in plain English. Get accurate answers with page-level source citations — powered by a local LLM running entirely on your machine.

---

## Quick start

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Backend |
| Ollama | Latest | Local LLM |
| VS Code Live Server | - | Serve frontend |

### 1. Install Ollama and pull model

```bash
# Download from https://ollama.ai
ollama pull qwen2.5:1.5b
```

### 2. Run setup

```bat
setup.bat
```

### 3. Start backend

```bat
start_server.bat
```

Backend runs at: `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

### 4. Open frontend

Open `frontend/login.html` with VS Code Live Server (default port 5500).

---

## Default accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@prefinance.ai | Admin@123456 |

> Change the admin password in `.env` before first run.

---

## Project structure

```
Pre-Finance AI/
├── backend/
│   ├── main.py          # FastAPI app + startup
│   ├── models.py        # SQLAlchemy ORM
│   ├── schemas.py       # Pydantic validation
│   ├── config.py        # Settings from .env
│   ├── database.py      # Async SQLite engine
│   ├── dependencies.py  # Auth guards
│   ├── routers/         # auth, users, documents, chat, admin
│   ├── services/        # document processor, embeddings, RAG, LLM
│   └── security/        # Argon2 hashing, JWT
├── frontend/
│   ├── login.html
│   ├── register.html
│   └── pages/
│       ├── dashboard.html
│       ├── documents.html
│       ├── chat.html
│       └── admin/
│           ├── dashboard.html
│           └── users.html
├── data/
│   ├── uploads/         # User files (git-ignored)
│   └── vector_store/    # FAISS indexes (git-ignored)
└── requirements.txt
```

---

## Technology stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | HTML + CSS + JS | Zero build tools, fast iteration |
| Backend | FastAPI + Python | Async, auto-generated API docs |
| Database | SQLite + SQLAlchemy | Zero-config, file-based |
| Auth | JWT + Argon2id | Secure, stateless |
| AI model | Ollama (Qwen 2.5 1.5B) | Local inference, 8GB RAM friendly |
| Embeddings | Sentence Transformers | Free, runs offline |
| Vector DB | FAISS | Fast similarity search, no server |
| PDF | PyMuPDF | Fast extraction with page numbers |
| Charts | Chart.js | CDN, no build step |

---

## Development phases

- [x] Phase 1 – Project foundation (this phase)
- [ ] Phase 2 – Complete frontend design
- [ ] Phase 3 – Auth system
- [ ] Phase 4 – Database models
- [ ] Phase 5 – Document processing (PDF/DOCX/TXT → chunks)
- [ ] Phase 6 – RAG pipeline (embeddings + FAISS + Ollama)
- [ ] Phase 7 – Chat system
- [ ] Phase 8 – Admin panel
- [ ] Phase 9 – Testing and security hardening
- [ ] Phase 10 – GitHub README and deployment guide

---

## Security notes

- Passwords hashed with Argon2id (not bcrypt, not plaintext)
- JWT secret in `.env` — never hardcode
- Admin account seeded manually — no public registration creates admins
- File uploads validated by extension and MIME type
- Each document is owner-scoped — users cannot access each other's data
- CORS restricted to localhost origins in development
