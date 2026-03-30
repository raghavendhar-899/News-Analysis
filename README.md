# News-Analysis (Scraping Pipeline)

News scraping and sentiment analysis pipeline for the News Analysis platform ("stocks.ai"). Fetches news from Google News, filters by stock relevance using Ollama, summarizes articles, and assigns sentiment scores (−10 to +10).

## Quick Start

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt / pip install -r requirements.txt
python3 run.py
```

Create `.env`:
```
DATABASE_URL=mongodb+srv://...
OLLAMA_MODEL=llama3.2
```

```bash
python run.py
```

## Pipeline

1. **Scrape** — Google News links for each company
2. **Verify** — Filter by stock relevance (Ollama)
3. **Scrape** — Full article content (Selenium)
4. **Analyze** — Summarize & sentiment score (Ollama)
5. **Store** — MongoDB (per-company collections)

## Endpoints

| Path | Description |
|------|-------------|
| `POST /start` | Start scraping for all companies |
| `GET /test` | Health check |
| `GET /health` | Liveness |

to start the pipeline: curl -X POST http://127.0.0.1:8081/start   

## Prerequisites

- Python 3.11
- MongoDB
- Ollama + model (e.g. `llama3.2`)
- Chrome/Chromium

---

**Full documentation:** See [DOCUMENTATION.md](./DOCUMENTATION.md) for the complete platform guide (News-Analysis + news-analysis-api + news-analysis-ui).
