# Pre-Deployment Checklist

This checklist ensures you're ready to deploy the SAP O2C Graph System to production.

---

## 📋 Phase 1: Prerequisites

### Accounts & Services

- [ ] GitHub account created and repository set up
- [ ] Railway account created (https://railway.app/)
- [ ] Vercel account created (https://vercel.com/)
- [ ] Neo4j Aura account created (https://console.neo4j.io/)
- [ ] Google account for Gemini API (https://makersuite.google.com/)

### API Keys & Credentials

- [ ] Gemini API key obtained and tested locally
- [ ] Neo4j Aura instance created
- [ ] Neo4j connection details saved (URI, username, password)
- [ ] All credentials stored securely (password manager)

---

## 📦 Phase 2: Code Preparation

### Files & Configuration

- [ ] All code pushed to GitHub repository
- [ ] `.gitignore` file present and configured
- [ ] `.env` files NOT committed to Git
- [ ] `backend/.env.example` exists with template
- [ ] `frontend/.env.example` exists with template
- [ ] `requirements.txt` includes `neo4j==5.16.0`
- [ ] `Procfile` exists in backend folder
- [ ] `railway.json` exists in backend folder
- [ ] `vercel.json` exists in frontend folder

### Local Testing

- [ ] Backend runs successfully with `USE_NEO4J=false`
- [ ] Frontend connects to local backend
- [ ] Sample queries work correctly
- [ ] Graph visualization displays properly
- [ ] No console errors in browser
- [ ] API health check returns 200 OK

---

## 🗄️ Phase 3: Database Setup

### Neo4j Configuration

- [ ] Neo4j Aura instance is running
- [ ] Database credentials tested and working
- [ ] Connection URI format verified (`neo4j+s://...`)
- [ ] Test connection from local machine successful
- [ ] Database is empty and ready for data

### Performance Optimization

- [ ] Indexes created for key node types:
  ```cypher
  CREATE INDEX sales_order_id IF NOT EXISTS FOR (n:SalesOrder) ON (n.id);
  CREATE INDEX customer_id IF NOT EXISTS FOR (n:Customer) ON (n.id);
  CREATE INDEX product_id IF NOT EXISTS FOR (n:Product) ON (n.id);
  CREATE INDEX invoice_id IF NOT EXISTS FOR (n:Invoice) ON (n.id);
  CREATE INDEX delivery_id IF NOT EXISTS FOR (n:Delivery) ON (n.id);
  ```

---

## 🚀 Phase 4: Backend Deployment (Railway)

### Railway Project Setup

- [ ] Railway project created
- [ ] GitHub repository connected
- [ ] Root directory set to `backend` (if needed)
- [ ] Python buildpack detected
- [ ] First deployment successful

### Environment Variables

All required variables set in Railway:

- [ ] `ENVIRONMENT=production`
- [ ] `USE_NEO4J=true`
- [ ] `DATA_PATH=/app/data`
- [ ] `NEO4J_URI=neo4j+s://...` (your actual URI)
- [ ] `NEO4J_USERNAME=neo4j`
- [ ] `NEO4J_PASSWORD=...` (your actual password)
- [ ] `GEMINI_API_KEY=...` (your actual key)

### Verification

- [ ] Railway deployment completed without errors
- [ ] Public URL generated (e.g., `your-app.railway.app`)
- [ ] Health endpoint accessible: `/api/health`
- [ ] Graph stats endpoint works: `/api/graph/stats`
- [ ] Data loaded successfully (check node/edge counts)
- [ ] Logs show no errors
- [ ] Test query works via Swagger docs (`/docs`)

---

## 🎨 Phase 5: Frontend Deployment (Vercel)

### Vercel Project Setup

- [ ] Vercel project created
- [ ] GitHub repository imported
- [ ] Framework preset: Create React App
- [ ] Root directory set to `frontend`
- [ ] Build command: `npm run build`
- [ ] Output directory: `build`

### Environment Variables

- [ ] `REACT_APP_API_URL=https://your-app.railway.app` (your actual Railway URL)

### Verification

- [ ] Vercel deployment completed without errors
- [ ] Public URL accessible (e.g., `your-app.vercel.app`)
- [ ] Homepage loads without errors
- [ ] Graph visualization renders
- [ ] Sample query works
- [ ] Console shows no CORS errors
- [ ] All features functional

---

## 🔒 Phase 6: Security & Configuration

### CORS Setup

- [ ] Update backend `ALLOWED_ORIGINS` with Vercel domain
- [ ] Test cross-origin requests work
- [ ] Verify preflight OPTIONS requests succeed

### API Key Security

- [ ] API keys not visible in frontend code
- [ ] Environment variables properly configured
- [ ] No credentials in Git history
- [ ] Different keys for dev/prod environments

### Access Control

- [ ] Neo4j database firewall configured (if applicable)
- [ ] Railway service not publicly accessible (optional)
- [ ] Rate limiting considered (if needed)

---

## 📊 Phase 7: Data & Performance

### Data Migration

- [ ] Initial data loaded into Neo4j
- [ ] Node count matches expectations
- [ ] Edge count matches expectations
- [ ] Sample queries return correct data
- [ ] No duplicate nodes/edges

### Performance Testing

- [ ] Query response time acceptable (< 1s)
- [ ] Graph visualization loads within 5s
- [ ] Large result sets paginated properly
- [ ] No memory leaks observed
- [ ] Database performance metrics reviewed

---

## 🔍 Phase 8: Monitoring & Maintenance

### Monitoring Setup

- [ ] Railway logs accessible and readable
- [ ] Vercel logs accessible and readable
- [ ] Neo4j monitoring dashboard reviewed
- [ ] Error tracking configured (optional: Sentry, etc.)

### Documentation

- [ ] README.md updated with deployment URLs
- [ ] Team members have access credentials
- [ ] Backup procedure documented
- [ ] Update procedure documented

### Testing

- [ ] End-to-end test completed
- [ ] All major features tested
- [ ] Mobile responsiveness checked
- [ ] Different browsers tested

---

## ✅ Phase 9: Go-Live

### Final Checks

- [ ] All previous checklist items completed
- [ ] Stakeholders notified
- [ ] Support plan in place
- [ ] Rollback plan documented
- [ ] Contact information updated

### Post-Deployment

- [ ] Monitor logs for 24 hours
- [ ] Test all critical workflows
- [ ] Collect initial user feedback
- [ ] Document any issues encountered

---

## 🆘 Troubleshooting Reference

### Backend Issues

| Issue | Check | Solution |
|-------|-------|----------|
| App won't start | Railway logs | Verify env vars, Neo4j connection |
| Database connection fails | Neo4j console | Check URI format, credentials |
| Data not loading | Backend logs | Verify DATA_PATH, file permissions |
| Slow queries | Neo4j metrics | Create indexes, optimize queries |

### Frontend Issues

| Issue | Check | Solution |
|-------|-------|----------|
| Build fails | Vercel logs | Check dependencies, Node version |
| Can't connect to API | Browser console | Verify REACT_APP_API_URL, CORS |
| Graph won't render | Console errors | Check data format, dependencies |
| Blank page | Browser console | Check for JS errors, API status |

### Database Issues

| Issue | Check | Solution |
|-------|-------|----------|
| Connection timeout | Network/firewall | Check Neo4j Aura settings |
| Out of memory | Neo4j metrics | Upgrade plan, optimize queries |
| Slow queries | Query logs | Add indexes, limit result size |
| Data inconsistency | Neo4j browser | Check constraints, run validation |

---

## 📞 Support Contacts

### Services
- **Railway Support**: https://railway.app/help
- **Vercel Support**: https://vercel.com/support
- **Neo4j Support**: https://neo4j.com/support/
- **Google AI Support**: https://developers.google.com/

### Documentation
- **Deployment Guide**: `DEPLOYMENT_GUIDE.md`
- **Environment Variables**: `ENVIRONMENT_VARIABLES.md`
- **Quick Start**: `QUICKSTART.md`
- **Summary**: `DEPLOYMENT_SUMMARY.md`

---

## 🎯 Success Criteria

Your deployment is successful when:

- ✅ Backend is accessible and responding
- ✅ Frontend loads without errors
- ✅ Natural language queries work
- ✅ Graph visualization renders
- ✅ Data is accurate and complete
- ✅ Performance is acceptable (< 1s queries)
- ✅ No errors in production logs
- ✅ All stakeholders have access

---

## 📈 Next Steps After Deployment

1. Monitor system for 48 hours
2. Gather user feedback
3. Optimize slow queries
4. Plan feature enhancements
5. Schedule regular backups
6. Review security settings
7. Update documentation as needed

---

**Good luck with your deployment!** 🚀

If you encounter any issues, refer to the troubleshooting sections in:
- `DEPLOYMENT_GUIDE.md`
- `ENVIRONMENT_VARIABLES.md`
- This checklist
