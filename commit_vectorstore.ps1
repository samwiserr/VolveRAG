# Script to commit vectorstore with Git LFS
# Run this script to add the pre-built vectorstore to the repository

Write-Host "=== Committing Vectorstore with Git LFS ===" -ForegroundColor Cyan
Write-Host ""

# Check if Git LFS is installed
try {
    $lfsVersion = git lfs version 2>&1
    Write-Host "✓ Git LFS found: $lfsVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git LFS not found. Please install Git LFS first." -ForegroundColor Red
    Write-Host "  Download from: https://git-lfs.github.com/" -ForegroundColor Yellow
    exit 1
}

# Initialize Git LFS (if not already done)
Write-Host ""
Write-Host "Initializing Git LFS..." -ForegroundColor Yellow
git lfs install
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to initialize Git LFS" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Git LFS initialized" -ForegroundColor Green

# Add .gitattributes
Write-Host ""
Write-Host "Adding .gitattributes..." -ForegroundColor Yellow
git add .gitattributes
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to add .gitattributes" -ForegroundColor Red
    exit 1
}
Write-Host "✓ .gitattributes added" -ForegroundColor Green

# Add .gitignore
Write-Host ""
Write-Host "Adding .gitignore..." -ForegroundColor Yellow
git add .gitignore
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to add .gitignore" -ForegroundColor Red
    exit 1
}
Write-Host "✓ .gitignore added" -ForegroundColor Green

# Check if vectorstore exists
Write-Host ""
if (-not (Test-Path "advanced_rag/data/vectorstore/chroma.sqlite3")) {
    Write-Host "✗ Vectorstore not found at advanced_rag/data/vectorstore/" -ForegroundColor Red
    Write-Host "  Please build the index first:" -ForegroundColor Yellow
    Write-Host "  cd advanced_rag" -ForegroundColor Yellow
    Write-Host "  python -m src.main --build-index --documents-path ../spwla_volve-main" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Vectorstore found" -ForegroundColor Green

# Add vectorstore with Git LFS
Write-Host ""
Write-Host "Adding vectorstore files (tracked by Git LFS)..." -ForegroundColor Yellow
git add advanced_rag/data/vectorstore/
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to add vectorstore" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Vectorstore files added" -ForegroundColor Green

# Check status
Write-Host ""
Write-Host "Files to be committed:" -ForegroundColor Cyan
git status --short | Select-Object -First 20

# Commit
Write-Host ""
$response = Read-Host "Commit these changes? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host ""
    Write-Host "Committing..." -ForegroundColor Yellow
    git commit -m "feat: Add pre-built vectorstore via Git LFS for immediate use

- Track vectorstore files with Git LFS (handles large binary files)
- Include ChromaDB vectorstore with embeddings
- Include all cache files (section_index, petro_params, eval_params, facts)
- Include lexical store for BM25 search
- Users can now use the app without building the index"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to commit" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Changes committed" -ForegroundColor Green
    
    # Push
    Write-Host ""
    $pushResponse = Read-Host "Push to GitHub? (y/n)"
    if ($pushResponse -eq "y" -or $pushResponse -eq "Y") {
        Write-Host ""
        Write-Host "Pushing to GitHub (this may take a while for large files)..." -ForegroundColor Yellow
        git push origin main
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Failed to push" -ForegroundColor Red
            Write-Host "  You may need to push manually: git push origin main" -ForegroundColor Yellow
            exit 1
        }
        Write-Host ""
        Write-Host "=== SUCCESS! ===" -ForegroundColor Green
        Write-Host "Vectorstore has been committed and pushed to GitHub." -ForegroundColor Cyan
        Write-Host "Users can now use the app without building the index." -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "Changes committed locally. Push manually with: git push origin main" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "Changes staged but not committed. Commit manually when ready." -ForegroundColor Yellow
}

