# TruthLayer AI - PDF Fact Checker

TruthLayer AI is a fact-checking utility built with Streamlit and Google Gemini. It extracts factual claims from PDF documents and cross-references them against real-time search results to categorize each claim as **Verified**, **Inaccurate**, or **False**.

---

## Features

- **PDF Text Parsing**: In-memory text extraction using `PyMuPDF` with built-in validation for size limits (up to 10MB) and scanned documents.
- **Factual Claim Mining**: Utilizes the Google Gemini 2.5 Flash API to parse document text and isolate verifiable factual assertions (statistics, dates, percentages, financial values, and technical configurations) while filtering out subjective opinions or marketing fluff.
- **Real-Time Verification**: Coordinates live search queries via DuckDuckGo with an optional direct REST API fallback to Tavily Search.
- **Credibility Analysis**: Cross-references extracted assertions against web search evidence to output verification classifications, source attribution logs, and corrected fact statements.
- **Interactive UI**: A dashboard built in Streamlit featuring summary metrics, claim categorization lists, and expandable evidence panels.
- **CSV Export**: Consolidates fact-checking results and source links into a standard CSV download.

---

## Project Structure

```text
fact-check-agent/
│
├── app.py                      # Main Streamlit dashboard interface
├── requirements.txt            # Python dependencies
├── README.md                   # Setup and usage instructions
│
├── services/
│   ├── __init__.py
│   ├── pdf_parser.py           # Text parsing and size validation
│   ├── claim_extractor.py     # Gemini structural factual claim extraction
│   ├── search_service.py       # DuckDuckGo and Tavily API search coordinator
│   ├── verifier.py             # Gemini claim verification and correction service
│
├── utils/
│   ├── __init__.py
│   ├── report_generator.py     # Tabular Pandas CSV reporting utility
│   ├── helpers.py              # CSS styles and custom UI widgets
│
└── .streamlit/
    └── secrets.toml.example    # Configuration template for local Streamlit secrets
```

---

## Installation & Setup

### Prerequisites
- Python 3.9 or higher
- A Google Gemini API Key (available from [Google AI Studio](https://aistudio.google.com/))
- An optional Tavily Search API Key (available from [Tavily](https://tavily.com/))

### 1. Clone the project and navigate to the directory:
```bash
cd fact-check-agent
```

### 2. Set up a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install the dependencies:
```bash
pip install -r requirements.txt
```

### 4. Configure API credentials:
You can provide your API credentials in one of two ways:
- **Local Config**: Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in your keys:
  ```toml
  GEMINI_API_KEY = "your-api-key"
  TAVILY_API_KEY = "your-api-key"
  ```
- **UI Input**: Paste the credentials directly into the sidebar inputs of the app when running.

### 5. Run the application:
```bash
streamlit run app.py
```

---

## Streamlit Cloud Deployment

1. Push your repository to GitHub (ensure `requirements.txt` is at the root level).
2. Go to [share.streamlit.io](https://share.streamlit.io/) and connect your repository.
3. Open **Advanced Settings** before deploying and add your API keys inside the **Secrets** section in TOML format:
   ```toml
   GEMINI_API_KEY = "your-actual-api-key"
   TAVILY_API_KEY = "your-actual-api-key"
   ```
4. Click **Deploy!**
