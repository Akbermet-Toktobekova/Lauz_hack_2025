# Backend Integration Guide

## Overview

The frontend has been fully integrated with the Flask backend API. All API communication is handled through the `fraudApi.ts` service layer.

## Backend Endpoints

### 1. Health Check
- **Endpoint**: `GET /health`
- **Service Function**: `checkHealth()`
- **Response**: `{ status: "healthy", llama_server: string }`

### 2. Risk Assessment
- **Endpoint**: `POST /api/assess-risk`
- **Service Function**: `assessRisk(partnerId: string)`
- **Request**: `{ partner_id: string }`
- **Response**: `{ partner_id, risk_score (0-100), rationale, raw_response, status }`

### 3. Partner Profile
- **Endpoint**: `POST /api/profile`
- **Service Function**: `getProfile(partnerId: string)`
- **Request**: `{ partner_id: string }`
- **Response**: `{ partner_id, profile_text, status }`

### 4. Combined Analysis
- **Service Function**: `analyzeFraudRisk(partnerId: string)`
- **Description**: Fetches both risk assessment and profile in parallel
- **Returns**: Combined `FraudAnalysisResponse` object

## Configuration

### Vite Proxy
The `vite.config.ts` is configured to proxy API requests:
- `/api/*` → `http://localhost:5000/api/*`
- `/health` → `http://localhost:5000/health`

### Environment Variables
Set `VITE_API_URL` to override the default backend URL:
```bash
VITE_API_URL=http://localhost:5000
```

## Data Flow

```
User Input (Partner ID)
    ↓
QueryInput Component
    ↓
Index.tsx → handleQuery(partnerId)
    ↓
fraudApi.ts → analyzeFraudRisk(partnerId)
    ↓
Parallel API Calls:
    ├─ POST /api/assess-risk
    └─ POST /api/profile
    ↓
Combined Response
    ↓
AnalysisPanel + VisualizationPanel
```

## Type Definitions

All types are defined in `src/types/fraud.ts`:
- `AssessRiskResponse` - Risk assessment API response
- `ProfileResponse` - Profile API response
- `FraudAnalysisResponse` - Combined frontend data structure
- `QueryMessage` - Chat message structure

## Key Changes Made

1. **API Service** (`fraudApi.ts`):
   - Replaced mock data with real API calls
   - Added error handling and network error detection
   - Implemented parallel fetching for risk and profile

2. **Query Input** (`QueryInput.tsx`):
   - Changed from natural language to Partner ID (UUID) input
   - Added UUID format validation
   - Updated placeholder text

3. **Main Page** (`Index.tsx`):
   - Updated to use `partnerId` instead of natural language query
   - Added backend health check on mount
   - Added backend status indicator in header
   - Updated error handling

4. **Analysis Panel** (`AnalysisPanel.tsx`):
   - Updated to display `risk_score` (0-100 scale)
   - Shows `rationale` as main analysis text
   - Displays `profile_text` in separate section
   - Shows `raw_response` in collapsible section
   - Updated risk level calculation (0-100 scale)

5. **Visualization Panel** (`VisualizationPanel.tsx`):
   - Updated to work with new data structure
   - Removed references to old `visualizationData`
   - Added placeholders for future visualizations

6. **Vite Config** (`vite.config.ts`):
   - Added proxy configuration for backend
   - Changed port to 3000 (standard frontend port)

## Running the Application

### Start Backend
```bash
cd backend
python app.py
```
Backend runs on port 5000.

### Start Frontend
```bash
cd frontend/frontend
npm run dev
```
Frontend runs on port 3000.

### Access Application
Open browser to: `http://localhost:3000`

## Error Handling

The API service includes comprehensive error handling:
- Network errors (connection failures)
- HTTP errors (4xx, 5xx responses)
- Validation errors (missing partner_id)
- User-friendly error messages displayed via toast notifications

## CORS Configuration

If you encounter CORS errors, you may need to add CORS support to the Flask backend:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
```

Or install flask-cors:
```bash
pip install flask-cors
```

## Testing

1. Start both backend and frontend servers
2. Enter a valid Partner ID (UUID format) in the input field
3. Click submit or press Enter
4. View the analysis results in the panels

## Example Partner IDs

Use UUID format partner IDs from your data:
- Example: `96a660ff-08e0-49c1-be6d-bb22a84e742e`

## Future Enhancements

- Add caching for frequently accessed partners
- Implement request cancellation for in-flight requests
- Add retry logic for failed requests
- Implement real-time updates via WebSocket
- Add data visualization charts using recharts library

