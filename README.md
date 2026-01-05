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

### Option 1: Docker Compose (Recommended)

Start all services (frontend, backend, database) with one command:

```bash
# Ensure .env file exists in backend/
# Default values work for development

# Build and start all services
docker-compose up --build

# Or run in background (detached mode)
docker-compose up -d

# View logs
docker-compose logs -f
```

**Services will be available at:**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: localhost:5432

Note: The frontend expects `VITE_API_BASE_URL` to be the backend origin (e.g.
`http://localhost:8000`). API paths already include the `/api/v1` prefix.

**Hot reload is enabled** - changes to frontend or backend code will
automatically reload.

**Stop services:**

```bash
docker-compose down

# To remove volumes (database data)
docker-compose down -v
```

### Option 2: Local Development (Without Docker)

#### 1. Database Setup

```bash
# Start only PostgreSQL in Docker
docker-compose up -d postgres

# Verify database is running
docker-compose ps
```

**Important:** Change DB_HOST in backend/.env from `postgres` to `localhost`
when running backend locally.

#### 2. Backend Setup

```bash
cd backend

# Edit .env - change DB_HOST=postgres to DB_HOST=localhost
sed -i '' 's/DB_HOST=postgres/DB_HOST=localhost/' .env

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Run development server
pnpm run dev
```

Frontend will be available at: http://localhost:5173 (or 3000 if configured)

## Docker Commands Reference

### Service Management

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop all services (keeps data)
docker-compose down

# Stop and remove volumes (deletes database data)
docker-compose down -v

# Restart specific service
docker-compose restart backend

# View running containers
docker-compose ps
```

### Logs and Debugging

```bash
# View all logs
docker-compose logs

# Follow logs (like tail -f)
docker-compose logs -f

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Execute command in running container
docker-compose exec backend bash
docker-compose exec postgres psql -U ai_interviewer_user -d ai_interviewer_db
```

### Rebuilding

```bash
# Rebuild all services
docker-compose build

# Rebuild specific service
docker-compose build backend

# Rebuild and start
docker-compose up --build

# Force rebuild (no cache)
docker-compose build --no-cache
```

### Database Management

```bash
# Connect to database
docker-compose exec postgres psql -U ai_interviewer_user -d ai_interviewer_db

# Run Alembic migrations in Docker
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Reset database (WARNING: Destroys all data)
docker-compose down -v
docker-compose up -d
```

## Troubleshooting

### Port Already in Use (3000, 8000, or 5432)

```bash
# Find process using port
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Kill process
kill -9 <PID>

# Or stop local services
brew services stop postgresql  # macOS
sudo systemctl stop postgresql # Linux

# Alternative: Change port in docker-compose.yml
ports:
  - "3001:3000"  # Frontend on 3001
  - "8001:8000"  # Backend on 8001
  - "5433:5432"  # Postgres on 5433
```

### Frontend Hot Reload Not Working

Issue: Changes to frontend files don't trigger reload in Docker.

**Solution:** Verify `vite.config.ts` has polling enabled:

```typescript
server: {
  host: '0.0.0.0',
  port: 3000,
  watch: {
    usePolling: true,  // Required for Docker
    interval: 1000,
  },
}
```

### Backend Hot Reload Not Working

Issue: Changes to backend files don't trigger reload.

**Solution:**

1. Verify volume mount in docker-compose.yml: `./backend/app:/app/app:ro`
2. Check command has `--reload` flag: `uvicorn app.main:app --reload`
3. View backend logs: `docker-compose logs backend`

### Database Connection Failed

```bash
# 1. Verify containers are running
docker-compose ps

# 2. Check backend environment
docker-compose exec backend env | grep DB_

# Expected: DB_HOST=postgres (not localhost)

# 3. Check postgres logs
docker-compose logs postgres

# 4. Test connection from backend
docker-compose exec backend python -c "from app.core.database import engine; print('Connected')"
```

### Build Errors

```bash
# Clear Docker cache and rebuild
docker-compose down
docker system prune -a
docker-compose build --no-cache
docker-compose up
```

### "Cannot connect to Docker daemon"

```bash
# Ensure Docker Desktop is running
open -a Docker  # macOS

# Or start Docker service
sudo systemctl start docker  # Linux
```

## Project Structure

```
.
├── backend/
│   ├── app/               # FastAPI application code
│   ├── alembic/           # Database migrations
│   ├── tests/             # Backend tests
│   ├── Dockerfile         # Backend container definition
│   ├── .dockerignore      # Excluded from Docker build
│   ├── requirements.txt   # Python dependencies
│   └── .env               # Backend environment variables
├── frontend/
│   ├── src/               # React application code
│   ├── public/            # Static assets
│   ├── Dockerfile.dev     # Frontend dev container
│   ├── .dockerignore      # Excluded from Docker build
│   ├── vite.config.ts     # Vite configuration (Docker-compatible)
│   └── package.json       # Node dependencies
├── docker-compose.yml     # Multi-service orchestration
├── .gitignore             # Git exclusions
└── README.md              # This file
```

## Development Workflow

### Using Docker (Recommended)

```bash
# Start all services
docker-compose up

# Make changes to code - hot reload automatically reloads

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Local Development

1. Start database: `docker-compose up -d postgres`
2. Start backend:
   `cd backend && source venv/bin/activate && uvicorn app.main:app --reload`
3. Start frontend: `cd frontend && pnpm run dev`

**Note:** Remember to change `DB_HOST=postgres` to `DB_HOST=localhost` in
backend/.env for local development.

## CI/CD Pipeline

This project uses GitHub Actions for automated testing, linting, and deployment.

### Workflow Jobs

The workflow consists of four jobs with dependencies:

1. **Build** - Install dependencies for frontend and backend (using matrix
   strategy)
2. **Test** - Run pytest for backend tests with coverage (depends on build)
3. **Lint** - Run Ruff for backend and ESLint for frontend (depends on build)
4. **Deploy** - Build and push Docker images to GitHub Container Registry (main
   branch only, depends on test and lint)

### Running Tests Locally

**Backend Tests:**

```bash
cd backend
source venv/bin/activate
pip install pytest pytest-cov pytest-asyncio httpx

# Run tests with coverage
pytest tests/ -v --cov=app --cov-report=term

# Run specific test file
pytest tests/test_main.py -v
```

**Frontend Tests:**

```bash
cd frontend
pnpm install

# Run tests
pnpm test --run

# Run tests in watch mode
pnpm test
```

### Running Linting Locally

**Backend Linting:**

```bash
cd backend
source venv/bin/activate
pip install ruff

# Check code quality
ruff check app/ tests/

# Auto-fix issues
ruff check --fix app/ tests/

# Format code
ruff format app/ tests/
```

**Frontend Linting:**

```bash
cd frontend
pnpm install

# Run ESLint
pnpm run lint

# Auto-fix issues
pnpm run lint -- --fix
```

### Workflow Configuration

Workflow is defined in `.github/workflows/ci.yml` with the following features:

- **Caching** - Dependencies cached using actions/cache and setup actions
- **Artifacts** - Test coverage reports uploaded using actions/upload-artifact
- **Service Containers** - PostgreSQL service container for integration tests
- **Branch Protection** - Deploy job runs only on main branch
- **Container Registry** - Images pushed to GitHub Container Registry (ghcr.io)
- **Matrix Strategy** - Build, test, and lint jobs use matrix for
  backend/frontend

### GitHub Actions Secrets and Variables

The following are automatically provided by GitHub Actions:

- `GITHUB_TOKEN` - Authentication token (automatically provided)
- `REGISTRY` - GitHub Container Registry URL (ghcr.io)
- `IMAGE_NAME` - Repository name (from github.repository)
- `github.actor` - Username triggering the workflow
- `github.ref` - Branch/tag reference
- `github.sha` - Current commit SHA

### Viewing Workflow Status

1. Navigate to **Actions** tab in GitHub repository
2. Click on a workflow run to see job details
3. Click on a job to view logs and artifacts
4. Coverage reports available in workflow artifacts

### Docker Images

After successful deployment, Docker images are available:

```bash
# Pull images from GitHub Container Registry
docker pull ghcr.io/OWNER/REPO/backend:latest
docker pull ghcr.io/OWNER/REPO/frontend:latest

# Or specific commit
docker pull ghcr.io/OWNER/REPO/backend:main-SHA
```

## License

Educational project for diploma work.
