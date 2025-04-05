#!/bin/bash

# Create root project folder
mkdir lastbite-ai && cd lastbite-ai

# Frontend structure
mkdir -p frontend/public
mkdir -p frontend/src/components
mkdir -p frontend/src/pages
mkdir -p frontend/src/utils
touch frontend/src/App.js
touch frontend/src/index.js
touch frontend/README.md

# Backend structure
mkdir -p backend/api
mkdir -p backend/models
mkdir -p backend/services
mkdir -p backend/utils
touch backend/main.py
touch backend/requirements.txt
touch backend/README.md

# ML model & notebook
mkdir -p ml_model
touch ml_model/expiry_model.py
touch ml_model/train_model.ipynb
touch ml_model/README.md

# Firebase config
mkdir -p firebase/functions
touch firebase/firebase.json
touch firebase/functions/index.js

# Docs and assets
mkdir -p docs
mkdir -p assets/images

# Git essentials
touch .gitignore
touch README.md
touch LICENSE

# Init Git
git init

echo "✅ LastBite AI project structure created!"