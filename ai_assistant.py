import json

def _get_genai():
    import google.generativeai as genai
    return genai

def initialize_gemini(api_key):
    """Configures the Gemini API client."""
    genai = _get_genai()
    genai.configure(api_key=api_key)

def get_rag_context(vector_store, query, k=5):
    """Retrieves relevant chunks from the vector store."""
    results = vector_store.similarity_search(query, k=k)
    context = "\n\n".join([doc.page_content for doc in results])
    return context

def answer_question(vector_store, query, global_search=False):
    """Answers a question strictly using the provided context, or general AI knowledge if Global Search is on."""
    if not global_search and vector_store:
        context = get_rag_context(vector_store, query)
        prompt = f"""You are an AI Study Buddy. Answer the student's question based strictly on the provided context.
If the answer is not contained in the context, say "I cannot answer this based on the provided document."

Context:
{context}

Question: {query}
Answer:"""
    else:
        prompt = f"""You are a helpful AI Study Buddy. Answer the student's question accurately and clearly based on your general knowledge.

Question: {query}
Answer:"""

    model = _get_genai().GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    return response.text

def feynman_explain(vector_store, topic, global_search=False):
    """Explains a topic simply, utilizing analogies, with or without provided context."""
    if not global_search and vector_store:
        context = get_rag_context(vector_store, topic, k=3)
        prompt = f"""You are an AI Study Buddy using the Feynman Technique. 
Explain the following topic simply as if to a middle school student. Use clear analogies and avoid unnecessary jargon. 
Base your explanation on the core concepts found in the provided context.

Context:
{context}

Topic to explain: {topic}
Explanation:"""
    else:
        prompt = f"""You are an AI Study Buddy using the Feynman Technique. 
Explain the following topic simply as if to a middle school student. Use clear analogies and avoid unnecessary jargon based on your general knowledge.

Topic to explain: {topic}
Explanation:"""

    model = _get_genai().GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    return response.text

def generate_quiz(vector_store, global_search=False, topic="general knowledge", num_questions=5):
    """Generates a dynamic length quiz (JSON format) supporting MCQ and MSQ."""
    
    json_schema = '''
    [
      {
        "question": "The question text here?",
        "type": "MCQ", // or "MSQ" for multiple select
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answers": ["Option A"], // List of correct options
        "explanation": "Explanation of why these are correct."
      }
    ]
    '''

    if not global_search and vector_store:
        context = get_rag_context(vector_store, "main ideas concepts summary", k=6)
        prompt = f"""Based on the following context extracted from study notes, generate exactly {num_questions} quiz questions. Include a mix of Multiple Choice (MCQ - one correct answer) and Multiple Select (MSQ - more than one correct answer).
Return the output STRICTLY as a valid JSON array matching this schema:
{json_schema}
Do NOT wrap the JSON in markdown code blocks. Just output the raw JSON array.

Context:
{context}

Quiz JSON:"""
    else:
        prompt = f"""Generate exactly {num_questions} quiz questions on the topic of '{topic}'. Include a mix of Multiple Choice (MCQ - one correct answer) and Multiple Select (MSQ - more than one correct answer).
Return the output STRICTLY as a valid JSON array matching this schema:
{json_schema}
Do NOT wrap the JSON in markdown code blocks. Just output the raw JSON array.

Quiz JSON:"""

    model = _get_genai().GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
    response = model.generate_content(prompt)
    
    try:
        # Validate that it's parseable JSON
        quiz_data = json.loads(response.text)
        return quiz_data
    except json.JSONDecodeError:
        print("Failed to parse JSON quiz out of response:", response.text)
        return []

def summarize_notes(vector_store, global_search=False, topic="general knowledge"):
    """Generates a comprehensive summary of the uploaded study notes, or asks for a general summary if global search."""
    if not global_search and vector_store:
        context = get_rag_context(vector_store, "main ideas overall summary key points", k=8)
        prompt = f"""Based on the following extracted context from study notes, provide a concise but comprehensive summary.
Highlight the main concepts and key takeaways.

Context:
{context}

Summary:"""
    else:
        prompt = f"""Provide a concise but comprehensive summary of the key concepts and ideas regarding the topic of '{topic}'.

Summary:"""

    model = _get_genai().GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    return response.text

def generate_flashcards(vector_store, topic="key concepts and definitions", global_search=False):
    """Generates a set of flashcards from the notes or general knowledge."""
    if not global_search and vector_store:
        context = get_rag_context(vector_store, topic, k=6)
        prompt = f"""Based on the following context, generate 5-10 useful flashcards for studying.
Format each flashcard clearly with a 'Front: [Question/Concept]' and 'Back: [Answer/Definition]'.

Context:
{context}

Flashcards:"""
    else:
        prompt = f"""Generate 5-10 useful flashcards for studying the topic of '{topic}'.
Format each flashcard clearly with a 'Front: [Question/Concept]' and 'Back: [Answer/Definition]'.

Flashcards:"""

    model = _get_genai().GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    return response.text

def get_youtube_recommendations(vector_store, global_search=False, topic=None):
    """Generates optimal YouTube search queries and links based on the context or a specific topic."""
    if not global_search and vector_store:
        # Retrieve a broad summary of the document context to figure out what it's about
        context = get_rag_context(vector_store, "What are the main topics discussed here?", k=4)
        prompt = f"""Based on the following study materials, what are 3 highly specific, highly effective YouTube search queries a student should use to find visual learning aids or video essays about this exact subject matter?
Format the output as a clean, engaging Markdown list. For each recommendation, provide:
1. The search query in bold
2. A brief 1-sentence reason why this search term helps explain the notes.
3. A clickable markdown hyperlink to YouTube search: `[Search on YouTube](https://www.youtube.com/results?search_query=THE+QUERY+HERE)`

Context:
{context}

Recommendations:"""
    else:
        topic_str = f"the topic of {topic}" if topic else "general science and history"
        prompt = f"""What are 3 highly specific, highly effective YouTube search queries a student should use to find the best educational videos, documentaries, or visual learning aids about {topic_str}?
Format the output as a clean, engaging Markdown list. For each recommendation, provide:
1. The search query in bold
2. A brief 1-sentence reason why this search term is great for learning.
3. A clickable markdown hyperlink to YouTube search: `[Search on YouTube](https://www.youtube.com/results?search_query=THE+QUERY+HERE)`

Recommendations:"""

    model = _get_genai().GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    return response.text

def analyze_knowledge_gaps(vector_store, incorrect_items, global_search=False):
    """Analyzes incorrect quiz answers and provides targeted review materials."""
    # incorrect_items should be a list of dicts: [{'question': '...', 'user_answer': '...', 'correct_answer': '...'}]
    if not incorrect_items:
        return "Great job! You didn't get any questions wrong."
        
    gaps_str = ""
    for idx, item in enumerate(incorrect_items):
        gaps_str += f"{idx+1}. Question: {item['question']}\n   Your Answer: {item['user_answer']}\n   Correct Answer: {item['correct_answer']}\n\n"
        
    if not global_search and vector_store:
        # Use the specific questions to grab targeted context
        search_query = " ".join([item['question'] for item in incorrect_items])
        context = get_rag_context(vector_store, search_query, k=5)
        
        prompt = f"""You are an AI Study Tutor analyzing a student's incorrect quiz answers. 
Based on the following original study materials, help the student understand *why* they got these specific questions wrong and provide a highly targeted, 1-2 paragraph mini-lesson on these exact concepts to patch their knowledge gap.

Context from study materials:
{context}

Student's Incorrect Answers:
{gaps_str}

Format your response as a friendly, encouraging Markdown report titled "🧠 Knowledge Gap Analysis". Use headers for each concept they missed, briefly explain the correct concept from the text, and gently clarify their misunderstanding. Keep it concise but highly educational."""
    else:
        prompt = f"""You are an AI Study Tutor analyzing a student's incorrect quiz answers on a general knowledge quiz. 
Please help the student understand *why* they got these specific questions wrong and provide a highly targeted, 1-2 paragraph mini-lesson on these exact concepts to patch their knowledge gap based on your general knowledge.

Student's Incorrect Answers:
{gaps_str}

Format your response as a friendly, encouraging Markdown report titled "🧠 Knowledge Gap Analysis". Use headers for each concept they missed, briefly explain the correct concept, and gently clarify their misunderstanding. Keep it concise but highly educational."""

    model = _get_genai().GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    return response.text

def generate_study_plan(subjects, total_hours, custom_topics=""):
    """Generates a structured study schedule based on the user's current subjects and topics."""
    if not subjects and not custom_topics:
        subjects_str = "General Studies"
    else:
        subjects_str = ", ".join([sub['name'] for sub in subjects])
        if custom_topics:
            subjects_str += f", and additionally focus heavily on: {custom_topics}"
        
    prompt = f"""You are an expert AI Study Planner. A student has {total_hours} hours available to study this week.
Their specific study goals for this week are to cover: {subjects_str}.

Please generate a highly structured, realistic, and optimized Markdown study schedule for the week.
Break down the {total_hours} hours reasonably across the days of the week, allocating time to the specific subjects listed.
Include short, actionable goals for each study block (e.g., "Review flashcards", "Read Chapter 1", "Practice Quiz").

Format the output cleanly with Headers for each Day, and bullet points for the tasks. Make it encouraging and practical."""

    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    return response.text
