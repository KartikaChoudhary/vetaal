# Vetaal 🕯️

A webtoon-style landing page with a live FastAPI + PostgreSQL backend. Users can log in
and answer the Vetaal's riddles — answers are stored in the database.

## Stack
- **Frontend:** plain HTML/CSS/JS (no framework)
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL, via SQLAlchemy

## Project structure
```
vetal/
├── vetal.html          # the site
├── script.js            # frontend logic (fetches data, handles login/quiz)
├── auth-and-quiz.css    # styling for the login modal + riddle box
├── vetal.img.gif
└── backend/
    ├── main.py           # API routes
    ├── models.py         # database tables
    ├── schemas.py        # request/response shapes
    ├── database.py       # DB connection
    ├── auth.py           # password hashing + JWT tokens
    ├── seed.py           # fills the DB with starter content
    ├── requirements.txt
    └── .env.example      # copy this to .env and fill in your own values
```

## Running this locally

**You'll need:** Python 3.11+, and PostgreSQL installed (or a free hosted instance
like [Neon](https://neon.tech) or [Supabase](https://supabase.com)).

1. **Clone the repo**
   ```bash
   git clone <your-repo-url>
   cd vetal
   ```

2. **Create a database and a database user** (in `psql` or pgAdmin):
   ```sql
   CREATE DATABASE vetaal_db;
   CREATE USER vetaal_user WITH PASSWORD 'your_own_password';
   GRANT ALL PRIVILEGES ON DATABASE vetaal_db TO vetaal_user;
   \c vetaal_db
   GRANT ALL ON SCHEMA public TO vetaal_user;
   ```

3. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   # Mac/Linux:
   source venv/bin/activate
   # Windows (PowerShell):
   .\venv\Scripts\Activate.ps1

   pip install -r requirements.txt
   cp .env.example .env
   ```
   Open `.env` and set `DATABASE_URL` to match the user/password/database you just
   created, and set `SECRET_KEY` to any random string (or generate one:
   `python -c "import secrets; print(secrets.token_hex(32))"`).

4. **Run the server** (this also creates all the tables automatically)
   ```bash
   python -m uvicorn main:app --reload --reload-exclude "venv/*"
   ```

5. **Seed starter content** (in a second terminal, with the venv activated)
   ```bash
   python seed.py
   ```

6. **Open the site** — just open `vetal.html` in your browser (or use a
   "Live Server" extension). The backend must be running at `http://127.0.0.1:8000`
   for the page to load its data and for login/quiz to work.

## Notes
- `.env` is intentionally not committed to this repo (see `.gitignore`) — it holds
  your real database password. Only `.env.example` (a template with no real secrets)
  is committed.
- This is a learning project — auth uses a simple JWT setup and the CORS policy is
  wide open (`allow_origins=["*"]`), which is fine for local development but should
  be locked down before any real deployment.
