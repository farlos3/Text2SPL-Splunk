@echo off
setlocal

REM Windows Docker Management Script

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker first.
    exit /b 1
)

if "%1"=="build" goto build
if "%1"=="dev" goto dev
if "%1"=="dev-daemon" goto dev_daemon
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="clean" goto clean
if "%1"=="status" goto status
if "%1"=="shell-backend" goto shell_backend
if "%1"=="shell-frontend" goto shell_frontend
goto help

:build
echo [INFO] Building Docker images...
docker-compose -f docker-compose.dev.yml build --no-cache
echo [INFO] Build completed!
goto end

:dev
echo [INFO] Starting services in development mode...
docker-compose -f docker-compose.dev.yml up --build
goto end

:dev_daemon
echo [INFO] Starting services in development mode (background)...
docker-compose -f docker-compose.dev.yml up --build -d
echo [INFO] Services started! Check logs with: docker-dev.bat logs
goto end

:stop
echo [INFO] Stopping services...
docker-compose -f docker-compose.dev.yml down
echo [INFO] Services stopped!
goto end

:restart
echo [INFO] Restarting services...
call :stop
call :dev_daemon
goto end

:logs
if "%2"=="" (
    docker-compose -f docker-compose.dev.yml logs -f
) else (
    docker-compose -f docker-compose.dev.yml logs -f %2
)
goto end

:clean
echo [WARNING] Cleaning up Docker containers and volumes...
docker-compose -f docker-compose.dev.yml down -v
docker system prune -f
echo [INFO] Cleanup completed!
goto end

:status
echo [INFO] Service status:
docker-compose -f docker-compose.dev.yml ps
goto end

:shell_backend
echo [INFO] Opening shell in backend container...
docker-compose -f docker-compose.dev.yml exec backend bash
goto end

:shell_frontend
echo [INFO] Opening shell in frontend container...
docker-compose -f docker-compose.dev.yml exec frontend sh
goto end

:help
echo Usage: %0 ^<command^>
echo.
echo Commands:
echo   build          Build Docker images
echo   dev            Start in development mode (foreground)
echo   dev-daemon     Start in development mode (background)
echo   stop           Stop all services
echo   restart        Restart all services
echo   logs [service] View logs for all services or specific service
echo   clean          Stop services and clean up containers/volumes
echo   status         Show service status
echo   shell-backend  Open shell in backend container
echo   shell-frontend Open shell in frontend container
echo   help           Show this help message
echo.
echo Examples:
echo   %0 dev                # Start development environment
echo   %0 logs backend       # View backend logs
echo   %0 shell-backend      # SSH into backend container

:end
endlocal
