import os
import logging
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore

logging.basicConfig(level=logging.INFO)

# Use the repo-local service account key path (robust to current working dir)
KEY_PATH = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")
PROJECT_ID = "emotion-aware-interview-coach"

db = None

if not os.path.exists(KEY_PATH):
    logging.warning("Firebase service account key not found at %s. Firebase disabled.", KEY_PATH)
else:
    try:
        cred = credentials.Certificate(KEY_PATH)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {"projectId": PROJECT_ID})
        db = firestore.client()
        logging.info("Initialized Firebase Firestore client for project: %s", PROJECT_ID)
    except Exception:
        logging.exception("Failed to initialize Firebase Admin SDK. Firebase disabled.")
        db = None


def save_timeline_to_firestore(video_id, timeline_data, metadata=None):
    """Save emotion detection timeline to Firestore.

    Args:
        video_id: unique identifier for the video (e.g., UUID string)
        timeline_data: list of timeline entries (strings or dicts with emotion/timestamp info)
        metadata: optional dict with extra metadata (filename, user_id, etc.)

    Returns:
        document_id of the created/updated document on success, None on failure.

    Raises:
        RuntimeError if Firestore is not initialized.
    """
    if db is None:
        raise RuntimeError("Firestore is not initialized. Check service account key and initialization logs.")

    try:
        doc_data = {
            "video_id": video_id,
            "timeline": timeline_data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        if metadata:
            doc_data.update(metadata)

        # Use video_id as document ID for easy retrieval
        db.collection("analyses").document(video_id).set(doc_data)
        logging.info("Saved timeline to Firestore for video: %s", video_id)
        return video_id
    except Exception:
        logging.exception("Failed to save timeline to Firestore for video: %s", video_id)
        raise


def get_timeline_from_firestore(video_id):
    """Retrieve emotion detection timeline from Firestore.

    Args:
        video_id: unique identifier for the video

    Returns:
        dict with timeline and metadata, or None if document not found.

    Raises:
        RuntimeError if Firestore is not initialized.
    """
    if db is None:
        raise RuntimeError("Firestore is not initialized. Check service account key and initialization logs.")

    try:
        doc = db.collection("analyses").document(video_id).get()
        if doc.exists:
            logging.info("Retrieved timeline from Firestore for video: %s", video_id)
            return doc.to_dict()
        else:
            logging.warning("No timeline found in Firestore for video: %s", video_id)
            return None
    except Exception:
        logging.exception("Failed to retrieve timeline from Firestore for video: %s", video_id)
        raise


def delete_timeline_from_firestore(video_id):
    """Delete an emotion detection timeline from Firestore.

    Args:
        video_id: unique identifier for the video

    Returns:
        True on success, False on failure.

    Raises:
        RuntimeError if Firestore is not initialized.
    """
    if db is None:
        raise RuntimeError("Firestore is not initialized. Check service account key and initialization logs.")

    try:
        db.collection("analyses").document(video_id).delete()
        logging.info("Deleted timeline from Firestore for video: %s", video_id)
        return True
    except Exception:
        logging.exception("Failed to delete timeline from Firestore for video: %s", video_id)
        return False


def list_timelines_from_firestore(limit=100):
    """List all emotion detection timelines from Firestore.

    Args:
        limit: maximum number of documents to retrieve

    Returns:
        list of dicts with timeline data, or empty list if none found.

    Raises:
        RuntimeError if Firestore is not initialized.
    """
    if db is None:
        raise RuntimeError("Firestore is not initialized. Check service account key and initialization logs.")

    try:
        docs = db.collection("analyses").limit(limit).stream()
        results = [doc.to_dict() for doc in docs]
        logging.info("Retrieved %d timelines from Firestore", len(results))
        return results
    except Exception:
        logging.exception("Failed to list timelines from Firestore")
        raise

