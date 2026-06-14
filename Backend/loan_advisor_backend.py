"""
Loan Eligibility Advisor - FastAPI Backend
Uses RAG to ground answers in loan products, agents to make decisions
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import os
from datetime import datetime

# LLM & RAG
from langchain_ollama import ChatOllama
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain.agents import create_agent

# Plaid
import plaid
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest

app = FastAPI(title="Loan Eligibility Advisor")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ CONFIGURATION ============

# Ollama LLM (runs locally)
LLM = ChatOllama(
    model="llama3.2:1b ",  # or llama2, neural-chat, etc
    base_url="http://localhost:11434",
    temperature=0.3,
)

# Embeddings
EMBEDDINGS = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434",
)

# Plaid Configuration
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID", "sandbox")
PLAID_SECRET = os.getenv("PLAID_SECRET", "sandbox")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")

plaid_config = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        "clientId": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
    }
)
plaid_client = plaid_api.PlaidApi(plaid.ApiClient(plaid_config))

# ============ LOAN PRODUCTS DATABASE ============
# In production, this would come from a real database
LOAN_PRODUCTS = {
    "personal_loan_standard": {
        "name": "Personal Loan - Standard",
        "min_amount": 5000,
        "max_amount": 50000,
        "min_annual_income": 30000,
        "max_debt_to_income": 0.40,
        "min_credit_score": 620,
        "interest_rate_range": "6% - 12%",
    },
    "personal_loan_prime": {
        "name": "Personal Loan - Prime",
        "min_amount": 10000,
        "max_amount": 100000,
        "min_annual_income": 75000,
        "max_debt_to_income": 0.35,
        "min_credit_score": 740,
        "interest_rate_range": "3% - 6%",
    },
    "debt_consolidation": {
        "name": "Debt Consolidation Loan",
        "min_amount": 5000,
        "max_amount": 75000,
        "min_annual_income": 40000,
        "max_debt_to_income": 0.50,
        "min_credit_score": 640,
        "interest_rate_range": "5% - 10%",
    },
}

# ============ RAG SETUP ============

def setup_rag():
    """Initialize RAG with loan product documents"""
    loan_docs = "\n\n".join([
        f"Product: {prod['name']}\n"
        f"Min Amount: ${prod['min_amount']}\n"
        f"Max Amount: ${prod['max_amount']}\n"
        f"Min Annual Income Required: ${prod['min_annual_income']}\n"
        f"Max Debt-to-Income Ratio: {prod['max_debt_to_income']}\n"
        f"Min Credit Score: {prod['min_credit_score']}\n"
        f"Interest Rate Range: {prod['interest_rate_range']}"
        for prod in LOAN_PRODUCTS.values()
    ])
    
    # Create vector store with loan product info
    vector_store = Chroma.from_texts(
        texts=[loan_docs],
        embedding=EMBEDDINGS,
        persist_directory="./chroma_db",
    )
    return vector_store

vector_store = setup_rag()

# ============ TOOLS FOR AGENT ============

@tool
def get_loan_product_info(product_name: str) -> str:
    """Get detailed information about a specific loan product"""
    if product_name in LOAN_PRODUCTS:
        prod = LOAN_PRODUCTS[product_name]
        return json.dumps(prod)
    return f"Product {product_name} not found"

@tool
def evaluate_eligibility(annual_income: float, existing_debt: float, credit_score: int) -> dict:
    """
    Evaluate customer eligibility for loan products
    Returns list of eligible products with risk assessment
    """
    debt_to_income = existing_debt / annual_income if annual_income > 0 else 1.0
    
    eligible_products = []
    risk_flags = []
    
    # Check eligibility for each product
    for product_key, product in LOAN_PRODUCTS.items():
        is_eligible = (
            annual_income >= product["min_annual_income"] and
            debt_to_income <= product["max_debt_to_income"] and
            credit_score >= product["min_credit_score"]
        )
        
        if is_eligible:
            eligible_products.append({
                "product_key": product_key,
                "name": product["name"],
                "risk_level": "low" if credit_score > 740 else "medium",
            })
        
    # Flag risks
    if debt_to_income > 0.50:
        risk_flags.append("HIGH: Debt-to-income ratio exceeds 50%")
    if credit_score < 650:
        risk_flags.append("MEDIUM: Credit score below 650 - may face higher rates")
    if annual_income < 30000:
        risk_flags.append("HIGH: Income below minimum threshold for standard products")
    
    return {
        "eligible_products": eligible_products,
        "risk_flags": risk_flags,
        "debt_to_income_ratio": round(debt_to_income, 2),
        "requires_human_review": len(risk_flags) > 1 or any("HIGH" in flag for flag in risk_flags),
    }

@tool
def check_loan_amount_approval(annual_income: float, loan_amount: float) -> dict:
    """Check if loan amount is reasonable for the customer's income"""
    # Rule of thumb: loan should not exceed 5x annual income
    max_recommended = annual_income * 5
    
    return {
        "requested_amount": loan_amount,
        "max_recommended_amount": max_recommended,
        "is_reasonable": loan_amount <= max_recommended,
        "approval_confidence": "high" if loan_amount <= max_recommended else "low",
    }

# ============ AGENT SETUP ============

def setup_agent():
    """Create tool-calling agent"""
    tools = [
        get_loan_product_info,
        evaluate_eligibility,
        check_loan_amount_approval,
    ]
    

    # ChatPromptTemplate.from_messages([
    #     ("system", 
    prompt =  """You are a helpful loan eligibility advisor. Use the provided tools to:
1. Look up loan product requirements
2. Evaluate customer eligibility based on income, debt, and credit score
3. Check if loan amounts are reasonable
4. Provide clear recommendations on which products the customer qualifies for
5. Flag any risks that require human review

Always be conservative - if uncertain, flag for human review.
Make decisions based on actual data, not assumptions."""
         
    #      ),
    #     ("user", "{input}"),
    #     MessagesPlaceholder(variable_name="agent_scratchpad"),
    # ])
    
    # agent = create_tool_calling_agent(LLM, tools, prompt)
    # agent_executor = AgentExecutor(
    #     agent=agent,
    #     tools=tools,
    #     verbose=False,
    #     handle_parsing_errors=True,
    # )

    agent = create_agent(model=LLM, tools = tools, system_prompt=prompt)
    return agent #agent_executor

agent_executor = setup_agent()

# ============ DATA MODELS ============

class LoanEligibilityRequest(BaseModel):
    annual_income: float
    existing_debt: float
    credit_score: int
    requested_loan_amount: float

class EvaluationResult(BaseModel):
    customer_profile: dict
    eligible_products: list
    risk_assessment: list
    recommendation: str
    requires_human_review: bool
    evaluation_timestamp: str

# ============ EVALUATION METRICS ============

class EvaluationMetrics:
    """Track evaluation metrics for post-launch analysis"""
    def __init__(self):
        self.total_evaluations = 0
        self.flagged_for_review = 0
        self.high_risk_flags = 0
    
    def record_evaluation(self, result: dict):
        self.total_evaluations += 1
        if result.get("requires_human_review"):
            self.flagged_for_review += 1
        if any("HIGH" in flag for flag in result.get("risk_flags", [])):
            self.high_risk_flags += 1
    
    def get_metrics(self):
        return {
            "total_evaluations": self.total_evaluations,
            "flagged_for_review": self.flagged_for_review,
            "flag_rate_percent": round(
                (self.flagged_for_review / max(1, self.total_evaluations)) * 100, 2
            ),
            "high_risk_flags": self.high_risk_flags,
        }

metrics = EvaluationMetrics()

# ============ API ENDPOINTS ============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "Loan Eligibility Advisor"}

@app.post("/evaluate", response_model=EvaluationResult)
async def evaluate_loan_eligibility(request: LoanEligibilityRequest):
    """
    Evaluate loan eligibility using RAG + Agent
    
    This endpoint:
    1. Uses tools to check product eligibility
    2. Evaluates risks
    3. Recommends products
    4. Flags for human review if needed
    """
    try:
        # Prepare context for agent
        query = f"""
        Customer Profile:
        - Annual Income: ${request.annual_income:,.0f}
        - Existing Debt: ${request.existing_debt:,.0f}
        - Credit Score: {request.credit_score}
        - Requested Loan Amount: ${request.requested_loan_amount:,.0f}
        
        Please:
        1. Evaluate which loan products this customer is eligible for
        2. Check if the requested loan amount is reasonable
        3. Identify any risks or concerns
        4. Provide a clear recommendation
        """
        
        # Run agent
        result = agent_executor.invoke({
            "messages": [
                {"role":"user",
                 "content":query
                }
             ]
            })
          # Extract response from v1.0 format
        agent_response = ""
        if "messages" in result and result["messages"]:
            # Get the last message which contains the agent's response
            last_message = result["messages"][-1]
            if hasattr(last_message, "content"):
                agent_response = last_message.content
            elif isinstance(last_message, dict) and "content" in last_message:
                agent_response = last_message["content"]
        
        
        # Get detailed eligibility assessment
        eligibility = evaluate_eligibility.func(
            annual_income=request.annual_income,
            existing_debt=request.existing_debt,
            credit_score=request.credit_score,
        )
        
        # Record metrics
        metrics.record_evaluation(eligibility)
        
        # Build response
        response = EvaluationResult(
            customer_profile={
                "annual_income": request.annual_income,
                "existing_debt": request.existing_debt,
                "debt_to_income_ratio": eligibility["debt_to_income_ratio"],
                "credit_score": request.credit_score,
                "requested_loan_amount": request.requested_loan_amount,
            },
            eligible_products=[
                {
                    "name": prod["name"],
                    "product_key": prod["product_key"],
                    "risk_level": prod["risk_level"],
                }
                for prod in eligibility["eligible_products"]
            ],
            risk_assessment=eligibility["risk_flags"],
            recommendation=agent_response if agent_response else "Please contact our loan specialists for a custom evaluation.",
            requires_human_review=eligibility["requires_human_review"],
            evaluation_timestamp=datetime.now().isoformat(),
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@app.get("/metrics")
async def get_metrics():
    """Get evaluation metrics"""
    return metrics.get_metrics()

@app.get("/products")
async def get_loan_products():
    """Get all available loan products"""
    return {
        "products": LOAN_PRODUCTS,
        "count": len(LOAN_PRODUCTS),
    }

# ============ PLAID INTEGRATION (Optional) ============
# This is a placeholder for real Plaid integration
# In production, you'd implement token exchange and transaction pulling

@app.post("/plaid/create-link-token")
async def create_plaid_link_token():
    """
    Create a Plaid Link token for frontend to use
    Frontend would then use this to open Plaid Link modal
    """
    try:
        # This is a simplified example
        return {
            "link_token": "link-sandbox-token-example",
            "expiration": "2024-12-31T23:59:59Z",
            "message": "Use this link token in Plaid Link on frontend"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("loan_advisor_backend:app", host="0.0.0.0", port=8000, log_level="info", reload=True)
