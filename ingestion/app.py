from fastapi import FASTAPI

app = FASTAPI()

@app.post('/loan/approval')
def loan_approval(application):
    pass

@app.post("/fraud/investigate")
def fraud_investigate():
    pass

@app.post("/rag/query")
def rag_query():
    pass 

@app.post("/support/chat")
def support_chat():
    pass