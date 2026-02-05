# DevOps Project Startup Script
# Run this when you start developing

Write-Host "Starting DevOps Project..." -ForegroundColor Green

# Start backend (rebuild containers)
Write-Host "Building and starting backend containers..." -ForegroundColor Cyan
docker-compose down
docker-compose up -d --build

# docker-compose up -d (if no changes to backend)

Write-Host "Waiting for backend to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 8

# Start frontend
Write-Host "Starting frontend development server..." -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "Backend: http://localhost:5000" -ForegroundColor Green
pnpm dev
