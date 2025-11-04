# TrueMesh API Documentation

## Overview

The TrueMesh Provider Intelligence platform exposes a comprehensive REST API with **30+ endpoints** across **9 modules**, providing access to all 12 AI agents and their capabilities.

**Base URL:** `http://localhost:8000/api/v1/`  
**API Docs:** `http://localhost:8000/docs` (Swagger UI)  
**Alternative Docs:** `http://localhost:8000/redoc` (ReDoc)

---

## API Modules

### 1. Providers API (`/providers`)

Manage healthcare provider records (hospitals, doctors, clinics).

**Endpoints:**
- `POST /providers/` - Create new provider
- `GET /providers/{provider_id}` - Get provider details
- `PUT /providers/{provider_id}` - Update provider
- `DELETE /providers/{provider_id}` - Delete provider
- `GET /providers/` - List providers with pagination
- `GET /providers/{provider_id}/score` - Get confidence score
- `POST /providers/{provider_id}/verify` - Trigger verification

---

### 2. Verification API (`/verification`)

Provider data verification and validation.

**Endpoints:**
- `POST /verification/verify` - Verify provider data
- `GET /verification/{verification_id}` - Get verification status
- `GET /verification/provider/{provider_id}` - Get verification history
- `POST /verification/batch` - Batch verification

---

### 3. PITL API (`/pitl`)

Provider-Initiated Trust Loop for self-service updates.

**Endpoints:**
- `POST /pitl/update` - Provider initiates update
- `GET /pitl/status/{update_id}` - Check update status
- `GET /pitl/history/{provider_id}` - Update history
- `POST /pitl/approve` - Approve update
- `POST /pitl/reject` - Reject update

---

### 4. Federation API (`/federation`)

Multi-node federation and data sharing.

**Endpoints:**
- `GET /federation/nodes` - List federation nodes
- `POST /federation/sync` - Sync with federation nodes
- `GET /federation/health-check` - Check node health
- `POST /federation/publish` - Publish to federation

---

### 5. Admin API (`/admin`)

System administration and monitoring.

**Endpoints:**
- `GET /admin/agents/status` - Get all agents status
- `GET /admin/orchestrator/status` - Orchestrator status
- `GET /admin/provenance/chain-info` - Blockchain info
- `POST /admin/provenance/verify` - Verify blockchain integrity
- `POST /admin/compliance/exception` - Create compliance exception
- `GET /admin/compliance/exceptions` - List exceptions
- `GET /admin/stats/overview` - System overview stats
- `GET /admin/health` - Admin health check

---

### 6. Analytics API (`/analytics`) ⭐ NEW

Dashboard metrics, reports, and visualizations.

**Endpoints:**

#### Overview & Dashboards
```http
POST /analytics/generate
```
Generate any analytics type with filters and export format.

**Request Body:**
```json
{
  "analytics_type": "overview",
  "filters": {"state": "Maharashtra"},
  "export_format": "json"
}
```

**Analytics Types:**
- `overview` - System overview with summary metrics
- `geospatial` - Regional distribution and maps
- `trends` - Historical trends and patterns
- `confidence_distribution` - Score distribution analysis
- `anomaly_report` - Fraud and anomaly reports

```http
GET /analytics/overview?start_date=2025-10-01&end_date=2025-11-01
```
Get system overview dashboard.

**Response:**
```json
{
  "analytics_type": "overview",
  "data": {
    "summary": {
      "total_providers": 15247,
      "verified_providers": 12876,
      "verification_rate": 0.844
    },
    "confidence_metrics": {
      "average_confidence": 0.782,
      "high_confidence_count": 9823
    },
    "fraud_metrics": {
      "total_alerts": 234,
      "critical_alerts": 12
    }
  }
}
```

#### Geospatial Analysis
```http
GET /analytics/geospatial?state=Maharashtra&metric=provider_count
```
Regional maps, heatmaps, and city clusters with coordinates.

#### Trend Analysis
```http
GET /analytics/trends?days=30
```
Historical trends with AQI-style data quality index.

#### Confidence Distribution
```http
GET /analytics/confidence-distribution?provider_type=hospital
```
Statistical analysis of confidence scores.

#### Anomaly Reports
```http
GET /analytics/anomaly-report?risk_level=critical
```
Comprehensive fraud and anomaly detection reports.

#### Data Quality Index
```http
GET /analytics/data-quality-index?provider_id=PRV-12345
```
Calculate 0-100 data quality score based on:
- Completeness (30%)
- Accuracy (25%)
- Consistency (20%)
- Timeliness (15%)
- Uniqueness (10%)

#### Export
```http
GET /analytics/export/{analytics_type}?format=pdf
```
Export analytics in JSON, CSV, or PDF format.

---

### 7. Entity Resolution API (`/entity-resolution`) ⭐ NEW

Deduplication and entity matching using fuzzy logic.

#### Resolve Entities
```http
POST /entity-resolution/resolve
```
Identify and merge duplicate provider records.

**Request Body:**
```json
{
  "providers": [
    {
      "name": "Apollo Hospital",
      "city": "Chennai",
      "registration_number": "REG-001"
    },
    {
      "name": "Apollo Hosptial",
      "city": "Chennai",
      "registration_number": "REG001"
    }
  ],
  "similarity_threshold": 0.85
}
```

**Response:**
```json
{
  "canonical_entities": [
    {
      "canonical_id": "ENT-ABC123",
      "name": "Apollo Hospital",
      "member_count": 2,
      "member_ids": ["1", "2"],
      "sources": ["manual"],
      "resolved_at": "2025-11-04T12:00:00Z"
    }
  ],
  "duplicate_groups": [
    {
      "canonical_id": "ENT-ABC123",
      "members": ["1", "2"],
      "member_count": 2
    }
  ],
  "entity_count": 1,
  "duplicate_count": 1,
  "resolution_stats": {
    "input_records": 2,
    "unique_entities": 1,
    "deduplication_rate": 0.5
  }
}
```

#### Check Duplicates
```http
POST /entity-resolution/check-duplicates
```
Quick duplicate check without creating canonical entities.

#### Calculate Similarity
```http
POST /entity-resolution/similarity
```
Calculate similarity score (0-1) between two providers.

**Request:**
```json
{
  "provider_a": {"name": "Apollo Hospital", "city": "Chennai"},
  "provider_b": {"name": "Apollo Hosptial", "city": "Chennai"}
}
```

**Response:**
```json
{
  "similarity_score": 0.9234,
  "is_duplicate": true,
  "threshold": 0.85,
  "field_scores": {
    "name": 0.95,
    "registration": 0.88,
    "phone": 0.00,
    "email": 0.00,
    "address": 0.92
  }
}
```

#### Statistics
```http
GET /entity-resolution/stats
```
Resolution statistics and metrics.

---

### 8. Data Ingestion API (`/data-ingestion`) ⭐ NEW

Multi-source data collection and normalization.

#### Ingest Data
```http
POST /data-ingestion/ingest
```
Pull data from multiple sources.

**Request:**
```json
{
  "source_type": "all",
  "filters": {
    "state": "Maharashtra",
    "city": "Mumbai"
  }
}
```

**Source Types:**
- `health_facilities` - Hospital/clinic data (NHM)
- `doctors` - Doctor registry (NMC)
- `accreditation` - Accreditation data (NABH)
- `business_entities` - Business registry (MCA)
- `all` - All sources

**Response:**
```json
{
  "ingested_count": 125,
  "by_source": {
    "health_facilities": 45,
    "doctors": 67,
    "accreditation": 8,
    "business_entities": 5
  },
  "ingestion_stats": {
    "sources_queried": 4,
    "sources_succeeded": 4
  }
}
```

#### List Sources
```http
GET /data-ingestion/sources
```
Available data sources with status.

#### Health Facilities
```http
GET /data-ingestion/health-facilities?state=Maharashtra&city=Mumbai
```

#### Doctors
```http
GET /data-ingestion/doctors?state=Tamil Nadu&specialization=Cardiology
```

#### Accreditation
```http
GET /data-ingestion/accreditation?state=Karnataka
```

#### Business Entities
```http
GET /data-ingestion/business-entities?state=Delhi
```

#### Geocode Address
```http
POST /data-ingestion/geocode
```
Convert address to latitude/longitude.

**Request:**
```json
{
  "address": "Apollo Hospital, Greams Lane, Chennai"
}
```

**Response:**
```json
{
  "address": "Apollo Hospital, Greams Lane, Chennai",
  "latitude": 13.0522,
  "longitude": 80.2537,
  "geocoded": true
}
```

#### Statistics
```http
GET /data-ingestion/stats
```
Ingestion statistics and performance metrics.

---

### 9. Model Lifecycle API (`/model-lifecycle`) ⭐ NEW

ML model monitoring, drift detection, and retraining.

#### Manage Lifecycle
```http
POST /model-lifecycle/manage
```
Generic model lifecycle management.

**Actions:**
- `monitor` - Monitor performance
- `detect_drift` - Detect drift
- `evaluate_performance` - Evaluate metrics
- `trigger_retrain` - Start retraining
- `version_control` - Manage versions
- `rollback` - Rollback model

#### Monitor Models
```http
GET /model-lifecycle/monitor?model_name=fraud_detection
```
Model health, metrics, and drift status.

**Response:**
```json
{
  "action": "monitor",
  "model_name": "fraud_detection",
  "result": {
    "models": {
      "fraud_detection": {
        "status": "attention_needed",
        "version": "2.1.0",
        "metrics": {
          "accuracy": 0.923,
          "precision": 0.887,
          "recall": 0.945,
          "f1_score": 0.915
        },
        "drift_detected": true,
        "drift_score": 0.067,
        "recommendation": "Consider retraining"
      }
    }
  }
}
```

#### Detect Drift
```http
GET /model-lifecycle/drift?model_name=all
```
Data drift and concept drift detection.

#### Evaluate Performance
```http
GET /model-lifecycle/performance?model_name=confidence_scoring
```
Performance evaluation vs baseline.

#### Trigger Retraining
```http
POST /model-lifecycle/retrain
```
Start model retraining job.

**Request:**
```json
{
  "model_name": "fraud_detection",
  "reason": "performance_degradation",
  "training_period": "last_90_days",
  "notify_email": "admin@truemesh.io"
}
```

**Response:**
```json
{
  "status": "initiated",
  "training_job_id": "TRAIN-20251104120000",
  "estimated_completion": "2025-11-04T15:00:00Z",
  "stages": [
    {"stage": "data_preparation", "status": "pending"},
    {"stage": "model_training", "status": "pending"}
  ]
}
```

#### List Versions
```http
GET /model-lifecycle/versions?model_name=confidence_scoring
```
Model version history.

#### Compare Versions
```http
POST /model-lifecycle/versions/compare
```
Compare two model versions.

**Request:**
```json
{
  "model_name": "fraud_detection",
  "version1": "2.0.9",
  "version2": "2.1.0"
}
```

#### Rollback Model
```http
POST /model-lifecycle/rollback
```
Rollback to previous version.

**Request:**
```json
{
  "model_name": "fraud_detection",
  "target_version": "2.0.9",
  "reason": "performance_issue"
}
```

#### A/B Testing
```http
POST /model-lifecycle/ab-test
```
Start A/B test between versions.

**Request:**
```json
{
  "model_a": "fraud_detection:2.0.9",
  "model_b": "fraud_detection:2.1.0",
  "duration_hours": 48,
  "sample_size": 5000
}
```

#### Statistics
```http
GET /model-lifecycle/stats
```
Model lifecycle statistics.

---

## Common Patterns

### Pagination
```http
GET /providers/?page=1&per_page=20
```

### Filtering
```http
GET /providers/?state=Maharashtra&provider_type=hospital
```

### Sorting
```http
GET /providers/?sort_by=name&sort_order=asc
```

### Date Ranges
```http
GET /analytics/overview?start_date=2025-10-01&end_date=2025-11-01
```

---

## Authentication

**Current:** Development mode (no auth required)  
**Production:** JWT bearer tokens

```http
Authorization: Bearer <token>
```

---

## Response Format

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "timestamp": "2025-11-04T12:00:00Z"
}
```

### Error Response
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

---

## Rate Limiting

**Default Limits:**
- 100 requests per hour
- 1000 requests per day

**Headers:**
- `X-RateLimit-Limit` - Request limit
- `X-RateLimit-Remaining` - Remaining requests
- `X-RateLimit-Reset` - Reset timestamp

---

## API Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "TrueMesh Provider Intelligence"
}
```

---

## System Status Summary

✅ **30+ API Endpoints** across 9 modules  
✅ **12 AI Agents** accessible via API  
✅ **Auto-generated documentation** (Swagger UI)  
✅ **Pydantic validation** on all requests  
✅ **Production ready** with comprehensive error handling  

---

## Quick Start

### 1. Start Server
```bash
python main.py
```

### 2. Access API Docs
Open http://localhost:8000/docs

### 3. Test Endpoint
```bash
curl http://localhost:8000/health
```

### 4. Create Provider
```bash
curl -X POST http://localhost:8000/api/v1/providers/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Apollo Hospital", "city": "Chennai"}'
```

### 5. Get Analytics
```bash
curl http://localhost:8000/api/v1/analytics/overview
```

---

## Support

**Documentation:** http://localhost:8000/docs  
**Repository:** https://github.com/harshith-varma07/TrueMesh  
**Issues:** GitHub Issues  

---

**Last Updated:** 2025-11-04  
**API Version:** 1.0.0  
**Status:** Production Ready ✅
