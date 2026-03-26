# News Analysis Platform — Comprehensive Documentation

**Version:** 1.0  
**Last Updated:** March 2025  

This document provides comprehensive documentation for the News Analysis platform—a stock news scraping, sentiment analysis, and visualization system composed of three interconnected projects.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture](#2-architecture)
3. [Project 1: News-Analysis (Scraping Pipeline)](#3-project-1-news-analysis-scraping-pipeline)
4. [Project 2: news-analysis-api (Backend API)](#4-project-2-news-analysis-api-backend-api)
5. [Project 3: news-analysis-ui (Frontend)](#5-project-3-news-analysis-ui-frontend)
6. [Data Flow & Integration](#6-data-flow--integration)
7. [Getting Started](#7-getting-started)
8. [Environment Variables Reference](#8-environment-variables-reference)
9. [Known Issues & Considerations](#9-known-issues--considerations)

---

## 1. System Overview

The News Analysis platform ("stocks.ai") helps users:

- **Search** companies by name with autocomplete
- **View** news articles with sentiment scores (−10 to +10)
- **Track** aggregate sentiment scores per company
- **Visualize** stock price charts with multiple timeframes
- **Add** new companies for tracking

### The Three Projects

| Project | Purpose | Technology |
|---------|---------|------------|
| **News-Analysis** | Scraping pipeline: fetches news, filters by stock relevance, summarizes, scores sentiment | Python, Flask, Selenium, Ollama |
| **news-analysis-api** | Backend API: serves news from DB, stock data, user auth | Python, Flask, PyMongo, yfinance |
| **news-analysis-ui** | Frontend dashboard | React, Tailwind CSS, Chart.js |

All three share the same **MongoDB** database for persistence.

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NEWS ANALYSIS PLATFORM                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────┐      ┌─────────────────┐       ┌─────────────────┐    │
│   │  news-analysis  │────► │ news-analysis-  │ ◄──── │  news-analysis  │    │
│   │      -ui        │      │      api        │       │   (Pipeline)    │    │
│   │  (React :3000)  │      │  (Flask :8080)  │       │  (Flask :8081)  │    │
│   └─────────────────┘      └──────┬──────────┘       └────────┬────────┘    │
│            │                         │                        │             │
│            │                         │                        │             │
│            │                         ▼                        ▼             │
│            │                    ┌────────────┐          ┌────────────┐      │
│            │                    │  yfinance  │          │  Ollama    │      │
│            │                    │ (stock API)│          │ (local LLM)│      │
│            │                    └────────────┘          └────────────┘      │
│            │                         │                        │             │
│            │                         │                        │             │
│            │                         ▼                        ▼             │
│            │                    ┌────────────────────────────────┐          │
│            │                    │           MongoDB              │          │
│            │                    │  (companies, users, articles)  │          │
│            │                    └────────────────────────────────┘          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```


### Data Flow

1. **News-Analysis** (pipeline): Scrapes Google News → filters with Ollama → scrapes full articles → summarizes & scores with Ollama → writes to MongoDB
2. **news-analysis-api**: Reads news from MongoDB, fetches stock data from yfinance, serves UI
3. **news-analysis-ui**: Calls API for company data, news, and stock charts

---

## 3. Project 1: News-Analysis (Scraping Pipeline)

**Path:** `News-Analysis/`  
**Role:** Fetches news, filters by stock relevance, summarizes, and assigns sentiment scores.

### Directory Structure

```
News-Analysis/
├── app/
│   ├── __init__.py           # Flask app factory, CORS, blueprints
│   ├── main.py               # Core pipeline: scrape → verify → analyze
│   ├── api/
│   │   └── news.py           # /start, /test, /health endpoints
│   ├── repository/
│   │   ├── article.py        # MongoDB article CRUD (per-company collections)
│   │   └── company.py        # MongoDB company CRUD
│   ├── services/
│   │   ├── analyze.py       # Summarization & sentiment scoring (Ollama)
│   │   ├── scrape.py        # Google News scraping, article scraping (Selenium)
│   │   └── verify.py        # Stock-relevance filtering (Ollama)
│   └── utils/
│       └── database.py      # MongoDB client
├── run.py                    # Flask entry point (host 0.0.0.0, port 8080)
├── requirements.txt
├── Dockerfile
└── .env                      # DATABASE_URL, OLLAMA_MODEL
```

### Pipeline Flow

```
process_company_articles() → get_article_data() → Scrape_links() → stockify() → scrape_article() 
   → get_summary() → get_score() → insert_article()
```

| Step | Function | Description |
|------|----------|-------------|
| 1 | `Scrape_links()` | Fetches news links from Google News for a company |
| 2 | `stockify()` | Filters headlines by stock relevance using Ollama |
| 3 | `scrape_article()` | Extracts full article body via Selenium + BeautifulSoup |
| 4 | `get_summary()` | Summarizes article in ≤30 words via Ollama |
| 5 | `get_score()` | Assigns sentiment score −10 to +10 via Ollama |
| 6 | `insert_article()` | Stores in MongoDB (per-company collection) |

### Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | `process_company_articles()`, `start()`, `calculate_score()`, `get_article_data()` |
| `app/services/analyze.py` | `get_summary()`, `get_score()` — uses `OLLAMA_MODEL` |
| `app/services/scrape.py` | `Scrape_links()`, `scrape_article()` — Selenium, webdriver_manager |
| `app/services/verify.py` | `stockify()` — filters by stock relevance |

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/start` | Starts scraping for all companies (long-running) |
| GET | `/test` | Returns "Up and running" |
| GET | `/health` | Health check (200) |

### Dependencies (requirements.txt)

- `flask`, `flask_cors` — Web framework
- `pymongo`, `python-dotenv`, `certifi` — MongoDB
- `requests`, `bs4` — HTTP & HTML
- `selenium`, `webdriver_manager` — Browser automation
- `ollama` — Local LLM calls
- `torch`, `transformers` — Optional BART summarization
- `thread6`, `simplejson`, `databases`, `TIME-python`

### Running

```bash
cd News-Analysis
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Create .env with DATABASE_URL, OLLAMA_MODEL
python run.py              # Listens on http://0.0.0.0:8080
```

**CLI pipeline (no server):**
```bash
cd app
python -c "from main import start; start()"
```

**Docker:**
```bash
docker build -t news-analysis .
docker run -p 8080:8080 news-analysis
```
*Note: Dockerfile copies only `app/` and uses `flask run`; `run.py` is not in the image. Set `FLASK_APP` if needed.*

### Prerequisites

- Python 3.11
- MongoDB (Atlas or local)
- Ollama with model (e.g. `llama3.2`) matching `OLLAMA_MODEL`
- Chrome/Chromium for Selenium

---

## 4. Project 2: news-analysis-api (Backend API)

**Path:** `news-analysis-api/`  
**Role:** Serves company news, stock data, and user authentication to the UI.

### Directory Structure

```
news-analysis-api/
├── app/
│   ├── __init__.py          # App factory, blueprint registration, CORS
│   ├── api/
│   │   ├── auth.py          # /auth/signup, /auth/login
│   │   ├── users.py         # /me (JWT-protected)
│   │   ├── news.py          # Company news, suggestions, newcompany
│   │   └── stockdata.py     # Stock price data (yfinance)
│   ├── repository/
│   │   ├── article.py       # Article CRUD
│   │   ├── company.py       # Company CRUD
│   │   └── user.py          # User CRUD
│   ├── services/
│   │   └── auth_service.py  # Registration, login, JWT
│   └── utils/
│       ├── database.py      # MongoDB connection
│       └── security.py      # Password hashing, JWT validation
├── run.py                   # Entry point
├── requirements.txt
└── .env                     # DATABASE_URL, JWT_SECRET_KEY
```

### API Endpoints

#### News & Companies

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/<companyname>` | News for company; returns `{Data, score, yfinance_ticker}` |
| POST | `/newcompany` | Add company: `{name, ticker, location}` |
| GET | `/suggestions?query=<str>` | Company name suggestions for search |
| GET | `/test` | "Up and running" |
| GET | `/health` | Health check (200) |

#### Stock Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/stockprice/<ticker>/<timeframe>` | Historical stock data |

**Timeframes:** `1D`, `5D`, `1M`, `6M`, `YTD`, `1Y`, `5Y`, `MAX`

#### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Register: `{email, password}` |
| POST | `/auth/login` | Login: `{email, password}` → JWT |

#### Users (Protected)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/me` | Current user (requires `x-access-token` header) |

### Dependencies

- `flask`, `flask_cors` — Web
- `pymongo`, `python-dotenv`, `certifi` — MongoDB
- `bcrypt` — Password hashing
- `yfinance` — Stock data
- `requests`, `simplejson`, `thread6`, `TIME-python`

### Running

```bash
cd news-analysis-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Create .env with DATABASE_URL, JWT_SECRET_KEY
python run.py    # Listens on http://0.0.0.0:8080
```

---

## 5. Project 3: news-analysis-ui (Frontend)

**Path:** `news-analysis-ui/`  
**Role:** React dashboard for searching companies, viewing news, sentiment scores, and stock charts.

### Directory Structure

```
news-analysis-ui/
├── public/
│   ├── index.html
│   ├── manifest.json
│   └── robots.txt
├── src/
│   ├── components/
│   │   ├── AddCompany.js    # Modal to add new companies
│   │   ├── NavBar.js        # Top navigation
│   │   ├── NewsFeed.js      # News list with scores
│   │   ├── ScoreDisplay.js  # Sentiment score badge
│   │   ├── SearchBar.js     # Search with autocomplete
│   │   └── StockChart.js    # Price chart (Chart.js)
│   ├── pages/
│   │   ├── Home.js          # Landing page
│   │   └── Company.js       # Company detail view
│   ├── App.js               # Routing
│   └── index.js             # Entry point
├── package.json
├── tailwind.config.js
└── .env                     # REACT_APP_API_URL
```

### Routes

| Path | Component | Description |
|------|-----------|-------------|
| `/` | Home | Search bar |
| `/company/:companyname` | Company | News, chart, sentiment |
| `/health` | Home | Alias |
| `/chart` | StockChart | Standalone chart |

### Key Components

| Component | Purpose |
|-----------|---------|
| **SearchBar** | Type-ahead suggestions from `/suggestions`, navigates to company |
| **NewsFeed** | Renders articles with title, summary, link, date, score |
| **ScoreDisplay** | Sentiment badge (−10 to +10) with color coding |
| **StockChart** | Line chart with 1D, 5D, 1M, 6M, YTD, 1Y, 5Y, MAX |
| **AddCompany** | Modal: name, ticker, location → POST `/newcompany` |

### API Integration

Base URL: `REACT_APP_API_URL` or `http://localhost:8080`

| Endpoint | Used By |
|----------|---------|
| `GET /{companyName}` | Company.js |
| `GET /suggestions?query=` | SearchBar.js |
| `POST /newcompany` | AddCompany.js |
| `GET /stockprice/{ticker}/{timeframe}` | StockChart.js |

### Dependencies

- `react`, `react-dom` — UI
- `react-router-dom` — Routing
- `chart.js`, `react-chartjs-2` — Charts
- `react-modal`, `react-toastify` — Modals & notifications
- `@fortawesome/fontawesome-free`, `react-icons` — Icons
- `tailwindcss` — Styling

### Running

```bash
cd news-analysis-ui
npm install
# .env: REACT_APP_API_URL=http://127.0.0.1:8080
npm start    # http://localhost:3000
```

---

## 6. Data Flow & Integration

### MongoDB Collections

| Collection | Description |
|------------|-------------|
| `companies` | `name`, `ticker`, `locations`, `score`, `primary_location` |
| `users` | User accounts (auth) |
| `<company_name>` | One collection per company for articles |

### Article Schema (per-company collection)

- `title`, `link`, `date`, `summary`, `score`
- TTL index on `date`: `expireAfterSeconds=345600` (4 days)

### Company Flow

1. User adds company via UI → API `POST /newcompany` → MongoDB `companies`
2. News-Analysis pipeline runs (`/start` or CLI) → scrapes, analyzes → writes articles to `<company_name>` collection
3. User views company in UI → API `GET /<companyname>` → returns articles + score from MongoDB
4. Stock chart → API `GET /stockprice/<ticker>/<timeframe>` → yfinance

---

## 7. Getting Started

### Full System Setup

1. **MongoDB**  
   Create cluster (e.g. MongoDB Atlas) and obtain `DATABASE_URL`.

2. **Ollama** (for News-Analysis pipeline)  
   ```bash
   ollama pull llama3.2
   ```

3. **news-analysis-api** (primary API for UI)
   ```bash
   cd news-analysis-api
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   echo "DATABASE_URL=<your_mongo_uri>" > .env
   echo "JWT_SECRET_KEY=<random_secret>" >> .env
   python run.py
   ```

4. **news-analysis-ui**
   ```bash
   cd news-analysis-ui
   npm install
   echo "REACT_APP_API_URL=http://127.0.0.1:8080" > .env
   npm start
   ```

5. **News-Analysis** (optional — for scraping)
   - Run on a **different port** (e.g. 8081) to avoid conflict with API
   - Or run as scheduled job / separate service
   ```bash
   cd News-Analysis
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   # .env: DATABASE_URL, OLLAMA_MODEL=llama3.2
   # Edit run.py port to 8081 if needed
   python run.py
   ```
   - Trigger scraping: `curl http://localhost:8081/start`

### Port Summary

| Service | Default Port | Note |
|---------|--------------|------|
| news-analysis-api | 8080 | Used by UI |
| news-analysis-ui | 3000 | React dev server |
| News-Analysis | 8080 | Change to 8081 if running with API |

---

## 8. Environment Variables Reference

### News-Analysis

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | MongoDB connection string |
| `OLLAMA_MODEL` | Yes | Ollama model name (e.g. `llama3.2`) |

### news-analysis-api

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | MongoDB connection string |
| `JWT_SECRET_KEY` | Yes | Secret for JWT signing |

### news-analysis-ui

| Variable | Required | Description |
|----------|----------|-------------|
| `REACT_APP_API_URL` | No | API base URL (default: `http://localhost:8080`) |

---

## 9. Known Issues & Considerations

### News-Analysis

1. **Missing modules:** `app/__init__.py` imports `auth` and `users` from `app.api`, but only `news.py` exists. The app will fail to start. **Fix:** Remove these imports or add stub modules.
2. **Dockerfile:** Copies only `app/`, not `run.py`. `FLASK_APP` is not set. Update Dockerfile to include `run.py` and set `FLASK_APP=run:app`.
3. **Test code in scrape.py:** Lines 210–211 may call `scrape_article()` on import; remove or guard with `if __name__ == '__main__'`.

### news-analysis-ui

1. **Route case:** `SearchBar` may navigate to `/Company/...` while `App.js` uses `/company/:companyname`. Ensure case consistency.
2. **Placeholder stats:** Company page shows fixed values for price, day change, market cap, P/E ratio instead of live API data.
3. **Unused deps:** `pusher-js`, `pushid` are installed but not used.

### General

- **Port conflict:** News-Analysis and news-analysis-api both use 8080. Run one on a different port when running locally.
- **CORS:** API allows `*` origins; restrict in production.
- **Auth:** JWT tokens are sent via `x-access-token` header.

---

## Quick Reference

| What | Where |
|------|-------|
| Trigger scraping | `GET http://localhost:8081/start` (News-Analysis) |
| Company news | `GET http://localhost:8080/<companyname>` |
| Stock data | `GET http://localhost:8080/stockprice/<ticker>/<timeframe>` |
| Add company | `POST http://localhost:8080/newcompany` |
| Auth header | `x-access-token: <jwt>` |
| Database name | `news_analysis` |

---

*For questions or contributions, refer to the individual project READMEs and source code.*
