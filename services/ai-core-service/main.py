from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os

# Import your inference functions (assuming they are in inference.py)
from .inference import (
    analyze_financial_data,
    categorize_transaction_text,
    recommend_recipes_stub,
    parse_command_stub
)

app = FastAPI(
    title="Multifaceted AI Core Service",
    description="Provides AI/ML models for finance, health, education, and assistant features.",
    version="0.1.0"
)

# --- Pydantic Models for Request/Response Validation ---

class TransactionInput(BaseModel):
    amount: float
    description: Optional[str] = None
    type: Optional[str] = None # e.g., EXPENSE, REVENUE

class FinancialAnalysisRequest(BaseModel):
    user_id: str
    transactions: List[TransactionInput]
    requested_insights: List[str] = Field(default_factory=list) # e.g., ["spending_patterns", "savings_suggestions"]
    # Add more context if needed: user_goals, account_balances etc.

class FinancialAnalysisResponse(BaseModel):
    insights: Dict[str, Any] # e.g., {"spending_patterns": {...}, "savings_suggestions": [...]}
    error: Optional[str] = None

class CategorizationRequest(BaseModel):
    description: str
    type: Optional[str] = None
    amount: Optional[float] = None

class CategorizationResponse(BaseModel):
    suggested_category: Optional[str] = None
    confidence: Optional[float] = None
    error: Optional[str] = None

# --- Add models for Health, Education, Assistant ---


# --- API Endpoints ---

@app.post("/analyze/financial", response_model=FinancialAnalysisResponse)
async def analyze_financial_endpoint(request: FinancialAnalysisRequest):
    """ Analyzes financial transactions to generate insights. """
    try:
        # Call the actual analysis function from inference.py
        results = analyze_financial_data(request.user_id, request.transactions, request.requested_insights)
        return FinancialAnalysisResponse(insights=results)
    except Exception as e:
        print(f"Error during financial analysis: {e}") # Log the error
        # Return generic error or more specific based on exception type
        raise HTTPException(status_code=500, detail=f"Failed to analyze financial data: {e}")


@app.post("/categorize/transaction", response_model=CategorizationResponse)
async def categorize_transaction_endpoint(request: CategorizationRequest):
    """ Suggests a category for a financial transaction based on its description. """
    if not request.description:
         raise HTTPException(status_code=400, detail="Transaction description is required.")
    try:
        # Call the categorization function from inference.py
        category, confidence = categorize_transaction_text(request.description)
        return CategorizationResponse(suggested_category=category, confidence=confidence)
    except Exception as e:
        print(f"Error during transaction categorization: {e}") # Log the error
        raise HTTPException(status_code=500, detail=f"Failed to categorize transaction: {e}")

# --- Add endpoints for Health, Education, Assistant ---
# @app.post("/recommend/recipes", ...)
# async def recommend_recipes_endpoint(...):
#     ...

# @app.post("/parse/command", ...)
# async def parse_command_endpoint(...):
#     ...


@app.get("/health")
async def health_check():
    """ Basic health check endpoint """
    return {"status": "ok"}

# --- Add startup events if needed to load models ---
# @app.on_event("startup")
# async def load_models():
#     print("Loading AI models...")
#     # Call functions in inference.py to load models into memory
#     load_finance_models()
#     load_assistant_models()
#     print("Models loaded.")
