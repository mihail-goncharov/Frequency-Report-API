# FastAPI Report Export

Service that accepts a text file, lemmatizes Russian words, and exports frequency statistics to XLSX.

## Features
- Streaming file processing (supports large files)
- Lemmatization with `pymorphy3`
- XLSX export with per-line counts
- Background queue with fixed workers to keep API responsive
- DDD‑style structure

## Requirements
- Python 3.10+
- Windows/Linux/macOS

## Setup
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Run
```powershell
uvicorn main:app --reload
```
Open docs: `http://127.0.0.1:8000/docs`

## Endpoints
### POST /public/report/export
Upload a .txt file.

Response:
```json
{
  "job_id": "uuid",
  "status": "PENDING"
}
```

### GET /public/report/status/{job_id}
Check job status.

### GET /public/report/download/{job_id}
Download XLSX when status is DONE.

## Example Input (txt)
```text
Житель города пришёл домой
Жители города были у дома
Жителем быть нелегко
```

### Output (XLSX)
Columns:
- lemma
- total_count
- per_line_counts (comma-separated string like 0,11,32,0)

## Architecture
- app/domain: tokenization + lemmatization
- app/application: report building logic
- app/infrastructure: queue, job store, xlsx writer
- app/api: FastAPI routes

## Notes
- Uploaded files: `data/uploads`
- Generated reports: `data/outputs`
- Job metadata is stored in-memory (restarting the app clears job statuses)