# Environment Variables Configuration Guide

## Overview

This document explains all environment variables used in the SAP O2C Graph System.

---

## Backend Environment Variables

### Required Variables

#### `GEMINI_API_KEY` (Required)
- **Description**: Google Gemini API key for natural language processing
- **How to get**: https://makersuite.google.com/app/apikey
- **Example**: `AIzaSyBx...your_key_here`
- **Security**: Never commit this to version control!

```env
GEMINI_API_KEY=AIzaSyBx...your_key_here
```

---

### Optional Variables

#### `ENVIRONMENT`
- **Description**: Application environment
- **Default**: `development`
- **Options**: `development`, `production`, `staging`
- **Example**: `ENVIRONMENT=production`

#### `USE_NEO4J`
- **Description**: Enable Neo4j database (vs in-memory graph)
- **Default**: `false`
- **Options**: `true`, `false`
- **Example**: `USE_NEO4J=true`

**When to use:**
- `false`: Local development, testing
- `true`: Production deployment with persistent storage

#### `DATA_PATH`
- **Description**: Path to JSONL data files
- **Default**: `./data`
- **Example**: `DATA_PATH=../data` or `DATA_PATH=/app/data`

---

### Neo4j Configuration (Required when `USE_NEO4J=true`)

#### `NEO4J_URI`
- **Description**: Neo4j database connection URI
- **Format**: `neo4j+s://[host]:[port]`
- **Example**: `NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io`

#### `NEO4J_USERNAME`
- **Description**: Neo4j username
- **Default**: `neo4j`
- **Example**: `NEO4J_USERNAME=neo4j`

#### `NEO4J_PASSWORD`
- **Description**: Neo4j password
- **Security**: Keep this secret!
- **Example**: `NEO4J_PASSWORD=your_secure_password_here`

---

### CORS Configuration (Optional)

#### `ALLOWED_ORIGINS`
- **Description**: Comma-separated list of allowed frontend origins
- **Default**: `*` (all origins - use only in development!)
- **Example**: `ALLOWED_ORIGINS=https://your-app.vercel.app,https://custom-domain.com`

**Production recommendation:**
```env
ALLOWED_ORIGINS=https://your-app.vercel.app
```

---

## Frontend Environment Variables

### `REACT_APP_API_URL`
- **Description**: Backend API base URL
- **Required**: Yes
- **Example (local)**: `REACT_APP_API_URL=http://localhost:8000`
- **Example (production)**: `REACT_APP_API_URL=https://your-app.railway.app`

**Note**: React requires environment variables to start with `REACT_APP_`

---

## Configuration by Environment

### Local Development

**Backend `.env`:**
```env
# Application
ENVIRONMENT=development
USE_NEO4J=false
DATA_PATH=../data

# Gemini API (Required!)
GEMINI_API_KEY=AIzaSyBx...your_key_here

# Neo4j (not needed for local dev)
# NEO4J_URI=
# NEO4J_USERNAME=
# NEO4J_PASSWORD=

# CORS (allow all in development)
ALLOWED_ORIGINS=*
```

**Frontend `.env`:**
```env
REACT_APP_API_URL=http://localhost:8000
```

---

### Production Deployment

**Railway (Backend):**
```env
# Application
ENVIRONMENT=production
USE_NEO4J=true
DATA_PATH=/app/data

# Neo4j Database
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_secure_password

# Gemini API
GEMINI_API_KEY=AIzaSyBx...your_production_key

# CORS (restrict to your frontend)
ALLOWED_ORIGINS=https://your-app.vercel.app
```

**Vercel (Frontend):**
```env
REACT_APP_API_URL=https://your-app.railway.app
```

---

## Security Best Practices

### 1. Never Commit Secrets

Add to `.gitignore`:
```
.env
.env.local
.env.production
*.key
```

### 2. Use Different Keys per Environment

| Environment | Key Type | Purpose |
|-------------|----------|---------|
| Development | Development API key | Local testing |
| Staging | Staging API key | Testing before prod |
| Production | Production API key | Live deployment |

### 3. Rotate Keys Regularly

- Rotate API keys every 90 days
- Immediately rotate if compromised
- Keep old keys for 7 days during transition

### 4. Limit Key Permissions

- Use API key restrictions in Google Cloud Console
- Restrict by referrer (HTTP)
- Restrict by IP address (if possible)
- Set usage quotas

### 5. Monitor Key Usage

- Check Google Cloud Console regularly
- Set up alerts for unusual usage
- Review API logs monthly

---

## Platform-Specific Configuration

### Railway

**Add environment variables:**
1. Go to your Railway project
2. Click on your service
3. Go to "Variables" tab
4. Click "New Variable"
5. Add each variable and value
6. Click "Deploy" to apply changes

**Tips:**
- Railway automatically injects `PORT` variable
- Use Railway's secret management for sensitive data
- Can use Railway CLI: `railway variables set KEY=value`

### Vercel

**Add environment variables:**
1. Go to your Vercel project
2. Settings → Environment Variables
3. Add variable name and value
4. Select environments (Production, Preview, Development)
5. Click "Save"

**Tips:**
- Variables starting with `REACT_APP_` are available in React
- Need to redeploy after adding variables
- Can use Vercel CLI: `vercel env add VARIABLE_NAME`

### Neo4j Aura

**Get connection details:**
1. Go to Neo4j Console (https://console.neo4j.io/)
2. Click on your database
3. Click "Connect"
4. Copy connection URI, username, and password

---

## Troubleshooting

### "GEMINI_API_KEY not configured"

**Check:**
1. `.env` file exists in backend folder
2. Variable is spelled correctly: `GEMINI_API_KEY`
3. No spaces around `=`: `GEMINI_API_KEY=value` ✅ not `GEMINI_API_KEY = value` ❌
4. Backend was restarted after adding variable

### "Failed to connect to Neo4j"

**Check:**
1. `USE_NEO4J=true` is set
2. All three Neo4j variables are configured:
   - `NEO4J_URI`
   - `NEO4J_USERNAME`
   - `NEO4J_PASSWORD`
3. URI format is correct: `neo4j+s://...` (note the `+s` for secure connection)
4. Firewall/network allows connection
5. Neo4j instance is running

### Frontend can't reach backend

**Check:**
1. `REACT_APP_API_URL` is set correctly
2. Backend URL is accessible (test in browser)
3. CORS is configured correctly on backend
4. No trailing slash in URL: `https://api.com` ✅ not `https://api.com/` ❌

### Environment variables not loading

**React/Frontend:**
- Must start with `REACT_APP_`
- Need to rebuild: `npm run build`
- Clear cache: Delete `.env.local` and rebuild

**FastAPI/Backend:**
- Use `python-dotenv` package (already in requirements.txt)
- `.env` file must be in same directory as `app.py`
- Check variable name in `config.py`

---

## Template Files

### `.env.example` (Backend)

```env
# See ENVIRONMENT_VARIABLES.md for full documentation

# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Application Configuration
ENVIRONMENT=development
USE_NEO4J=false
DATA_PATH=../data

# Neo4j Configuration (required if USE_NEO4J=true)
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# CORS
ALLOWED_ORIGINS=*
```

### `.env.example` (Frontend)

```env
# Backend API URL
REACT_APP_API_URL=http://localhost:8000
```

---

## Validation Checklist

Before deploying, verify:

- [ ] All required variables are set
- [ ] API keys are valid and have correct permissions
- [ ] Neo4j connection works (if enabled)
- [ ] Frontend can reach backend API
- [ ] CORS is configured correctly
- [ ] No secrets committed to Git
- [ ] Production uses different keys than development
- [ ] Monitoring/alerts are set up for key usage

---

## Additional Resources

- **Google Gemini API**: https://ai.google.dev/
- **Neo4j Aura**: https://neo4j.com/cloud/aura/
- **Railway Docs**: https://docs.railway.app/
- **Vercel Docs**: https://vercel.com/docs/environment-variables

---

**Need help?** Check the [QUICKSTART.md](./QUICKSTART.md) or [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
