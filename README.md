# Loan Eligibility Advisor

AI-powered loan eligibility assessment using RAG + LLM agents.

## Tech Stack
- **Frontend**: React + TypeScript + Vite
- **Backend**: FastAPI + LangChain v1.0
- **LLM**: Ollama (llama3.2b)
- **Database**: Chroma (vector store)

## Local Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python loan_advisor_backend.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Live Demo
- Frontend: [Your Vercel URL]
- Backend API: [Your Railway URL]

## Architecture
- Separate services (microservices)
- RAG for grounding product data
- Tool-calling agent for decisions
- Risk flagging for compliance

## Evaluation
- 5 test cases covering scenarios
- Metrics: accuracy, flag rates, risk detection