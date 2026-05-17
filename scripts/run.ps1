# Local development runner (Windows PowerShell)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (-not (Test-Path "venv")) {
    python -m venv venv
}

& .\venv\Scripts\Activate.ps1
pip install -q -r requirements-dev.txt

if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
    Write-Host "Created .env from .env.example — review before production use."
}

python app.py
