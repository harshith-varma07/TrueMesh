# TrueMesh Provider Intelligence - Architecture

## System Overview

TrueMesh Provider Intelligence is an autonomous healthcare provider data validation and provenance platform designed for Indian payers and TPAs. The system uses multi-agent orchestration to automate provider verification, fraud detection, confidence scoring, and compliance checking.

## Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────────┐
│                              Client Layer                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐         │
│  │  Web Apps  │  │  Mobile    │  │  Partner   │  │   Admin    │         │
│  │            │  │   Apps     │  │   Systems  │  │  Dashboard │         │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘         │
└────────┼───────────────┼───────────────┼───────────────┼────────────────┘
         │               │               │               │
         └───────────────┴───────────────┴───────────────┘
                               │
         ┌─────────────────────┴──────────────────────┐
         │                                             │
┌────────▼─────────────────────────────────────────────▼─────────────────┐
│                         API Gateway (FastAPI)                           │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐             │
│  │ Provider │ Verifi-  │   PITL   │ Federa-  │  Admin   │             │
│  │   APIs   │ cation   │   APIs   │  tion    │  APIs    │             │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘             │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────┴──────────────────────────────────────────┐
│                    Multi-Agent Orchestration Layer                       │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │                    Orchestrator Agent                           │     │
│  │  • Workflow Coordination   • Task Routing   • Agent Lifecycle  │     │
│  └────────────┬───────────────────────────────────────────────────┘     │
│               │                                                          │
│  ┌────────────┴──────────────────────────────────────────────────────┐  │
│  │                       Specialized Agents                          │  │
│  │                                                                    │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐ │  │
│  │  │  Data Verification│  │ Confidence Scoring│  │ Fraud Detection│ │  │
│  │  │  • MCI Registry   │  │  • ML Scoring     │  │ • Anomaly Det. │ │  │
│  │  │  • IRDAI Data     │  │  • Random Forest  │  │ • Iso. Forest  │ │  │
│  │  │  • Gov Database   │  │  • Trust Metrics  │  │ • Duplicate Det│ │  │
│  │  └──────────────────┘  └──────────────────┘  └────────────────┘ │  │
│  │                                                                    │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐ │  │
│  │  │Provenance Ledger │  │Federated Publisher│  │  PITL Agent    │ │  │
│  │  │  • Blockchain     │  │  • Multi-node Sync│  │ • Provider Upd.│ │  │
│  │  │  • Hash Chain     │  │  • Consensus      │  │ • Challenges   │ │  │
│  │  │  • Merkle Tree    │  │  • Replication    │  │ • Verification │ │  │
│  │  └──────────────────┘  └──────────────────┘  └────────────────┘ │  │
│  │                                                                    │  │
│  │  ┌──────────────────────────────────────────────────────────────┐ │  │
│  │  │              Compliance Manager Agent                        │ │  │
│  │  │  • Policy Enforcement  • Auto Resolution  • Exceptions       │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────┴──────────────────────────────────────────┐
│                          Data & Storage Layer                            │
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │  PostgreSQL  │  │    Redis     │  │  ML Models   │  │ Blockchain │  │
│  │              │  │              │  │              │  │   Ledger   │  │
│  │ • Providers  │  │ • Queue      │  │ • Confidence │  │ • Blocks   │  │
│  │ • Verif.     │  │ • Cache      │  │ • Fraud Det. │  │ • Txns     │  │
│  │ • Scores     │  │ • Sessions   │  │ • Trained    │  │ • Hashes   │  │
│  │ • Compliance │  │              │  │              │  │            │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘  │
└───────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Multi-Agent System

#### Orchestrator Agent
- **Purpose**: Central coordinator for all workflows
- **Responsibilities**:
  - Route tasks to appropriate agents
  - Manage workflow execution
  - Handle task dependencies and sequencing
  - Monitor agent health and performance

#### Data Verification Agent
- **Purpose**: Multi-source data validation
- **Data Sources**:
  - MCI (Medical Council of India) Registry
  - IRDAI Insurance Registry
  - Government Databases
- **Features**:
  - Concurrent verification
  - Cross-reference validation
  - Confidence scoring per source

#### Confidence Scoring Agent
- **Purpose**: ML-based trust and confidence assessment
- **Algorithm**: Random Forest Classifier
- **Features**:
  - 6-feature ML model
  - Automated retraining
  - Component scores (verification, consistency, historical, external)

#### Fraud Detection Agent
- **Purpose**: Detect fraudulent provider entries
- **Algorithm**: Isolation Forest (Anomaly Detection)
- **Checks**:
  - Duplicate detection
  - Data inconsistency analysis
  - Fake pattern recognition
  - ML-based anomaly detection

#### Provenance Ledger Agent
- **Purpose**: Immutable record tracking
- **Technology**: Blockchain-style hash chain
- **Features**:
  - SHA-256 hashing
  - Merkle tree integrity
  - Proof of work
  - PII sanitization

#### Federated Publisher Agent
- **Purpose**: Decentralized data synchronization
- **Features**:
  - Multi-node publishing
  - Health monitoring
  - Sync conflict resolution
  - Network status tracking

#### PITL Agent (Provider-Initiated Trust Loop)
- **Purpose**: Secure provider-initiated updates
- **Features**:
  - Update request handling
  - Challenge submission
  - Verification workflow
  - Trust maintenance

#### Compliance Manager Agent
- **Purpose**: Policy enforcement and exception handling
- **Policies**:
  - Data completeness
  - Data accuracy
  - Verification freshness
  - Fraud risk thresholds
  - Confidence thresholds
  - PII protection
- **Features**:
  - Automated compliance checking
  - Auto-resolution where possible
  - Exception management

### 2. API Layer

Built with FastAPI, providing REST endpoints for:

#### Provider Operations
- Create, read, update, delete providers
- List with filtering and pagination
- Provenance history retrieval

#### Verification Operations
- Multi-source verification
- Fraud detection
- Confidence scoring
- Compliance checking

#### PITL Operations
- Update requests
- Challenge submission and resolution
- Challenge status tracking

#### Federation Operations
- Data synchronization
- Network status
- Health checks

#### Admin Operations
- Agent status monitoring
- Blockchain information
- Compliance exception management
- System statistics

### 3. Data Layer

#### PostgreSQL Database
- **Tables**:
  - `providers`: Healthcare provider data
  - `provider_verifications`: Verification records
  - `confidence_scores`: ML confidence scores
  - `fraud_alerts`: Fraud detection alerts
  - `provenance_records`: Blockchain ledger
  - `compliance_records`: Compliance checks
  - `federation_nodes`: Network nodes
  - `audit_logs`: System audit trail

#### Redis Cache
- Task queues
- Session management
- Temporary data caching
- Rate limiting

#### ML Models
- Confidence scoring model (Random Forest)
- Fraud detection model (Isolation Forest)
- Stored in pickle format
- Versioned and tracked

## Workflows

### Provider Registration Workflow

```
1. Client submits provider data
   ↓
2. Orchestrator receives request
   ↓
3. Data Verification Agent validates data
   ↓
4. Fraud Detection Agent checks for fraud
   ↓
5. Confidence Scoring Agent calculates scores
   ↓
6. Provenance Ledger Agent records transaction
   ↓
7. Compliance Manager Agent checks policies
   ↓
8. Result returned to client
```

### Provider Update Workflow (via PITL)

```
1. Provider submits update request
   ↓
2. PITL Agent validates request
   ↓
3. Data Verification Agent re-validates
   ↓
4. Confidence Scoring Agent recalculates
   ↓
5. Provenance Ledger Agent records change
   ↓
6. Federated Publisher Agent syncs to network
   ↓
7. Update confirmed to provider
```

### Fraud Investigation Workflow

```
1. Trigger fraud check
   ↓
2. Fraud Detection Agent performs checks
   ↓
3. Data Verification Agent cross-references
   ↓
4. Compliance Manager Agent reviews violations
   ↓
5. Results logged and flagged if necessary
```

## Security Architecture

### Authentication & Authorization
- JWT-based authentication (configurable)
- Role-based access control
- API key management for external systems

### Data Protection
- Encryption at rest (configurable)
- PII masking in provenance ledger
- Secure communication between services
- Rate limiting

### Audit & Compliance
- Complete audit trail in database
- Immutable provenance chain
- Compliance policy enforcement
- Exception tracking

## Scalability

### Horizontal Scaling
- Multiple API server instances behind load balancer
- Distributed agent execution
- PostgreSQL read replicas
- Redis cluster for caching

### Performance Optimization
- Async/await throughout
- Concurrent agent execution
- Database connection pooling
- Response caching

## Deployment

### Docker Compose (Development/Small Production)
- Single-host deployment
- PostgreSQL + Redis + Application
- Simple scaling with replicas

### Kubernetes (Large Production)
- Multi-host deployment
- Auto-scaling
- High availability
- Service mesh integration

## Monitoring & Observability

### Health Checks
- Application health endpoint
- Database connectivity
- Agent status monitoring
- Federation network health

### Logging
- Structured JSON logging
- Centralized log aggregation ready
- Multiple log levels
- Agent-specific logging

### Metrics (Future)
- Prometheus integration
- Grafana dashboards
- Alert management
- Performance tracking

## Technology Stack

- **Language**: Python 3.12+
- **Framework**: FastAPI
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **ML**: scikit-learn, numpy
- **Blockchain**: Custom hash chain implementation
- **Container**: Docker, Docker Compose
- **Orchestration**: Kubernetes (optional)

## Future Enhancements

1. **Advanced ML Models**
   - Deep learning for confidence scoring
   - NLP for data validation
   - Reinforcement learning for optimization

2. **Enhanced Blockchain**
   - Distributed consensus
   - Smart contracts
   - Cross-chain integration

3. **Real-time Dashboard**
   - Live monitoring
   - Interactive analytics
   - Alert management

4. **Mobile Applications**
   - Provider mobile app
   - Admin mobile dashboard

5. **Advanced Integration**
   - More registry integrations
   - Government API connections
   - International standards support

## Conclusion

TrueMesh Provider Intelligence provides a robust, scalable, and secure platform for automated healthcare provider data validation. The multi-agent architecture ensures modularity and extensibility, while the blockchain-style provenance system guarantees data integrity and auditability.
