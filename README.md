# TwinMind Frontend

Bilingual English/Arabic Streamlit interface for the TwinMind cognitive journaling MVP.

## Included

- Dashboard with sentiment overview.
- Multi-source entry capture: journal, email, meeting minutes, thoughts, emotions, insights, voice-note transcripts, calendar context and other entries.
- Arabic/English interface with RTL support.
- AI analysis results: summary, sentiment, emotions, well-being suggestion and constructive response suggestion.
- Cognitive timeline.
- Memory recall.
- Seven-day reflection.

## Run

Start the backend first, then:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export API_BASE_URL=http://localhost:8000
streamlit run app.py
```

On Windows PowerShell:

```powershell
$env:API_BASE_URL="http://localhost:8000"
streamlit run app.py
```

## Deployment

Deploy this repository to Streamlit Community Cloud or another Python host and set `API_BASE_URL` to the public URL of the deployed `twinmind-backend` API.

> Sentiment and emotion signals are AI interpretations for reflection and decision support; they are not clinical diagnoses.
