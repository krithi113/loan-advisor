# DEPLOYMENT GUIDE - APPROACH 1: SEPARATE DEPLOYMENT
## Frontend on Vercel + Backend on Railway

This approach separates frontend and backend into different services, which is how modern apps are built.

### Overview
```
┌─────────────────────────┐
│   React Frontend        │
│   (Vercel / Netlify)    │
│   Deployed at:          │
│   app.vercel.app        │
└────────────┬────────────┘
             │
             │ HTTP/CORS
             ↓
┌─────────────────────────┐
│   FastAPI Backend       │
│   (Railway / Render)    │
│   Deployed at:          │
│   api.railway.app       │
└─────────────────────────┘
```

---

## STEP 1: Setup Ollama (Local or Cloud)

### Option A: Run Ollama Locally (Recommended for Testing)
```bash
# Install Ollama from https://ollama.ai
# Download and run these models:
ollama pull mistral
ollama pull nomic-embed-text

# Keep Ollama running in background
ollama serve
# It will be available at http://localhost:11434
```

### Option B: Run Ollama in a Container
```bash
docker run -d \
  -p 11434:11434 \
  -v ollama_data:/root/.ollama \
  --name ollama \
  ollama/ollama:latest

# Pull models
docker exec ollama ollama pull mistral
docker exec ollama ollama pull nomic-embed-text
```

---

## STEP 2: Deploy Backend to Railway

### 2.1 Create Railway Account
- Go to https://railway.app
- Sign up with GitHub
- Create new project

### 2.2 Prepare Backend for Deployment

Create `.env` for local testing:
```bash
PLAID_CLIENT_ID=sandbox
PLAID_SECRET=sandbox
PLAID_ENV=sandbox
OLLAMA_URL=http://localhost:11434  # Change this when deploying
```

### 2.3 Push to GitHub
```bash
# Initialize git repo (if not already)
git init
git add .
git commit -m "Initial loan advisor project"
git remote add origin https://github.com/YOUR_USERNAME/loan-advisor.git
git push -u origin main
```

### 2.4 Deploy on Railway
1. Go to Railway dashboard
2. Click "New Project"
3. Select "GitHub" and authorize
4. Choose your repository
5. Click "Deploy Now"
6. Railway auto-detects FastAPI (Procfile)

Create a `Procfile` in root:
```
web: python loan_advisor_backend.py
```

### 2.5 Configure Environment Variables in Railway
In Railway dashboard → Settings → Environment:
```
OLLAMA_URL=http://localhost:11434  # Or your cloud Ollama instance
PLAID_CLIENT_ID=sandbox
PLAID_SECRET=sandbox
PLAID_ENV=sandbox
```

**Important**: For cloud deployment, you need to either:
- Option A: Run Ollama on the same Railway instance (complex, memory-heavy)
- Option B: Use a separate Ollama instance in the cloud
- Option C: Use a paid LLM API (OpenAI, Claude) instead

For now, assume Ollama is running locally. Update OLLAMA_URL after deployment.

### 2.6 Test Backend
After deployment, Railway gives you a URL like: `https://loan-advisor-api.railway.app`

Test it:
```bash
curl https://loan-advisor-api.railway.app/health
# Should return: {"status": "ok", "service": "Loan Eligibility Advisor"}
```

---

## STEP 3: Deploy Frontend to Vercel

### 3.1 Create React App (if you haven't)
```bash
npx create-react-app frontend
cd frontend

# Copy App.jsx and App.css into src/
cp ../App.jsx src/
cp ../App.css src/

# Update src/index.js to import App.jsx
```

### 3.2 Install Dependencies
```bash
npm install axios
```

### 3.3 Create `.env.production` for Vercel
```
REACT_APP_API_URL=https://loan-advisor-api.railway.app
```

### 3.4 Push Frontend to GitHub
```bash
cd frontend
git init
git add .
git commit -m "Loan advisor frontend"
git remote add origin https://github.com/YOUR_USERNAME/loan-advisor-frontend.git
git push -u origin main
```

### 3.5 Deploy on Vercel
1. Go to https://vercel.com
2. Click "New Project"
3. Import your GitHub repository
4. Vercel auto-detects React
5. Add environment variables:
   - `REACT_APP_API_URL=https://loan-advisor-api.railway.app`
6. Click "Deploy"

Vercel will give you a URL like: `https://loan-advisor.vercel.app`

---

## STEP 4: Handle CORS Issues

When frontend calls backend from different domains, you need CORS headers.

Backend already has CORS configured:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for demo)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, change to:
```python
allow_origins=[
    "https://loan-advisor.vercel.app",
    "https://your-domain.com",
]
```

---

## STEP 5: Setup Custom Domain (Optional)

### Vercel Custom Domain
1. In Vercel dashboard → Settings → Domains
2. Add your custom domain
3. Update DNS records (Vercel provides instructions)

### Railway Custom Domain
1. In Railway dashboard → Settings → Custom Domains
2. Add your domain
3. Update DNS records

---

## STEP 6: Monitoring & Logging

### Railway Logs
- Dashboard → Deployments → Logs
- See all API requests, errors, etc.

### Vercel Analytics
- Dashboard → Analytics
- See frontend performance, requests, etc.

---

## TROUBLESHOOTING

### Issue: 503 Service Unavailable from Backend
**Cause**: Ollama not running or unreachable from Railway instance
**Fix**:
1. Check OLLAMA_URL environment variable in Railway
2. Ensure Ollama is running: `curl http://localhost:11434/api/tags`
3. For cloud deployment, you'll need to run Ollama on same instance or separate cloud service

### Issue: CORS Error in Browser Console
**Cause**: Frontend can't call backend
**Fix**:
1. Check REACT_APP_API_URL is correct
2. Verify backend CORS headers: `curl -i https://api.railway.app/health`
3. Check browser console for exact error message

### Issue: Slow Response Times
**Cause**: Ollama models are heavy, Cold starts on Railway/Vercel
**Fix**:
1. Free tier instances have limited CPU
2. First request takes 10-30 seconds
3. Upgrade to paid tier for better performance
4. Or use smaller models: `ollama pull neural-chat` (faster, less accurate)

---

## COST ESTIMATE

- **Railway**: ~$5-10/month (free tier limited, $7/month for decent performance)
- **Vercel**: Free tier is generous (up to 12 deployments/month)
- **Ollama Cloud**: ~$10-50/month depending on provider
- **Total**: ~$15-60/month depending on usage

---

## PROS & CONS

### Pros ✅
- Modern architecture (separate frontend/backend)
- Independent scaling (frontend/backend scale separately)
- Fast frontend deployments (Vercel is instant)
- Industry standard setup

### Cons ⚠️
- Network latency between services
- More complex to debug (frontend/backend logs separate)
- CORS can be tricky
- Need two separate deployments

---

## NEXT STEPS

1. Deploy backend first, test with `curl`
2. Deploy frontend, update API_URL
3. Test end-to-end from browser
4. Monitor logs for issues
5. If Ollama performance is bad, consider using an LLM API instead

