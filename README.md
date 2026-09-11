# AI HR Recruitment Assistant

**Capabilities:** Agent + Tools + RAG

An automated HR screening tool that takes a candidate's resume, matches it against a given target job role, outputs a match score, highlights matching and missing skills, and generates customized technical and behavioral interview questions.

## Setup & Running

1. Ensure Ollama is running and model `llama3.2` is pulled:
   ```bash
   ollama pull llama3.2
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```
