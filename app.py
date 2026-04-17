import os
import logging
from flask import Flask, request, jsonify, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# Import our custom services
from services.gemini_service import get_ai_response, search_and_recommend
from services.firestore_service import get_session, save_session

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure Rate Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

@app.route("/")
def index():
    """Renders the main shopping assistant UI"""
    try:
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/health")
def health():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route("/api/chat", methods=["POST"])
@limiter.limit("30 per minute")
def chat():
    """
    Handles chat messages from the user.
    Expects JSON: {"message": str, "session_id": str}
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Missing JSON payload"}), 400
            
        message = data.get("message", "").strip()
        session_id = data.get("session_id", "").strip()
        
        # Validation
        if not message or not session_id:
            return jsonify({"error": "Fields 'message' and 'session_id' are required"}), 400
            
        if len(message) > 1000:
            return jsonify({"error": "Message exceeds maximum length of 1000 characters"}), 400
            
        # Get history from Firestore (or in-memory fallback)
        history = get_session(session_id)
        
        # Call Gemini AI
        response_text, updated_history = get_ai_response(message, history)
        
        # Save updated history
        save_session(session_id, updated_history)
        
        return jsonify({"response": response_text}), 200
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": "An unexpected error occurred processing your request."}), 500

@app.route("/api/products/search", methods=["GET"])
def search_products():
    """
    Handles product search using Gemini AI to simulate an inventory.
    Query Params: ?q=...&category=...
    """
    try:
        query = request.args.get("q", "").strip()
        category = request.args.get("category", "All").strip()
        
        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
            
        # Limit query length
        if len(query) > 100:
            query = query[:100]
            
        products = search_and_recommend(query, category)
        
        return jsonify({"products": products}), 200
        
    except Exception as e:
        logger.error(f"Error in product search endpoint: {e}")
        return jsonify({"error": "An unexpected error occurred while searching for products."}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
