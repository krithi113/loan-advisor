# DEPLOYMENT GUIDE - APPROACH 2: MONOLITHIC DEPLOYMENT
## Single Docker Container on Render or Railway

This approach containerizes everything together - frontend, backend, and Ollama.

### Overview
```
┌──────────────────────────────────────┐
│     Docker Container on Render       │
│  ┌──────────────────────────────────┐│
│  │  Nginx (Frontend reverse proxy)   ││
│  └──────────────────────────────────┘│
│  ┌──────────────────────────────────┐│
│  │  FastAPI Backend                 ││
│  └──────────────────────────────────┘│
│  ┌──────────────────────────────────┐│
│  │  Ollama (inside container)       ││
│  └──────────────────────────────────┘│
└──────────────────────────────────────┘
        Available at:
      app.onrender.com
```

---

## STEP 1: Create Multi-Stage Dockerfile

Create a unified `Dockerfile` that includes everything:

```dockerfile
# Stage 1: Build Node/React
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/src ./src
COPY frontend/public ./public
RUN npm run build

# Stage 2: Build Python Backend
FROM python:3.11-slim AS backend-builder

WORKDIR /app/backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Final Image
FROM python:3.11-slim

# Install Node and Nginx
RUN apt-get update && apt-get install -y \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Pull Ollama models (this increases image size significantly)
# Note: Ollama is best run separately. For monolithic, we'll skip it
# and assume backend connects to external Ollama instance

WORKDIR /app

# Copy Python backend
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY loan_advisor_backend.py .

# Copy built React frontend
COPY --from=frontend-builder /app/frontend/build ./static

# Copy Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose ports
EXPOSE 3000 8000

# Create startup script
RUN echo '#!/bin/bash\n\
    # Start FastAPI in background\n\
    python loan_advisor_backend.py &\n\
    # Start Nginx (frontend)\n\
    nginx -g "daemon off;"\n\
    ' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
```

**Problem**: This image becomes ~2GB (includes Python, Node, React, Nginx). Not ideal.

---

## STEP 2: Better Approach - Docker Compose with Separate Services

Create `docker-compose.prod.yml` for production:

```yaml
version: '3.8'

services:
  # Ollama - Runs in container
  ollama:
    image: ollama/ollama:latest
    container_name: ollama-prod
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - NVIDIA_VISIBLE_DEVICES=all  # For GPU support if available
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3

  # FastAPI Backend
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: loan-advisor-backend
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_URL=http://ollama:11434
      - PLAID_CLIENT_ID=${PLAID_CLIENT_ID}
      - PLAID_SECRET=${PLAID_SECRET}
      - PLAID_ENV=sandbox
    depends_on:
      ollama:
        condition: service_healthy
    volumes:
      - ./chroma_db:/app/chroma_db
    networks:
      - app-network
    restart: unless-stopped

  # React Frontend with Nginx
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: loan-advisor-frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - app-network
    restart: unless-stopped

networks:
  app-network:
    driver: bridge

volumes:
  ollama_data:
```

---

## STEP 3: Deploy to Render

### 3.1 Prepare Repository
```bash
git add .
git commit -m "Monolithic deployment with docker-compose"
git push origin main
```

### 3.2 Create Render Account
- Go to https://render.com
- Sign up with GitHub
- Create new Web Service

### 3.3 Configure Render
1. Select "Docker" as the runtime
2. Point to your GitHub repo
3. Set build command: `docker-compose build`
4. Set start command: `docker-compose up`

### 3.4 Set Environment Variables in Render
```
PLAID_CLIENT_ID=sandbox
PLAID_SECRET=sandbox
PLAID_ENV=sandbox
```

### 3.5 Deploy
Click "Create Web Service" and Render will:
1. Clone your repo
2. Build Docker images
3. Start containers
4. Give you a URL like: `https://loan-advisor.onrender.com`

---

## STEP 4: Optimize Image Size

Docker images can get large. Here's how to reduce them:

### Use Multi-Stage Builds
```dockerfile
# Only copy what's needed to final stage
```

### Use Alpine Images
```dockerfile
FROM python:3.11-alpine  # Much smaller than python:3.11-slim
```

### Remove Build Dependencies
```dockerfile
RUN pip install --no-cache-dir -r requirements.txt  # --no-cache-dir saves space
```

### Combine RUN Commands
```dockerfile
# Bad: Creates multiple layers
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# Good: Single layer
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
```

---

## STEP 5: Handle Ollama in Production

**Problem**: Ollama is heavy (~5GB with models).

**Solutions**:

### Option A: Ollama in Separate Container
Run Ollama separately (cloud service), point backend to it.
Backend in `docker-compose`:
```yaml
environment:
  - OLLAMA_URL=https://ollama-cloud.example.com  # External Ollama
```

### Option B: Use Ollama Lite Models
```bash
ollama pull neural-chat  # Smaller, faster
ollama pull tinyllama   # Even smaller
```

### Option C: Replace Ollama with LLM API
Instead of local Ollama, use Claude API or OpenAI:
```python
from langchain_anthropic import ChatAnthropic

LLM = ChatAnthropic(model="claude-opus", api_key=os.getenv("ANTHROPIC_API_KEY"))
```

This removes the need for Ollama entirely and is more reliable in production.

---

## STEP 6: Database & Persistence

### Vector Store (Chroma)
Currently stored in `./chroma_db` directory. For production:

**Option A: Use Volume**
```yaml
volumes:
  - chroma_data:/app/chroma_db

volumes:
  chroma_data:
```

**Option B: Use Managed Service**
```python
# Use Chroma Cloud instead
client = chromadb.HttpClient(
    host="api.trychroma.com",
    port=443,
    headers={"x-token": os.getenv("CHROMA_API_KEY")},
)
```

---

## STEP 7: Monitoring & Logs

### Render Logs
Go to Render dashboard → Logs tab
See all output from all containers

### Health Checks
Both images have health checks configured:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

If health check fails, Render auto-restarts the container.

---

## STEP 8: Zero-Downtime Deployments

Render automatically handles:
1. Building new image
2. Starting new container
3. Running health checks
4. Switching traffic to new container
5. Stopping old container

You get zero-downtime deployments automatically.

---

## TROUBLESHOOTING

### Issue: Out of Memory
**Cause**: Ollama + Python + Node = memory heavy
**Fix**:
- Use paid tier (more memory)
- Run Ollama separately (external service)
- Use smaller LLM models
- Replace with API-based LLM

### Issue: Slow Cold Starts
**Cause**: Container takes 2-3 minutes to start on free tier
**Fix**:
- Keep-alive service (monitor service to ping every 15 min)
- Use paid tier (always warm)
- Split into separate microservices

### Issue: Port Conflicts
**Cause**: Frontend (3000) and Backend (8000) both exposed
**Fix**: Use Nginx reverse proxy to serve both on port 80/443
```nginx
location / { proxy_pass http://frontend:3000; }
location /api/ { proxy_pass http://backend:8000; }
```

---

## COST ESTIMATE

- **Render**: ~$7-12/month for single web service
- **Storage**: ~$5-10/month for persistent volume (Ollama models)
- **Total**: ~$12-22/month

---

## PROS & CONS

### Pros ✅
- Single deployment (simpler)
- Everything in one place
- Easier to debug
- All services talk via localhost

### Cons ⚠️
- Large Docker image (~2-4GB)
- Slow deploys
- If one service crashes, whole thing restarts
- Less scalable (frontend and backend scale together)
- Memory usage is high

---

## COMPARISON: Approach 1 vs Approach 2

| Aspect | Approach 1 (Separate) | Approach 2 (Monolithic) |
|--------|----------------------|------------------------|
| Deployment Complexity | Higher (2 services) | Lower (1 container) |
| Image Size | Small (100MB) | Large (2-4GB) |
| Deploy Time | Fast (both independent) | Slow (rebuild everything) |
| Scaling | Independent | Together |
| Cost | $5-15/month | $7-20/month |
| Industry Practice | More common | Less common |
| Debugging | Harder (separate logs) | Easier (one log) |

---

## RECOMMENDATION

For a portfolio project:
- **Use Approach 1** (Separate) because it shows you understand modern architecture
- For small MVP: **Use Approach 2** (Monolithic) because it's simpler

---

## NEXT STEPS

1. Choose one approach
2. Test locally: `docker-compose -f docker-compose.yml up`
3. Fix issues locally before deploying
4. Deploy to Render/Railway
5. Monitor logs and debug
6. Optimize once it's working

