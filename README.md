# TrueMesh Provider Intelligence

> **Automated Healthcare Provider Data Validation and Provenance Platform for Indian Payers and TPAs**

A fully autonomous, production-ready Python-based system that validates, scores, detects fraud, records provenance, and publishes verified healthcare provider data using multi-agent orchestration.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        TrueMesh Provider Intelligence                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌───────────────────┐                                              │
│  │   Orchestrator    │ ──────────── Coordinates all workflows       │
│  │      Agent        │                                              │
│  └────────┬──────────┘                                              │
│           │                                                          │
│           ├─── Data Verification Agent (Multi-source validation)    │
│           ├─── Confidence Scoring Agent (ML-based trust scoring)    │
│           ├─── Fraud Detection Agent (Duplicate/fake detection)     │
│           ├─── Provenance Ledger Agent (Blockchain-style records)   │
│           ├─── Federated Publisher Agent (Decentralized updates)    │
│           ├─── PITL Agent (Provider-initiated updates)              │
│           └─── Compliance Manager Agent (Policy enforcement)        │
│                                                                       │
├─────────────────────────────────────────────────────────────────────┤
│  FastAPI REST API │ PostgreSQL │ Redis │ ML Models │ Blockchain    │
└─────────────────────────────────────────────────────────────────────┘
```

## ✨ Features

### Multi-Agent Orchestration
- **Orchestrator Agent**: Coordinates workflows and manages agent lifecycle
- **Data Verification Agent**: Validates provider data from MCI, IRDAI, and other registries
- **Confidence Scoring Agent**: ML-based trust scoring using Random Forest
- **Fraud Detection Agent**: Anomaly detection using Isolation Forest
- **Provenance Ledger Agent**: Immutable blockchain-style record tracking
- **Federated Publisher Agent**: Decentralized data synchronization
- **PITL Agent**: Provider-Initiated Trust Loop for secure updates
- **Compliance Manager Agent**: Automated policy enforcement and exception handling

### Autonomous Workflows
- ✅ Provider registration and verification
- ✅ Multi-source data validation
- ✅ Automated confidence scoring
- ✅ Real-time fraud detection
- ✅ Immutable provenance tracking
- ✅ Federation synchronization
- ✅ Compliance checking with auto-resolution

### Security & Privacy
- 🔐 JWT authentication
- 🔐 PII masking and encryption
- 🔐 Encryption at rest
- 🔐 Blockchain-style data integrity
- 🔐 Rate limiting

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+ (for local development)
- PostgreSQL 15+
- Redis 7+

### One-Command Deployment

```bash
# Clone the repository
git clone https://github.com/harshith-varma07/TrueMesh.git
cd TrueMesh

# Copy environment configuration
cp .env.example .env

# Edit .env and set your secret keys
# SECRET_KEY and ENCRYPTION_KEY must be changed in production!

# Start all services with Docker Compose
docker-compose up -d

# Check services are running
docker-compose ps

# View logs
docker-compose logs -f app
```

The application will be available at:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the application
python main.py
```

## 📚 API Documentation

### Provider Operations

#### Create Provider
```bash
POST /api/v1/providers/
Content-Type: application/json

{
  "registration_number": "MCI123456",
  "name": "Dr. Amit Sharma",
  "provider_type": "doctor",
  "specialization": "Cardiology",
  "email": "amit.sharma@example.com",
  "phone": "+919876543210",
  "city": "Mumbai",
  "state": "Maharashtra"
}
```

#### Get Provider
```bash
GET /api/v1/providers/{provider_id}
```

#### Update Provider
```bash
PUT /api/v1/providers/{provider_id}
Content-Type: application/json

{
  "email": "new.email@example.com",
  "phone": "+919876543211"
}
```

#### List Providers
```bash
GET /api/v1/providers/?status=verified&provider_type=doctor&city=Mumbai
```

#### Get Provider History (Provenance Chain)
```bash
GET /api/v1/providers/{provider_id}/history
```

### Verification Operations

#### Verify Provider
```bash
POST /api/v1/verification/
Content-Type: application/json

{
  "provider_id": "uuid-here",
  "verification_type": "full"
}
```

#### Fraud Check
```bash
POST /api/v1/verification/{provider_id}/fraud-check
```

#### Calculate Confidence Score
```bash
POST /api/v1/verification/{provider_id}/confidence-score
```

#### Compliance Check
```bash
POST /api/v1/verification/{provider_id}/compliance-check
```

### PITL (Provider-Initiated Trust Loop)

#### Submit Update Request
```bash
POST /api/v1/pitl/update
Content-Type: application/json

{
  "provider_id": "uuid-here",
  "updates": {
    "email": "updated@example.com",
    "phone": "+919999999999"
  }
}
```

#### Submit Challenge
```bash
POST /api/v1/pitl/challenge
Content-Type: application/json

{
  "provider_id": "uuid-here",
  "challenge_data": {
    "field": "specialization",
    "current_value": "General Medicine",
    "correct_value": "Cardiology"
  },
  "challenge_reason": "My specialization was incorrectly recorded"
}
```

#### Get Challenge Status
```bash
GET /api/v1/pitl/challenges/{challenge_id}
```

### Federation Operations

#### Sync to Federation
```bash
POST /api/v1/federation/sync
Content-Type: application/json

{
  "provider_data": {...},
  "operation": "update"
}
```

#### Get Federation Status
```bash
GET /api/v1/federation/status
```

#### Federation Health Check
```bash
POST /api/v1/federation/health-check
```

### Admin Operations

#### Get Agent Status
```bash
GET /api/v1/admin/agents/status
```

#### Get Blockchain Info
```bash
GET /api/v1/admin/provenance/chain-info
```

#### Verify Provenance Record
```bash
POST /api/v1/admin/provenance/verify?block_hash=xxx&data_hash=yyy
```

#### Grant Compliance Exception
```bash
POST /api/v1/admin/compliance/exception
Content-Type: application/json

{
  "provider_id": "uuid-here",
  "policy_type": "verification_freshness",
  "reason": "Provider in remote area with limited connectivity",
  "duration_days": 90
}
```

#### System Overview
```bash
GET /api/v1/admin/stats/overview
```

## 🧠 Machine Learning Models

### Confidence Scoring Model
- **Algorithm**: Random Forest Classifier
- **Features**: 
  - Verification count
  - Average verification confidence
  - Data consistency
  - Historical score
  - External validations
  - Source diversity
- **Output**: Confidence score (0-1)

### Fraud Detection Model
- **Algorithm**: Isolation Forest (Anomaly Detection)
- **Features**:
  - Data completeness
  - Pattern consistency
  - Registration format validity
  - Contact validity
  - Location validity
  - Verification diversity
- **Output**: Fraud score (0-1) and risk level

### Model Training
Models are automatically initialized with synthetic training data. To retrain with real data:

```python
from app.agents.confidence_scoring import ConfidenceScoringAgent
from app.agents.fraud_detection import FraudDetectionAgent

# Retrain confidence scoring model
scoring_agent = ConfidenceScoringAgent()
scoring_agent.retrain_model(training_data)

# Models are automatically saved to MODEL_STORAGE_PATH
```

## 🔗 Provenance Blockchain

The system implements a blockchain-style immutable ledger for provider data:

### Features
- SHA-256 hash chain
- Merkle tree for transaction integrity
- Proof of work (configurable difficulty)
- PII sanitization for ledger records
- Complete audit trail

### Verify Chain Integrity
```bash
curl -X GET http://localhost:8000/api/v1/admin/provenance/chain-info
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Application
ENV=production|development
PORT=8000

# Security (MUST CHANGE IN PRODUCTION)
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# ML Thresholds
CONFIDENCE_THRESHOLD=0.7
FRAUD_THRESHOLD=0.8

# Agent Configuration
MAX_CONCURRENT_AGENTS=10
AGENT_TIMEOUT_SECONDS=300

# Federation
NODE_ID=node-1
FEDERATION_NODES=http://node2:8000,http://node3:8000
```

## 📊 Monitoring & Logging

### Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Admin health
curl http://localhost:8000/api/v1/admin/health
```

### Logs
- **Format**: Structured JSON logging
- **Level**: Configurable via LOG_LEVEL
- **Output**: stdout (captured by Docker)

```bash
# View application logs
docker-compose logs -f app

# View all logs
docker-compose logs -f
```

## 🧪 Testing

```bash
# Run tests (once implemented)
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_agents.py::test_orchestrator
```

## 🏛️ Database Schema

Key tables:
- `providers`: Healthcare provider data
- `provider_verifications`: Verification records
- `confidence_scores`: ML confidence scores
- `fraud_alerts`: Fraud detection alerts
- `provenance_records`: Blockchain ledger
- `compliance_records`: Compliance checks
- `federation_nodes`: Federation network
- `audit_logs`: System audit trail

### Run Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🚢 Deployment

### Production Deployment

1. **Update configuration**:
   ```bash
   # Generate secure keys
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # Update .env with production values
   ENV=production
   DEBUG=false
   SECRET_KEY=<generated-key>
   ENCRYPTION_KEY=<generated-key>
   DATABASE_URL=<production-db-url>
   ```

2. **Deploy with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

3. **Or deploy to Kubernetes**:
   ```bash
   # Create Kubernetes manifests (to be added)
   kubectl apply -f k8s/
   ```

### Scaling

The system is designed for horizontal scaling:
- **API Servers**: Multiple FastAPI instances behind load balancer
- **Agent Workers**: Distributed agent execution
- **Database**: PostgreSQL with read replicas
- **Cache**: Redis cluster
- **Federation**: Multi-node deployment

## 🔒 Security Considerations

### Production Checklist
- [ ] Change SECRET_KEY and ENCRYPTION_KEY
- [ ] Use strong database passwords
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Backup strategy
- [ ] Disaster recovery plan

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Medical Council of India (MCI) for registry data
- IRDAI for insurance provider data
- Open Agent Platform for agent orchestration framework
- FastAPI for the excellent web framework
- scikit-learn for ML capabilities

## 📞 Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/harshith-varma07/TrueMesh/issues
- Email: support@truemesh.ai (example)

## 🗺️ Roadmap

- [ ] Real-time dashboard
- [ ] Advanced ML models (deep learning)
- [ ] Blockchain network consensus
- [ ] Mobile application
- [ ] Integration with more registries
- [ ] Advanced analytics and reporting
- [ ] Multi-tenancy support
- [ ] GraphQL API

---

**Built with ❤️ for the Indian Healthcare Ecosystem**
