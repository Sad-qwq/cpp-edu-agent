# Start Backend
Write-Host "Starting Backend..." -ForegroundColor Green
$backendProcess = Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "& .venv\Scripts\Activate.ps1; cd backend; uvicorn main:app --reload" -PassThru

# Start Frontend
Write-Host "Starting Frontend..." -ForegroundColor Green
$frontendProcess = Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -PassThru

Write-Host "Both services started in new windows." -ForegroundColor Cyan
