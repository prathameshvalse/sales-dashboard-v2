from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import pandas as pd
import json

from models import LeadCreate, LeadUpdate, LeadResponse, LoginRequest, AIPitchRequest
import database as db
import ai

app = FastAPI(title="Sales Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Sales Dashboard API"}

@app.post("/api/auth/login")
def login(request: LoginRequest):
    # Simple hardcoded auth based on the original streamlit logic
    users = {
        "pratham": {"role": "Salesperson", "name": "Pratham"},
        "dolly": {"role": "Salesperson", "name": "Dolly"},
        "sanket": {"role": "Salesperson", "name": "Sanket"},
        "admin": {"role": "Leadership", "name": "Admin"}
    }
    
    # In the original app, it used a simple hash check for specific passwords.
    # For this migration, we'll allow these usernames with password "password123" for simplicity.
    if request.username.lower() in users and request.password == "password123":
        return users[request.username.lower()]
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/leads")
def get_leads(salesperson: str = None):
    df = db.load_data()
    if salesperson:
        df = df[df['salesperson'] == salesperson]
    
    # Convert NaNs to None for JSON serialization
    df = df.where(pd.notnull(df), None)
    return json.loads(df.to_json(orient="records"))

@app.post("/api/leads")
def create_lead(lead: LeadCreate):
    new_lead = db.add_lead(lead.dict())
    if new_lead:
        return new_lead
    raise HTTPException(status_code=500, detail="Failed to create lead")

@app.put("/api/leads/{lead_id}")
def update_lead(lead_id: str, lead: LeadUpdate):
    update_data = {k: v for k, v in lead.dict().items() if v is not None}
    if db.update_lead(lead_id, update_data):
        return {"status": "success", "message": "Lead updated"}
    raise HTTPException(status_code=404, detail="Lead not found or failed to update")

@app.post("/api/ai/pitch")
def generate_pitch(request: AIPitchRequest):
    pitch = ai.generate_sales_pitch(
        request.lead_name, 
        request.category, 
        request.comments, 
        request.po_value
    )
    return {"pitch": pitch}

@app.get("/api/metrics")
def get_metrics():
    df = db.load_data()
    total_pipeline = df['po_value_expected'].sum()
    active_leads = len(df[df['status'] != 'Closed Won'])
    closed_won = df[df['status'] == 'Closed Won']['po_value_expected'].sum()
    
    return {
        "total_pipeline": total_pipeline,
        "active_leads": active_leads,
        "closed_won": closed_won
    }
