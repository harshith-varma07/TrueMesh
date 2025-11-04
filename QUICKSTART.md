# 🚀 TrueMesh - Quick Start Guide

Get TrueMesh Provider Intelligence up and running in minutes!

## ⚡ Prerequisites

- **Python 3.12+** installed
- **PostgreSQL 15+** running
- **Redis 7+** running (optional but recommended)

## 📦 Installation (5 minutes)

### 1. Setup Virtual Environment

```powershell
# Navigate to project
cd C:\Users\Admin\Documents\GitHub\TrueMesh

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment

The `.env` file is already configured with defaults. Update if needed:

```properties
# Database (Update with your credentials)
DATABASE_URL=postgresql://truemesh:truemesh_password@localhost:5432/truemesh

# Security (CHANGE THESE IN PRODUCTION!)
SECRET_KEY=dev-secret-key-change-in-production-12345678
ENCRYPTION_KEY=dev-encryption-key-change-in-production-12345678
```

### 4. Setup Database

```powershell
# Option 1: Use Alembic migrations (recommended)
alembic upgrade head

# Option 2: Use initialization script
python scripts/init_db.py
```

### 5. Initialize ML Models

```powershell
python scripts/init_models.py
```

### 6. Verify Installation

```powershell
python scripts/verify_backend.py
```

You should see:
```
✅ All tests passed! Backend is ready.
```

## 🎯 Running the Application

### Development Mode

```powershell
# Start the server
python main.py
```

The server will start on `http://localhost:8000`

### Access API Documentation

Open your browser and visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🧪 Test the API

### 1. Create a Provider

```powershell
# Using PowerShell
$body = @{
    registration_number = "MCI123456"
    name = "Dr. Test Provider"
    provider_type = "doctor"
    specialization = "Cardiology"
    email = "doctor@example.com"
    phone = "+919876543210"
    city = "Mumbai"
    state = "Maharashtra"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/providers/" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### 2. Check Provider Status

```powershell
# Replace {workflow_id} with the ID from previous response
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/providers/{provider_id}" `
    -Method GET
```

### 3. Verify Provider

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/verification/" `
    -Method POST `
    -ContentType "application/json" `
    -Body '{"provider_id": "your-provider-id", "verification_type": "full"}' | ConvertFrom-Json
```

### 4. Check Admin Dashboard

```powershell
# Get system overview
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/admin/stats/overview" `
    -Method GET | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

## 🎨 Frontend

### Access the Frontend

1. Open `frontend/index.html` in your browser, or
2. Use a simple HTTP server:

```powershell
# Using Python HTTP server
cd frontend
python -m http.server 8080
```

Then visit: http://localhost:8080

### Frontend Pages

- **Home**: `index.html` - Landing page with features
- **Login**: `login.html` - Authentication page
- **Dashboard**: `dashboard.html` - Main dashboard
- **Providers**: `providers.html` - Provider management
- **Verification**: `verification.html` - Verification tools
- **Profile**: `profile.html` - User profile and settings
- **About**: `about.html` - About TrueMesh

## 🔍 Verify Components

### Check Blockchain

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/admin/provenance/chain-info" `
    -Method GET | ConvertFrom-Json
```

### Check Agents

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/admin/agents/status" `
    -Method GET | ConvertFrom-Json
```

### Check ML Models

```powershell
# Confidence scoring
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/verification/{provider_id}/confidence-score" `
    -Method POST | ConvertFrom-Json

# Fraud detection
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/verification/{provider_id}/fraud-check" `
    -Method POST | ConvertFrom-Json
```

## 📊 Sample Workflow

### Complete Provider Registration Flow

```powershell
# 1. Create provider
$createResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/providers/" `
    -Method POST `
    -ContentType "application/json" `
    -Body (@{
        registration_number = "DOC789012"
        name = "Dr. Sample Physician"
        provider_type = "doctor"
        specialization = "General Medicine"
        email = "sample@example.com"
        phone = "+919123456789"
        city = "Delhi"
        state = "Delhi"
    } | ConvertTo-Json) | ConvertFrom-Json

$workflowId = $createResponse.workflow_id
Write-Host "Workflow ID: $workflowId"

# 2. Wait for processing (agents work asynchronously)
Start-Sleep -Seconds 5

# 3. Check orchestrator status
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/admin/orchestrator/status" `
    -Method GET | ConvertFrom-Json

# 4. Get provider details
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/providers/$providerId" `
    -Method GET | ConvertFrom-Json

# 5. Get provenance history
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/providers/$providerId/history" `
    -Method GET | ConvertFrom-Json

# 6. Get scores
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/providers/$providerId/scores" `
    -Method GET | ConvertFrom-Json
```

## 🐛 Troubleshooting

### Database Connection Error

```powershell
# Check PostgreSQL is running
Get-Service -Name postgresql*

# Test connection
psql -U truemesh -d truemesh -h localhost
```

### Port Already in Use

```powershell
# Change port in .env
PORT=8001

# Or kill process using port 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
```

### Redis Connection Error

Redis is optional for basic functionality. To disable:
```powershell
# Comment out Redis-related code or set
REDIS_URL=redis://localhost:6379/0  # Will fail gracefully
```

### ML Models Not Loading

```powershell
# Reinitialize models
python scripts/init_models.py

# Check model directory
dir data/models
```

## 📚 Next Steps

1. **Read Full Documentation**: Check `BACKEND_README.md`
2. **Explore API**: Visit http://localhost:8000/docs
3. **Test Frontend**: Open `frontend/index.html`
4. **Add More Providers**: Use the API to add test data
5. **Monitor System**: Check `/api/v1/admin/stats/overview`

## 🔐 Security Notes

**⚠️ For Development Only**

The default `.env` file contains development credentials. 

**Before Production:**
1. Generate secure keys:
   ```powershell
   # Generate random secret
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
2. Update `SECRET_KEY` and `ENCRYPTION_KEY`
3. Use strong database credentials
4. Enable HTTPS
5. Configure CORS properly
6. Set `ENV=production` and `DEBUG=false`

## 📞 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: See `BACKEND_README.md`
- **API Docs**: http://localhost:8000/docs

## ✅ Success Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Database initialized
- [ ] ML models initialized
- [ ] Backend verification passed
- [ ] Server running on port 8000
- [ ] API docs accessible
- [ ] Test provider created
- [ ] Frontend accessible

---

**Congratulations! 🎉 TrueMesh is ready to use!**
