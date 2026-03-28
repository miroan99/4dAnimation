# Set up the development environment
Set-Location $PSScriptRoot\..

Write-Host "Creating virtual environment..."
python -m venv .venv

Write-Host "Activating virtual environment..."
.\.venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Setup complete. Run 'scripts\run.ps1' to start."
