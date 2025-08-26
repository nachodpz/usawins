# =============== Rick&Nacho — Publicar en GitHub (PowerShell) ===============
# DÓNDE: ejecuta este .ps1 dentro de la carpeta del proyecto (USAwins)
# QUÉ HACE: configura Git, crea .gitignore, hace commit, añade remoto y push

# 1) Comprobar que Git existe
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git no está instalado o no está en PATH." -ForegroundColor Red
    Write-Host "Instálalo desde https://git-scm.com/download/win y vuelve a ejecutar el script."
    exit 1
}

# 2) Mostrar carpeta actual
$here = Get-Location
Write-Host "📂 Carpeta actual: $here"

# 3) Config global (si falta)
$userName = (git config --global user.name) 2>$null
$userEmail = (git config --global user.email) 2>$null

if (-not $userName) {
    $userName = Read-Host "Escribe tu nombre para Git (ej. Nacho)"
    git config --global user.name "$userName"
}
if (-not $userEmail) {
    $userEmail = Read-Host "Escribe tu email de GitHub"
    git config --global user.email "$userEmail"
}

Write-Host "✅ Git user: $((git config --global user.name))  |  email: $((git config --global user.email))"

# 4) Inicializar repo si no existe
if (-not (Test-Path ".git")) {
    git init | Out-Null
    Write-Host "🆕 Repo Git inicializado."
} else {
    Write-Host "ℹ️ Repo Git ya existía."
}

# 5) Crear .gitignore básico si no existe
$gitignorePath = ".gitignore"
if (-not (Test-Path $gitignorePath)) {
@"
# ---- Python / FastAPI ----
__pycache__/
*.pyc
.env
.venv/
venv/
.env.*
# IDEs
.vscode/
.idea/
# OS
.DS_Store
Thumbs.db
"@ | Out-File $gitignorePath -Encoding utf8
    Write-Host "📝 .gitignore creado."
}

# 6) Asegurar archivos mínimos
if (-not (Test-Path "app.py")) {
    Write-Host "⚠️ No encuentro app.py en esta carpeta. Asegúrate de estar en la carpeta USAwins." -ForegroundColor Yellow
}

# 7) Añadir y crear commit
git add . | Out-Null
$hasChanges = git status --porcelain
if ($hasChanges) {
    git commit -m "USAwins V1" | Out-Null
    Write-Host "✅ Commit creado: USAwins V1"
} else {
    Write-Host "ℹ️ No hay cambios nuevos para commitear."
}

# 8) Rama principal = main
git branch -M main 2>$null
Write-Host "🌿 Rama actual: main"

# 9) Configurar remoto
$currentOrigin = (git remote get-url origin) 2>$null
if (-not $currentOrigin) {
    $repoUrl = Read-Host "Pega la URL del repo en GitHub (ej. https://github.com/TU_USUARIO/usawins.git)"
    git remote add origin $repoUrl
    Write-Host "🔗 Remoto 'origin' añadido: $repoUrl"
} else {
    Write-Host "🔗 Remoto 'origin' ya existe: $currentOrigin"
    $change = Read-Host "¿Quieres cambiarlo? (s/n)"
    if ($change -eq "s") {
        $repoUrl = Read-Host "Nueva URL del repo"
        git remote set-url origin $repoUrl
        Write-Host "🔗 Remoto actualizado: $repoUrl"
    }
}

# 10) Push
Write-Host "⬆️  Haciendo push a GitHub (te pedirá usuario y token si es la primera vez)…"
git push -u origin main
if ($LASTEXITCODE -eq 0) {
    Write-Host "🎉 ¡Listo! Código publicado en GitHub." -ForegroundColor Green
} else {
    Write-Host "❌ Hubo un error en el push. Revisa el mensaje de arriba." -ForegroundColor Red
    Write-Host "Pista: si pide contraseña, usa un Personal Access Token de GitHub (scope: repo)." -ForegroundColor Yellow
}
# ============================================================================ #
