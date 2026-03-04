import streamlit as st
import time
import streamlit.components.v1 as components
from database import init_db, create_user, verify_user, update_study_streak, add_subject, get_subjects, get_materials, add_quiz, get_quizzes, add_flashcard, get_flashcards, add_xp, award_badge, log_study_session, get_study_analytics, add_search_history, get_search_history
from database import init_db, create_user, verify_user, update_study_streak, add_subject, get_subjects, get_materials, add_quiz, get_quizzes, add_flashcard, get_flashcards, add_xp, award_badge, log_study_session, get_study_analytics, add_search_history, get_search_history, add_study_plan, get_study_plans
from document_processor import process_pdf, create_vector_store
from ai_assistant import initialize_gemini, answer_question, feynman_explain, generate_quiz, summarize_notes, generate_flashcards, get_youtube_recommendations, analyze_knowledge_gaps, generate_study_plan
from exporter import create_pdf, create_audio

st.set_page_config(page_title="AI Study Buddy", page_icon="🎓", layout="wide")

# Initialize DB
init_db()

def apply_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Lexend:wght@400;500;700&display=swap');
        
        /* Global Background and Text */
        html {
            scroll-behavior: smooth;
        }
        .stApp {
            background: #0b0f19; /* Solid dark background to match 3D containers */
            color: #FFFFFF;
            font-family: 'Inter', sans-serif;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Lexend', sans-serif;
            color: #ffffff;
            font-weight: 700;
        }
        
        .stMarkdown, p {
            color: #cbd5e1 !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: rgba(11, 15, 25, 0.95);
            color: #e2e8f0;
            border-right: 1px solid rgba(255,255,255,0.05);
        }

        /* Solid 3D Container (Replaced Glass effect) */
        .glass-container {
            padding: 10px;
            margin-bottom: 15px;
        }
        
        .glass-container:hover {
            /* Removed hover effects */
        }
        
        /* Input Fields */
        div.stTextInput input, div.stFileUploader section {
            background-color: rgba(0,0,0,0.3) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 8px !important;
            color: #ffffff !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        div.stTextInput input:focus {
            border-color: #EC4186 !important;
            box-shadow: 0 0 0 1px #EC4186 !important;
        }
        
        /* Pill Buttons Custom Tab System */
        .stButton > button.tab-btn {
            background-color: transparent;
            color: #94a3b8;
            border: none;
            border-radius: 50px;
            padding: 8px 24px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            transition: all 0.3s ease;
        }
        
        .stButton > button.tab-btn:hover {
            color: #ffffff;
            background-color: rgba(255,255,255,0.05);
        }
        
        /* Primary Action Buttons (e.g. Explain, Ask, Active Tab, Login/Signup) */
        .stButton > button[kind="primary"] {
            background: linear-gradient(90deg, #EC4186 0%, #EE544A 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 50px !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(236, 65, 134, 0.4) !important;
        }

        .stButton > button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(238, 84, 74, 0.6) !important;
            filter: brightness(1.1);
        }
        
        /* Secondary Action Buttons (Glass look) */
        .stButton > button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.03) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            border-radius: 50px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton > button[kind="secondary"]:hover {
            background: rgba(255, 255, 255, 0.08) !important;
            border-color: rgba(236, 65, 134, 0.4) !important;
            box-shadow: 0 4px 15px rgba(236, 65, 134, 0.2) !important;
        }
        
        /* Animations */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
            animation: fadeInUp 1s ease-out forwards;
        }
        .animate-delay-1 { animation-delay: 0.2s; opacity: 0; }
        .animate-delay-2 { animation-delay: 0.4s; opacity: 0; }
        .animate-delay-3 { animation-delay: 0.6s; opacity: 0; }
        
        /* Typewriter text */
        .typewriter-text {
            display: inline-block;
            overflow: hidden;
            white-space: nowrap;
            border-right: 4px solid #EC4186;
            animation: typing 3.5s steps(40, end) forwards, blink 1s step-end infinite;
            top: 0;
            vertical-align: bottom;
            color: #FFFFFF;
        }
        
        @keyframes typing {
            from { top: 0; }
            to { top: 100%; }
        }
        @keyframes blink {
            50% { border-color: transparent; }
        }
        </style>
    """, unsafe_allow_html=True)

def landing_page():
    # Top Navigation Bar
    col_logo, col_login, col_signup = st.columns([8, 1, 1])
    with col_logo:
        st.markdown('<h3 style="margin-top: 5px;">🎓 AI Study Buddy</h3>', unsafe_allow_html=True)
    
    # State to toggle auth modal-like view
    if 'show_auth' not in st.session_state:
        st.session_state.show_auth = False
    if 'auth_action' not in st.session_state:
        st.session_state.auth_action = "Login"

    with col_login:
        if st.button("Log In", use_container_width=True, type="secondary"):
            st.session_state.show_auth = True
            st.session_state.auth_action = "Login"
            st.rerun()
    with col_signup:
        if st.button("Sign Up", use_container_width=True, type="primary"):
            st.session_state.show_auth = True
            st.session_state.auth_action = "Sign Up"
            st.rerun()

    st.markdown("---")

    # Conditionally render the Auth Form OR the Landing Page Body
    if st.session_state.show_auth:
        col_space1, col_form, col_space2 = st.columns([1, 2, 1])
        with col_form:
            st.markdown('<div class="glass-container animate-fade-in">', unsafe_allow_html=True)
            if st.session_state.auth_action == "Login":
                st.markdown("### Welcome Back")
                login_user = st.text_input("Username", key="login_user")
                login_pass = st.text_input("Password", type="password", key="login_pass")
                if st.button("Submit Login", type="primary", use_container_width=True):
                    user = verify_user(login_user, login_pass)
                    if user:
                        st.session_state.user = user
                        new_streak = update_study_streak(user['id'])
                        st.session_state.user['current_streak'] = new_streak
                        st.success("Login successful!")
                        time.sleep(0.5)
                        st.session_state.show_auth = False
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
            else:
                st.markdown("### Create Account")
                signup_user = st.text_input("Username", key="signup_user")
                signup_pass = st.text_input("Password", type="password", key="signup_pass")
                if st.button("Submit Sign Up", type="primary", use_container_width=True):
                    if signup_user and signup_pass:
                        if create_user(signup_user, signup_pass):
                            st.success("Account created successfully! Please log in.")
                            st.session_state.auth_action = "Login"
                            st.rerun()
                        else:
                            st.error("Username already exists.")
                    else:
                        st.warning("Please fill out all fields.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Back to Home", type="secondary"):
                st.session_state.show_auth = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Hero Section 3D (Vanta.js Halo)
        hero_html = """
        <!DOCTYPE html>
        <html>
        <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.net.min.js"></script>
        <style>
        body { margin: 0; padding: 0; overflow: hidden; color: white; font-family: 'Inter', sans-serif; }
        #vanta-canvas { 
            width: 100vw; 
            height: 100vh; 
            display: flex; 
            flex-direction: column;
            align-items: center; 
            justify-content: center; 
            text-align: center; 
        }
        h1 { 
            font-size: 5rem; 
            font-family: 'Lexend', sans-serif;
            font-weight: 800;
            margin-bottom: 20px;
            text-shadow: 0 4px 20px rgba(0,0,0,0.5);
            line-height: 1.2;
            opacity: 0;
            animation: fadeIn 1.5s ease-out forwards;
        }
        .highlight { 
            background: linear-gradient(90deg, #EC4186, #EE544A);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline-block;
            animation: float 6s ease-in-out infinite;
        }
        p { 
            font-size: 1.4rem; 
            color: #e2e8f0;
            top: 650px;
            margin: 0 auto;
            text-shadow: 0 2px 10px rgba(0,0,0,0.6);
            line-height: 1.6;
            opacity: 0;
            animation: fadeIn 1.5s ease-out 0.5s forwards;
        }
        /* Typewriter text */
        .typewriter-text {
            display: inline-block;
            overflow: hidden;
            white-space: nowrap;
            border-right: 4px solid #EC4186;
            width: 0; /* Start width at 0 for typing effect */
            animation: typing 3s steps(40, end) forwards, blink 0.75s step-end infinite;
            top: 0;
            vertical-align: bottom;
            color: #FFFFFF;
        }
        @keyframes typing { from { width: 0; } to { width: 100%; } }
        @keyframes blink { 50% { border-color: transparent; } }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }
        .quote {
            font-family: 'Inter', sans-serif;
            color: #94a3b8;
            font-weight: 400;
            font-size: 1.25rem;
            margin-top: 15px;
            font-style: italic;
            opacity: 0;
            animation: fadeIn 1.5s ease-out 1.5s forwards;
        }
        .quote strong {
            color: #cbd5e1;
            font-style: normal;
        }
        </style>
        </head>
        <body>
        <div id="vanta-canvas">
            <h1>Elevate your mind<br>
                <span class="highlight">Learn faster</span><br>
                <span style="display: inline-block; max-width: max-content;">
                    <span class="typewriter-text">with AI Study Buddy.</span>
                </span>
            </h1>
            <div class="quote">
                "Empowering your learning journey, one concept at a time."<br>
                <strong>Unlock your full potential with tools that adapt to how you learn best.</strong>
            </div>
            <p style="margin-top: 30px;">Step into the future of education.<br>
               Instantly transform your documents into interactive quizzes, Feynman explanations, and immersive audio guides.</p>
        </div>
        <script>
        VANTA.NET({
          el: "#vanta-canvas",
          mouseControls: true,
          touchControls: true,
          gyroControls: false,
          minHeight: 200.00,
          minWidth: 200.00,
          scale: 1.00,
          scaleMobile: 1.00,
          color: 0xec4186,
          backgroundColor: 0x05050f,
          points: 15.00,
          maxDistance: 24.00,
          spacing: 16.00,
          showDots: true
        })
        </script>
        </body>
        </html>
        """
        # Render the 3D Animation Header Full Page
        components.html(hero_html, height=750)
        
        # Call to action floating over the 3D hero
        st.markdown('<div style="margin-top: -200px; position: relative; z-index: 10; text-align: center;">', unsafe_allow_html=True)
        col_space1, col_btn, col_space2 = st.columns([1.5, 1, 1.5])
        with col_btn:
            if st.button("Get Started It's Free", type="primary", use_container_width=True):
                st.session_state.show_auth = True
                st.session_state.auth_action = "Sign Up"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br><br><br><br>", unsafe_allow_html=True)

        # Features Section
        st.markdown('<h2 style="text-align: center;" class="animate-fade-in animate-delay-1">Everything you need to succeed</h2><br>', unsafe_allow_html=True)
        fcol1, fcol2, fcol3 = st.columns(3)
        
        with fcol1:
            st.markdown("""
            <div class="glass-container animate-fade-in animate-delay-1" style="text-align: center; min-height: 250px;">
                <h1 style="font-size: 3rem; margin-bottom: 10px;">🧠</h1>
                <h3>Feynman Technique</h3>
                <p>Break down complex topics into simple analogies. Understand the 'why', not just the 'what'.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with fcol2:
            st.markdown("""
            <div class="glass-container animate-fade-in animate-delay-2" style="text-align: center; min-height: 250px;">
                <h1 style="font-size: 3rem; margin-bottom: 10px;">📝</h1>
                <h3>Smart Quizzes</h3>
                <p>Test your knowledge with AI-generated interactive quizzes instantly created from your notes.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with fcol3:
            st.markdown("""
            <div class="glass-container animate-fade-in animate-delay-3" style="text-align: center; min-height: 250px;">
                <h1 style="font-size: 3rem; margin-bottom: 10px;">⏱️</h1>
                <h3>Focus Sessions</h3>
                <p>Built-in Pomodoro timers and study planners to keep you on track and motivated.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br><br><br><br>", unsafe_allow_html=True)

def view_dashboard():
    st.header(f"Welcome back, {st.session_state.user['username']}! 👋")
    
    # Quick Start Learning Module
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    st.markdown("### 🚀 What do you want to learn today?")
    st.markdown("Type any topic below to get an instant AI overview and curated video recommendations.")
    
    col_qs1, col_qs2 = st.columns([4, 1])
    with col_qs1:
        quick_topic = st.text_input("Enter a topic (e.g., Quantum Physics, French Revolution, Python Classes)", label_visibility="collapsed", key="quick_start_topic")
    with col_qs2:
        start_btn = st.button("Learn Now", type="primary", use_container_width=True)
        
    if start_btn and quick_topic:
        with st.spinner(f"Generating overview and video recommendations for '{quick_topic}'..."):
            # Act as a global summary
            overview = summarize_notes(None, global_search=True, topic=quick_topic)
            youtube_links = get_youtube_recommendations(None, global_search=True, topic=quick_topic)
            
            # Save to history
            add_search_history(st.session_state.user['id'], quick_topic, overview, youtube_links)
            
            st.markdown("---")
            st.success(f"**Instant Overview: {quick_topic}**")
            st.markdown(overview)
            st.markdown("### 🎬 Recommended Videos")
            st.markdown(youtube_links)
            
            # Log the ambient study time
            log_study_session(st.session_state.user['id'], "quick_start", 2)
            xp_gained = 5
            state = add_xp(st.session_state.user['id'], xp_gained)
            st.session_state.user['xp'] = state['xp']
            st.session_state.user['level'] = state['level']
            st.toast(f"+{xp_gained} XP for curiosity! 🌟")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Search History
    search_history = get_search_history(st.session_state.user['id'])
    if search_history:
        st.markdown("### 🕒 Recent Searches")
        for item in search_history[:3]:
            with st.expander(f"Search: {item['query']} ({item['created_at'][:10]})"):
                st.markdown(item['overview_text'])
                st.markdown("#### 🎬 Recommended Videos")
                st.markdown(item['youtube_links'])
        st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    
    # Streak Card
    with col1:
        st.markdown('<div class="glass-container" style="text-align: center;">', unsafe_allow_html=True)
        st.markdown("### 🔥 Study Streak")
        st.markdown(f'<h1 style="color: #f59e0b; font-size: 4rem; margin: 0;">{st.session_state.user["current_streak"]}</h1>', unsafe_allow_html=True)
        st.markdown("<p>Days in a row</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Level Card
    with col2:
        st.markdown('<div class="glass-container" style="text-align: center;">', unsafe_allow_html=True)
        st.markdown("### ⭐ Level")
        st.markdown(f'<h1 style="color: #8b5cf6; font-size: 4rem; margin: 0;">{st.session_state.user["level"]}</h1>', unsafe_allow_html=True)
        xp = st.session_state.user['xp']
        progress = xp % 100
        st.progress(progress / 100.0)
        st.markdown(f"<p>{progress} / 100 XP to next level</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Badges Card
    with col3:
        st.markdown('<div class="glass-container" style="text-align: center;">', unsafe_allow_html=True)
        st.markdown("### 🏆 Badges")
        badges = st.session_state.user.get("badges", [])
        if not badges:
            st.markdown("<p style='margin-top:20px; color:#A0AEC0;'>Complete quizzes and focus sessions to earn badges!</p>", unsafe_allow_html=True)
        else:
            for badge in badges:
                st.markdown(f'<div style="background: rgba(236,65,134,0.2); padding: 5px; border-radius: 10px; margin-bottom: 5px; border: 1px solid #EC4186;">🎖️ {badge}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Overview
    st.markdown("### 📊 Your Study Overview")
    
    analytics_data = get_study_analytics(st.session_state.user['id'], days=7)
    if not analytics_data:
        st.info("No study sessions logged yet. Head to Focus Sessions or generate Quizzes to start tracking your time!")
        # Fallback empty chart
        import pandas as pd
        df = pd.DataFrame({"log_date": [], "total_minutes": []})
        st.bar_chart(df, x="log_date", y="total_minutes", x_label="Date", y_label="Minutes Studied")
    else:
        import pandas as pd
        df = pd.DataFrame(analytics_data)
        st.bar_chart(df, x="date", y="minutes", color="#EC4186", x_label="Date", y_label="Minutes Studied")

def view_subjects():
    st.header("📚 My Subjects")
    
    # Add new subject
    with st.expander("+ Add New Subject"):
        with st.form("add_sub_form"):
            new_sub_name = st.text_input("Subject Name (e.g., Biology 101)")
            sub_color = st.color_picker("Color Code", "#6366f1")
            if st.form_submit_button("Create Subject"):
                if new_sub_name:
                    add_subject(st.session_state.user['id'], new_sub_name, sub_color)
                    st.success(f"Added {new_sub_name}!")
                    st.rerun()
                
    # List subjects
    subjects = get_subjects(st.session_state.user['id'])
    if not subjects:
        st.info("You don't have any subjects yet. Create one above to get started!")
    else:
        st.write("---")
        for sub in subjects:
            with st.container():
                st.markdown(f'<div style="border-left: 5px solid {sub["color"]}; padding-left: 15px;"><h4>{sub["name"]}</h4></div>', unsafe_allow_html=True)
                if st.button(f"Open {sub['name']} Workspace", key=f"open_sub_{sub['id']}", type="secondary"):
                    st.session_state.active_subject = sub
                    st.session_state.nav_selection = "Subject Workspace"
                    st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

def view_subject_workspace():
    sub = st.session_state.active_subject
    st.button("← Back to Subjects", on_click=lambda: st.session_state.update(nav_selection="Subjects"))
    st.header(f"📖 {sub['name']} Workspace")
    
    # Fetch existing materials for this subject
    existing_materials = get_materials(subject_id=sub['id'])
    
    # Old legacy file upload logic directly ported for now
    uploaded_file = st.file_uploader("Upload Notes (PDF)", type=["pdf"])
    st.divider()

    global_search = st.toggle("Enable Global Search (Do not use notes)", value=False if (uploaded_file or existing_materials) else True)
    if not uploaded_file and not existing_materials and not global_search:
        st.warning("Please upload a PDF or enable Global Search to interact with the AI.")
        return
        
    vector_store = None
    
    # Check if we need to process a NEW file
    if uploaded_file is not None:
        if "vector_store" not in st.session_state or st.session_state.get("last_uploaded") != uploaded_file.name:
            with st.spinner("Saving to Library and generating local embeddings for this subject..."):
                pdf_bytes = uploaded_file.read()
                
                # 1. Save file to disk
                uploads_dir = os.path.join(os.getcwd(), 'uploads')
                os.makedirs(uploads_dir, exist_ok=True)
                file_path = os.path.join(uploads_dir, uploaded_file.name)
                
                # Avoid DB duplicate if user re-uploads same file
                is_duplicate = any(m['name'] == uploaded_file.name for m in existing_materials)
                if not is_duplicate:
                    with open(file_path, "wb") as f:
                        f.write(pdf_bytes)
                    # 2. Save to database
                    add_material(sub['id'], uploaded_file.name, file_path, "pdf")
                
                # 3. Process LLM
                text = process_pdf(pdf_bytes)
                if text.strip():
                    st.session_state.vector_store = create_vector_store(text)
                    st.session_state.last_uploaded = uploaded_file.name
                    st.sidebar.success(f"{uploaded_file.name} saved to Materials Library!")
                else:
                    st.sidebar.error("No extractable text found in the PDF.")
        
        if "vector_store" in st.session_state:
            vector_store = st.session_state.vector_store
            
    # Or check if we have an EXISTING file to load (simplified single file support for now)
    elif existing_materials:
        mat = existing_materials[0] # Grab first material
        if "vector_store" not in st.session_state or st.session_state.get("last_uploaded") != mat['name']:
             with st.spinner(f"Loading {mat['name']} from your Library..."):
                 try:
                     if mat['file_type'] == 'pdf':
                         with open(mat['file_path'], "rb") as f:
                             pdf_bytes = f.read()
                             text = process_pdf(pdf_bytes)
                             if text and text.strip():
                                 st.session_state.vector_store = create_vector_store(text)
                                 st.session_state.last_uploaded = mat['name']
                 except Exception as e:
                     st.error(f"Failed to load previous material: {e}")
                     
        if "vector_store" in st.session_state:
            vector_store = st.session_state.vector_store

    if vector_store is not None or global_search:
        # --- Custom Tab System ---
        col1, col2, col3, col4, col5, col6 = st.columns([1, 1.4, 1.1, 1.1, 1.3, 1.1])
        
        def set_tab(tab_name):
            st.session_state.active_tab = tab_name
            
        with col1:
             if st.button("📚 Q&A", on_click=set_tab, args=("Q&A",), use_container_width=True, type="secondary" if st.session_state.active_tab != "Q&A" else "primary"):
                 pass # State handles switch
        with col2:
             if st.button("🧠 Feynman Mode", on_click=set_tab, args=("Feynman Mode",), use_container_width=True, type="secondary" if st.session_state.active_tab != "Feynman Mode" else "primary"):
                 pass
        with col3:
             if st.button("📝 Quiz Gen", on_click=set_tab, args=("Quiz Gen",), use_container_width=True, type="secondary" if st.session_state.active_tab != "Quiz Gen" else "primary"):
                 pass
        with col4:
             if st.button("📋 Summary", on_click=set_tab, args=("Summary",), use_container_width=True, type="secondary" if st.session_state.active_tab != "Summary" else "primary"):
                 pass
        with col5:
             if st.button("🗂️ Flashcards", on_click=set_tab, args=("Flashcards",), use_container_width=True, type="secondary" if st.session_state.active_tab != "Flashcards" else "primary"):
                 pass
        with col6:
             if st.button("🎬 Visuals", on_click=set_tab, args=("Visuals",), use_container_width=True, type="secondary" if st.session_state.active_tab != "Visuals" else "primary"):
                 pass
                 
        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.active_tab == "Q&A":
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            st.markdown("<h3>Ask Questions</h3>", unsafe_allow_html=True)
            if global_search:
                st.markdown("Ask any question and get an answer based on **General AI Knowledge**.")
            else:
                st.markdown("Ask any question and get an answer based *strictly* on your **uploaded notes**.")
                
            user_question = st.text_input("What would you like to know?", key="qa_input")
            if st.button("Ask", type="primary"):
                if user_question:
                    with st.spinner("Thinking..."):
                        answer = answer_question(vector_store, user_question, global_search)
                        st.write(answer)
                else:
                    st.warning("Please enter a question.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        elif st.session_state.active_tab == "Visuals":
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            st.markdown("<h3>🎬 Visual Learning Links</h3>", unsafe_allow_html=True)
            if global_search:
                st.markdown("Need help visualizing a concept? The AI will generate highly targeted YouTube video search links based on general knowledge for you.")
            else:
                st.markdown("Need help visualizing these notes? The AI will scrape your current notes Context and generate optimal YouTube video search links strictly tailored towards this subject matter.")
            
            if st.button("🔍 Find Video Recommendations", type="primary"):
                with st.spinner("Analyzing context and generating optimized search queries..."):
                    recommendations = get_youtube_recommendations(vector_store, global_search)
                    st.markdown("---")
                    st.markdown(recommendations)
            st.markdown('</div>', unsafe_allow_html=True)
                    
        elif st.session_state.active_tab == "Feynman Mode":
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            st.markdown("<h3>Feynman Technique</h3>", unsafe_allow_html=True)
            st.markdown("Enter a complex topic, and I will explain it using simple analogies.")
            topic = st.text_input("What topic should I simplify?", key="feynman_input")
            if st.button("Explain", type="primary"):
                if topic:
                    with st.spinner("Simplifying..."):
                        explanation = feynman_explain(vector_store, topic, global_search)
                        st.write(explanation)
                else:
                    st.warning("Please enter a topic.")
            st.markdown('</div>', unsafe_allow_html=True)
                    
        elif st.session_state.active_tab == "Quiz Gen":
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            st.markdown("<h3>Automated Quiz</h3>", unsafe_allow_html=True)
            
            num_questions = st.slider("Number of Questions", 5, 15, 5, key="subject_quiz_count")
            
            if global_search:
                st.markdown(f"Generate an interactive {num_questions}-question quiz on any topic.")
                quiz_topic = st.text_input("What topic should the quiz cover?", value="General Knowledge", key="quiz_input")
            else:
                st.markdown(f"Generate an interactive {num_questions}-question quiz based on the key concepts in your notes.")
                quiz_topic = "notes"
            
            # Manage quiz state
            if 'quiz_data' not in st.session_state:
                st.session_state.quiz_data = None
            if 'quiz_submitted' not in st.session_state:
                st.session_state.quiz_submitted = False

            if st.button("Generate New Quiz", type="primary"):
                with st.spinner("Creating your interactive quiz..."):
                    quiz_json = generate_quiz(vector_store, global_search, quiz_topic, num_questions)
                    if quiz_json:

                        # Save to DB
                        sub_id = st.session_state.active_subject['id'] if not global_search else None
                        add_quiz(st.session_state.user['id'], sub_id, quiz_topic, quiz_json)
                        st.session_state.quiz_data = quiz_json
                        st.session_state.quiz_submitted = False
                        st.rerun()
                    else:
                        st.error("Failed to generate quiz. Please try again.")
            
            # Render Quiz form if data exists
            if st.session_state.quiz_data:
                st.markdown("---")
                quiz_data = st.session_state.quiz_data
                
                with st.form("quiz_form"):
                    user_answers = {}
                    for i, q in enumerate(quiz_data):
                        st.markdown(f"**Q{i+1}: {q['question']}**")
                        
                        if q['type'] == 'MCQ':
                            # Single choice
                            ans = st.radio(f"Select one answer for Q{i+1}", q['options'], key=f"q_{i}", index=None, label_visibility="collapsed")
                            user_answers[i] = [ans] if ans else []
                        elif q['type'] == 'MSQ':
                            # Multiple choice
                            st.caption("(Select all that apply)")
                            selected = []
                            for opt in q['options']:
                                if st.checkbox(opt, key=f"q_{i}_{opt}"):
                                    selected.append(opt)
                            user_answers[i] = selected
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                    submitted = st.form_submit_button("Submit Answers")
                    if submitted:
                        st.session_state.quiz_submitted = True
                        st.session_state.user_answers = user_answers
                        
                        # Gamification
                        score = 0
                        for i, q in enumerate(quiz_data):
                            correct_set = set(q['correct_answers'])
                            user_set = set(user_answers[i])
                            if correct_set == user_set and len(user_set) > 0:
                                score += 1
                        
                        xp_gained = score * 10
                        if xp_gained > 0:
                            state = add_xp(st.session_state.user['id'], xp_gained)
                            st.session_state.user['xp'] = state['xp']
                            st.session_state.user['level'] = state['level']
                            st.toast(f"+{xp_gained} XP! 🌟")
                            if state['leveled_up']:
                                st.toast(f"Level Up! You are now level {state['level']}! 🎉", icon="⭐")
                                
                        # Log 5 mins equivalent query time per quiz taken
                        log_study_session(st.session_state.user['id'], "quiz", 5)
                            
                        if score == len(quiz_data) and len(quiz_data) > 0:
                            if award_badge(st.session_state.user['id'], "Quiz Master"):
                                 st.toast("Unlocked 'Quiz Master' Badge! 🏆")
                                 if "Quiz Master" not in st.session_state.user['badges']:
                                     st.session_state.user['badges'].append("Quiz Master")
                        
                        st.rerun()
                
                # Show results if submitted
                if st.session_state.quiz_submitted:
                    st.markdown("### Quiz Results")
                    score = 0
                    user_answers = st.session_state.user_answers
                    incorrect_items = []
                    
                    for i, q in enumerate(quiz_data):
                        correct_set = set(q['correct_answers'])
                        user_set = set(user_answers[i])
                        is_correct = correct_set == user_set and len(user_set) > 0
                        
                        if is_correct:
                            score += 1

                    # Animation for score
                    if score == len(quiz_data):
                        st.balloons()
                        st.success(f"**Perfect Score! {score} / {len(quiz_data)}**")
                    elif score >= len(quiz_data) // 2:
                        st.snow()
                        st.info(f"**Good Job! {score} / {len(quiz_data)}**")
                    else:
                        st.warning(f"**Keep Studying! {score} / {len(quiz_data)}**")
                        
                    st.markdown("---")

                    # Reveal correct answers and explanations
                    for i, q in enumerate(quiz_data):
                        correct_set = set(q['correct_answers'])
                        user_set = set(user_answers[i])
                        is_correct = correct_set == user_set and len(user_set) > 0
                        
                        if is_correct:
                            st.success(f"**Q{i+1}: Correct!**")
                        else:
                            st.error(f"**Q{i+1}: Incorrect.**")
                            incorrect_items.append({
                                'question': q['question'],
                                'user_answer': ', '.join(user_answers[i]) if user_answers[i] else 'None',
                                'correct_answer': ', '.join(q['correct_answers'])
                            })
                            st.info(f"Your answer: {', '.join(user_answers[i]) if user_answers[i] else 'None'}\n\nCorrect answer: {', '.join(q['correct_answers'])}")
                        
                        st.markdown(f"> *Explanation: {q['explanation']}*")
                        st.markdown("---")
                        
                    # Knowledge Gap Analysis Feature
                    if incorrect_items:
                        st.markdown("### 🔍 Need Help?")
                        st.markdown("It looks like you struggled with a few concepts. The AI can analyze your mistakes against your notes and provide a personalized mini-lesson to patch your knowledge gaps.")
                        if st.button("Analyze Knowledge Gaps", type="primary"):
                            with st.spinner("Analyzing your mistakes..."):
                                gap_report = analyze_knowledge_gaps(vector_store, incorrect_items, global_search)
                                st.markdown("---")
                                st.markdown(gap_report)
                                
                                # Gamification for reviewing mistakes
                                xp_gained = 5
                                state = add_xp(st.session_state.user['id'], xp_gained)
                                st.session_state.user['xp'] = state['xp']
                                st.session_state.user['level'] = state['level']
                                st.toast(f"+{xp_gained} XP for reviewing mistakes! 🧠")

            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.active_tab == "Summary":
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            st.markdown("<h3>Note Summary & Audio</h3>", unsafe_allow_html=True)
            if global_search:
                 st.markdown("Generate a comprehensive summary of any topic.")
                 summary_topic = st.text_input("What topic should I summarize?", value="", key="summary_input")
            else:
                 st.markdown("Generate a comprehensive summary of the key takeaways in your uploaded notes.")
                 summary_topic = "notes"
                 
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                if st.button("📝 Generate Text Summary", type="primary", use_container_width=True):
                    with st.spinner("Summarizing..."):
                        summary = summarize_notes(vector_store, global_search, summary_topic)
                        st.session_state.current_summary = summary
                        
            with col_s2:
                if st.button("🔊 Generate Audio Guide (Notes-to-Voice)", type="secondary", use_container_width=True):
                    if 'current_summary' not in st.session_state:
                        with st.spinner("Summarizing first..."):
                            summary = summarize_notes(vector_store, global_search, summary_topic)
                            st.session_state.current_summary = summary
                    
                    with st.spinner("Converting Notes to Voice..."):
                        audio_b = create_audio(st.session_state.current_summary)
                        st.session_state.current_audio = audio_b
                        
            if 'current_summary' in st.session_state:
                st.markdown("---")
                st.markdown(st.session_state.current_summary)
                
            if 'current_audio' in st.session_state:
                st.audio(st.session_state.current_audio, format="audio/mp3")
                
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.active_tab == "Flashcards":
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            st.markdown("<h3>Flashcards</h3>", unsafe_allow_html=True)
            
            if global_search:
                st.markdown("Generate study flashcards for any topic.")
                topic = st.text_input("Topic for flashcards:", value="Python Programming", key="flashcards_input")
            else:
                st.markdown("Generate study flashcards from your notes.")
                topic = st.text_input("Specific topic for flashcards? (Optional)", value="key concepts and definitions", key="flashcards_input")
                
            if st.button("Generate Flashcards", type="primary"):
                with st.spinner("Creating flashcards..."):
                    flashcards = generate_flashcards(vector_store, topic, global_search)

                    # Save to DB
                    sub_id = st.session_state.active_subject['id'] if not global_search else None
                    add_flashcard(st.session_state.user['id'], sub_id, topic, flashcards)
                    st.markdown(flashcards)
            st.markdown('</div>', unsafe_allow_html=True)

def view_materials():
    st.header("🗂️ Materials Library")
    materials = get_materials(user_id=st.session_state.user['id'])
    
    if not materials:
        st.info("You haven't uploaded any materials yet. Go to your Subjects to add some!")
    else:
        for mat in materials:
            st.markdown(f'<div class="glass-container"><h4>{mat["name"]}</h4><p>Subject: {mat["subject_name"]} | Uploaded: {mat["uploaded_at"]}</p></div>', unsafe_allow_html=True)

def view_assessments():
    st.header("📝 Quizzes & Flashcards")
    st.markdown("Use the Global AI Knowledge base to generate instant quizzes or flashcards on any topic.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        search_topic = st.text_input("What do you want to study today?", placeholder="e.g. World War 2 history, Cellular Biology...")
        num_questions = st.slider("Number of Quiz Questions", 5, 15, 5, key="global_quiz_count")
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            quiz_btn = st.button("Generate Quiz", type="primary", use_container_width=True)
        with btn_col2:
            flash_btn = st.button("Generate Flashcards", type="secondary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    if quiz_btn and search_topic:
        with st.spinner(f"Generating quiz on {search_topic}..."):
            quiz_json = generate_quiz(None, global_search=True, topic=search_topic, num_questions=num_questions)

            if quiz_json:
                add_quiz(st.session_state.user['id'], None, search_topic, quiz_json)
                st.session_state.global_quiz_data = quiz_json
                st.session_state.global_quiz_submitted = False
            else:
                st.error("Failed to generate quiz.")
                
    if flash_btn and search_topic:
        with st.spinner(f"Generating flashcards for {search_topic}..."):
            flashcards = generate_flashcards(None, topic=search_topic, global_search=True)
            add_flashcard(st.session_state.user['id'], None, search_topic, flashcards)
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            st.markdown(flashcards)
            st.markdown('</div>', unsafe_allow_html=True)
            
    # Render global quiz state if exists
    if hasattr(st.session_state, 'global_quiz_data') and st.session_state.global_quiz_data:
        st.markdown("---")
        quiz_data = st.session_state.global_quiz_data
        
        with st.form("global_quiz_form"):
            user_answers = {}
            for i, q in enumerate(quiz_data):
                st.markdown(f"**Q{i+1}: {q['question']}**")
                
                if q['type'] == 'MCQ':
                    ans = st.radio(f"Select one answer for Q{i+1}", q['options'], key=f"global_q_{i}", index=None, label_visibility="collapsed")
                    user_answers[i] = [ans] if ans else []
                elif q['type'] == 'MSQ':
                    st.caption("(Select all that apply)")
                    selected = []
                    for opt in q['options']:
                        if st.checkbox(opt, key=f"global_q_{i}_{opt}"):
                            selected.append(opt)
                    user_answers[i] = selected
                st.markdown("<br>", unsafe_allow_html=True)
                
            submitted = st.form_submit_button("Submit Answers")
            if submitted:
                st.session_state.global_quiz_submitted = True
                st.session_state.global_user_answers = user_answers
                
                # Gamification
                score = 0
                for i, q in enumerate(quiz_data):
                    correct_set = set(q['correct_answers'])
                    user_set = set(user_answers[i])
                    if correct_set == user_set and len(user_set) > 0:
                        score += 1
                
                xp_gained = score * 10
                if xp_gained > 0:
                    state = add_xp(st.session_state.user['id'], xp_gained)
                    st.session_state.user['xp'] = state['xp']
                    st.session_state.user['level'] = state['level']
                    st.toast(f"+{xp_gained} XP! 🌟")
                    if state['leveled_up']:
                        st.toast(f"Level Up! You are now level {state['level']}! 🎉", icon="⭐")
                        
                # Log 5 mins equivalent query time per quiz taken
                log_study_session(st.session_state.user['id'], "global_quiz", 5)
                    
                if score == len(quiz_data) and len(quiz_data) > 0:
                    if award_badge(st.session_state.user['id'], "World Scholar"):
                         st.toast("Unlocked 'World Scholar' Badge! 🏆")
                         if "World Scholar" not in st.session_state.user['badges']:
                             st.session_state.user['badges'].append("World Scholar")
                
                st.rerun()
        
        if getattr(st.session_state, 'global_quiz_submitted', False):
            st.markdown("### Quiz Results")
            score = 0
            user_answers = st.session_state.global_user_answers
            incorrect_items = []
            
            for i, q in enumerate(quiz_data):
                correct_set = set(q['correct_answers'])
                user_set = set(user_answers[i])
                is_correct = correct_set == user_set and len(user_set) > 0
                
                if is_correct:
                    score += 1

            if score == len(quiz_data):
                st.balloons()
                st.success(f"**Perfect Score! {score} / {len(quiz_data)}**")
            elif score >= len(quiz_data) // 2:
                st.snow()
                st.info(f"**Good Job! {score} / {len(quiz_data)}**")
            else:
                st.warning(f"**Keep Studying! {score} / {len(quiz_data)}**")
                
            for i, q in enumerate(quiz_data):
                correct_set = set(q['correct_answers'])
                user_set = set(user_answers[i])
                is_correct = correct_set == user_set and len(user_set) > 0
                
                if is_correct:
                    st.success(f"**Q{i+1}: Correct!**")
                else:
                    st.error(f"**Q{i+1}: Incorrect.**")
                    incorrect_items.append({
                        'question': q['question'],
                        'user_answer': ', '.join(user_answers[i]) if user_answers[i] else 'None',
                        'correct_answer': ', '.join(q['correct_answers'])
                    })
                    st.info(f"Your answer: {', '.join(user_answers[i]) if user_answers[i] else 'None'}\n\nCorrect answer: {', '.join(q['correct_answers'])}")
                    
                st.markdown(f"> *Explanation: {q['explanation']}*")
                st.markdown("---")
                
            # Knowledge Gap Analysis Feature
            if incorrect_items:
                st.markdown("### 🔍 Need Help?")
                st.markdown("The AI can analyze your mistakes and provide a personalized global mini-lesson to patch your knowledge gaps.")
                if st.button("Analyze Knowledge Gaps", key="global_gap_btn", type="primary"):
                    with st.spinner("Analyzing your mistakes..."):
                        gap_report = analyze_knowledge_gaps(None, incorrect_items, global_search=True)
                        st.markdown("---")
                        st.markdown(gap_report)
                        
                        # Gamification for reviewing mistakes
                        xp_gained = 5
                        state = add_xp(st.session_state.user['id'], xp_gained)
                        st.session_state.user['xp'] = state['xp']
                        st.session_state.user['level'] = state['level']
                        st.toast(f"+{xp_gained} XP for reviewing mistakes! 🧠")

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader("Your Assessment History")
    tab_q, tab_f = st.tabs(["Saved Quizzes", "Saved Flashcards"])
    
    with tab_q:
        quizzes = get_quizzes(st.session_state.user['id'])
        if not quizzes:
            st.info("No saved quizzes yet. Generate some above or in your Subjects!")
        else:
            for q in quizzes:
                with st.expander(f"Quiz: {q['topic']} ({q['subject_name']}) - {q['created_at'][:10]}"):
                    try:
                        pdf_bytes = create_pdf(f"Quiz: {q['topic']}", q['data_json'], is_quiz=True)
                        st.download_button("📥 Download as PDF", data=pdf_bytes, file_name=f"quiz_{q['id']}.pdf", mime="application/pdf", key=f"dl_q_{q['id']}")
                        st.markdown("---")
                    except Exception as e:
                        st.error(f"Failed to generate PDF export: {e}")
                        
                    for i, item in enumerate(q['data_json']):
                        st.markdown(f"**Q{i+1}: {item['question']}**")
                        st.markdown(f"*Correct Answer:* {', '.join(item['correct_answers'])}")
                        st.markdown(f"*Explanation:* {item['explanation']}")
                        st.markdown("---")
                        
    with tab_f:
        flashcards = get_flashcards(st.session_state.user['id'])
        if not flashcards:
            st.info("No saved flashcards yet. Generate some above or in your Subjects!")
        else:
            for f in flashcards:
                with st.expander(f"Flashcards: {f['topic']} ({f['subject_name']}) - {f['created_at'][:10]}"):
                    dl_col1, dl_col2 = st.columns(2)
                    with dl_col1:
                        try:
                            pdf_bytes = create_pdf(f"Flashcards: {f['topic']}", f['data'], is_quiz=False)
                            st.download_button("📥 Download as PDF", data=pdf_bytes, file_name=f"flashcards_{f['id']}.pdf", mime="application/pdf", key=f"dl_f_{f['id']}")
                        except Exception as e:
                            st.error(f"Failed to generate PDF export: {e}")
                    with dl_col2:
                        try:
                            audio_bytes = create_audio(f['data'])
                            st.download_button("🔊 Download Audio Guide", data=audio_bytes, file_name=f"audio_{f['id']}.mp3", mime="audio/mpeg", key=f"dl_a_{f['id']}")
                        except Exception as e:
                            st.error(f"Failed to generate Audio export: {e}")
                    st.markdown("---")
                    st.markdown(f['data'])

def view_planner():
    st.header("📅 Study Planner")
    
    tab1, tab2 = st.tabs(["AI Auto-Schedule", "Saved Plans"])
    with tab1:
        st.markdown("### Generate Schedule with AI")
        st.write("Let Gemini analyze your specific learning goals and create an optimized study plan for the week.")
        
        # Gather subjects for multiselect
        subjects = get_subjects(st.session_state.user['id'])
        subject_names = [sub['name'] for sub in subjects]
        
        selected_subjects_names = st.multiselect("Which of your active Subjects do you want to include?", options=subject_names, default=subject_names)
        custom_topics = st.text_input("Any specific topics or exams to prepare for? (Optional)", placeholder="e.g. Midterm prep, Learn Next.JS, Read chapter 4...")
        
        hours = st.slider("How many hours can you study this week?", 1, 40, 10)
        
        if st.button("Generate Plan", type="primary"):
            with st.spinner("Analyzing subjects and generating your weekly schedule..."):
                # Filter original objects
                filtered_subjects = [s for s in subjects if s['name'] in selected_subjects_names]
                
                plan_md = generate_study_plan(filtered_subjects, hours, custom_topics=custom_topics)
                

                # Save to DB
                add_study_plan(st.session_state.user['id'], hours, plan_md)
                
                st.success("Plan generated and saved!")
                st.markdown("---")
                st.markdown(plan_md)
                st.balloons()
            
    with tab2:
        st.markdown("### Your Saved Study Plans")
        plans = get_study_plans(st.session_state.user['id'])
        
        if not plans:
            st.info("You haven't generated any study plans yet. Go to the Auto-Schedule tab to create one!")
        else:
            for plan in plans:
                with st.expander(f"Study Plan for {plan['hours']} Hours - {plan['created_at'][:10]}"):
                    st.markdown(plan['plan_markdown'])

def view_focus():
    st.header("⏱️ Focus Sessions")
    st.markdown("Use the Pomodoro technique to maintain deep focus.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass-container" style="text-align: center;">', unsafe_allow_html=True)
        minutes = st.selectbox("Select Duration (Minutes)", [15, 25, 45, 60], index=1)
        
        # State management for timer
        if 'timer_running' not in st.session_state:
            st.session_state.timer_running = False
            st.session_state.timer_end_time = 0
            st.session_state.timer_start_minutes = 0
            
        if not st.session_state.timer_running:
            if st.button("▶️ Start Focus Timer", type="primary", use_container_width=True):
                st.session_state.timer_running = True
                st.session_state.timer_start_minutes = minutes
                st.session_state.timer_end_time = time.time() + (minutes * 60)
                st.rerun()
        else:
            time_left = max(0, int(st.session_state.timer_end_time - time.time()))
            
            if time_left > 0:
                if st.button("⏹️ Cancel Timer", type="secondary", use_container_width=True):
                    st.session_state.timer_running = False
                    st.rerun()
            else:
                st.success("Session Complete! Claim your XP.")
                if st.button("🎁 Claim XP", type="primary", use_container_width=True):
                    # Gamification
                    xp_gained = st.session_state.timer_start_minutes * 2
                    state = add_xp(st.session_state.user['id'], xp_gained)
                    st.session_state.user['xp'] = state['xp']
                    st.session_state.user['level'] = state['level']
                    st.toast(f"+{xp_gained} Focus XP! 🌟")
                    
                    # Logs
                    log_study_session(st.session_state.user['id'], "focus_session", st.session_state.timer_start_minutes)
                    
                    if award_badge(st.session_state.user['id'], "Focus Champion"):
                         st.toast("Unlocked 'Focus Champion' Badge! 🏆")
                         if "Focus Champion" not in st.session_state.user['badges']:
                             st.session_state.user['badges'].append("Focus Champion")
                             
                    st.session_state.timer_running = False
                    st.balloons()
                    st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown("### Today's Stats")
        st.metric("Total Focus Time", "0 hrs")
        st.metric("Completed Sessions", "0")

def view_your_searches():
    st.header("🕒 Your Searches")
    st.markdown("Here you can find a history of all the past topics you have explored using the Quick Start module.")
    
    search_history = get_search_history(st.session_state.user['id'])
    
    if not search_history:
        st.info("You haven't searched for anything yet. Head to the Dashboard and try the Quick Start module!")
        return
        
    for item in search_history:
        with st.container():
            st.markdown(f'<div class="glass-container">', unsafe_allow_html=True)
            st.markdown(f"### 🔍 {item['query']}")
            st.caption(f"Searched on: {item['created_at'][:10]} at {item['created_at'][11:16]}")
            st.markdown("---")
            st.markdown("#### Overview")
            st.markdown(item['overview_text'])
            st.markdown("#### 🎬 Recommended Videos")
            st.markdown(item['youtube_links'])
            st.markdown('</div>', unsafe_allow_html=True)

def main():
    apply_custom_css()
    initialize_gemini("AIzaSyDvz0oEIgyvksHjhhEcaB2MEWsY0fmCQUg")
    
    # State initializations
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'nav_selection' not in st.session_state:
        st.session_state.nav_selection = "Dashboard"
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Q&A"

    # Auth Routing
    if not st.session_state.user:
        landing_page()
    else:
        # Authenticated Sidebar
        with st.sidebar:
            st.title("🎓 Study Buddy")
            st.markdown(f"**{st.session_state.user['username']}** | ⭐ Lvl {st.session_state.user['level']} | 🔥 {st.session_state.user['current_streak']} Day Streak")
            st.divider()
            
            # Global Background Timer Injection
            if st.session_state.get('timer_running', False):
                timer_end = st.session_state.get('timer_end_time', 0)
                import streamlit.components.v1 as components
                components.html(
                    f"""
                    <script>
                        var parentDoc = window.parent.document;
                        var existingTimer = parentDoc.getElementById("floating-timer");
                        if (!existingTimer) {{
                            existingTimer = parentDoc.createElement("div");
                            existingTimer.id = "floating-timer";
                            existingTimer.style.cssText = "position: fixed; top: 80px; right: 20px; background: linear-gradient(135deg, #a855f7 0%, #EC4186 100%); color: white; padding: 10px 20px; border-radius: 50px; font-family: 'Inter', sans-serif; font-weight: 800; font-size: 1.2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.5); z-index: 9999; transition: all 0.3s ease;";
                            parentDoc.body.appendChild(existingTimer);
                        }}
                        
                        var endTime = {timer_end} * 1000;
                        var timerInterval = setInterval(function() {{
                            var now = new Date().getTime();
                            var distance = endTime - now;
                            
                            var timerDiv = window.parent.document.getElementById("floating-timer");
                            if (!timerDiv) return;

                            if (distance < 0) {{
                                clearInterval(timerInterval);
                                timerDiv.innerHTML = "🎉 Focus Complete!";
                                timerDiv.style.background = "#10b981";
                            }} else {{
                                var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                                var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                                minutes = minutes < 10 ? "0" + minutes : minutes;
                                seconds = seconds < 10 ? "0" + seconds : seconds;
                                timerDiv.innerHTML = "⏱️ " + minutes + ":" + seconds;
                            }}
                        }}, 1000);
                    </script>
                    """,
                    height=0, width=0 # hidden iframe to inject JS onto parent document
                )
            
            nav_options = ["Dashboard", "Subjects", "Materials", "Quizzes & Flashcards", "Your Searches", "Study Planner", "Focus Sessions"]
            
            for opt in nav_options:
                # Highlight active selection
                btn_type = "primary" if st.session_state.nav_selection == opt else "secondary"
                if st.button(opt, use_container_width=True, type=btn_type):
                    st.session_state.nav_selection = opt
                    st.rerun()
            
            st.divider()
            if st.button("Log Out", use_container_width=True):
                st.session_state.user = None
                st.rerun()
                
        # Main View Routing
        nav = st.session_state.nav_selection
        if nav == "Dashboard":
            view_dashboard()
        elif nav == "Subjects":
            view_subjects()
        elif nav == "Subject Workspace":
             view_subject_workspace()
        elif nav == "Materials":
            view_materials()
        elif nav == "Quizzes & Flashcards":
            view_assessments()
        elif nav == "Study Planner":
            view_planner()
        elif nav == "Focus Sessions":
            view_focus()
        elif nav == "Your Searches":
            view_your_searches()

if __name__ == "__main__":
    main()
