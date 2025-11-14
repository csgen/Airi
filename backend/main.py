from fastapi import FastAPI, Request
import pandas as pd
import os
from sqlalchemy import create_engine

app = FastAPI(title="Airi Backend")

DATABASE_URL = os.getenv("APP_DATABASE_URL")
engine = create_engine(DATABASE_URL)

@app.get("/")
def root():
    return {"message": "Airi Backend is running!"}

@app.post("/api/upload_activity")
async def upload_activity(request: Request):
    data = await request.json()
    df = pd.DataFrame(data)

    df.to_sql("activity_logs", con=engine, if_exists="append", index=False)
    return {"status": "ok", "records_saved": len(df)}