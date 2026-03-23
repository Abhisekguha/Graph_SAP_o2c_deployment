# SAP O2C Graph System - Deployment Guide

This guide covers deploying your SAP Order-to-Cash Graph System using:
- **Neo4j Aura** (Graph Database)
- **Railway** (Backend API)
- **Vercel** (Frontend)

## Prerequisites

- GitHub account
- Vercel account (https://vercel.com)
- Railway account (https://railway.app)
- Neo4j Aura account (https://neo4j.com/cloud/aura/)
- Gemini API key (https://makersuite.google.com/app/apikey)

---

## Step 1: Setup Neo4j Database

### 1.1 Create Neo4j Aura Instance

1. Go to https://console.neo4j.io/
2. Click **"Create Instance"**
3. Choose **"AuraDB Free"** (or Professional for production)
4. Select a region close to your Railway deployment
5. Set a strong password and **save it securely**
6. Wait for the instance to be created

### 1.2 Get Connection Details

After creation, you'll receive:
- **URI**: `neo4j+s://xxxxx.databases.neo4j.io`
- **Username**: `neo4j`
- **Password**: *the one you set*

**Important**: Keep these credentials safe!

### 1.3 Configure Database

1. Open the Neo4j Browser (click "Open" in the console)
2. Run these commands to create indexes for better performance:

```cypher
// Create indexes for faster queries
CREATE INDEX sales_order_id IF NOT EXISTS FOR (n:SalesOrder) ON (n.id);
CREATE INDEX customer_id IF NOT EXISTS FOR (n:Customer) ON (n.id);
CREATE INDEX product_id IF NOT EXISTS FOR (n:Product) ON (n.id);
CREATE INDEX invoice_id IF NOT EXISTS FOR (n:Invoice) ON (n.id);
CREATE INDEX delivery_id IF NOT EXISTS FOR (n:Delivery) ON (n.id);
```

---

## Step 2: Deploy Backend to Railway

### 2.1 Push Code to GitHub

```bash
cd sap-o2c-graph-system
git init
git add .
git commit -m "Initial commit - SAP O2C Graph System"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2.2 Create Railway Project

1. Go to https://railway.app/
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Connect your GitHub account and select the repository
5. Railway will detect the Python app in `/backend` folder

### 2.3 Configure Railway Environment Variables

In Railway project settings, add these environment variables:

```env
# Application Settings
ENVIRONMENT=production
USE_NEO4J=true
DATA_PATH=/app/data

# Neo4j Database Connection
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password

# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Python Runtime
PYTHON_VERSION=3.9
```

### 2.4 Configure Root Directory (if needed)

If Railway doesn't detect the backend folder automatically:
1. Go to Settings → Service
2. Set **Root Directory** to `backend`

### 2.5 Deploy

Railway will automatically:
1. Install dependencies from `requirements.txt`
2. Start the application using the `Procfile`
3. Assign a public URL (e.g., `https://your-app.railway.app`)

**Save this URL** - you'll need it for the frontend!

### 2.6 Initial Data Load

After deployment, trigger the data load:

**Option 1: Automatic (on first startup)**
The system will automatically detect an empty Neo4j database and load data from the JSONL files.

**Option 2: Manual Migration**
If you need to reload data:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Run migration script
railway run python migrate_to_neo4j.py
```

### 2.7 Verify Backend Deployment

Test the backend API:
- Health check: `https://your-app.railway.app/api/health`
- Graph stats: `https://your-app.railway.app/api/graph/stats`

---

## Step 3: Deploy Frontend to Vercel

### 3.1 Prepare Frontend

1. Update frontend to use Railway backend URL
2. Create `.env.production` file in `/frontend`:

```env
REACT_APP_API_URL=https://your-app.railway.app
```

3. Commit changes:

```bash
git add frontend/.env.production
git commit -m "Configure production API URL"
git push
```

### 3.2 Deploy to Vercel

**Option 1: Vercel Dashboard**

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Configure project:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

4. Add Environment Variables:
   ```
   REACT_APP_API_URL=https://your-app.railway.app
   ```

5. Click **"Deploy"**

**Option 2: Vercel CLI**

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to frontend
cd frontend

# Deploy
vercel --prod

# Follow prompts and set environment variables
```

### 3.3 Configure CORS (if needed)

Update backend to allow Vercel domain:

In Railway, add environment variable:
```env
ALLOWED_ORIGINS=https://your-app.vercel.app
```

Or update backend `app.py` to include your Vercel domain in allowed origins.

### 3.4 Verify Frontend Deployment

1. Open the Vercel URL (e.g., `https://your-app.vercel.app`)
2. Test the application:
   - Check if graph loads
   - Try a sample query: "How many sales orders?"
   - Verify visualization works

---

## Step 4: Post-Deployment Configuration

### 4.1 Custom Domains (Optional)

**Vercel Frontend:**
1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed

**Railway Backend:**
1. Go to Settings → Networking
2. Add custom domain
3. Configure DNS CNAME record

### 4.2 Security Hardening

1. **Update CORS settings** in backend to only allow your Vercel domain
2. **Enable authentication** (if needed) for sensitive queries
3. **Set rate limiting** to prevent abuse
4. **Review Neo4j security** settings

### 4.3 Monitoring Setup

**Railway:**
- Check logs: `railway logs`
- Monitor metrics in Railway dashboard
- Set up alerts for errors

**Neo4j Aura:**
- Monitor database usage in Neo4j console
- Check query performance
- Set up alerts for high memory usage

**Vercel:**
- Check deployment logs
- Monitor bandwidth usage
- Review analytics

---

## Step 5: Data Management

### 5.1 Updating Data

To update the graph data:

1. **Upload new JSONL files** to your backend
2. **Run migration** script:
   ```bash
   railway run python migrate_to_neo4j.py --clear
   ```
3. **Or clear and rebuild**:
   ```bash
   # Clear database
   railway run python -c "from neo4j_adapter import Neo4jAdapter; adapter = Neo4jAdapter(); adapter.clear_database()"
   
   # Rebuild automatically on restart
   railway run restart
   ```

### 5.2 Backup Strategy

**Neo4j Aura** (Professional plan):
- Automatic backups daily
- Manual backup: Export to CSV or JSON dump

**Railway:**
- Code is in Git (already backed up)
- Environment variables are stored in Railway

---

## Troubleshooting

### Backend Issues

**Problem: App won't start**
- Check Railway logs: `railway logs`
- Verify all environment variables are set
- Check Neo4j connection credentials

**Problem: "Graph not initialized" error**
- Check if data files are accessible
- Verify Neo4j connection
- Check logs for data loading errors

**Problem: Slow queries**
- Create Neo4j indexes (see Step 1.3)
- Optimize Neo4j query patterns
- Consider upgrading Neo4j plan

### Frontend Issues

**Problem: Frontend can't connect to backend**
- Verify `REACT_APP_API_URL` is correct
- Check CORS settings
- Test backend URL directly in browser

**Problem: Build fails on Vercel**
- Check Node.js version compatibility
- Verify all dependencies are listed in `package.json`
- Review Vercel build logs

### Database Issues

**Problem: Neo4j connection timeout**
- Check network firewalls
- Verify URI format is correct
- Ensure Railway and Neo4j are in same region

**Problem: Out of memory**
- Upgrade Neo4j plan
- Optimize queries to return less data
- Use pagination for large result sets

---

## Environment Variables Summary

### Backend (Railway)

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Deployment environment | `production` |
| `USE_NEO4J` | Enable Neo4j database | `true` |
| `DATA_PATH` | Path to JSONL data files | `/app/data` |
| `NEO4J_URI` | Neo4j connection URI | `neo4j+s://xxx.neo4j.io` |
| `NEO4J_USERNAME` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `your_password` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |

### Frontend (Vercel)

| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `https://your-app.railway.app` |

---

## Cost Estimates

### Free Tier

- **Neo4j Aura Free**: $0 (limited to 200k nodes, 400k relationships)
- **Railway**: $5/month credit (then $0.000231/GB-hour)
- **Vercel**: Free (100 GB bandwidth/month)

**Total**: ~$5-10/month for small-scale deployment

### Production (Recommended)

- **Neo4j Aura Professional**: $65/month (2GB RAM, 8GB storage)
- **Railway Pro**: $20/month (includes $20 usage credit)
- **Vercel Pro**: $20/month (1TB bandwidth)

**Total**: ~$105/month for production deployment

---

## Next Steps

1. ✅ Set up monitoring and alerts
2. ✅ Configure custom domains
3. ✅ Implement authentication (if needed)
4. ✅ Set up CI/CD pipeline
5. ✅ Document API endpoints
6. ✅ Create user guide
7. ✅ Plan backup strategy

---

## Support & Resources

- **Neo4j Documentation**: https://neo4j.com/docs/
- **Railway Documentation**: https://docs.railway.app/
- **Vercel Documentation**: https://vercel.com/docs
- **FastAPI Documentation**: https://fastapi.tiangolo.com/

---

## Maintenance Checklist

### Weekly
- [ ] Review error logs
- [ ] Check API response times
- [ ] Monitor database size

### Monthly
- [ ] Review usage costs
- [ ] Update dependencies
- [ ] Backup Neo4j data
- [ ] Review security logs

### Quarterly
- [ ] Performance optimization
- [ ] Update system documentation
- [ ] Review and update API
- [ ] Plan feature enhancements

---

**Congratulations!** Your SAP O2C Graph System is now deployed and ready for production use! 🎉
