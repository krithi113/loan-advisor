# 💰 Loan Eligibility Advisor
## Production-Grade AI Agent with RAG + Evaluation Framework

A full-stack application that uses **RAG (Retrieval-Augmented Generation)** and **LLM Agents** to provide AI-powered loan eligibility assessment. Built with FastAPI, React, and Ollama.

### 🎯 Key Features
- ✅ **RAG System**: Grounds answers in actual loan product data
- ✅ **Multi-Tool Agent**: Makes eligibility decisions using specialized tools
- ✅ **Risk Assessment**: Flags cases for human review based on compliance rules
- ✅ **Evaluation Framework**: 5 test cases to measure system accuracy
- ✅ **Dual Deployment Options**: Learn both separate and monolithic architectures
- ✅ **Production-Ready**: CORS, health checks, monitoring, error handling
- ✅ **Interview-Ready**: Clean code, clear architecture, documented decisions

---

## 📋 What This Project Teaches

### Architecture
- How modern AI agents use tools and reasoning
- RAG vs pure generation trade-offs
- Multi-component system design

### Evaluation
- How to measure AI system performance
- Test case design for financial applications
- Metrics that matter: precision, recall, false negatives

### Deployment
- **Approach 1**: Separate services (Vercel + Railway) - Modern architecture
- **Approach 2**: Monolithic Docker container - Simpler deployment
- CORS handling, environment management, scaling considerations

### BFSI Domain
- Loan eligibility rules and compliance
- Risk flagging and human review workflows
- Why you need guardrails in financial AI

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│            React Frontend (localhost:3000)          │
│  - Form input for customer profile                  │
│  - Results display (eligible products, risks)       │
│  - Metrics visualization                            │
└────────────────┬────────────────────────────────────┘
                 │ HTTP
                 ▼
┌─────────────────────────────────────────────────────┐
│         FastAPI Backend (localhost:8000)            │
│                                                     │
│  ┌────────────────────────────────────────────────┐ │
│  │  RAG Pipeline                                  │ │
│  │  - Chroma Vector Store (Loan Products)        │ │
│  │  - Ollama Embeddings (nomic-embed-text)       │ │
│  └────────────────────────────────────────────────┘ │
│                                                     │
│  ┌────────────────────────────────────────────────┐ │
│  │  Tool-Calling Agent                           │ │
│  │  - get_loan_product_info                       │ │
│  │  - evaluate_eligibility                        │ │
│  │  - check_loan_amount_approval                  │ │
│  └────────────────────────────────────────────────┘ │
│                                                     │
│  ┌────────────────────────────────────────────────┐ │
│  │  Evaluation Metrics                            │ │
│  │  - Track all evaluations                       │ │
│  │  - Measure flag rates                          │ │
│  └────────────────────────────────────────────────┘ │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│         Ollama (localhost:11434)                    │
│  - mistral (main reasoning model)                   │
│  - nomic-embed-text (embeddings)                    │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Ollama installed locally

### 1. Install Ollama & Download Models
```bash
# Download from https://ollama.ai
# Then pull models:
ollama pull mistral
ollama pull nomic-embed-text

# Keep running in background:
ollama serve &
```

### 2. Setup Backend
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run backend (requires Ollama running)
python loan_advisor_backend.py
# Available at http://localhost:8000
```

### 3. Setup Frontend
```bash
# Create React app
npx create-react-app frontend
cd frontend

# Copy UI files
cp ../App.jsx src/
cp ../App.css src/

# Install additional dependencies
npm install axios

# Run frontend
npm start
# Available at http://localhost:3000
```

### 4. Test the System
```bash
# In another terminal
python evaluation_framework.py
```

---

## 📊 Evaluation Framework

The project includes 5 test cases covering different scenarios:

### Test Cases
1. **Prime Borrower**: High income, low debt, excellent credit
   - Expected: 2+ eligible products, no review needed

2. **Standard Borrower**: Moderate income, manageable debt, good credit
   - Expected: 1+ eligible products, no review needed

3. **High Debt Ratio**: Good income but excessive existing debt
   - Expected: Flag for review, identify risk

4. **Low Credit Score**: Decent income but poor credit history
   - Expected: Flag risk, limited eligibility

5. **Low Income**: Below minimum threshold
   - Expected: No eligibility, flag for review

### Running Evaluation
```bash
# Make sure backend is running first
python evaluation_framework.py
```

Output:
```
============================================================
LOAN ELIGIBILITY SYSTEM EVALUATION
============================================================

Running: Prime Borrower... ✅ PASS
Running: Standard Borrower... ✅ PASS
Running: High Debt Ratio... ✅ PASS
Running: Low Credit Score... ✅ PASS
Running: Low Income... ✅ PASS

============================================================
EVALUATION SUMMARY
============================================================
Total Tests: 5
Passed: 5 ✅
Failed: 0 ❌
Accuracy: 100%
============================================================
```

---

## 🎤 How to Talk About This in Interviews

### The Problem
> "I built a loan eligibility advisor because banks need AI systems that are transparent and don't hallucinate about eligibility criteria. Using RAG grounds the system in actual product rules, and agents let the system reason through complex customer profiles."

### The Solution
> "I used three key components: (1) RAG to retrieve exact loan product requirements, (2) a tool-calling agent to evaluate eligibility against those rules, (3) risk flagging to catch edge cases for human review. I measured success with 5 test cases covering happy paths and edge cases."

### The Trade-offs
> "I could have used pure generation, but that risks hallucination. I could have built static eligibility rules, but agents are more flexible. The trade-off is latency—agents take 5-10 seconds because they reason step-by-step, but that's acceptable for loan applications."

### The Deployment
> "I learned two deployment approaches: Approach 1 separates frontend and backend (modern, scalable), Approach 2 uses monolithic Docker (simpler, but less flexible). For production BFSI, I'd go with Approach 1 and use a managed LLM instead of local Ollama."

### The Evaluation
> "I created an evaluation framework with 5 test cases because measuring accuracy matters in financial services. If the system incorrectly denies a customer or flags false positives, that costs money. My metrics track accuracy, flag rates, and high-risk cases."

---

## 📝 API Endpoints

### Health Check
```bash
GET /health
# Response: {"status": "ok", "service": "Loan Eligibility Advisor"}
```

### Evaluate Eligibility
```bash
POST /evaluate
Content-Type: application/json

{
  "annual_income": 75000,
  "existing_debt": 15000,
  "credit_score": 720,
  "requested_loan_amount": 25000
}
```

Response:
```json
{
  "customer_profile": {
    "annual_income": 75000,
    "existing_debt": 15000,
    "debt_to_income_ratio": 0.2,
    "credit_score": 720,
    "requested_loan_amount": 25000
  },
  "eligible_products": [
    {
      "name": "Personal Loan - Standard",
      "product_key": "personal_loan_standard",
      "risk_level": "low"
    }
  ],
  "risk_assessment": [],
  "recommendation": "You qualify for...",
  "requires_human_review": false,
  "evaluation_timestamp": "2024-01-15T10:30:45.123456"
}
```

### Get Metrics
```bash
GET /metrics
# Response: {"total_evaluations": 42, "flagged_for_review": 8, "flag_rate_percent": 19.05, ...}
```

### Get Loan Products
```bash
GET /products
# Response: {"products": {...}, "count": 3}
```

---

## 🐳 Docker Deployment

### Approach 1: Separate Services (Modern)
```bash
# Build and run each service separately
docker build -f Dockerfile.backend -t loan-advisor-api .
docker run -p 8000:8000 loan-advisor-api

# In another terminal
docker build -f Dockerfile.frontend -t loan-advisor-web ./frontend
docker run -p 3000:3000 loan-advisor-web
```

See `DEPLOYMENT_APPROACH_1.md` for detailed guide.

### Approach 2: Docker Compose (Monolithic)
```bash
# Run everything together
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

See `DEPLOYMENT_APPROACH_2.md` for detailed guide.

---

## 📚 Project Structure

```
loan-advisor/
├── loan_advisor_backend.py      # FastAPI app with RAG + Agent
├── requirements.txt             # Python dependencies
├── App.jsx                       # React component
├── App.css                       # React styling
├── evaluation_framework.py       # Test cases + metrics
├── docker-compose.yml           # Local development
├── Dockerfile.backend           # Backend container
├── Dockerfile.frontend          # Frontend container
├── nginx.conf                   # Frontend reverse proxy
├── DEPLOYMENT_APPROACH_1.md     # Separate services guide
├── DEPLOYMENT_APPROACH_2.md     # Monolithic guide
└── README.md                    # This file
```

---

## 🔑 Key Design Decisions

### Why RAG?
Instead of letting the LLM make up loan rules, RAG ensures answers come from actual product specifications. This prevents hallucinations like "you qualify for $1M loans at 0% APR."

### Why Agents?
A simple semantic search could find product info, but agents can reason: "This customer has high debt, so even if they have income, they might be risky." Tools let the agent branch logic.

### Why Tool-Calling?
Instead of writing Python code to evaluate eligibility, the agent uses tools. This is more flexible and shows how real LLM systems work (OpenAI, Claude, etc. all use tool-calling).

### Why Evaluation Framework?
If you evaluate using vague intuition ("It seems right"), you can't improve. Test cases give you signal. A 100% flag rate is bad (too conservative). A 0% flag rate is bad (missing real risks). My 5 tests cover the spectrum.

### Why Two Deployment Approaches?
Both have trade-offs. Learning both makes you dangerous—you understand when to use microservices vs monoliths. Interview signal: "I chose this architecture because..."

---

## 🚨 Known Limitations & Future Work

### Current Limitations
1. **Loan Products are Hardcoded**: Ideally from a database
2. **Ollama on Local Machine**: Doesn't scale to production (use managed LLM instead)
3. **No Real Plaid Integration**: Placeholder only (add real credentials to enable)
4. **Synchronous Only**: No async job processing for long evaluations
5. **No Persistence**: Evaluation history lost on restart

### Future Improvements
- [ ] Switch to Claude API (remove Ollama complexity)
- [ ] Add PostgreSQL for loan products and evaluation history
- [ ] Implement real Plaid integration for actual bank data
- [ ] Add async task queue (Celery) for long-running evaluations
- [ ] Build dashboard for monitoring evaluation accuracy
- [ ] Add authentication (JWT) for production use
- [ ] Implement caching (Redis) for common queries
- [ ] Add rate limiting and quota enforcement

---

## 💡 Interview Tips

### What to Emphasize
1. **Trade-offs**: You made conscious decisions (RAG vs pure gen, monolithic vs microservices)
2. **Evaluation**: You measured success, not just "it works"
3. **Production Thinking**: Health checks, CORS, error handling, monitoring
4. **Domain Knowledge**: You understand compliance/risk in finance
5. **Scalability**: You learned how it would break at scale

### What NOT to Say
❌ "I built this in a weekend" (Implies shallow understanding)
❌ "It's just a RAG + agent, nothing fancy" (You're underselling)
❌ "I didn't have time for evals" (Red flag for production readiness)
❌ "I don't know what happens when Ollama crashes" (You should)

### Questions You Should Be Ready For
- **"How would you scale this to 1M daily requests?"**
  - Answer: Switch to managed LLM, add load balancer, separate services, cache results, add database
  
- **"What if Ollama returns an incorrect answer?"**
  - Answer: Evaluation framework catches it, risk flags catch edge cases, human review process
  
- **"Why not just use OpenAI?"**
  - Answer: Ollama for learning/control, OpenAI for production (cheaper, more reliable)
  
- **"How do you know the system isn't hallucinating?"**
  - Answer: RAG grounds answers, evaluation tests verify accuracy, humans review edge cases

---

## 📞 Support & Debugging

### Backend Not Starting?
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check Python deps
pip list | grep -i langchain

# View backend logs
python loan_advisor_backend.py
```

### Frontend Can't Connect to Backend?
```bash
# Check backend is listening
curl http://localhost:8000/health

# Check CORS headers
curl -i http://localhost:8000/health

# Frontend needs environment variable
echo "REACT_APP_API_URL=http://localhost:8000" > frontend/.env
```

### Evaluation Tests Failing?
```bash
# Make sure both backend and Ollama are running
curl http://localhost:8000/health
curl http://localhost:11434/api/tags

# Run with verbose output
python evaluation_framework.py
```

---

## 📖 Learning Resources

- **LangChain Docs**: https://python.langchain.com/docs/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Ollama**: https://ollama.ai
- **Docker**: https://docs.docker.com/
- **Vercel Deployment**: https://vercel.com/docs
- **Railway Deployment**: https://docs.railway.app/

---

## 📄 License

This project is provided as-is for portfolio and educational purposes.

---

## 🤝 Contributing

This is a personal portfolio project. Feel free to fork and adapt for your own learning.

---

## 📞 Questions?

If you have questions about the architecture, evaluation methodology, or deployment approaches, refer to the detailed guides:
- `DEPLOYMENT_APPROACH_1.md` - Separate services (Vercel + Railway)
- `DEPLOYMENT_APPROACH_2.md` - Monolithic Docker deployment

---

**Built with ❤️ for AI engineers learning production systems.**
