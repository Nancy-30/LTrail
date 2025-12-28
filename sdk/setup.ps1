# PowerShell script to install the SDK in development mode

Write-Host "Installing LTrail SDK in development mode..." -ForegroundColor Green

# Navigate to SDK directory
Set-Location $PSScriptRoot

# Upgrade pip
python -m pip install --upgrade pip

# Install the SDK in editable mode
pip install -e .

Write-Host "SDK installed successfully!" -ForegroundColor Green
Write-Host "You can now run: python examples/competitor_selection.py" -ForegroundColor Yellow

