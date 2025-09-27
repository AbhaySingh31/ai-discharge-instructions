# AI Agent for Personalized Patient Discharge Instructions - Setup Guide

## Quick Start

This guide will help you set up and run the AI-powered personalized patient discharge instructions system.

## Prerequisites

- **Python 3.9+** (for backend)
- **Node.js 16+** (for frontend)
- **OpenAI API Key** (for AI features)
- **Git** (for version control)

## Installation Steps

### 1. Clone and Navigate to Project

```bash
cd C:\Users\YoYo\CascadeProjects\ai-discharge-instructions
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Environment Configuration
```bash
# Copy the example environment file
copy .env.example .env

# Edit .env file and add your OpenAI API key
# OPENAI_API_KEY=your_openai_api_key_here
```

#### Initialize Database
```bash
# The database will be created automatically when you first run the application
# SQLite is used by default for development
```

#### Run Backend Server
```bash
# From the backend directory
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### 3. Frontend Setup

#### Install Node.js Dependencies
```bash
cd ../frontend
npm install
```

#### Install Additional Dependencies
```bash
npm install @tailwindcss/forms
```

#### Run Frontend Development Server
```bash
npm start
```

The frontend will be available at: `http://localhost:3000`

## Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=sqlite:///./discharge_instructions.db

# OpenAI (Required for AI features)
OPENAI_API_KEY=your_openai_api_key_here

# Security
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True

# HIPAA Compliance
ENABLE_AUDIT_LOGGING=True
ENABLE_ENCRYPTION=True
```

#### Frontend
The frontend automatically connects to the backend at `http://localhost:8000`

## Getting Your OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

## Testing the Application

### 1. Access the Application
- Open your browser and go to `http://localhost:3000`
- You should see the AI Discharge Instructions dashboard

### 2. Create a Test Patient
- Click "Add Patient" or navigate to `/patients/new`
- Fill in the patient information form
- Submit to create your first patient

### 3. Add Medical Records
- Navigate to the patient detail page
- Add medical records and discharge notes
- This data will be used to generate personalized instructions

### 4. Generate AI Instructions
- Once you have patient data and medical records
- Click "Generate Instructions" to create personalized discharge instructions
- Test the interactive Q&A system

## Project Structure

```
ai-discharge-instructions/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration and security
│   │   ├── models/         # Data models
│   │   └── services/       # Business logic and AI services
│   ├── requirements.txt    # Python dependencies
│   └── .env.example       # Environment template
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Application pages
│   │   └── services/      # API services
│   ├── package.json       # Node.js dependencies
│   └── tailwind.config.js # Tailwind CSS configuration
└── README.md              # Project documentation
```

## Key Features

### For Healthcare Providers
- **Patient Management**: Create and manage patient records
- **Medical Records**: Track diagnoses, treatments, and procedures
- **AI-Generated Instructions**: Automatically create personalized discharge instructions
- **HIPAA Compliance**: Built-in security and audit logging

### For Patients
- **Patient Portal**: Secure access to discharge instructions
- **Interactive Q&A**: Ask questions about discharge instructions
- **Print-Friendly**: Easy-to-print discharge instructions
- **Mobile Responsive**: Access from any device

### AI Features
- **Personalized Instructions**: Tailored to patient's specific condition and history
- **Natural Language**: Easy-to-understand, non-medical language
- **Comprehensive Coverage**: Medications, activities, diet, follow-up care
- **Interactive Support**: Answer patient questions in real-time

## API Endpoints

### Patient Management
- `POST /api/v1/patients/` - Create patient
- `GET /api/v1/patients/` - List patients
- `GET /api/v1/patients/{patient_id}` - Get patient details

### Medical Records
- `POST /api/v1/medical-records/` - Create medical record
- `GET /api/v1/medical-records/{patient_id}` - Get patient's medical records

### Discharge Instructions
- `POST /api/v1/generate-instructions/{patient_id}` - Generate AI instructions
- `POST /api/v1/ask-question/{patient_id}` - Ask questions about instructions

## Security Features

### HIPAA Compliance
- **Data Encryption**: Sensitive data encrypted at rest
- **Audit Logging**: All access and modifications logged
- **Access Controls**: Role-based access to patient data
- **Data Retention**: Automatic compliance with retention policies

### Security Measures
- **JWT Authentication**: Secure API access
- **Input Validation**: Prevent injection attacks
- **Rate Limiting**: Prevent abuse
- **HTTPS Ready**: SSL/TLS support for production

## Troubleshooting

### Common Issues

#### Backend Won't Start
- Check Python version (3.9+ required)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check if port 8000 is available

#### Frontend Won't Start
- Check Node.js version (16+ required)
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

#### AI Features Not Working
- Verify OpenAI API key is set in `.env`
- Check API key has sufficient credits
- Review backend logs for error messages

#### Database Issues
- Delete the SQLite file and restart: `rm discharge_instructions.db`
- Check file permissions in the backend directory

### Getting Help

1. Check the application logs in the terminal
2. Review the API documentation at `http://localhost:8000/docs`
3. Ensure all environment variables are properly set
4. Verify network connectivity for OpenAI API calls

## Production Deployment

### Backend
- Use PostgreSQL instead of SQLite
- Set `DEBUG=False` in environment
- Use proper secret keys and encryption
- Configure reverse proxy (nginx)
- Set up SSL certificates

### Frontend
- Build for production: `npm run build`
- Serve static files with web server
- Configure proper API endpoints
- Enable HTTPS

### Security
- Regular security updates
- Monitor audit logs
- Backup encryption keys
- Implement proper user authentication

## Next Steps

1. **Customize the AI prompts** in `backend/app/services/ai_agent.py`
2. **Add user authentication** for multi-user support
3. **Integrate with EHR systems** for real patient data
4. **Deploy to production** with proper security measures
5. **Add more AI features** like risk assessment or medication interactions

## Support

For technical support or questions about this implementation:
- Review the code documentation
- Check the API documentation at `/docs`
- Examine the audit logs for security events
- Test with sample data before using real patient information

---

**Important**: This is a demonstration system. For production use in healthcare environments, ensure proper HIPAA compliance, security audits, and regulatory approval.
