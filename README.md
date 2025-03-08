# 🚀 DynamicKnowledgeAssistant

DynamicKnowledgeAssistant is a powerful Streamlit-based web application that empowers you to create dynamic knowledge bases using PDFs, PDF URLs, and website links. With the integration of Agentic AI, Groq models, and a PostgreSQL-based vector database, this assistant provides intelligent, AI-driven responses to your queries.

# ✨ Features

📂 Multiple Knowledge Sources: Upload PDFs, provide PDF URLs, or enter website links.

🤖 AI-Powered Chat Interface: Ask questions and get instant, intelligent responses.

💾 Vector Database Integration: Leverages PgVector for embedding and efficient storage.

🖥️ Modern UI: Built with Streamlit for a smooth and clean user experience.

# 🛠 Tech Stack

Python 🐍

Streamlit 🌐

Agentic AI (Phi) 🤖

Groq Models 🧠

PostgreSQL with PgVector 🗃️

Gemini Embedder ✨

Docker 🐳

# 🚧 Setup Instructions

📋 Prerequisites

Python 3.8+

Docker Desktop

# ⚙️ Installation

Clone the Repository
```
git clone https://github.com/yourusername/DynamicKnowledgeAssistant.git
cd DynamicKnowledgeAssistant
```

Create a Virtual Environment
```
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

Install Dependencies

pip install -r requirements.txt

Setup Environment Variables
Create a .env file with the following variables:

```
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key
DB_URL=postgresql+psycopg://ai:ai@localhost:5532/ai
```

🐳 Docker Desktop Setup (Bash Terminal)
```
docker run -d \
  -e POSTGRES_DB=ai \
  -e POSTGRES_USER=ai \
  -e POSTGRES_PASSWORD=ai \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v pgvolume:/var/lib/postgresql/data \
  -p 5532:5432 \
  --name pgvector \
  phidata/pgvector:16
```

Run the Application
```
streamlit run app.py
```

# 💡 Usage

Upload a PDF, provide a PDF URL, or enter a website link.

Click on 'Load Knowledge Base' to initialize the AI model.

Start asking questions using the chat interface.

