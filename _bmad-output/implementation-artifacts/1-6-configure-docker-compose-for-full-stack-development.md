# Story 1.6: Configure Docker Compose for Full Stack Development

Status: ready-for-dev

## Story

As a developer, I want to configure Docker Compose to orchestrate frontend,
backend, and database services, so that the entire application can start with
one command.

## Acceptance Criteria

1. **Given** I have frontend, backend, and database configured individually
   **When** I update docker-compose.yml with services for frontend, backend, and
   postgres **Then** running `docker-compose up` starts all three services

2. **Given** all services are configured **Then** the backend service depends on
   postgres service (starts after database is ready) **And** the frontend is
   accessible at http://localhost:3000 **And** the backend API is accessible at
   http://localhost:8000

3. **Given** Docker Compose is running **Then** code changes trigger hot reload
   in both frontend (Vite HMR) and backend (uvicorn reload) **And** environment
   variables are properly configured for each service **And** data persists
   across container restarts

## Tasks / Subtasks

- [ ] Task 1: Update docker-compose.yml with all three services (AC: #1)

  - [ ] Keep existing postgres service configuration
  - [ ] Add backend service with Python/FastAPI configuration
  - [ ] Add frontend service with Node.js/Vite configuration
  - [ ] Define service dependencies (backend depends on postgres)

- [ ] Task 2: Create Dockerfile for backend service (AC: #1)

  - [ ] Create backend/Dockerfile with Python 3.11+ base image
  - [ ] Install Python dependencies from requirements.txt
  - [ ] Configure uvicorn with --reload for development
  - [ ] Expose port 8000

- [ ] Task 3: Create Dockerfile for frontend service (AC: #1)

  - [ ] Create frontend/Dockerfile.dev with Node.js base image
  - [ ] Install pnpm and dependencies
  - [ ] Configure Vite dev server with HMR
  - [ ] Expose port 3000 (remapped from 5173)

- [ ] Task 4: Configure environment variables for services (AC: #3)

  - [ ] Update .env with DB_HOST=postgres for backend container
  - [ ] Create .env.docker for container-specific settings
  - [ ] Configure frontend API URL to point to backend container
  - [ ] Ensure secrets not committed to repository

- [ ] Task 5: Configure volume mounts for hot reload (AC: #3)

  - [ ] Mount backend/app directory for Python code changes
  - [ ] Mount frontend/src directory for React code changes
  - [ ] Exclude node_modules and **pycache** from mounts
  - [ ] Mount alembic directory for migration access

- [ ] Task 6: Configure networking between services (AC: #2)

  - [ ] Define Docker network for service communication
  - [ ] Backend connects to postgres via service name
  - [ ] Frontend connects to backend via service name
  - [ ] Expose frontend and backend to host machine

- [ ] Task 7: Verify full stack operation (AC: #1, #2, #3)
  - [ ] Run `docker-compose up` and verify all services start
  - [ ] Test frontend accessible at http://localhost:3000
  - [ ] Test backend API at http://localhost:8000
  - [ ] Test health endpoint: http://localhost:8000/health
  - [ ] Test hot reload by editing frontend and backend files
  - [ ] Verify database connection from backend container

## Dev Notes

### Critical Architecture Requirements

**Technology Stack (from architecture.md & project-context.md):**

- Docker Compose v3.9 for orchestration
- Multi-container setup: postgres, backend, frontend
- Development mode with hot reload for both services
- Volume mounts for source code
- Service dependencies and health checks
- Network isolation with named network

**Docker Compose Configuration Standards:**

- **Compose Version**: 3.9
- **Network**: Custom bridge network for service communication
- **Volumes**: Named volumes for persistence, bind mounts for code
- **Environment**: .env file for configuration
- **Health Checks**: Postgres health check, backend startup dependency
- **Restart Policy**: unless-stopped for all services

### Technical Implementation Details

**Step 1: Update docker-compose.yml**

Replace `docker-compose.yml` at project root with full stack configuration:

```yaml
version: '3.9'

services:
  # PostgreSQL Database Service
  postgres:
    image: postgres:15-alpine
    container_name: ai-interviewer-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-ai_interviewer_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-dev_password_change_in_production}
      POSTGRES_DB: ${POSTGRES_DB:-ai_interviewer_db}
    ports:
      - '5432:5432'
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U ${POSTGRES_USER:-ai_interviewer_user}']
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - app-network

  # FastAPI Backend Service
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ai-interviewer-backend
    environment:
      # Database connection (use service name 'postgres' as host)
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: ${POSTGRES_DB:-ai_interviewer_db}
      DB_USER: ${POSTGRES_USER:-ai_interviewer_user}
      DB_PASSWORD: ${POSTGRES_PASSWORD:-dev_password_change_in_production}
      # Application settings
      DEBUG: ${DEBUG:-true}
      SECRET_KEY: ${SECRET_KEY:-dev-secret-key-change-in-production}
    ports:
      - '8000:8000'
    volumes:
      # Mount source code for hot reload
      - ./backend/app:/app/app:ro
      - ./backend/alembic:/app/alembic:ro
      - ./backend/alembic.ini:/app/alembic.ini:ro
    depends_on:
      postgres:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    restart: unless-stopped
    networks:
      - app-network

  # Vite + React Frontend Service
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: ai-interviewer-frontend
    environment:
      # API URL pointing to backend service
      VITE_API_BASE_URL: http://backend:8000/api/v1
    ports:
      - '3000:3000'
    volumes:
      # Mount source code for hot reload
      - ./frontend/src:/app/src:ro
      - ./frontend/public:/app/public:ro
      - ./frontend/index.html:/app/index.html:ro
      - ./frontend/vite.config.ts:/app/vite.config.ts:ro
      # Prevent mounting node_modules (use container's version)
      - /app/node_modules
    depends_on:
      - backend
    command: pnpm run dev --host 0.0.0.0 --port 3000
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres_data:
    driver: local

networks:
  app-network:
    driver: bridge
```

**Key Configuration Decisions:**

1. **Service Dependencies**: backend waits for postgres health check, frontend
   starts after backend
2. **DB_HOST=postgres**: Backend uses service name instead of localhost
3. **Port Mapping**: Frontend 3000 (instead of 5173), Backend 8000, Postgres
   5432
4. **Volume Mounts**: Read-only mounts for source code, excluded node_modules
5. **Networks**: Custom bridge network for service-to-service communication
6. **Health Checks**: Postgres health check ensures database ready before
   backend starts

**Step 2: Create Backend Dockerfile**

Create `backend/Dockerfile`:

```dockerfile
# Use official Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Default command (overridden in docker-compose.yml for development)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Key Dockerfile Features:**

1. **Python 3.11-slim**: Smaller image size (~150MB vs ~900MB for full)
2. **Environment Variables**: Prevent .pyc files, unbuffered output for logs
3. **System Dependencies**: gcc for compiling Python packages, postgresql-client
   for debugging
4. **Layer Caching**: requirements.txt copied separately for better caching
5. **Working Directory**: /app matches volume mounts in docker-compose.yml

**Step 3: Create Frontend Dockerfile**

Create `frontend/Dockerfile.dev`:

```dockerfile
# Use official Node.js LTS image
FROM node:20-alpine

# Install pnpm globally
RUN npm install -g pnpm

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy application code
COPY . .

# Expose Vite dev server port
EXPOSE 3000

# Default command (overridden in docker-compose.yml)
CMD ["pnpm", "run", "dev", "--host", "0.0.0.0", "--port", "3000"]
```

**Key Dockerfile Features:**

1. **Node 20 Alpine**: Latest LTS with smaller image size
2. **pnpm**: Matches local development environment
3. **Frozen Lockfile**: Ensures consistent dependencies
4. **Port 3000**: Remapped from Vite default 5173
5. **Host 0.0.0.0**: Required for Docker container access

**Step 4: Update Vite Configuration for Docker**

Update `frontend/vite.config.ts` to support Docker:

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Listen on all interfaces for Docker
    port: 3000, // Changed from default 5173
    strictPort: true,
    watch: {
      usePolling: true, // Required for file watching in Docker
      interval: 1000,
    },
  },
});
```

**Important Changes:**

1. **host: '0.0.0.0'**: Allows access from outside container
2. **port: 3000**: Consistent with docker-compose.yml
3. **usePolling: true**: Required for hot reload in Docker volumes
4. **interval: 1000**: Check for file changes every second

**Step 5: Create .env.docker for Container Environment**

Create `.env.docker` (optional, for container-specific overrides):

```env
# Docker Compose Environment Variables
# Copy to .env and customize as needed

# PostgreSQL Database
POSTGRES_USER=ai_interviewer_user
POSTGRES_PASSWORD=dev_password_change_in_production
POSTGRES_DB=ai_interviewer_db

# Backend Configuration
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production

# Important: DB_HOST is set in docker-compose.yml to 'postgres' (service name)
# When running backend outside Docker, use DB_HOST=localhost in local .env
```

**Update .env for Container Mode:**

```env
# Database Configuration (for Docker Compose)
DB_HOST=postgres  # Changed from localhost - use service name
DB_PORT=5432
DB_NAME=ai_interviewer_db
DB_USER=ai_interviewer_user
DB_PASSWORD=dev_password_change_in_production

# PostgreSQL Configuration
POSTGRES_USER=ai_interviewer_user
POSTGRES_PASSWORD=dev_password_change_in_production
POSTGRES_DB=ai_interviewer_db

# Application Configuration
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
```

**Step 6: Update .gitignore**

Add to `.gitignore`:

```gitignore
# Environment files
.env
.env.local
.env.docker

# Docker
.dockerignore

# Python
backend/__pycache__/
backend/**/__pycache__/
backend/.pytest_cache/
backend/venv/

# Node.js
frontend/node_modules/
frontend/dist/
frontend/.vite/
```

**Step 7: Verification and Testing**

```bash
# Build and start all services
docker-compose up --build

# Expected output:
# Creating network "ai-interviewer_app-network" with driver "bridge"
# Creating volume "ai-interviewer_postgres_data" with local driver
# Building backend...
# Building frontend...
# Creating ai-interviewer-postgres ... done
# Creating ai-interviewer-backend  ... done
# Creating ai-interviewer-frontend ... done
# Attaching to ai-interviewer-postgres, ai-interviewer-backend, ai-interviewer-frontend
# backend  | INFO:     Uvicorn running on http://0.0.0.0:8000
# backend  | INFO:     Application startup complete
# frontend | VITE v5.x.x ready in xxx ms
# frontend | ➜  Local:   http://localhost:3000/
```

**Test Service Access:**

```bash
# Test frontend
curl http://localhost:3000
# Should return HTML

# Test backend root endpoint
curl http://localhost:8000/
# Expected: {"message":"AI Interviewer API","status":"running","version":"1.0.0"}

# Test backend health endpoint
curl http://localhost:8000/health
# Expected: {"status":"healthy","database":"connected","api":"operational"}

# Test backend OpenAPI docs
open http://localhost:8000/docs
# Should show Swagger UI
```

**Test Hot Reload:**

```bash
# Terminal 1: Keep docker-compose running
docker-compose up

# Terminal 2: Edit backend file
echo "# Test comment" >> backend/app/main.py
# Backend should automatically reload

# Terminal 3: Edit frontend file
echo "// Test comment" >> frontend/src/App.tsx
# Frontend should automatically reload in browser
```

**Test Database Connection:**

```bash
# Execute commands in backend container
docker-compose exec backend python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"

# Should output:
# ✓ Database connected successfully
# ✓ Connection URL: postgres:5432/ai_interviewer_db
# ✓ Pool size: 5-20 connections
```

### Docker Compose Commands Reference

```bash
# Build and start all services
docker-compose up --build

# Start services in detached mode (background)
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes database data)
docker-compose down -v

# View logs for all services
docker-compose logs

# View logs for specific service
docker-compose logs backend
docker-compose logs -f frontend  # Follow logs

# Restart specific service
docker-compose restart backend

# Execute command in running container
docker-compose exec backend bash
docker-compose exec postgres psql -U ai_interviewer_user -d ai_interviewer_db

# View running services
docker-compose ps

# Rebuild specific service
docker-compose build backend

# Pull latest images
docker-compose pull

# Remove stopped containers
docker-compose rm
```

### Previous Story Learnings

**From Story 1.1 (Frontend Setup):**

- Frontend uses pnpm for package management
- Vite dev server originally on port 5173 (now 3000 in Docker)
- Hot module replacement requires polling in Docker

**From Story 1.2 (Backend Setup):**

- Backend uses uvicorn with --reload for hot reload
- Python virtual environment not needed in Docker
- FastAPI application in app/main.py

**From Story 1.3 (PostgreSQL Setup):**

- PostgreSQL service already configured in docker-compose.yml
- Named volume postgres_data for persistence
- Health check configured with pg_isready

**From Story 1.4 (SQLAlchemy Integration):**

- Backend connects via DB_HOST environment variable
- Must use 'postgres' service name (not localhost) in Docker
- Connection pooling configured for 5-20 connections

**From Story 1.5 (Alembic Setup):**

- Alembic directory and migrations need to be mounted
- Alembic migrations can run in container or on host

**Integration Changes:**

- Backend: DB_HOST changes from localhost to postgres
- Frontend: API URL points to backend service
- Vite: Needs polling for hot reload in Docker volumes
- All services: Connected via app-network for communication

### Common Issues & Solutions

**Issue: "bind: address already in use" for port 3000/8000/5432**

- **Cause**: Port already used by another process
- **Solution**: Stop conflicting services or change port mapping
- **Check**: `lsof -i :3000`, `lsof -i :8000`, `lsof -i :5432`
- **Alternative**: Change port in docker-compose.yml: `"3001:3000"`

**Issue: Backend "cannot connect to database" in Docker**

- **Cause**: Using DB_HOST=localhost instead of postgres
- **Solution**: Verify .env has DB_HOST=postgres (service name)
- **Test**: `docker-compose exec backend env | grep DB_HOST`

**Issue: Frontend hot reload not working**

- **Cause**: File watching doesn't work with Docker volumes by default
- **Solution**: Set `watch: { usePolling: true }` in vite.config.ts
- **Verify**: Edit frontend/src/App.tsx, check browser auto-refreshes

**Issue: Backend hot reload not working**

- **Cause**: Source code not mounted or uvicorn not in reload mode
- **Solution**: Verify volume mount and --reload flag in docker-compose.yml
- **Test**: Add comment to app/main.py, check backend logs for reload

**Issue: "exec format error" when starting containers**

- **Cause**: Building images on different architecture (M1 Mac vs x86)
- **Solution**: Use `--platform linux/amd64` in Dockerfile FROM line
- **Example**: `FROM --platform=linux/amd64 python:3.11-slim`

**Issue: Frontend cannot connect to backend API**

- **Cause**: Incorrect API URL or CORS configuration
- **Solution**: Verify VITE_API_BASE_URL points to http://backend:8000/api/v1
- **Note**: From browser, use http://localhost:8000/api/v1
- **CORS**: Backend must allow localhost:3000 origin

**Issue: "Cannot connect to Docker daemon"**

- **Cause**: Docker daemon not running
- **Solution**: Start Docker Desktop or Docker daemon
- **Verify**: `docker ps` should return container list

**Issue: Slow build times**

- **Cause**: Not using Docker layer caching effectively
- **Solution**:
  - Copy requirements.txt/package.json first before copying code
  - Use .dockerignore to exclude unnecessary files
  - Use docker-compose build --parallel for multiple services

**Issue: Database data lost after docker-compose down**

- **Cause**: Used `docker-compose down -v` which removes volumes
- **Solution**: Use `docker-compose down` without `-v` flag
- **Restore**: Restart postgres and rerun migrations: `alembic upgrade head`

### Testing Requirements

**Manual Testing Checklist:**

1. **Docker Compose Build**

   - [ ] `docker-compose build` completes without errors
   - [ ] All three services build successfully (postgres, backend, frontend)
   - [ ] No "ERROR" messages in build output

2. **Service Startup**

   - [ ] `docker-compose up` starts all three services
   - [ ] Postgres starts first and becomes healthy
   - [ ] Backend starts after postgres is healthy
   - [ ] Frontend starts last
   - [ ] No error messages in startup logs

3. **Service Access**

   - [ ] Frontend accessible at http://localhost:3000
   - [ ] Backend API accessible at http://localhost:8000
   - [ ] Health endpoint returns healthy: http://localhost:8000/health
   - [ ] OpenAPI docs accessible: http://localhost:8000/docs

4. **Database Connection**

   - [ ] Backend logs show "Database connected successfully"
   - [ ] Health endpoint shows database: connected
   - [ ] Can execute queries in backend container

5. **Hot Reload - Backend**

   - [ ] Edit backend/app/main.py
   - [ ] Backend container logs show reload
   - [ ] Changes reflected immediately without restart

6. **Hot Reload - Frontend**

   - [ ] Edit frontend/src/App.tsx
   - [ ] Browser shows "Vite connected" or auto-refreshes
   - [ ] Changes visible immediately

7. **Data Persistence**

   - [ ] Create test data in database
   - [ ] Stop containers: `docker-compose down`
   - [ ] Start containers: `docker-compose up`
   - [ ] Test data still exists

8. **Service Communication**

   - [ ] Backend can query postgres via 'postgres' hostname
   - [ ] Frontend can call backend API via 'backend' hostname (from container)
   - [ ] Frontend can call backend from browser via localhost:8000

9. **Environment Variables**

   - [ ] Backend has correct DB_HOST=postgres
   - [ ] Frontend has correct VITE_API_BASE_URL
   - [ ] Check with: `docker-compose exec backend env`

10. **Clean Shutdown**
    - [ ] `docker-compose down` stops all services
    - [ ] No hanging processes
    - [ ] Volume persists: `docker volume ls` shows postgres_data

### Future Considerations

**Production Docker Compose (Post-MVP):**

- Use production Dockerfiles without --reload
- Multi-stage builds to reduce image size
- Nginx reverse proxy for frontend static files
- SSL/TLS certificates with Let's Encrypt
- Health checks for all services
- Resource limits (CPU, memory)
- Logging drivers for centralized logs

**Kubernetes Migration (Post-MVP):**

- Convert docker-compose.yml to Kubernetes manifests
- Use Helm charts for templating
- Configure horizontal pod autoscaling
- Set up ingress for external access
- Implement proper secrets management

**Development Workflow:**

- Story 1.7 will add CI/CD to build and push Docker images
- Epic 2+ will run Alembic migrations in Docker
- Tests will run in isolated Docker containers

### Project Structure Notes

**Alignment with Architecture:**

- Docker Compose orchestration matches architecture requirements
- Full stack development environment with one command
- Hot reload for rapid development
- Service isolation with custom network
- Persistent data with named volumes

**Files Created/Modified:**

```
ai-interviewer/
├── docker-compose.yml          # MODIFIED - Added backend and frontend services
├── .env                        # MODIFIED - Changed DB_HOST to postgres
├── .gitignore                  # MODIFIED - Added Docker entries
├── backend/
│   ├── Dockerfile              # NEW - Backend container definition
│   └── .dockerignore           # NEW - Exclude files from Docker build
├── frontend/
│   ├── Dockerfile.dev          # NEW - Frontend dev container definition
│   ├── .dockerignore           # NEW - Exclude node_modules
│   └── vite.config.ts          # MODIFIED - Added Docker polling for HMR
└── README.md                   # MODIFIED - Added Docker setup instructions
```

**No Conflicts Detected:**

- PostgreSQL service from Story 1.3 remains unchanged
- Backend code from Stories 1.2, 1.4 works in container
- Frontend from Story 1.1 works in container with vite.config update
- Alembic from Story 1.5 can run in backend container

**Integration Preview (Epic 2 - User Authentication):**

```bash
# Run migrations in Docker
docker-compose exec backend alembic upgrade head

# Create first user via API
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### References

- [Source: _bmad-output/architecture.md - Section "Infrastructure & Deployment"]
- [Source: _bmad-output/architecture.md - Section "Starter Template Evaluation -
  Docker Compose Setup"]
- [Source: _bmad-output/project-context.md - Infrastructure configuration]
- [Source:
  _bmad-output/implementation-artifacts/1-3-configure-postgresql-database-with-docker-compose.md
  - PostgreSQL service]
- [Source:
  _bmad-output/implementation-artifacts/1-4-integrate-backend-with-database-using-sqlalchemy.md
  - Backend connection]

## Dev Agent Record

### Agent Model Used

_To be filled by Dev agent during implementation_

### Debug Log References

_To be filled by Dev agent during implementation_

### Completion Notes List

_To be filled by Dev agent during implementation_

- [ ] docker-compose.yml updated with all three services
- [ ] backend/Dockerfile created
- [ ] frontend/Dockerfile.dev created
- [ ] frontend/vite.config.ts updated for Docker hot reload
- [ ] .env updated with DB_HOST=postgres
- [ ] .gitignore updated with Docker entries
- [ ] All services build successfully
- [ ] All services start with docker-compose up
- [ ] Frontend accessible at localhost:3000
- [ ] Backend accessible at localhost:8000
- [ ] Health check confirms database connection
- [ ] Hot reload works for backend and frontend
- [ ] Data persists across container restarts
- [ ] README.md updated with Docker instructions

### File List

_To be filled by Dev agent during implementation_

Expected files created/modified:

- `docker-compose.yml` (modify - add backend and frontend services)
- `backend/Dockerfile` (create)
- `backend/.dockerignore` (create)
- `frontend/Dockerfile.dev` (create)
- `frontend/.dockerignore` (create)
- `frontend/vite.config.ts` (modify - add Docker config)
- `.env` (modify - change DB_HOST to postgres)
- `.gitignore` (modify - add Docker entries)
- `README.md` (modify - add Docker setup section)
