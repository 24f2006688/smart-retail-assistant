# ShopBot AI — Smart Retail Assistant

## Chosen vertical: Retail & E-commerce

A smart shopping chatbot and product search assistant powered by Google Gemini AI.

## Features
- Interactive chat interface with intelligent product recommendations
- Contextual product search and display
- Auto-scrolling, typing indicators, and quick suggestion chips
- Chat history tracking

## Google Services Used
- **Google Gemini AI**: Provides the conversational intelligence and structured product search capabilities.
- **Google Firestore**: Maintains user chat session histories across requests.
- **Google Cloud Run** (Planned): Docker-ready setup for scalable, containerized deployment.

## How to run locally

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)
- A Google Gemini API key

### Steps
1. Create a virtual environment and load it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your environment variables (in `.env` or exported in shell):
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   PORT=8080
   ```
4. Run the application:
   ```bash
   python app.py
   ```
   Or use the provided Dockerfile:
   ```bash
   docker build -t shopbot .
   docker run -p 8080:8080 -e GEMINI_API_KEY=your_gemini_api_key shopbot
   ```

## Approach and logic explanation
The app aims to be a single-page interactive experience mirroring modern e-commerce "smart assistants". 
- **Backend (Flask)**: Handles the API contract, orchestrates communication between the frontend, the generative AI logic, and the database.
- **AI Service (Gemini)**: We employ structured prompting to enforce JSON output for product searches and maintain a specific conversational brand persona (ShopBot) for chats.
- **Database (Firestore)**: Stores the past conversation context using unique session IDs. If Firestore is unavailable, the application degrades gracefully to use an in-memory dictionary.
- **Frontend (Vanilla JS + CSS)**: Leverages pure CSS for an attractive UI without external frameworks, managing state asynchronously to provide a snappy experience.

## Assumptions made
- The fallback logic for database operations strictly handles standard JSON-serializable dictionaries.
- Without a real inventory database, Gemini is trusted to "hallucinate" high-quality, realistic-looking products for demonstration purposes.