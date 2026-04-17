import os
import json
import logging
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY environment variable not found.")

MODEL_NAME = "gemini-1.5-flash"

SYSTEM_PROMPT = """You are ShopBot, a helpful, enthusiastic, and knowledgeable retail shopping assistant.
Your goal is to help users find products, offer gift ideas, and assist with their shopping needs.
Keep your responses concise, friendly, and well-formatted. Focus on retail and e-commerce topics.
If asked about topics outside retail, politely steer the conversation back to shopping."""

def get_ai_response(user_message, history):
    """
    Sends a message to Gemini and returns the response along with the updated history.
    Keeps the last 20 messages.
    """
    try:
        # Initialize model
        model = genai.GenerativeModel(
            MODEL_NAME,
            system_instruction=SYSTEM_PROMPT
        )
        
        # Format history for Gemini API
        # Gemini expects roles to be 'user' or 'model'
        formatted_history = []
        for msg in history:
            role = "model" if msg.get("role") in ["bot", "model"] else "user"
            formatted_history.append({
                "role": role,
                "parts": [msg.get("content", "")]
            })
            
        # Start chat session with history
        chat = model.start_chat(history=formatted_history)
        
        # Send new message
        response = chat.send_message(user_message)
        response_text = response.text
        
        # Update history
        updated_history = history.copy()
        updated_history.append({"role": "user", "content": user_message})
        updated_history.append({"role": "model", "content": response_text})
        
        # Keep only the last 20 messages
        if len(updated_history) > 20:
            updated_history = updated_history[-20:]
            
        return response_text, updated_history
        
    except Exception as e:
        logger.error(f"Error getting AI response: {e}")
        err_msg = "I'm sorry, I'm having trouble connecting to my brain right now. Please try again later."
        
        updated_history = history.copy()
        updated_history.append({"role": "user", "content": user_message})
        updated_history.append({"role": "model", "content": err_msg})
        
        return err_msg, updated_history

def search_and_recommend(query, category="All"):
    """
    Prompts Gemini to return a JSON array of 4 products based on the query.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        prompt = f"""
        You are an e-commerce search engine API. The user is searching for "{query}" 
        in the category "{category}".
        
        Generate realistic mock data for 4 products that match this search.
        Return ONLY a raw JSON array (no markdown code blocks, no explanation) of 4 objects.
        
        Each object MUST have the following structure exactly:
        {{
            "id": "unique string or number",
            "name": "Product Name",
            "price": numeric value indicating price in USD,
            "category": "category name",
            "rating": numeric value between 1.0 and 5.0,
            "description": "short description (1-2 sentences)",
            "inStock": boolean true or false,
            "imageKeyword": "a single emoji that represents the product well"
        }}
        """
        
        response = model.generate_content(prompt)
        text_response = response.text.strip()
        
        # Clean up in case Gemini returns markdown code blocks
        if text_response.startswith("```json"):
            text_response = text_response.replace("```json", "", 1)
        if text_response.endswith("```"):
            text_response = text_response[::-1].replace("```", "", 1)[::-1]
            
        text_response = text_response.strip()
        products = json.loads(text_response)
        
        if not isinstance(products, list) or len(products) == 0:
            raise ValueError("Response is not a valid list of products")
            
        return products[:4]
        
    except Exception as e:
        logger.error(f"Error in search_and_recommend: {e}")
        return get_fallback_products(query)

def get_fallback_products(query):
    """
    Returns 2 hardcoded products in case of error.
    """
    return [
        {
            "id": "err-1",
            "name": f"Premium {query.capitalize() if query else 'Item'}",
            "price": 99.99,
            "category": "General",
            "rating": 4.5,
            "description": "A high-quality product matching your search. (Fallback item)",
            "inStock": True,
            "imageKeyword": "📦"
        },
        {
            "id": "err-2",
            "name": "Standard Option",
            "price": 29.99,
            "category": "Basic",
            "rating": 4.0,
            "description": "A reliable and affordable alternative. (Fallback item)",
            "inStock": False,
            "imageKeyword": "🛒"
        }
    ]
