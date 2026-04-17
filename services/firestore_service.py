import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Try to initialize Firestore, fallback to in-memory dictionary
try:
    from google.cloud import firestore
    db = firestore.Client()
    USE_FIRESTORE = True
    logger.info("Successfully initialized Google Cloud Firestore.")
except Exception as e:
    logger.warning(f"Failed to initialize Firestore. Using in-memory fallback. Reason: {e}")
    db = None
    USE_FIRESTORE = False

# In-memory session store
_sessions = {}

def get_session(session_id):
    """
    Retrieves the chat history for a given session ID.
    Returns a list of messages.
    """
    try:
        if USE_FIRESTORE:
            doc_ref = db.collection("sessions").document(session_id)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                history_json = data.get("history", "[]")
                return json.loads(history_json)
            return []
        else:
            if session_id in _sessions:
                return json.loads(_sessions[session_id].get("history", "[]"))
            return []
    except Exception as e:
        logger.error(f"Error fetching session {session_id}: {e}")
        return []

def save_session(session_id, history):
    """
    Saves the chat history for a given session ID.
    """
    try:
        history_json = json.dumps(history)
        timestamp = datetime.now(timezone.utc)
        
        data = {
            "history": history_json,
            "updated_at": timestamp
        }
        
        if USE_FIRESTORE:
            db.collection("sessions").document(session_id).set(data)
        else:
            _sessions[session_id] = {
                "history": history_json,
                "updated_at": timestamp.isoformat()
            }
        return True
    except Exception as e:
        logger.error(f"Error saving session {session_id}: {e}")
        return False
