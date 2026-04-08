# AI Job Market Intelligence Engine
A sophisticated data engineering and LLM-powered pipeline designed to scrape, structure, and analyze the AI job market. This project demonstrates high-level Python proficiency, moving beyond simple automation into a robust RAG-ready (Retrieval-Augmented Generation) architecture.

Overview
This repository hosts an automated engine that monitors the evolving AI job landscape. It navigates complex web environments to extract job data, validates it through strict schemas, and prepares it for semantic search and AI-driven candidate matching.

TECHNICAL STACK
- Language: Python 3.12+ (Focus on OOP, Type Hinting, and modular design)
- Data Validation: Pydantic V2 (Ensuring 100% schema integrity)
- AI Integration: Google Gemini API (GenAI) for semantic analysis and candidate-job matching
- Vector Infrastructure: Optimized for Vector Databases (Pinecone/ChromaDB)

SYSTEM ARCHITECTURE:

The pipeline follows a modular ETL (Extract, Transform, Load) + AI Analysis pattern, ensuring data integrity at every stage through strict Pydantic modeling.

1. Data Acquisition & Concurrency (scrape_aijn.py)
- The AIscraper class orchestrates the high-speed extraction of job data.
- Asynchronous Execution: Utilizes aiohttp and asyncio.gather to concurrently fetch detailed tech stacks, responsibilities, and benefits for dozens of job listings simultaneously, drastically reducing execution time.
- Resilient Parsing: Uses BeautifulSoup to navigate dynamic HTML structures and extract deep-link information from individual job postings.

2. The Data Integrity Layer (job_record.py)
- All scraped data is instantly funneled into the JobRecord Pydantic model.
- Validation Gate: This model acts as a quality control layer, ensuring that essential fields (like id and title) are present and that optional fields (like salary or tech_stack) are handled gracefully without breaking the downstream pipeline.

3. Vector Ingestion & Semantic Search (build_job_database.py)
- The dbBuilder class manages the lifecycle of the persistent ChromaDB vector store.
- Document Synthesis: Implements a custom create_document_string method that transforms raw database records into high-context natural language blobs, specifically optimized for embedding models.
- Hybrid Storage: Splits data between "Documents" (for semantic search) and "Metadatas" (for efficient filtering and UI display).
- Profile Matching: Queries the vector database using a candidate's profile to retrieve the Top-3 most relevant roles based on mathematical distance (similarity).

4. AI Analysis Agent (agent.py & orchestrator.py)
- The final stage uses the CareerMatchAgent to provide human-like reasoning over the data.
- Structured Reasoning: Leverages Gemini (via google-genai) to compare the candidate's profile against the ChromaDB results.
- JSON Constraints: Forces the LLM to return a structured JobAnalysis Pydantic object, ensuring the "Fit Summary" and "Actionable Gaps" can be programmatically displayed or stored.
- Fault Tolerance: The orchestrator.py manages the agent's execution, featuring specific try-except handling for 503 Service Unavailable errors to maintain pipeline stability during high-demand periods.

ENGINEERING HIGHLIGHTS
- Schema-First Design: By using Pydantic models as the "source of truth," the pipeline is immune to the common "garbage in, garbage out" issues found in basic web scrapers.
- Vector-Ready Pipelines: Includes a custom create_document_string utility that transforms structured data into natural language blobs optimized for embedding models.
- Robustness: Implements logic to handle high-demand API spikes and server-side unavailability gracefully.

INSTALLATION

# Clone the repository
git clone https://github.com/[Your-Username]/AI_job_tracker.git

# Install dependencies
pip install -r requirements.txt

# Configure your .env with Google API Keys
echo "GOOGLE_API_KEY=your_key_here" > .env

# Run the system
python orchestrator.py
