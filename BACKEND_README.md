# TrueMesh Provider Intelligence - Backend Documentation

## 🎯 Overview

TrueMesh is a **production-ready, fully automated Python-based healthcare provider data validation and provenance platform** designed for Indian payers and TPAs. It uses a multi-agent AI architecture with blockchain-based provenance tracking to ensure data integrity and trust.

## 🏗️ Architecture

### Multi-Agent System
The platform consists of 9 specialized AI agents working in coordination:

1. **OrchestratorAgent** - Coordinates all agent activities and workflows
2. **DataVerificationAgent** - Validates provider data against multiple sources
3. **ConfidenceScoringAgent** - ML-based trust and confidence assessment
4. **FraudDetectionAgent** - Anomaly detection and fraud identification
5. **ProvenanceLedgerAgent** - Blockchain-based immutable record tracking
6. **FederatedPublisherAgent** - Multi-node federation and data synchronization
7. **PITLAgent** - Provider-Initiated Trust Loop for self-service updates
8. **ComplianceManagerAgent** - Policy enforcement and compliance checking
9. **AgentRegistry** - Agent discovery and lifecycle management

### Core Technologies
- **Python 3.12+** with asyncio for concurrent processing
- **FastAPI** for high-performance REST API
- **PostgreSQL 15+** with SQLAlchemy ORM
- **Redis 7+** for caching and sessions
- **Scikit-learn** for ML models
- **Custom Blockchain** for provenance

## 📁 Project Structure

```
TrueMesh/
├── app/
│   ├── agents/              # AI agents (9 agents)
│   │   ├── orchestrator.py
│   │   ├── data_verification.py
│   │   ├── confidence_scoring.py
│   │   ├── fraud_detection.py
│   │   ├── provenance_ledger.py
│   │   ├── federated_publisher.py
│   │   ├── pitl.py
│   │   ├── compliance_manager.py
│   │   └── registry.py
│   ├── api/                 # FastAPI endpoints
│   │   ├── main.py
│   │   └── endpoints/
│   │       ├── providers.py
│   │       ├── verification.py
│   │       ├── admin.py
│   │       ├── pitl.py
│   │       └── federation.py
│   ├── blockchain/          # Blockchain implementation
│   │   └── core.py          # Complete blockchain with PoW
│   ├── ml/                  # Machine Learning models
│   │   └── models.py        # Confidence & Fraud ML models
│   ├── models/              # SQLAlchemy database models
│   │   └── __init__.py      # 8 complete models
│   ├── core/                # Core utilities
│   │   ├── agent_base.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── logging.py
│   └── security/            # Security utilities
│       └── security.py
├── frontend/                # Frontend (HTML/CSS/JS)
├── migrations/              # Alembic database migrations
├── scripts/                 # Initialization scripts
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── alembic.ini             # Alembic configuration
└── .env                    # Environment configuration
```

## 🗄️ Database Models

Complete SQLAlchemy models with relationships:

1. **Provider** - Healthcare provider records
2. **ProviderVerification** - Verification results from multiple sources
3. **ConfidenceScore** - ML-generated trust scores
4. **FraudAlert** - Fraud detection alerts
5. **ProvenanceRecord** - Blockchain provenance records
6. **ComplianceRecord** - Compliance check results
7. **FederationNode** - Federation network nodes
8. **AuditLog** - System audit trail

## 🤖 Machine Learning

### Confidence Scoring Model
- **Algorithm**: Random Forest Classifier (150 estimators)
- **Features** (10):
  - Verification count & confidence
  - Data consistency score
  - Historical pattern score
  - External validation count
  - Source diversity score
  - Time since registration
  - Update frequency score
  - Compliance score
  - Fraud risk score (inverted)
- **Output**: Confidence probability (0-1) with feature importance

### Fraud Detection Model
- **Algorithm**: Isolation Forest (150 estimators)
- **Features** (10):
  - Claim frequency & amount patterns
  - Approval rate
  - Duplicate claims ratio
  - Verification inconsistency
  - Location anomaly score
  - Billing pattern score
  - Time pattern score
  - Relationship network score
- **Output**: Fraud probability + risk level (low/medium/high/critical)

## ⛓️ Blockchain

Complete blockchain implementation with:
- **Transaction** data structure with hash calculation
- **MerkleTree** for transaction verification
- **Block** with proof of work mining
- **Blockchain** with full chain validation
- Configurable difficulty level
- Chain integrity verification
- Transaction querying by provider

## 🚀 Getting Started

### Prerequisites
```bash
# Required services
- PostgreSQL 15+
- Redis 7+
- Python 3.12+
```

### Installation

1. **Clone and navigate**
```bash
cd TrueMesh
```

2. **Create virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
# Edit .env file with your database credentials
DATABASE_URL=postgresql://user:password@localhost:5432/truemesh
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here
```

5. **Initialize database**
```bash
# Run migrations
alembic upgrade head

# Or use initialization script
python scripts/init_db.py
```

6. **Initialize ML models**
```bash
python scripts/init_models.py
```

7. **Initialize complete system**
```bash
# Runs all initialization steps
python scripts/init_system.py
```

### Running the Application

**Development**
```bash
python main.py
```

**Production with Uvicorn**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Access API Documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## 📡 API Endpoints

### Provider Endpoints (`/api/v1/providers`)
- `POST /` - Create provider & initiate verification
- `GET /{id}` - Get provider details
- `PUT /{id}` - Update provider information
- `DELETE /{id}` - Delete provider (soft delete)
- `GET /` - List providers with filters
- `GET /{id}/history` - Get provenance history
- `POST /{id}/verify` - Trigger verification
- `GET /{id}/scores` - Get confidence & fraud scores

### Verification Endpoints (`/api/v1/verification`)
- `POST /` - Verify provider data
- `GET /{id}/status` - Get verification status
- `POST /{id}/fraud-check` - Run fraud detection
- `POST /{id}/confidence-score` - Calculate confidence
- `POST /{id}/compliance-check` - Check compliance

### PITL Endpoints (`/api/v1/pitl`)
- `POST /update` - Provider-initiated update
- `POST /challenge` - Challenge existing data
- `GET /challenges/{id}` - Get challenge status
- `GET /challenges` - List pending challenges
- `POST /challenges/{id}/resolve` - Resolve challenge

### Federation Endpoints (`/api/v1/federation`)
- `POST /sync` - Sync to federation
- `GET /status` - Get federation status
- `POST /health-check` - Check node health
- `GET /updates` - Get federation updates

### Admin Endpoints (`/api/v1/admin`)
- `GET /agents/status` - Get all agent status
- `GET /orchestrator/status` - Orchestrator status
- `GET /provenance/chain-info` - Blockchain info
- `POST /provenance/verify` - Verify provenance
- `POST /compliance/exception` - Grant exception
- `GET /compliance/exceptions` - List exceptions
- `GET /stats/overview` - System overview

## 🔐 Security Features

### Authentication & Authorization
- JWT-based authentication
- Token expiration and refresh
- Role-based access control (RBAC)

### Data Protection
- AES-256 encryption for sensitive data
- PII masking in logs
- Email and phone masking utilities
- Secure password hashing (bcrypt)

### Audit Trail
- Complete audit logging
- Event tracking with timestamps
- User and agent activity tracking
- Resource access logging

## 🔄 Workflows

### Provider Registration Workflow
1. Provider data submitted via API
2. Orchestrator creates verification workflow
3. Data Verification Agent validates against sources
4. Confidence Scoring Agent calculates trust score
5. Fraud Detection Agent checks for anomalies
6. Provenance Ledger records transaction
7. Compliance Manager checks policies
8. Results stored and provider notified

### Verification Workflow
1. Trigger verification (manual or scheduled)
2. Multi-source data validation (MCI, Insurance Registry)
3. Confidence score calculation
4. Fraud detection analysis
5. Blockchain record creation
6. Compliance validation
7. Federation sync (if enabled)

### PITL (Provider-Initiated Trust Loop)
1. Provider submits update or challenge
2. PITL Agent validates request
3. Verification workflow triggered
4. Challenge review process
5. Resolution and notification
6. Provenance update

## 📊 Monitoring & Logging

### Structured Logging
- JSON format for production
- Rich console output for development
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Component-specific loggers

### Health Checks
- API health endpoint
- Database connection status
- Redis connectivity
- Agent status monitoring

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_agents.py
```

## 🔧 Configuration

### Environment Variables

**Application**
- `ENV` - Environment (development/production)
- `DEBUG` - Debug mode (true/false)
- `PORT` - Server port (default: 8000)

**Security**
- `SECRET_KEY` - JWT secret key
- `ENCRYPTION_KEY` - Data encryption key
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration (default: 30)

**Database**
- `DATABASE_URL` - PostgreSQL connection string
- `DATABASE_ECHO` - SQL query logging (true/false)
- `REDIS_URL` - Redis connection string

**ML Models**
- `MODEL_STORAGE_PATH` - Model storage directory
- `CONFIDENCE_THRESHOLD` - Confidence threshold (default: 0.7)
- `FRAUD_THRESHOLD` - Fraud threshold (default: 0.8)

**Blockchain**
- `BLOCKCHAIN_NETWORK` - Network type (local/testnet/mainnet)
- `GENESIS_HASH` - Genesis block hash

**Agents**
- `MAX_CONCURRENT_AGENTS` - Max concurrent agents (default: 10)
- `AGENT_TIMEOUT_SECONDS` - Agent timeout (default: 300)

**Federation**
- `NODE_ID` - Node identifier
- `FEDERATION_NODES` - Comma-separated node URLs

## 📈 Performance

### Scalability
- Async/await for concurrent processing
- Database connection pooling (20 connections)
- Redis caching for frequently accessed data
- Background task processing

### Optimization
- Index optimization on database tables
- Query optimization with proper joins
- ML model caching
- Blockchain validation caching

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check PostgreSQL is running
# Verify DATABASE_URL in .env
# Run migrations: alembic upgrade head
```

**Agent Not Starting**
```bash
# Check logs for errors
# Verify all dependencies installed
# Check Redis connectivity
```

**ML Models Not Loading**
```bash
# Initialize models: python scripts/init_models.py
# Check MODEL_STORAGE_PATH directory exists
```

## 📝 Development

### Adding a New Agent
1. Create agent class in `app/agents/`
2. Inherit from `BaseAgent`
3. Implement `get_agent_type()` and `process_task()`
4. Register in `app/agents/registry.py`

### Adding a New Endpoint
1. Create endpoint file in `app/api/endpoints/`
2. Define FastAPI router
3. Add to `app/api/main.py`

### Adding a New Model
1. Define model in `app/models/__init__.py`
2. Create migration: `alembic revision --autogenerate -m "description"`
3. Apply migration: `alembic upgrade head`

## 🤝 Contributing

1. Follow PEP 8 style guide
2. Add type hints to all functions
3. Write docstrings for all classes and methods
4. Add tests for new features
5. Update documentation

## 📄 License

Proprietary - All rights reserved

## 👥 Support

For issues or questions:
- Create an issue in the repository
- Contact the development team

---

**Built with ❤️ for Indian Healthcare**
