#!/bin/bash

# Root directory
mkdir lastbite-source && cd lastbite-source

# ---------------------
# Frontend
# ---------------------
mkdir -p frontend/src/{components,pages,utils}
echo "// App entry point" > frontend/src/App.js
echo "// Index file" > frontend/src/index.js
echo "// API utility functions" > frontend/src/utils/api.js
echo "# Frontend README" > frontend/README.md

# ---------------------
# Backend
# ---------------------
mkdir -p backend/{routes,ml,services}
echo "# Main backend entry point" > backend/main.py
echo "# API routes" > backend/routes/api.py
echo "# Expiry model logic" > backend/ml/expiry_model.py
echo "# GPT generator logic" > backend/ml/gpt_generator.py
echo "# Utility functions" > backend/services/utils.py
echo "# Backend dependencies" > backend/requirements.txt
echo "# Backend README" > backend/README.md

# ---------------------
# Shared
# ---------------------
mkdir -p assets/images
mkdir docs

# ---------------------
# Project Essentials
# ---------------------
echo "# LastBite AI" > README.md
echo "# Ignore files" > .gitignore
echo "# License information" > LICENSE

# Git init
git init

echo "✅ LastBite AI MVP structure created successfully!"