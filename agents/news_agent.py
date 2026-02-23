# News & sentiment

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any 
import asyncio
import uvicorn
from datetime import datetime
import json
import os

app = FastAPI(title="Creation of News Agent", description="News Agents", version="1.0.0")


@app.get("/health")
async def health_check():
    return {'status': 'Helthy', 'version':'1.0.0'}

@app.get('/stock/time')
async def stock_time():
    return datetime.now().isoformat()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
