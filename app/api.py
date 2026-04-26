from fastapi import FastAPI, UploadFile, File
import shutil
import uuid
import os
import sys
import asyncio
import json
sys.path.append(os.path.dirname(os.path.dirname(__file__)))



# local imports
from service import serviceA
from data.db import Base, engine, SessionLocal
from data.models import Analysis
Base.metadata.create_all(bind=engine)
import logging

# Firebase Firestore for timeline metadata (Storage removed)
from firebase.firebase_client import save_timeline_to_firestore, get_timeline_from_firestore, list_timelines_from_firestore, delete_timeline_from_firestore
from app.bitnet_llm import get_default_bitnet


# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    # Save uploaded file
    video_id = str(uuid.uuid4())
    temp_path = f"{UPLOAD_DIR}/{video_id}.mp4"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Call your serviceA logic (the model analysis) in a thread
    timeline = await asyncio.to_thread(serviceA.analyze_video, serviceA.model, temp_path)

    # -------------------------------
    # NEW (Stage 4): Save to database
    # -------------------------------
    db = SessionLocal()
    analysis = Analysis(
        video_id=video_id,
        input_filename=file.filename,
        status="completed",
        timeline_json=json.dumps(timeline, ensure_ascii=False),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    db.close()
    # -------------------------------
    # Also persist timeline to Firestore (best-effort)
    try:
        save_timeline_to_firestore(video_id, timeline, metadata={"input_filename": file.filename})
    except Exception as e:
        logging.exception("Failed to save timeline to Firestore for video %s: %s", video_id, e)
    
    # Return timeline to client
    return {
        "analysis_id": analysis.id,
        "video_id": video_id,
        "timeline": timeline
    }


# -------------------------------
# NEW (Stage 4): GET history
# -------------------------------
@app.get("/analyses")
def list_analyses():
    db = SessionLocal()
    rows = db.query(Analysis).all()
    db.close()

    return [
        {
            "id": r.id,
            "video_id": r.video_id,
            "input_filename": r.input_filename,
            "created_at": r.created_at,
            "status": r.status
        }
        for r in rows
    ]


@app.get("/analyses/{analysis_id}")
def get_analysis(analysis_id: int):
    db = SessionLocal()
    row = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    db.close()

    if not row:
        return {"error": "Analysis not found"}

    return {
        "id": row.id,
        "video_id": row.video_id,
        "input_filename": row.input_filename,
        "created_at": row.created_at,
        "status": row.status,
        "timeline": json.loads(row.timeline_json)
    }
# -------------------------------


@app.get("/firestore/analyses/{video_id}")
def get_analysis_firestore(video_id: str):
    try:
        doc = get_timeline_from_firestore(video_id)
        if not doc:
            return {"error": "Not found"}
        return doc
    except Exception as e:
        logging.exception("Error fetching Firestore analysis %s: %s", video_id, e)
        return {"error": "internal"}



@app.post("/bitnet/analyze")
async def bitnet_analyze(payload: dict):
    """Analyze a short utterance and emotion change.

    Expected JSON payload: {"text": str, "from_emotion": str (optional), "to_emotion": str (optional)}
    """
    text = payload.get("text")
    from_emotion = payload.get("from_emotion")
    to_emotion = payload.get("to_emotion")

    if not text:
        return {"error": "missing 'text' in payload"}

    bitnet = get_default_bitnet()
    # Run analysis in thread to avoid blocking
    result = await asyncio.to_thread(bitnet.analyze, text, from_emotion, to_emotion)
    return result

# File storage endpoints removed - timelines are now stored in Firestore only
