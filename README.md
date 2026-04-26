# Emotion-Aware Interview Coach
A FastAPI microservice that detects facial emotions in video and returns LLM-generated language feedback

This project analyses video frames for facial emotions using a YOLO11-based model, pairs each emotion shift with spoken or written transcripts, and feeds them into a BitNet LLM to produce actionable self-improvement feedback. The target use-case is interview practice: by reviewing what you said alongside how the listener reacted, you learn what to say and what to avoid. It was built as coursework for 5CCSACCA Cloud Computing for Artificial Intelligence at King's College London.


## Project Context

| | |
|---|---|
| **Type** | Coursework project (5CCSACCA) |
| **Institution** | King's College London |
| **Original repository** | https://github.com/5CCSACCA/coursework-sdsdsdasa |
| **This repository** | Public portfolio version |
| **Version** | Phase 4 — April 2026 |


## What I Built

- Designed and implemented the full FastAPI service in `app/api.py`, including video upload, emotion timeline generation, and LLM analysis endpoints
- Integrated the YOLO11 emotion detection model (`service/serviceA.py`) and wrapped it for async video analysis
- Built the BitNet LLM wrapper (`app/bitnet_llm.py`) for utterance-level language feedback
- Set up dual persistence: SQLite via SQLAlchemy for analysis history and optional Firestore for timeline metadata
- Containerised the service with Docker and Docker Compose for reproducible deployment
- Trained and evaluated the YOLO11 model on the RAF-DB facial expression dataset


## Features

- Upload a video and receive a per-second emotion timeline (e.g. `00:03 Sad -> Happy (0.66)`)
- Seven emotion classes: anger, disgust, fear, happiness, neutral, sadness, surprise
- BitNet LLM endpoint that takes an utterance and an emotion change and returns a reason, suggestions, and confidence score
- Analysis history stored in a local SQLite database, queryable via REST
- Optional Firestore integration for cloud-persisted timelines (gracefully disabled if key is absent)
- Dockerfile and Docker Compose for one-command deployment


## Architecture

```
Video upload ─► serviceA (YOLO11) ─► emotion timeline
                                          │
                                          ▼
                           app/api.py (FastAPI)  ◄── SQLite (app.db)
                                          │         ◄── Firestore (optional)
                                          ▼
                        bitnet_llm.py (BitNet LLM) ─► feedback
```


## Tech Stack

| Layer | Technology |
|---|---|
| **API** | FastAPI + Uvicorn |
| **Emotion detection** | YOLO11 (Ultralytics) |
| **LLM feedback** | BitNet |
| **Local persistence** | SQLite via SQLAlchemy |
| **Cloud persistence** | Firebase Firestore (optional) |
| **Containerisation** | Docker + Docker Compose |
| **Language** | Python 3.11 |


## Setup

### Prerequisites

- Python 3.10+
- Docker & Docker Compose (optional, for containerised runs)
- *(Optional)* A Firebase service account JSON at `firebase/serviceAccountKey.json` to enable Firestore

### Install dependencies locally

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```


## Running the Project

### Local development server

```bash
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

### Quick single-image test

```bash
python app/main.py
```

### Docker Compose (recommended for reproducibility)

```bash
docker compose build
docker compose up
```


## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/analyze` | Upload a video file for emotion analysis |
| `GET` | `/analyses` | List all analysis records |
| `GET` | `/analyses/{id}` | Retrieve a single analysis with its timeline |
| `POST` | `/bitnet/analyze` | Run LLM feedback on an utterance + emotion change |
| `GET` | `/firestore/analyses/{video_id}` | Retrieve a timeline from Firestore |

**Example — analyse a video:**
```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -F "file=@./media/video/example2.mp4"
```

**Example — get LLM feedback:**
```bash
curl -sS -X POST http://127.0.0.1:8000/bitnet/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"I told them I was disappointed, but I still care.", "from_emotion":"neutral", "to_emotion":"upset"}'
```


## Project Structure

```
coursework-sdsdsdasa/
├── app/
│   ├── api.py              — FastAPI application and all endpoints
│   ├── main.py             — Quick local single-image runner
│   └── bitnet_llm.py       — BitNet LLM wrapper
├── service/
│   ├── serviceA.py         — YOLO11 emotion detection and video analysis
│   └── serviceB.py         — LLM integration support
├── data/
│   ├── db.py               — SQLAlchemy + SQLite setup
│   └── models.py           — Analysis ORM model
├── firebase/
│   └── firebase_client.py  — Firestore helper (key excluded from repo)
├── media/
│   ├── image/              — Sample face images
│   └── video/              — Sample video files
├── scripts/
│   └── run_analysis_and_llm.sh  — End-to-end shell script
├── existModel/             — Pre-trained model files and notebook
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── rafdb.yaml              — YOLO dataset config for RAF-DB
```


## Academic Note

This repository is provided for portfolio and demonstration purposes only. It should not be copied, reused, or submitted as academic work.
