# LegalEase

AI-assisted legal document drafting app based on the supplied requirements PDF. Frontend: Streamlit. Backend: FastAPI. AI: Google Gemini. Exports: TXT, DOCX, PDF.

> LegalEase produces drafts, not legal advice. Verify all facts and have consequential documents reviewed by a qualified lawyer.

## Requirements
- Python 3.10+
- A Gemini API key
- VS Code (recommended)

## Setup (Windows PowerShell)
1. Extract the project and open the `LegalEase` folder in VS Code.
2. Create and activate a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If activation is blocked, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.
3. Install packages:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and add your Gemini API key. Keep `.env private; do not commit it.
5. Start the API in Terminal 1:
   ```powershell
   uvicorn main:app --reload
   ```
   Check `http://127.0.0.1:8000/` and interactive docs at `http://127.0.0.1:8000/docs`.
6. Start Streamlit in Terminal 2 (same virtual environment):
   ```powershell
   streamlit run app.py
   ```
   Open the local URL Streamlit prints (usually `http://localhost:8501`).

## Test
- Open the UI, enter document type, parties, effective date, jurisdiction, and terms.
- Click **Generate document**; confirm text appears in the editor.
- Edit a sentence and download TXT, DOCX, and PDF.
- Open the downloaded files and verify formatting and content.
- To test the backend independently, use `/docs` and POST `/generate` with:
  ```json
  {
    "document_type": "Non-Disclosure Agreement",
    "parties": "Person A (Disclosing Party), Company B (Receiving Party)",
    "terms": "Use information only for evaluation; Keep information confidential; Return materials upon request",
    "effective_date": "2026-10-02",
    "jurisdiction": "Tamil Nadu, India",
    "additional_instructions": ""
  }
  ```

## Troubleshooting
- **Missing API key:** confirm `.env` exists beside `main.py`, contains `GEMINI_API_KEY=...`, and restart Uvicorn.
- **Backend unavailable:** start Uvicorn before using Streamlit; check `LEGAL_EASE_API_URL` if the backend runs elsewhere.
- **Gemini errors:** verify the key, account access, model availability, quotas, and internet connection.
- **PDF logo issue:** use a standard PNG or JPEG. Logo is optional.

## Project structure
```text
LegalEase/
├── ai_core/
│   ├── __init__.py
│   └── gemini_generator.py
├── app.py
├── exporters.py
├── main.py
├── routes.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```
