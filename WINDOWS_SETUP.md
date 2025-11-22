# Windows Setup Guide for pdf_agent

## Prerequisites

1. **Docker Desktop for Windows**

   - Download and install from: https://www.docker.com/products/docker-desktop
   - Ensure WSL 2 backend is enabled
   - Start Docker Desktop before running any commands

2. **Python 3.13** (for local development)

   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

3. **Make** (optional, for using Makefile)
   - Install via Chocolatey: `choco install make`
   - Or use nmake (comes with Visual Studio)
   - Or use PowerShell scripts directly

## Quick Start

### Using Docker (Recommended)

1. **Start the application:**

   ```powershell
   docker-compose up pdf-agent
   ```

   Or with Make:

   ```powershell
   make -f Makefile.windows run
   ```

2. **Build the container:**

   ```powershell
   docker-compose build pdf-agent
   ```

   Or with Make:

   ```powershell
   make -f Makefile.windows build
   ```

3. **Run tests:**
   ```powershell
   docker-compose run --rm pdf-agent-test
   ```
   Or with Make:
   ```powershell
   make -f Makefile.windows test
   ```

### Local Development (Without Docker)

1. **Set up Python virtual environment:**

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. **Install dependencies:**

   ```powershell
   pip install -r requirements.txt
   ```

3. **Set environment variables:**

   ```powershell
   $env:DB_HOST="localhost"
   $env:DB_NAME="postgres"
   $env:DB_PASSWORD="postgres"
   $env:DB_PORT="5432"
   $env:DB_USERNAME="postgres"
   $env:ENVIRONMENT="development"
   $env:LOG_LEVEL="DEBUG"
   ```

4. **Start PostgreSQL** (using Docker):

   ```powershell
   docker-compose up pdf-agent-postgres
   ```

5. **Run the application:**
   ```powershell
   .\bin\boot.ps1
   ```
   Or directly:
   ```powershell
   uvicorn --reload --host 0.0.0.0 --port 8000 pdf_agent.app:app
   ```

## Available Commands

### PowerShell Scripts

- `.\bin\boot.ps1` - Start the application (waits for DB and runs migrations)
- `.\bin\refreeze.ps1` - Rebuild container and update requirements.txt
- `.\bin\boot.bat` - Batch wrapper for boot.ps1
- `.\bin\refreeze.bat` - Batch wrapper for refreeze.ps1

### Make Commands (using Makefile.windows)

```powershell
make -f Makefile.windows clean        # Remove cache directories
make -f Makefile.windows destroy      # Stop and remove containers
make -f Makefile.windows lint         # Run linting checks
make -f Makefile.windows refreeze     # Update dependencies
make -f Makefile.windows run          # Run in Docker
make -f Makefile.windows run-local    # Run locally
make -f Makefile.windows build        # Build Docker image
make -f Makefile.windows test         # Run tests
make -f Makefile.windows coverage     # Run tests with coverage
make -f Makefile.windows help         # Show available commands
```

### Docker Compose Commands

```powershell
docker-compose up pdf-agent              # Start the service
docker-compose up pdf-agent-postgres     # Start only the database
docker-compose down                              # Stop all services
docker-compose build                             # Build all services
docker-compose run --rm pdf-agent-test   # Run tests
docker-compose logs -f pdf-agent         # View logs
```

## Environment Variables

Create a `.env` file in the root directory (optional, for local development):

```
DB_HOST=localhost
DB_NAME=postgres
DB_PASSWORD=postgres
DB_PORT=5432
DB_USERNAME=postgres
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

## Troubleshooting

### PowerShell Execution Policy Error

If you get an execution policy error, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Docker Not Found

Make sure Docker Desktop is running. Check with:

```powershell
docker --version
docker-compose --version
```

### Port Already in Use

If port 8200 or 5432 is already in use, modify `compose.yml` to use different ports:

```yaml
ports:
  - "8201:80" # Change 8200 to 8201
```

### Database Connection Issues

Ensure PostgreSQL container is running:

```powershell
docker-compose ps
docker-compose logs pdf-agent-postgres
```

## Accessing the Application

Once running, access the application at:

- **Main service:** http://localhost:8200
- **Health check:** http://localhost:8200/health
- **API docs:** http://localhost:8200/docs

## Notes

- The original Linux shell scripts (`boot.sh`, `refreeze.sh`) are still available for WSL or Linux environments
- Windows-specific scripts (`*.ps1`, `*.bat`) provide equivalent functionality
- Docker containers work identically on Windows and Linux
- For WSL users: You can use the original Makefile and `.sh` scripts directly
