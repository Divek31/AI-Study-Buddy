import io

def process_pdf(pdf_bytes):
    """Extracts text from a PDF file byte stream."""
    from PyPDF2 import PdfReader
    pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def create_vector_store(text):
    """
    Splits text into chunks, generates embeddings, and creates a Chroma vector store.
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma

    # Split text into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    
    # Initialize HuggingFace embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Create and return a Chroma vector store
    # Using an ephemeral collection for the session
    vector_store = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        collection_name="study_notes"
    )
    
    return vector_store
