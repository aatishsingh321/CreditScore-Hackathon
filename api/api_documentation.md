# API Documentation

## Credit Risk Scoring API

**Base URL**: `http://localhost:8000`  
**Version**: 1.0.0  
**Interactive Docs**: http://localhost:8000/docs

---

## Endpoints

### 1. Health Check
**GET** `/health`

Check API health status and model availability.

**Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0",
  "timestamp": "2026-02-03T12:00:00"
}
```

---

### 2. Predict Risk (Single)
**POST** `/predict`

Predict default risk for a single applicant.

**Request Body**:
```json
{
  "applicant_id": "APP123456",
  "age": 35,
  "annual_income": 75000,
  "credit_score": 720,
  "debt_to_income_ratio": 0.35
}
```

**Response**:
```json
{
  "applicant_id": "APP123456",
  "risk_score": 0.245,
  "risk_category": "Low Risk",
  "decision": "APPROVED",
  "reason_codes": [
    "Good credit score (720)",
    "Low debt-to-income ratio (35%)",
    "Stable employment"
  ],
  "timestamp": "2026-02-03T12:00:00"
}
```

---

### 3. Model Information
**GET** `/model/info`

Get model metadata and performance metrics.

**Response**:
```json
{
  "model_type": "LightGBM",
  "version": "1.0.0",
  "training_date": "2026-02-03",
  "performance": {
    "auc_roc": 0.6764,
    "ks_statistic": 26.30,
    "accuracy": 0.6925
  },
  "features": 103
}
```

---

## Usage Examples

### Python
```python
import requests

url = "http://localhost:8000/predict"
data = {
    "applicant_id": "APP001",
    "age": 35,
    "annual_income": 75000,
    "credit_score": 720,
    "debt_to_income_ratio": 0.35
}

response = requests.post(url, json=data)
print(response.json())
```

### cURL
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "APP001",
    "age": 35,
    "annual_income": 75000,
    "credit_score": 720,
    "debt_to_income_ratio": 0.35
  }'
```

---

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 422 | Validation Error |
| 500 | Server Error |
| 503 | Model Not Available |

---

## Field Validation

| Field | Type | Range | Required |
|-------|------|-------|----------|
| applicant_id | string | - | Yes |
| age | integer | 18-100 | Yes |
| annual_income | float | >0 | Yes |
| credit_score | integer | 300-850 | Yes |
| debt_to_income_ratio | float | 0-1 | Yes |

---

## Risk Categories

- **Low Risk** (score < 0.3): APPROVED
- **Medium Risk** (0.3-0.6): REVIEW
- **High Risk** (score > 0.6): DECLINED

---

## Running the API

```bash
# Development
python api/inference_api.py

# Production
uvicorn api.inference_api:app --workers 4 --host 0.0.0.0 --port 8000

# Docker
docker run -p 8000:8000 credit-risk-api
```

---

**Support**: For questions, see [README.md](../README.md)
