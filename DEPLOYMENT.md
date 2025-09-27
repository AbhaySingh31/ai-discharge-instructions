# 🚀 Deployment Guide

## Quick Start for GitHub

### 1. Push to GitHub
```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit: AI Discharge Instructions System with Q&A"

# Add remote repository
git remote add origin https://github.com/yourusername/ai-discharge-instructions.git

# Push to GitHub
git push -u origin main
```

### 2. Set Up OpenRouter API Key
1. Sign up at [OpenRouter.ai](https://openrouter.ai)
2. Get your free API key
3. Create `.env` file in backend directory:
```bash
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DATABASE_URL=sqlite:///./discharge_instructions.db
DEBUG=True
LOG_LEVEL=INFO
APP_NAME="AI Discharge Instructions"
```

### 3. Local Development Setup
```bash
# Backend setup
cd backend
pip install -r requirements.txt
python seed_database.py
python simple_migration.py
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend setup (new terminal)
cd frontend
npm install
npm start
```

### 4. Access Application
- **Main App**: http://localhost:3000
- **Patient Q&A**: http://localhost:3000/patients/P000001/qa
- **API Docs**: http://localhost:8000/docs

## Production Deployment

### Environment Variables
```bash
# Production .env
OPENROUTER_API_KEY=your_production_api_key
DATABASE_URL=postgresql://user:password@host:port/database
DEBUG=False
LOG_LEVEL=WARNING
CORS_ORIGINS=["https://yourdomain.com"]
```

### Docker Deployment
```dockerfile
# Dockerfile for backend
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Vercel/Netlify Frontend
```bash
# Build command
npm run build

# Output directory
build/
```

## Features Overview

### ✅ Core Features
- **106 Patients** with complete medical data
- **AI Q&A System** with PII protection
- **Real-time Search** and live updates
- **Prescription Management**
- **Discharge Instructions** generation

### 🔒 Security Features
- **PII Protection**: No personal data exposed to AI
- **Medical Safety**: Anti-hallucination measures
- **Audit Trail**: Complete patient activity tracking
- **HIPAA-Compliant**: Enterprise-level privacy

### 🤖 AI Integration
- **OpenRouter**: Free Llama 3.2 model
- **LLM-Only Responses**: No fallback content
- **Safety Validation**: Medical fact checking
- **Confidence Scoring**: Response reliability

## Testing

### Test Patient Data
- **Patient IDs**: P000001 to P000106
- **Sample**: Anthony Griffin (P000001)
- **Medications**: Prednisone, Lisinopril, Metformin

### API Testing
```bash
cd backend
python test_patients.py        # Test patient endpoints
python test_medication_qa.py   # Test Q&A system
python test_openrouter.py      # Test AI integration
```

## Support

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: See README.md for detailed setup
- **API Reference**: http://localhost:8000/docs
