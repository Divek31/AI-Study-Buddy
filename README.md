# AI Study Buddy

An interactive, AI-powered learning workspace designed to help you organize notes, generate interactive quizzes, and learn faster using the Feynman Technique.

## Features
- **Smart Note Processing (RAG)**: Chat with your custom PDF notes directly.
- **Feynman Technique AI**: Flattens complex topics into simple analogies.
- **Gamified Progress**: Earn XP and level up for studying consistently.
- **Auto-Generated Resources**: Get dynamic flashcards, PDF exports, and audio study guides instantly.

## Local Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Divek31/AI-Study-Buddy.git
   cd AI-Study-Buddy
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your Google Gemini API Key:**
   This project relies on the Google Gemini Pro 2.5 API.
   - Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and generate an API key.
   - Create a file named `.env` in the root folder of this project.
   - Insert your API key into the `.env` file like this:
     ```env
     GEMINI_API_KEY=your_actual_api_key_here
     ```

5. **Run the Streamlit app:**
   ```bash
   python -m streamlit run app.py
   ```
## 🔗 Live Demo
👉 https://ai-buddy-study.streamlit.app
