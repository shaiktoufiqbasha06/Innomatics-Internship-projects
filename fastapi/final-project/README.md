# 🎬 Movie Ticket Booking System — FastAPI

A complete FastAPI backend project is built as part of the Innomatics Research Labs internship.

## 🚀 How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
uvicorn main:app --reload

# 3. Open Swagger UI
http://127.0.0.1:8000/docs
```

## 📋 Features Implemented

| Day | Concept | Endpoints |
|-----|---------|-----------|
| Day 1 | GET APIs | `/`, `/movies`, `/movies/{id}`, `/movies/summary/stats` |
| Day 2 | POST + Pydantic | `/movies` (POST), `/bookings` (POST) |
| Day 3 | Helper Functions + Query Params | `/movies/filter/options`, `/bookings`, `/bookings/{id}` |
| Day 4 | CRUD Operations | PUT `/movies/{id}`, DELETE `/movies/{id}`, DELETE `/bookings/{id}` |
| Day 5 | Multi-step Workflow | `/cart/add` → `/orders` → `/checkin` |
| Day 6 | Search, Sort, Pagination | `/movies/search/keyword`, `/movies/sort/results`, `/movies/paginate/list`, `/movies/browse/all` |

## 🗂️ Project Structure

```
fastapi-movie-ticket-booking/
├── main.py
├── requirements.txt
├── README.md
└── screenshots/
    ├── Q1_home_route.png
    ├── Q2_get_all_movies.png
    └── ... (Q1–Q20)
```

## 🛠️ Tech Stack
- **FastAPI** — Web framework
- **Pydantic** — Data validation
- **Uvicorn** — ASGI server
- **Swagger UI** — API testing
