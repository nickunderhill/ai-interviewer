# AI Interviewer

AI-powered mock interview system for technical interview preparation.

## Tech Stack

- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS
- **Backend:** FastAPI + Python 3.11+ + SQLAlchemy (async)
- **Database:** PostgreSQL 15
- **Infrastructure:** Docker Compose

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- Docker & Docker Compose (for database)
- pnpm (for frontend package management)

## Quick Start

### 1. Database Setup

The application uses PostgreSQL running in Docker.

```bash
# Copy environment template and customize
cp .env.example .env

# IMPORTANT: Edit .env and change POSTGRES_PASSWORD
# Generate a secure password:
openssl rand -base64 32

# Start PostgreSQL container
docker-compose up -d postgres

# Verify database is running (should show "healthy" status)
docker-compose ps

# Check logs to confirm "database system is ready to accept connections"
docker-compose logs postgres
```

**Test database connection:**

```bash
# Using psql from within container
docker-compose exec postgres psql -U ai_interviewer_user -d ai_interviewer_db

# Once connected:
\l                 # List databases
\dt                # List tables
\q                 # Quit
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

API documentation: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Run development server
pnpm run dev
```

Frontend will be available at: http://localhost:5173

## Database Management

### Reset Database (Warning: Destroys All Data)

```bash
# Stop containers and remove volumes
docker-compose down -v

# Start fresh
docker-compose up -d postgres
```

### View Volumes

```bash
# List all volumes
docker volume ls

# Inspect PostgreSQL volume
docker volume inspect ai-interviewer_postgres_data
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop only database (keeps data)
docker-compose stop postgres
```

## Troubleshooting

### Port 5432 Already in Use

If you have PostgreSQL running locally:

```bash
# macOS
brew services stop postgresql

# Linux
sudo systemctl stop postgresql

# Or change port in docker-compose.yml:
ports:
  - "5433:5432"  # Use 5433 on host instead
```

### Database Connection Failed

1. Verify container is running and healthy: `docker-compose ps`
2. Check logs: `docker-compose logs postgres`
3. Ensure `.env` file exists with correct credentials
4. Verify password matches in both POSTGRES_PASSWORD and DB_PASSWORD

### Container Restarts Repeatedly

Check logs for errors: `docker-compose logs postgres`

Common fixes:

- Verify `.env` file syntax (no quotes around values)
- Check disk space: `df -h`
- Remove corrupted volume: `docker-compose down -v`

## Project Structure

```
.
├── backend/           # FastAPI backend
├── frontend/          # React frontend
├── docker-compose.yml # Database orchestration
├── .env.example       # Environment template
└── .env              # Your local config (not in git)
```

## Development Workflow

1. Start database: `docker-compose up -d postgres`
2. Start backend:
   `cd backend && source venv/bin/activate && uvicorn app.main:app --reload`
3. Start frontend: `cd frontend && pnpm run dev`
4. Access application at http://localhost:5173

## License

Educational project for diploma work.
