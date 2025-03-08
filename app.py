import streamlit as st
from typing import Optional, List
from phi.agent import Agent
from phi.model.groq import Groq
from phi.storage.agent.postgres import PgAgentStorage
from phi.knowledge.pdf import PDFKnowledgeBase, PDFReader
from phi.knowledge.website import WebsiteKnowledgeBase
from phi.knowledge.combined import CombinedKnowledgeBase
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.vectordb.pgvector import PgVector2
from phi.embedder.google import GeminiEmbedder

import os
from dotenv import load_dotenv
import tempfile
import groq

# Load environment variables
load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Check for API keys
if not os.environ["GROQ_API_KEY"] or not os.environ["GOOGLE_API_KEY"]:
    st.error("Missing API Keys! Check your .env file.")
    st.stop()

# Database URL
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

# Centered title and description
st.markdown(
    """
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: #4a90e2; font-size: 3em;">Dynamic Knowledge Base Assistant</h1>
        <p style="font-size: 1.2em; color: #555;">
            Upload PDFs, provide URLs, or enter website links to create a custom knowledge base. 
            Then ask questions and receive AI-powered responses instantly!
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Input section
st.markdown("### 📝 Input Sources")

pdf_url_input = st.text_input(
    "Enter PDF URL (Optional)", 
    placeholder="e.g., https://example.com/document.pdf"
)

uploaded_pdf_file = st.file_uploader(
    "Upload PDF File (Optional)", 
    type=["pdf"]
)

website_url_input = st.text_input(
    "Enter Website URL (Optional)", 
    placeholder="e.g., https://example.com"
)

# Load Knowledge Base Button
if st.button("Load Knowledge Base", type="primary"):
    st.session_state["load_knowledge_base"] = True

# Knowledge base creation functions
def create_pdf_url_knowledge_base(pdf_url: str) -> Optional[PDFUrlKnowledgeBase]:
    if pdf_url:
        return PDFUrlKnowledgeBase(
            model=Groq(id="llama3-70b-8192"),
            urls=[pdf_url],
            vector_db=PgVector2(
                collection="pdf_url",
                db_url=db_url,
                embedder=GeminiEmbedder()
            ),
        )
    return None

def create_local_pdf_knowledge_base(uploaded_file) -> Optional[PDFKnowledgeBase]:
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_pdf_path = temp_file.name
        
        return PDFKnowledgeBase(
            model=Groq(id="llama3-70b-8192"),
            path=temp_pdf_path,
            vector_db=PgVector2(
                collection="pdf_documents",
                db_url=db_url,
                embedder=GeminiEmbedder()
            ),
            reader=PDFReader(chunk=True),
        )
    return None

def create_website_knowledge_base(website_url: str) -> Optional[WebsiteKnowledgeBase]:
    if website_url:
        return WebsiteKnowledgeBase(
            model=Groq(id="llama3-70b-8192"),
            urls=[website_url],
            max_links=10,
            vector_db=PgVector2(
                collection="website_documents",
                db_url=db_url,
                embedder=GeminiEmbedder()
            ),
        )
    return None

def create_combined_knowledge_base() -> Optional[CombinedKnowledgeBase]:
    sources = []

    if pdf_url_input:
        sources.append(create_pdf_url_knowledge_base(pdf_url_input))

    if uploaded_pdf_file:
        sources.append(create_local_pdf_knowledge_base(uploaded_pdf_file))

    if website_url_input:
        sources.append(create_website_knowledge_base(website_url_input))

    if sources:
        return CombinedKnowledgeBase(
            sources=[s for s in sources if s],
            vector_db=PgVector2(
                embedder=GeminiEmbedder(),
                collection="combined_documents",
                db_url=db_url,
            ),
        )
    return None

# Initialize storage and load knowledge base
storage = PgAgentStorage(table_name="website_assistant", db_url=db_url)

@st.cache_resource
def load_knowledge_base() -> Optional[CombinedKnowledgeBase]:
    knowledge_base = create_combined_knowledge_base()
    if knowledge_base:
        knowledge_base.load(recreate=True)
    return knowledge_base

# Load knowledge base
knowledge_base = None
if st.session_state.get("load_knowledge_base", False):
    knowledge_base = load_knowledge_base()
    if knowledge_base:
        st.success("Knowledge Base Loaded Successfully!")
    else:
        st.warning("No knowledge bases available. Please configure at least one valid source.")

# Chat Interface
st.markdown("### 💬 Chat with Assistant")

user_input = st.text_input(
    "Ask a question:", 
    placeholder="e.g., What is machine learning?"
)
run_id: Optional[str] = None

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if user_input and knowledge_base:
    assistant = Agent(
        model=Groq(id="llama3-70b-8192", embedder=GeminiEmbedder()),
        run_id=run_id,
        user_id="user",
        knowledge_base=knowledge_base,
        storage=storage,
        show_tool_calls=False,
        search_knowledge=True,
        read_chat_history=True,
        max_tokens=5000
    )

    try:
        response = assistant.run(user_input)
        clean_response = response.content if hasattr(response, 'content') else str(response)

        st.session_state["chat_history"].append(("You", user_input))
        st.session_state["chat_history"].append(("Assistant", clean_response))
    
    except groq.APIStatusError as e:
        if "Request too large" in str(e):
            st.error("The request is too large for the model to handle. Please shorten your query or provide more specific input.")
        else:
            st.error(f"An error occurred: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

    user_input = ""

# Display chat history with minimalistic style
for speaker, text in st.session_state["chat_history"]:
    if speaker == "You":
        st.markdown(f"<div style='text-align: left; color: #333;'><strong>You:</strong> {text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align: left; color: #4a90e2;'><strong>Assistant:</strong> {text}</div>", unsafe_allow_html=True)

# Custom CSS for modern UI
st.markdown("""
    <style>
        button[aria-label="Load Knowledge Base"] {
            background-color: #4a90e2;
            color: white;
            border-radius: 10px;
            padding: 10px 20px;
            border: none;
            font-size: 16px;
            cursor: pointer;
        }
        button[aria-label="Load Knowledge Base"]:hover {
            background-color: #357ab8;
        }
        input[type="text"] {
            padding: 10px;
            font-size: 16px;
            border: 1px solid #ddd;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)
