# LOCAL DEVELOPMENT SETUP GUIDE

Get the entire system running on your machine in ~15 minutes.

---

## STEP 1: Install Prerequisites

### Install Ollama
Download from https://ollama.ai and install.

Verify installation:
```bash
ollama --version
# Should output: ollama version 0.x.x
```

### Install Python 3.11+
```bash
python --version
# Should be 3.11 or higher
```

### Install Node.js 18+
```bash
node --version
npm --version
```

### Install Docker (Optional, for containerized deployment)
```bash
docker --version
docker-compose --version
```

---

## STEP 2: Download and Run Ollama Models

Open a terminal and start Ollama:
```bash
ollama serve
# This starts the Ollama server on http://localhost:11434
```

In another terminal, download the models:
```bash
# Download Mistral (main reasoning model)
# This is ~4GB, might take 5-10 minutes
ollama pull mistral

# Download Nomic Embed Text (embeddings)
# This is ~274MB, takes 1-2 minutes
ollama pull nomic-embed-text

# Verify models are installed
ollama list
```

Output should show:
```
NAME                      ID              SIZE      MODIFIED
mistral                   8ceafd017fc5    4.1 GB    Just now
nomic-embed-text          0a109f4b3fe5    274 MB    Just now
```

**Keep the `ollama serve` terminal open** - Ollama needs to be running while you use the app.

---

## STEP 3: Setup and Run Backend

Open a new terminal:

```bash
# Clone or navigate to project directory
cd /path/to/loan-advisor

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Run the backend
python loan_advisor_backend.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Keep this terminal open.** Backend is now running at http://localhost:8000.

Test it in another terminal:
```bash
curl http://localhost:8000/health
# Response: {"status":"ok","service":"Loan Eligibility Advisor"}
```

---

## STEP 4: Setup and Run Frontend

Open another new terminal:

```bash
# Navigate to project directory
cd /path/to/loan-advisor

# Create React app
npx create-react-app frontend
cd frontend

# Copy UI files into React app
cp ../App.jsx src/
cp ../App.css src/

# Install additional dependency
npm install axios

# Start the frontend development server
npm start
```

The browser should automatically open to http://localhost:3000.

If not, manually navigate to http://localhost:3000.

---

## STEP 5: Test the System

Now you have 3 terminals open:
1. **Terminal 1**: `ollama serve` (Ollama server)
2. **Terminal 2**: `python loan_advisor_backend.py` (FastAPI backend)
3. **Terminal 3**: `npm start` (React frontend)

### Test in Browser
1. Go to http://localhost:3000
2. Fill in the form:
   - Annual Income: `75000`
   - Existing Debt: `15000`
   - Credit Score: `720`
   - Requested Loan Amount: `25000`
3. Click "Evaluate Eligibility"
4. Wait 5-10 seconds (first request is slow, Ollama loads models into memory)
5. See results!

### Test via API
```bash
# In a new terminal
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "annual_income": 75000,
    "existing_debt": 15000,
    "credit_score": 720,
    "requested_loan_amount": 25000
  }'
```

### Run Evaluation Tests
```bash
# In a new terminal (backend and Ollama must be running)
cd /path/to/loan-advisor
python evaluation_framework.py
```

You should see all 5 tests pass.

---

## STEP 6: Understanding the Data Flow

### What Happens When You Submit?

1. **Frontend** (React) → Sends form data to backend
   ```javascript
   POST /evaluate with {annual_income, existing_debt, credit_score, requested_loan_amount}
   ```

2. **Backend** (FastAPI) → Receives data
   ```python
   @app.post("/evaluate")
   async def evaluate_loan_eligibility(request):
   ```

3. **RAG Pipeline** → Retrieves loan products
   ```
   Customer query → Vector store search → Find relevant products
   ```

4. **Agent** → Makes decisions
   ```
   LLM with tools → evaluate_eligibility() → check_loan_amount_approval()
   ```

5. **Ollama** (Local LLM) → Reasons and generates response
   ```
   Query → Mistral model → Response
   ```

6. **Backend** → Formats response with metrics
   ```python
   {eligible_products, risk_assessment, recommendation, requires_human_review}
   ```

7. **Frontend** → Displays results
   ```javascript
   Show eligible products, risk flags, recommendation
   ```

---

## COMMON ISSUES & FIXES

### Issue: "Connection refused" when accessing localhost:3000
**Solution**: 
- Check Terminal 3 is still running (`npm start`)
- Frontend might still be starting, wait 30 seconds
- Try refreshing the page

### Issue: "Cannot connect to http://localhost:8000" from frontend
**Solution**:
- Check Terminal 2 is still running (`python loan_advisor_backend.py`)
- Check CORS is enabled (it is by default)
- Check API_URL is correct: `http://localhost:8000`

### Issue: "Error: No module named 'langchain'"
**Solution**:
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### Issue: "ollama: command not found"
**Solution**:
- Ollama not installed, download from https://ollama.ai
- Or add to PATH if installed elsewhere

### Issue: First evaluation takes 30+ seconds
**Solution**:
- Normal! Ollama is loading the Mistral model (4GB) into memory
- Subsequent evaluations are much faster (~5 seconds)
- Use smaller models for faster responses: `ollama pull neural-chat`

### Issue: "HTTP 500" errors in backend logs
**Solution**:
- Check Ollama is running: `curl http://localhost:11434/api/tags`
- Check Ollama has models: `ollama list`
- Look at backend logs for specific error message

### Issue: Frontend form shows errors but no results
**Solution**:
- Check browser console (F12) for error messages
- Check backend logs for what failed
- Try different input values

---

## NEXT STEPS

### Option 1: Explore the Code
Read through:
- `loan_advisor_backend.py` - Understand RAG + Agent architecture
- `App.jsx` - Understand React component structure
- `evaluation_framework.py` - Understand how to measure system performance

### Option 2: Make Changes
Try:
- Add a new loan product in `LOAN_PRODUCTS`
- Change the risk assessment rules
- Add a new evaluation test case
- Modify the UI styling

### Option 3: Deploy
When ready, follow deployment guides:
- `DEPLOYMENT_APPROACH_1.md` - Deploy to Vercel + Railway (modern)
- `DEPLOYMENT_APPROACH_2.md` - Deploy with Docker to Render (monolithic)

---

## TERMINAL MANAGEMENT TIP

To avoid managing 3 terminals, use `tmux` or `screen`:

### Using Tmux
```bash
# Create session
tmux new-session -d -s loan-advisor

# Split into 3 panes
tmux split-window -h -t loan-advisor
tmux split-window -v -t loan-advisor:0.1

# Run in each pane
tmux send-keys -t loan-advisor:0.0 'ollama serve' C-m
tmux send-keys -t loan-advisor:0.1 'source venv/bin/activate && python loan_advisor_backend.py' C-m
tmux send-keys -t loan-advisor:0.2 'cd frontend && npm start' C-m

# View all panes
tmux attach -t loan-advisor
```

Or just use VS Code Terminal with multiple tabs.

---

## STOPPING THE SYSTEM

To clean up when done:

```bash
# Terminal 1 (Ollama): Ctrl+C
# Terminal 2 (Backend): Ctrl+C
# Terminal 3 (Frontend): Ctrl+C

# Deactivate Python venv (if desired)
deactivate

# Verify services are stopped
curl http://localhost:8000/health  # Should fail
curl http://localhost:3000  # Should fail
```

---

## NEXT: DEPLOYMENT

Once everything works locally, you're ready to deploy. Choose one:

**Approach 1: Modern (Separate Services)**
- Frontend → Vercel
- Backend → Railway
- See `DEPLOYMENT_APPROACH_1.md`

**Approach 2: Simple (Docker Monolith)**
- Everything → Render
- See `DEPLOYMENT_APPROACH_2.md`

---

## SUPPORT

If you get stuck:
1. Check the error message carefully
2. Google the error (often simple fixes)
3. Check the relevant guide (README, DEPLOYMENT guides)
4. Check backend logs for detailed errors
5. Try a different input to see if it's data-specific or systemic

---

**You're all set! Happy building! 🚀**
