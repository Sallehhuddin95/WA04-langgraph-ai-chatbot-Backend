# Starts the backend dev server. Run from the backend repo root.
# Loads .env into process env, then serves app.main:app on port 8000.
$env:PYTHONPATH = 'src'
$envVars = @{}
Get-Content -LiteralPath '.env' | ForEach-Object {
  if ($_ -match '^\s*([^#\s=]+)\s*=\s*(.*)\s*$') {
    $envVars[$Matches[1]] = $Matches[2].Trim()
  }
}
foreach ($k in $envVars.Keys) {
  Set-Item -Path ('Env:' + $k) -Value $envVars[$k]
}
python -m uvicorn app.main:app --port 8000
