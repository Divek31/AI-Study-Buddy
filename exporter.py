import io

def sanitize_text(text):
    """Sanitize unicode strings for fpdf's standard latin-1 core fonts."""
    if not isinstance(text, str):
        text = str(text)
    return text.encode('latin-1', 'replace').decode('latin-1')
def create_pdf(title, content, is_quiz=False):
    """
    Generates a PDF byte array from quiz data or markdown text.
    Uses 'fpdf2' which has native utf-8 support.
    """
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    
    # Use Helvetica which is standard and safe
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, sanitize_text(title), new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)
    
    pdf.set_font("helvetica", size=12)
    
    if is_quiz and isinstance(content, list):
        for i, q in enumerate(content):
            pdf.set_font("helvetica", 'B', 12)
            # FPDF requires string conversion and encode/decode to avoid character issues if using base FPDF, 
            # but fpdf2 handles unicode well.
            pdf.multi_cell(0, 8, sanitize_text(f"Q{i+1}: {q.get('question', '')}"))
            
            pdf.set_font("helvetica", '', 12)
            for opt in q.get('options', []):
                pdf.set_x(20) # 10mm indent
                pdf.multi_cell(0, 6, sanitize_text(f"- {opt}"))
                
            pdf.ln(2)
            pdf.set_font("helvetica", 'I', 11)
            # We strip unicode emojis or strange symbols just in case
            ans_str = ", ".join(q.get('correct_answers', []))
            expl_str = q.get('explanation', '')
            pdf.multi_cell(0, 6, sanitize_text(f"Answer: {ans_str}"))
            pdf.multi_cell(0, 6, sanitize_text(f"Explanation: {expl_str}"))
            pdf.ln(5)
    else:
        # For flashcards/summaries (text)
        text = str(content)
        # Strip basic markdown for cleaner PDF
        text = text.replace("**", "").replace("#", "")
        pdf.multi_cell(0, 6, sanitize_text(text))
        
    return pdf.output()

def create_audio(text):
    """
    Generates an MP3 byte array from text using Google TTS.
    """
    from gtts import gTTS
    tts = gTTS(text=str(text), lang='en')
    mp3_fp = io.BytesIO()
    # Write to BytesIO straight away to avoid writing physical files
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp.read()
